from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uuid
import logging

from ..models import RunStatus
from ..services.run_service import RunService
from ..services.steel_service import SteelService
from ..sockets import emit_progress

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response models
class CreateRunRequest(BaseModel):
    flow_id: str = Field(..., min_length=1, description="UUID of the flow")
    user_id: str = Field(..., min_length=1, description="UUID of the user")


class CreateRunResponse(BaseModel):
    run_id: str
    session_url: str
    status: str = RunStatus.RUNNING


class GetRunResponse(BaseModel):
    run_id: str
    flow_id: str
    user_id: str
    status: str
    session_url: Optional[str] = None
    created_at: str
    updated_at: str


@router.post("/runs", response_model=CreateRunResponse, status_code=201)
async def create_run(request: CreateRunRequest):
    """Create a new run, initialize Steel.dev session, and return run details."""
    run_id = str(uuid.uuid4())
    run_service = RunService()
    steel_service = SteelService()

    try:
        # Create run (already committed to database)
        await run_service.create_run_with_transaction(run_id, request.flow_id, request.user_id)

        # Emit pending status event
        await emit_progress(
            run_id,
            {"status": "pending", "message": "Run created, initializing session"},
        )

        # Create Steel session
        session_data = await steel_service.create_session()

        if not session_data:
            # Update run status to FAILED
            await run_service.update_run_status(run_id, RunStatus.FAILED)
            raise HTTPException(
                status_code=500, detail="Failed to create browser session"
            )

        session_url = session_data.get("sessionViewerUrl")
        browser_session_id = session_data.get("id")

        # Create session record and update run
        await run_service.create_session_record(run_id, browser_session_id, session_url)
        await run_service.update_run_with_session(run_id, session_url, RunStatus.RUNNING)

        # Emit progress event via Socket.IO
        await emit_progress(
            run_id, {"status": "initialized", "session_url": session_url}
        )

        return CreateRunResponse(run_id=run_id, session_url=session_url)

    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        logger.error(f"Error creating run: {e}")
        try:
            await run_service.update_run_status(run_id, RunStatus.FAILED)
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")
        raise HTTPException(status_code=500, detail=f"Failed to create run: {str(e)}")




@router.get("/runs/{run_id}", response_model=GetRunResponse)
async def get_run(run_id: str):
    """Get details of a specific run by ID."""
    # Validate UUID format first
    try:
        uuid.UUID(run_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid run ID format")

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
        logger.error(f"Error getting run: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get run: {str(e)}")
