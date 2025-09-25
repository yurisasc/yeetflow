import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MAX_RUN_LIST_LIMIT
from app.db import get_db_session
from app.models import (
    EventRead,
    RunContinue,
    RunCreate,
    RunCreateResponse,
    RunRead,
    RunUpdate,
    SessionRead,
    User,
    UserRole,
)
from app.services.flow.errors import FlowAccessDeniedError, FlowNotFoundError
from app.services.run.errors import (
    MissingSessionURLError,
    RunFinalizationError,
    SessionCreationFailedError,
)
from app.services.run.service import RunService
from app.utils.auth import get_current_user
from app.utils.run import ensure_run_access

db_dependency = Depends(get_db_session)
current_user_dependency = Depends(get_current_user)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/runs", response_model=RunCreateResponse, status_code=HTTPStatus.CREATED)
async def create_run(
    request: RunCreate,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Create a new run, initialize browser session, return run with session URL."""
    service = RunService()
    try:
        run, session_url = await service.create_run_with_user(
            request, current_user, session
        )

        return RunCreateResponse(
            id=run.id,
            flow_id=run.flow_id,
            user_id=run.user_id,
            status=run.status,
            started_at=run.started_at,
            ended_at=run.ended_at,
            error=run.error,
            created_at=run.created_at,
            updated_at=run.updated_at,
            session_url=session_url,
        )
    except FlowNotFoundError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=str(e),
        ) from e
    except FlowAccessDeniedError as e:
        logger.info("Access denied to flow: %s", str(e))
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN,
            detail="Access denied to flow",
        ) from e
    except IntegrityError as e:
        # Handle FK violations across dialects
        orig = getattr(e, "orig", None)
        msg = str(e).lower()
        is_fk = "foreign key" in msg or getattr(orig, "pgcode", "") == "23503"
        if is_fk:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid flow_id: flow does not exist",
            ) from e
        # Handle other integrity errors
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid request data",
        ) from e
    except (RunFinalizationError, SessionCreationFailedError) as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except MissingSessionURLError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_GATEWAY,
            detail=str(e),
        ) from e


@router.get("/runs/{run_id}", response_model=RunRead)
async def get_run(
    run_id: UUID,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Get details of a specific run by ID."""
    service = RunService()
    return await ensure_run_access(run_id, current_user, session, service)


@router.get("/runs", response_model=list[RunRead])
async def list_runs(
    skip: int = Query(0, ge=0, le=1_000_000),
    limit: int = Query(100, ge=1, le=MAX_RUN_LIST_LIMIT),
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """List runs with pagination. Regular users see only their runs, admins see all."""
    service = RunService()

    # Filter runs based on user role
    if current_user.role == UserRole.ADMIN:
        # Admins can see all runs
        return await service.list_runs(session, skip, limit)
    # Regular users can only see their own runs
    return await service.list_runs_for_user(current_user.id, session, skip, limit)


@router.get("/runs/{run_id}/sessions", response_model=list[SessionRead])
async def get_run_sessions(
    run_id: UUID,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Get all sessions for a specific run."""
    service = RunService()
    await ensure_run_access(run_id, current_user, session, service)
    return await service.get_run_sessions(run_id, session)


@router.get("/runs/{run_id}/events", response_model=list[EventRead])
async def get_run_events(
    run_id: UUID,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Get all events for a specific run."""
    service = RunService()
    await ensure_run_access(run_id, current_user, session, service)
    return await service.get_run_events(run_id, session)


@router.patch("/runs/{run_id}", response_model=RunRead)
async def update_run(
    run_id: UUID,
    request: RunUpdate,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Update an existing run."""
    service = RunService()
    await ensure_run_access(run_id, current_user, session, service)
    try:
        return await service.update_run(
            run_id, request.model_dump(exclude_unset=True), session
        )
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e)) from e


@router.post("/runs/{run_id}/continue", response_model=RunRead)
async def continue_run(
    run_id: UUID,
    request: RunContinue,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Continue a run that is awaiting input."""
    service = RunService()
    await ensure_run_access(run_id, current_user, session, service)
    try:
        return await service.continue_run(run_id, request, session)
    except ValueError as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e)) from e
