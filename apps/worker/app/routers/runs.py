import logging
from datetime import UTC, datetime
from http import HTTPStatus
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.db import get_db_session
from app.models import (
    Event,
    EventRead,
    Run,
    RunCreate,
    RunRead,
    RunStatus,
    Session,
    SessionRead,
)
from app.services.steel_service import SteelService
from app.sockets import emit_progress

db_dependency = Depends(get_db_session)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/runs", response_model=RunRead, status_code=HTTPStatus.CREATED)
async def create_run(
    request: RunCreate,
    session: AsyncSession = db_dependency,
):
    """Create a new run, initialize Steel.dev session, and return run details."""
    run_id = uuid4()
    steel_service = SteelService()

    try:
        # Create run
        run = Run(
            id=run_id,
            flow_id=request.flow_id,
            user_id=request.user_id,
            status=RunStatus.PENDING,
        )
        session.add(run)
        await session.commit()
        await session.refresh(run)

        # Emit pending status event
        await emit_progress(
            str(run_id),
            {
                "status": RunStatus.PENDING.value,
                "message": "Run created, initializing session",
            },
        )

        # Create Steel session
        session_data = await steel_service.create_session()

        if not session_data:
            # Update run status to FAILED
            run.status = RunStatus.FAILED
            run.error = "Failed to create browser session"
            session.add(run)
            await session.commit()
            await emit_progress(
                str(run_id),
                {
                    "status": RunStatus.FAILED.value,
                    "message": "Failed to create browser session",
                },
            )
            raise HTTPException(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                detail="Failed to create browser session",
            )

        session_url = session_data.get("sessionViewerUrl")
        browser_session_id = session_data.get("id")

        if not session_url:
            # Mark run as failed if session URL is missing
            run.status = RunStatus.FAILED
            run.error = "Session created without viewer URL"
            session.add(run)
            await session.commit()
            await emit_progress(
                str(run_id),
                {
                    "status": RunStatus.FAILED.value,
                    "message": "Session created without viewer URL",
                },
            )
            raise HTTPException(
                status_code=HTTPStatus.BAD_GATEWAY,
                detail="Session created without viewer URL",
            )

        # Create session record and update run
        db_session = Session(
            id=uuid4(),
            run_id=run_id,
            browser_provider_session_id=browser_session_id,
            session_url=session_url,
            status="running",
        )
        session.add(db_session)

        # Update run
        run.status = RunStatus.RUNNING
        run.started_at = datetime.now(UTC)
        session.add(run)
        await session.commit()
        await session.refresh(run)

        # Emit progress event via Socket.IO
        await emit_progress(
            str(run_id),
            {
                "status": RunStatus.RUNNING.value,
                "session_url": session_url,
                "message": "Session initialized",
            },
        )

    except HTTPException:
        # Re-raise HTTPExceptions as-is
        raise
    except Exception as e:
        # Handle any other errors
        logger.exception("Error creating run")
        await session.rollback()
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to create run",
        ) from e
    else:
        return run


@router.get("/runs/{run_id}", response_model=RunRead)
async def get_run(run_id: UUID, session: AsyncSession = db_dependency):
    """Get details of a specific run by ID."""
    result = await session.execute(select(Run).where(Run.id == run_id))
    run = result.scalar_one_or_none()

    if not run:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Run not found")

    return run


@router.get("/runs", response_model=list[RunRead])
async def list_runs(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = db_dependency,
):
    """List all runs with pagination."""
    result = await session.execute(select(Run).offset(skip).limit(limit))
    return result.scalars().all()


@router.get("/runs/{run_id}/sessions", response_model=list[SessionRead])
async def get_run_sessions(
    run_id: UUID,
    session: AsyncSession = db_dependency,
):
    """Get all sessions for a specific run."""
    result = await session.execute(select(Session).where(Session.run_id == run_id))
    return result.scalars().all()


@router.get("/runs/{run_id}/events", response_model=list[EventRead])
async def get_run_events(run_id: UUID, session: AsyncSession = db_dependency):
    """Get all events for a specific run."""
    result = await session.execute(select(Event).where(Event.run_id == run_id))
    return result.scalars().all()
