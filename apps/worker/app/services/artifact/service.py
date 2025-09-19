import logging
from collections.abc import AsyncGenerator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.artifact.errors import ArtifactNotFoundError, RunNotFoundError
from app.services.artifact.factory import storage_backend
from app.services.artifact.repository import ArtifactRepository

logger = logging.getLogger(__name__)


class ArtifactService:
    """Service for managing artifact file operations."""

    def __init__(self, repository: ArtifactRepository | None = None):
        self.repository = repository or ArtifactRepository()

    async def get_run_artifact_info(
        self, run_id: UUID, session: AsyncSession
    ) -> tuple[str, str]:
        """Get artifact information for a run.

        Returns:
            tuple: (storage_uri, filename)
        """
        run = await self.repository.get_run_with_artifact(session, run_id)

        if not run:
            error_msg = f"Run {run_id} not found"
            raise RunNotFoundError(error_msg)

        if not run.result_uri:
            error_msg = f"No artifact available for run {run_id}"
            raise ArtifactNotFoundError(error_msg)

        # Get file info from storage backend
        filename, _ = await storage_backend.get_file_info(run.result_uri)

        return run.result_uri, filename

    async def store_artifact(self, run_id: UUID, filename: str, content: bytes) -> str:
        """Store artifact using configured storage backend."""
        return await storage_backend.store(run_id, filename, content)

    async def retrieve_artifact(self, storage_uri: str) -> AsyncGenerator[bytes, None]:
        """Retrieve artifact using configured storage backend."""
        if not await storage_backend.exists(storage_uri):
            error_msg = "Artifact not found"
            raise ArtifactNotFoundError(error_msg)

        async for chunk in storage_backend.retrieve(storage_uri):
            yield chunk

    async def delete_artifact(self, storage_uri: str) -> bool:
        """Delete artifact using configured storage backend."""
        return await storage_backend.delete(storage_uri)
