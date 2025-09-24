import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MAX_FLOW_LIST_LIMIT
from app.db import get_db_session
from app.models import FlowListResponse, FlowRead, User
from app.services.flow.errors import FlowAccessDeniedError, FlowNotFoundError
from app.services.flow.service import FlowService
from app.utils.auth import get_current_user

db_dependency = Depends(get_db_session)
current_user_dependency = Depends(get_current_user)

logger = logging.getLogger(__name__)

router = APIRouter()
service = FlowService()


@router.get("/flows", response_model=FlowListResponse)
async def list_flows(
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
    skip: int = Query(0, ge=0, le=1_000_000, description="Number of flows to skip"),
    limit: int = Query(
        100, ge=1, le=MAX_FLOW_LIST_LIMIT, description="Maximum flows to return"
    ),
):
    """List flows visible to the current user with pagination.

    Admins see all flows, users see flows they created.
    """
    flows = await service.list_flows(current_user, session, skip=skip, limit=limit)
    return FlowListResponse(flows=flows)


@router.get("/flows/{flow_id}", response_model=FlowRead)
async def get_flow(
    flow_id: UUID,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Get details of a specific flow if visible to the current user."""
    try:
        return await service.get_flow_by_id(flow_id, current_user, session)
    except (FlowNotFoundError, FlowAccessDeniedError):
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Flow not found",
        ) from None
