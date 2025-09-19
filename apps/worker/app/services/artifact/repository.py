import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Run

logger = logging.getLogger(__name__)


class ArtifactRepository:
    """Repository for artifact persistence operations."""

    async def get_run_with_artifact(
        self, session: AsyncSession, run_id: UUID
    ) -> Run | None:
        """Get a run by its ID, including artifact information."""
        result = await session.execute(select(Run).where(Run.id == run_id))
        return result.scalar_one_or_none()
