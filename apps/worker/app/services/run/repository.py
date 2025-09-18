import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.models import Run
from app.models import Session as SessionModel

logger = logging.getLogger(__name__)


class RunRepository:
    """Repository for run persistence operations."""

    async def create(self, session: AsyncSession, run: Run) -> Run:
        """Create a new run record."""
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    async def get_by_id(self, session: AsyncSession, run_id: UUID) -> Run | None:
        """Get a run by its ID."""
        result = await session.execute(select(Run).where(Run.id == run_id))
        return result.scalar_one_or_none()

    async def update(self, session: AsyncSession, run: Run) -> Run:
        """Update an existing run record."""
        session.add(run)
        await session.commit()
        await session.refresh(run)
        return run

    async def list_runs(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Run]:
        """List runs with pagination."""
        result = await session.execute(select(Run).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def get_sessions(
        self, session: AsyncSession, run_id: UUID
    ) -> list[SessionModel]:
        """Get all sessions for a specific run."""
        result = await session.execute(
            select(SessionModel).where(SessionModel.run_id == run_id)
        )
        return list(result.scalars().all())

    async def create_session(
        self, session: AsyncSession, session_model: SessionModel
    ) -> SessionModel:
        """Create a new session record."""
        session.add(session_model)
        await session.commit()
        await session.refresh(session_model)
        return session_model
