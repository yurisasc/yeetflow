import logging
import mimetypes
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.services.artifact.errors import (
    ArtifactAccessError,
    ArtifactNotFoundError,
    RunNotFoundError,
)
from app.services.artifact.service import ArtifactService
from app.utils.filename import sanitize_filename

db_dependency = Depends(get_db_session)

logger = logging.getLogger(__name__)


router = APIRouter()


async def _get_file_generator(service: ArtifactService, storage_uri: str):
    """Async generator to stream artifact content."""
    try:
        async for chunk in service.retrieve_artifact(storage_uri):
            yield chunk
    except ArtifactNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.exception("Error streaming artifact")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Error streaming artifact file",
        ) from e


@router.get("/runs/{run_id}/artifact")
async def get_run_artifact(run_id: UUID, session: AsyncSession = db_dependency):
    """Stream the artifact produced by a run to the client."""
    service = ArtifactService()

    try:
        # Get artifact information using the service
        artifact_info = await service.get_run_artifact_info(run_id, session)
        artifact_path, filename, file_size = artifact_info

        # Determine content type based on file extension
        content_type, _ = mimetypes.guess_type(filename)
        if not content_type:
            content_type = "application/octet-stream"

        # Sanitize filename for Content-Disposition header
        ascii_filename, utf8_filename = sanitize_filename(filename)

        # Stream the file
        return StreamingResponse(
            _get_file_generator(service, artifact_path),
            media_type=content_type,
            headers={
                "Content-Disposition": (
                    f'attachment; filename="{ascii_filename}"; '
                    f"filename*=UTF-8''{utf8_filename}"
                ),
                "Content-Length": str(file_size),
                "Cache-Control": "no-cache",
            },
        )

    except RunNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    except ArtifactNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
    except ArtifactAccessError as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e)
        ) from e
