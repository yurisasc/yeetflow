import logging
from uuid import UUID, uuid4

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.models import RunStatus
from app.services.run_service import RunService
from app.services.steel_service import SteelService
from app.sockets import emit_progress

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class CreateRunRequest(BaseModel):
    flow_id: UUID = Field(..., description="UUID of the flow")
    user_id: UUID = Field(..., description="UUID of the user")


class CreateRunResponse(BaseModel):
    run_id: str
    session_url: str
    status: RunStatus = RunStatus.RUNNING


class GetRunResponse(BaseModel):
    run_id: str
    flow_id: str
    user_id: str
    status: RunStatus
    session_url: str | None = None
    created_at: str
    updated_at: str


@router.post("/runs", response_model=CreateRunResponse, status_code=201)
async def create_run(request: CreateRunRequest):
    """Create a new run, initialize Steel.dev session, and return run details."""
    run_id = str(uuid4())
    run_service = RunService()
    steel_service = SteelService()

    try:
        # Create run (already committed to database)
        await run_service.create_run_with_transaction(
            run_id,
            str(request.flow_id),
            str(request.user_id),
        )

        # Emit pending status event
        await emit_progress(
            run_id,
            {
                "status": RunStatus.PENDING.value,
                "message": "Run created, initializing session",
            },
        )

        # Create Steel session
        session_data = await steel_service.create_session()

        if not session_data:
            # Update run status to FAILED
            await run_service.update_run_status(run_id, RunStatus.FAILED)
            await emit_progress(
                run_id,
                {
                    "status": RunStatus.FAILED.value,
                    "message": "Failed to create browser session",
                },
            )
            raise HTTPException(
                status_code=500,
                detail="Failed to create browser session",
            )

        session_url = session_data.get("sessionViewerUrl")
        browser_session_id = session_data.get("id")

        if not session_url:
            # Mark run as failed if session URL is missing
            await run_service.update_run_status(run_id, RunStatus.FAILED)
            await emit_progress(
                run_id,
                {
                    "status": RunStatus.FAILED.value,
                    "message": "Session created without viewer URL",
                },
            )
            raise HTTPException(
                status_code=502,
                detail="Session created without viewer URL",
            )

        # Create session record and update run
        await run_service.create_session_record(run_id, browser_session_id, session_url)
        await run_service.update_run_with_session(
            run_id,
            session_url,
            RunStatus.RUNNING,
        )

        # Emit progress event via Socket.IO
        await emit_progress(
            run_id,
            {
                "status": RunStatus.RUNNING.value,
                "session_url": session_url,
                "message": "Session initialized",
            },
        )

        return CreateRunResponse(run_id=run_id, session_url=session_url)

    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        logger.exception("Error creating run")
        try:
            await run_service.update_run_status(run_id, RunStatus.FAILED)
        except Exception:
            logger.exception("Error during cleanup")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create run: {e!s}",
        ) from None


@router.get("/runs/{run_id}", response_model=GetRunResponse)
async def get_run(run_id: str):
    """Get details of a specific run by ID."""
    # Validate UUID format first
    try:
        UUID(run_id, version=4)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid run ID format") from None

    run_service = RunService()

    try:
        run = await run_service.get_run_by_id(run_id)

        if not run:
            raise HTTPException(status_code=404, detail="Run not found")

        return GetRunResponse(
            run_id=run["id"],
            flow_id=run["flow_id"],
            user_id=run["user_id"],
            status=run["status"],
            session_url=run["session_url"],
            created_at=run["created_at"],
            updated_at=run["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error getting run")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get run: {e!s}",
        ) from None
