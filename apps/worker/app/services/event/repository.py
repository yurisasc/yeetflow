"""Event repository for data access operations."""

import logging
from uuid import UUID

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, EventCreate, EventType

logger = logging.getLogger(__name__)


class EventRepository:
    """Repository for event persistence operations."""

    async def create_event(
        self, session: AsyncSession, event_data: EventCreate
    ) -> Event:
        """Create a new event in the database."""
        event = Event(**event_data.model_dump())
        session.add(event)
        await session.commit()
        await session.refresh(event)
        logger.debug("Created event: %s for run %s", event.type.value, event.run_id)
        return event

    async def get_event_by_id(
        self, session: AsyncSession, event_id: UUID
    ) -> Event | None:
        """Get an event by its ID."""
        result = await session.execute(select(Event).where(Event.id == event_id))
        return result.scalar_one_or_none()

    async def get_run_events(
        self, session: AsyncSession, run_id: UUID, limit: int = 100
    ) -> list[Event]:
        """Get all events for a specific run."""
        stmt = (
            select(Event)
            .where(Event.run_id == run_id)
            .order_by(desc(Event.at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def get_run_events_by_type(
        self,
        session: AsyncSession,
        run_id: UUID,
        event_type: EventType,
        limit: int = 100,
    ) -> list[Event]:
        """Get events of a specific type for a run."""
        stmt = (
            select(Event)
            .where(Event.run_id == run_id)
            .where(Event.type == event_type)
            .order_by(desc(Event.at))
            .limit(limit)
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def delete_run_events(self, session: AsyncSession, run_id: UUID) -> int:
        """Delete all events for a run. Returns the number of deleted events."""
        result = await session.execute(
            Event.__table__.delete().where(Event.run_id == run_id)
        )
        await session.commit()
        deleted_count = result.rowcount
        logger.info("Deleted %d events for run %s", deleted_count, run_id)
        return deleted_count
