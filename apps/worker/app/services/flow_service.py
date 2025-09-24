import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Flow, FlowRead, User, UserRole

logger = logging.getLogger(__name__)


class FlowService:
    """Service for managing flow operations and visibility rules."""

    async def list_flows(
        self, current_user: User, session: AsyncSession
    ) -> list[FlowRead]:
        """List flows visible to the current user.

        Visibility rules:
        - Admins can see all flows
        - Users can see flows they created
        """
        if current_user.role == UserRole.ADMIN:
            # Admins see all flows
            result = await session.execute(select(Flow))
        else:
            # Users see only flows they created
            result = await session.execute(
                select(Flow).where(Flow.created_by == current_user.id)
            )

        flows = result.scalars().all()
        return [FlowRead.model_validate(flow) for flow in flows]

    async def get_flow_by_id(
        self, flow_id: UUID, current_user: User, session: AsyncSession
    ) -> FlowRead | None:
        """Get a flow by ID if visible to the current user.

        Returns None if flow doesn't exist or user doesn't have access.
        """
        result = await session.execute(select(Flow).where(Flow.id == flow_id))
        flow = result.scalar_one_or_none()

        if flow is None:
            return None

        # Check visibility
        if current_user.role != UserRole.ADMIN and flow.created_by != current_user.id:
            return None

        return FlowRead.model_validate(flow)
