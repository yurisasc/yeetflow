import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models import FlowListResponse, FlowRead, User
from app.services.flow_service import FlowService
from app.utils.auth import get_current_user

db_dependency = Depends(get_db_session)
current_user_dependency = Depends(get_current_user)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/flows", response_model=FlowListResponse)
async def list_flows(
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """List flows visible to the current user.

    Admins see all flows, users see flows they created.
    """
    service = FlowService()
    flows = await service.list_flows(current_user, session)
    return FlowListResponse(flows=flows)


@router.get("/flows/{flow_id}", response_model=FlowRead)
async def get_flow(
    flow_id: UUID,
    current_user: User = current_user_dependency,
    session: AsyncSession = db_dependency,
):
    """Get details of a specific flow if visible to the current user."""
    service = FlowService()
    flow = await service.get_flow_by_id(flow_id, current_user, session)

    if flow is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail="Flow not found",
        )

    return flow
