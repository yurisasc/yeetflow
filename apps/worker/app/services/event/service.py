"""Event service for managing flow execution events."""

import logging
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db_session
from app.models import EventCreate, EventRead, EventType
from app.services.event.errors import EventNotFoundError
from app.services.event.repository import EventRepository

logger = logging.getLogger(__name__)


class EventService:
    """Service for managing flow execution events with business logic."""

    def __init__(
        self,
        repository: EventRepository | None = None,
        session: AsyncSession | None = None,
    ):
        self.repository = repository or EventRepository()
        self.session = session

    async def create_event(
        self,
        run_id: UUID,
        event_type: EventType,
        message: str | None = None,
        payload: dict | None = None,
    ) -> EventRead:
        """Create a new event for a run.

        Args:
            run_id: UUID of the run this event belongs to
            event_type: Type of event (status, log, step_start, etc.)
            message: Optional human-readable message
            payload: Optional structured data payload

        Returns:
            EventRead: The created event data

        Raises:
            EventValidationError: If event data is invalid
        """

        if payload is None:
            payload = {}

        event_data = EventCreate(
            run_id=run_id,
            type=event_type,
            message=message,
            payload=payload,
        )

        session = self.session or get_db_session()
        try:
            event = await self.repository.create_event(session, event_data)
            return EventRead.model_validate(event)
        except Exception:
            if self.session is None:  # Only rollback if we created the session
                await session.rollback()
            logger.exception("Failed to create event")
            raise

    async def get_event_by_id(self, event_id: UUID) -> EventRead:
        """Get an event by its ID.

        Args:
            event_id: UUID of the event to retrieve

        Returns:
            EventRead: The event data

        Raises:
            EventNotFoundError: If the event doesn't exist
        """
        session = self.session or get_db_session()
        event = await self.repository.get_event_by_id(session, event_id)

        if event is None:
            raise EventNotFoundError(str(event_id))

        return EventRead.model_validate(event)

    async def get_run_events(self, run_id: UUID, limit: int = 100) -> list[EventRead]:
        """Get all events for a specific run.

        Args:
            run_id: UUID of the run to get events for
            limit: Maximum number of events to return (default: 100)

        Returns:
            List of EventRead objects
        """
        session = self.session or get_db_session()
        events = await self.repository.get_run_events(session, run_id, limit)
        return [EventRead.model_validate(event) for event in events]

    async def get_run_checkpoints(self, run_id: UUID) -> list[dict]:
        """Get all checkpoint events for a run.

        Args:
            run_id: UUID of the run to get checkpoints for

        Returns:
            List of checkpoint data dictionaries
        """
        session = self.session or get_db_session()
        events = await self.repository.get_run_events_by_type(
            session, run_id, EventType.CHECKPOINT
        )

        return [
            event.payload["checkpoint"]
            for event in events
            if event.payload and "checkpoint" in event.payload
        ]

    async def get_active_checkpoint(self, run_id: UUID) -> dict | None:
        """Get the most recent active checkpoint for a run.

        Args:
            run_id: UUID of the run to check for active checkpoints

        Returns:
            Checkpoint data dict if found and not expired, None otherwise
        """
        checkpoints = await self.get_run_checkpoints(run_id)

        # Find the most recent checkpoint that hasn't expired
        now = datetime.now(UTC)
        for checkpoint in sorted(
            checkpoints, key=lambda x: x.get("created_at", 0), reverse=True
        ):
            expires_at_str = checkpoint.get("expires_at")
            if expires_at_str:
                try:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    if expires_at > now:
                        return checkpoint
                except (ValueError, TypeError):
                    continue

        return None

    async def delete_run_events(self, run_id: UUID) -> int:
        """Delete all events for a run.

        Args:
            run_id: UUID of the run to delete events for

        Returns:
            Number of events deleted
        """
        session = self.session or get_db_session()
        try:
            return await self.repository.delete_run_events(session, run_id)
        except Exception:
            if self.session is None:  # Only rollback if we created the session
                await session.rollback()
            logger.exception("Failed to delete events for run %s", run_id)
            raise
