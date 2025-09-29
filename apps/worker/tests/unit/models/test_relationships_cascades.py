import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Event, EventType, Flow, Run, RunStatus, SessionStatus, User
from app.models import Session as DBSession

# Test constants
REL_USER_PASSWORD = "reluser_password_hash"
COMPLETE_REL_PASSWORD = "completerel_password_hash"
CASCADE_REL_PASSWORD = "cascaderel_password_hash"

# Magic value constants
EXPECTED_FLOW_COUNT = 2
EXPECTED_EVENT_COUNT = 2


@pytest.mark.unit
class TestRelationshipsAndCascades:
    """Unit tests for model relationships and cascade behavior."""

    async def test_user_flow_relationships(self, session):
        """Test User-Flow relationships."""
        user = User(email="reluser@example.com", password_hash=REL_USER_PASSWORD)
        flow1 = Flow(key="rel-flow1", name="Flow 1", created_by=user.id)
        flow2 = Flow(key="rel-flow2", name="Flow 2", created_by=user.id)

        session.add_all([user, flow1, flow2])
        await session.commit()

        # Load user with flows
        stmt = select(User).where(User.id == user.id).options(selectinload(User.flows))
        result = await session.execute(stmt)
        user_with_flows = result.scalar_one()

        assert len(user_with_flows.flows) == EXPECTED_FLOW_COUNT
        flow_keys = [f.key for f in user_with_flows.flows]
        assert "rel-flow1" in flow_keys
        assert "rel-flow2" in flow_keys

    async def test_run_relationships_complete(self, session):
        """Test complete Run relationships with all related entities."""
        # Create user and flow
        user = User(
            email="completerel@example.com", password_hash=COMPLETE_REL_PASSWORD
        )
        flow = Flow(key="complete-flow", name="Complete Flow", created_by=user.id)
        session.add_all([user, flow])
        await session.commit()

        # Create run
        run = Run(flow_id=flow.id, user_id=user.id, status=RunStatus.RUNNING)
        session.add(run)
        await session.commit()

        # Create sessions and events
        session1 = DBSession(run_id=run.id, status=SessionStatus.ACTIVE)
        session2 = DBSession(run_id=run.id, status=SessionStatus.ENDED)
        event1 = Event(run_id=run.id, type=EventType.STATUS, message="Starting")
        event2 = Event(run_id=run.id, type=EventType.STATUS, message="Done")

        session.add_all([session1, session2, event1, event2])
        await session.commit()

        # Load complete run with all relationships
        stmt = (
            select(Run)
            .where(Run.id == run.id)
            .options(
                selectinload(Run.user),
                selectinload(Run.flow),
                selectinload(Run.sessions),
                selectinload(Run.events),
            )
        )
        result = await session.execute(stmt)
        complete_run = result.scalar_one()

        # Verify the actual stored session statuses
        statuses = {getattr(s.status, "value", s.status) for s in complete_run.sessions}
        assert statuses == {"active", "ended"}

        assert complete_run.user.email == user.email
        assert complete_run.flow.key == flow.key
        assert len(complete_run.sessions) == EXPECTED_FLOW_COUNT
        assert len(complete_run.events) == EXPECTED_EVENT_COUNT
        assert complete_run.status == RunStatus.RUNNING

    async def test_cascade_delete_behavior(self, session):
        """Test cascade delete behavior for Run relationships."""
        # Create user and flow
        user = User(email="cascaderel@example.com", password_hash=CASCADE_REL_PASSWORD)
        flow = Flow(key="cascade-flow", name="Cascade Flow", created_by=user.id)
        session.add_all([user, flow])
        await session.commit()

        # Create run
        run = Run(flow_id=flow.id, user_id=user.id)
        session.add(run)
        await session.commit()

        # Create sessions and events
        session1 = DBSession(run_id=run.id)
        event1 = Event(run_id=run.id, type=EventType.STATUS)
        session.add_all([session1, event1])
        await session.commit()

        # Verify they exist
        stmt = select(DBSession).where(DBSession.run_id == run.id)
        result = await session.execute(stmt)
        sessions_before = result.scalars().all()
        assert len(sessions_before) == 1

        stmt = select(Event).where(Event.run_id == run.id)
        result = await session.execute(stmt)
        events_before = result.scalars().all()
        assert len(events_before) == 1

        # Delete run - should cascade to sessions and events
        await session.delete(run)
        await session.commit()

        # Verify cascade worked
        stmt = select(DBSession).where(DBSession.run_id == run.id)
        result = await session.execute(stmt)
        sessions_after = result.scalars().all()
        assert len(sessions_after) == 0

        stmt = select(Event).where(Event.run_id == run.id)
        result = await session.execute(stmt)
        events_after = result.scalars().all()
        assert len(events_after) == 0
