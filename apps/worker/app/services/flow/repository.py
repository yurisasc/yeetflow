import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.constants import MAX_FLOW_LIST_LIMIT
from app.models import Flow, FlowVisibility, User, UserRole

logger = logging.getLogger(__name__)


class FlowRepository:
    """Repository for flow persistence operations."""

    async def list_flows(
        self,
        session: AsyncSession,
        current_user: User,
        skip: int | None = 0,
        limit: int | None = 100,
    ) -> list[Flow]:
        """List flows visible to the current user with pagination."""
        # Normalize pagination params
        skip = max(0, int(skip or 0))
        limit = max(1, min(int(limit or 100), MAX_FLOW_LIST_LIMIT))

        if current_user.role == UserRole.ADMIN:
            # Admins see all flows
            result = await session.execute(
                select(Flow)
                .order_by(Flow.created_at.desc(), Flow.id.desc())
                .offset(skip)
                .limit(limit)
            )
        else:
            # Users see flows they created or shared publicly
            result = await session.execute(
                select(Flow)
                .where(
                    (Flow.created_by == current_user.id)
                    | (Flow.visibility == FlowVisibility.PUBLIC)
                )
                .order_by(Flow.created_at.desc(), Flow.id.desc())
                .offset(skip)
                .limit(limit)
            )

        return list(result.scalars().all())

    async def get_by_id(self, session: AsyncSession, flow_id: UUID) -> Flow | None:
        """Get a flow by its ID."""
        result = await session.execute(select(Flow).where(Flow.id == flow_id))
        return result.scalar_one_or_none()
