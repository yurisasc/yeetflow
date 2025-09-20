import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models import (
    EventRead,
    RunCreate,
    RunRead,
    RunUpdate,
    SessionRead,
)
from app.services.run.errors import (
    InvalidFlowError,
    MissingSessionURLError,
    RunNotFoundError,
    SessionCreationFailedError,
)
from app.services.run.service import RunService

db_dependency = Depends(get_db_session)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/runs", response_model=RunRead, status_code=HTTPStatus.CREATED)
async def create_run(
    request: RunCreate,
    session: AsyncSession = db_dependency,
):
    """Create a new run, initialize Steel.dev session, and return run details."""
    service = RunService()
    try:
        return await service.create_run(request, session)
    except InvalidFlowError as e:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=str(e),
        ) from e
    except IntegrityError as e:
        # Handle foreign key constraint violations (e.g., invalid flow_id)
        if "FOREIGN KEY constraint failed" in str(e):
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail="Invalid flow_id: flow does not exist",
            ) from e
        # Handle other integrity errors
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid request data",
        ) from e
    except SessionCreationFailedError as e:
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
async def get_run(run_id: UUID, session: AsyncSession = db_dependency):
    """Get details of a specific run by ID."""
    service = RunService()
    try:
        return await service.get_run(run_id, session)
    except RunNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e


@router.get("/runs", response_model=list[RunRead])
async def list_runs(
    skip: int = Query(0, ge=0, le=1_000_000),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = db_dependency,
):
    """List all runs with pagination."""
    service = RunService()
    return await service.list_runs(session, skip, limit)


@router.get("/runs/{run_id}/sessions", response_model=list[SessionRead])
async def get_run_sessions(
    run_id: UUID,
    session: AsyncSession = db_dependency,
):
    """Get all sessions for a specific run."""
    service = RunService()
    try:
        return await service.get_run_sessions(run_id, session)
    except RunNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e


@router.get("/runs/{run_id}/events", response_model=list[EventRead])
async def get_run_events(run_id: UUID, session: AsyncSession = db_dependency):
    """Get all events for a specific run."""
    service = RunService()
    try:
        return await service.get_run_events(run_id, session)
    except RunNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e


@router.patch("/runs/{run_id}", response_model=RunRead)
async def update_run(
    run_id: UUID,
    request: RunUpdate,
    session: AsyncSession = db_dependency,
):
    """Update an existing run."""
    service = RunService()
    try:
        return await service.update_run(
            run_id, request.model_dump(exclude_unset=True), session
        )
    except RunNotFoundError as e:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=str(e)) from e
