import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import FlowRead, FlowVisibility, User, UserRole
from app.services.flow.errors import FlowAccessDeniedError, FlowNotFoundError
from app.services.flow.repository import FlowRepository

logger = logging.getLogger(__name__)


class FlowService:
    """Service for managing flow operations and visibility rules."""

    def __init__(self, repository: FlowRepository | None = None):
        self.repository = repository or FlowRepository()

    async def list_flows(
        self,
        current_user: User,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> list[FlowRead]:
        """List flows visible to the current user with pagination.

        Visibility rules:
        - Admins can see all flows
        - Users can see flows they created

        Args:
            current_user: The authenticated user making the request
            session: Database session
            skip: Number of flows to skip (default: 0)
            limit: Maximum number of flows to return (default: 100, max: 200)
        """
        flows = await self.repository.list_flows(session, current_user, skip, limit)
        return [FlowRead.model_validate(flow) for flow in flows]

    async def get_flow_by_id(
        self, flow_id: UUID, current_user: User, session: AsyncSession
    ) -> FlowRead:
        """Get a flow by ID if visible to the current user.

        Args:
            flow_id: UUID of the flow to retrieve
            current_user: The authenticated user making the request
            session: Database session

        Returns:
            FlowRead: The flow data if accessible

        Raises:
            FlowNotFoundError: If the flow doesn't exist
            FlowAccessDeniedError: If the user doesn't have access
        """
        flow = await self.repository.get_by_id(session, flow_id)

        if flow is None:
            raise FlowNotFoundError(str(flow_id))

        # Check visibility
        if (
            current_user.role != UserRole.ADMIN
            and flow.created_by != current_user.id
            and flow.visibility != FlowVisibility.PUBLIC
        ):
            raise FlowAccessDeniedError(str(flow_id))

        return FlowRead.model_validate(flow)
