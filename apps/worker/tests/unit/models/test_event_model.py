from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.models import Event, EventCreate, EventRead, EventType, Flow, Run, User

# Test constants
EVENT_USER_PASSWORD = "eventuser_password_hash"
EVENT_ENUM_PASSWORD = "eventenum_password_hash"
EVENT_SERIALIZE_PASSWORD = "eventserialize_password_hash"


@pytest.mark.unit
class TestEventModel:
    """Unit tests for Event model operations."""

    async def test_create_event_with_json_payload(self, session):
        """Test creating Event with JSON payload."""
        # Create run first
        user = User(email="eventuser@example.com", password_hash=EVENT_USER_PASSWORD)
        flow = Flow(key="event-flow", name="Event Flow", created_by=user.id)
        run = Run(flow_id=flow.id, user_id=user.id)
        session.add_all([user, flow, run])
        await session.commit()
        await session.refresh(run)

        # Create event
        payload = {"action": "click", "element": "#submit", "timestamp": 1234567890}
        event_data = EventCreate(
            run_id=run.id,
            type=EventType.STATUS,
            message="Button clicked",
            payload=payload,
        )

        event = Event(**event_data.model_dump())
        session.add(event)
        await session.commit()
        await session.refresh(event)

        # Verify JSON round-trip
        assert event.run_id == run.id
        assert event.type == EventType.STATUS
        assert event.message == event_data.message
        assert event.payload == payload

    async def test_event_type_enum_validation(self, session):
        """Test Event type enum validation."""
        # Create run first
        user = User(email="eventenum@example.com", password_hash=EVENT_ENUM_PASSWORD)
        flow = Flow(key="eventenum-flow", name="Event Enum Flow", created_by=user.id)
        run = Run(flow_id=flow.id, user_id=user.id)
        session.add_all([user, flow, run])
        await session.commit()

        # Valid type should work
        event = Event(run_id=run.id, type=EventType.CHECKPOINT)
        session.add(event)
        await session.commit()

        # Note: SQLite doesn't enforce enum constraints like PostgreSQL
        # This test verifies that valid enum values work correctly
        # Invalid enum values would be caught by Pydantic validation before reaching DB
        assert event.type == EventType.CHECKPOINT

    def test_event_type_invalid_value_rejected_by_pydantic(self):
        with pytest.raises(ValidationError):
            EventCreate(run_id=uuid4(), type="invalid")  # type: ignore[arg-type]

    async def test_event_serialization(self, session):
        """Test Event serialization to API models."""
        # Create run
        user = User(
            email="eventserialize@example.com", password_hash=EVENT_SERIALIZE_PASSWORD
        )
        flow = Flow(
            key="eventserialize-flow", name="Event Serialize Flow", created_by=user.id
        )
        run = Run(flow_id=flow.id, user_id=user.id)
        session.add_all([user, flow, run])
        await session.commit()

        # Create event
        event = Event(
            run_id=run.id,
            type=EventType.STATUS,
            message="Task completed successfully",
            payload={"result": "success", "duration": 45.2},
        )
        session.add(event)
        await session.commit()
        await session.refresh(event)

        event_read = EventRead.model_validate(event)

        assert event_read.id == event.id
        assert event_read.run_id == event.run_id
        assert event_read.type == event.type
        assert event_read.message == event.message
        assert event_read.payload == event.payload
        assert event_read.at == event.at
