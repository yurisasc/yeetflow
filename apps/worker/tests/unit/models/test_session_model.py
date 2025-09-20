import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models import Flow, Run, SessionCreate, SessionRead, SessionStatus, User
from app.models import Session as DBSession

# Test constants
SESSION_USER_PASSWORD = "sessionuser_password_hash"
SESSION_SERIALIZE_PASSWORD = "sessionserialize_password_hash"


@pytest.mark.unit
class TestSessionModel:
    """Unit tests for Session model operations."""

    async def test_create_session_with_run_relationship(self, session):
        """Test creating Session with Run relationship."""
        # Create user, flow, and run
        user = User(
            email="sessionuser@example.com", password_hash=SESSION_USER_PASSWORD
        )
        flow = Flow(key="session-flow", name="Session Flow", created_by=user.id)
        run = Run(flow_id=flow.id, user_id=user.id)
        session.add_all([user, flow])
        await session.flush()
        session.add(run)
        await session.commit()
        await session.refresh(run)

        # Create session
        session_data = SessionCreate(run_id=run.id)
        db_session = DBSession(**session_data.model_dump(exclude_unset=True))
        session.add(db_session)
        await session.commit()
        await session.refresh(db_session)

        # Load relationship
        stmt = (
            select(DBSession)
            .where(DBSession.id == db_session.id)
            .options(selectinload(DBSession.run))
        )
        result = await session.execute(stmt)
        session_with_run = result.scalar_one()

        assert session_with_run.run_id == run.id
        assert session_with_run.run.id == run.id
        assert session_with_run.status == SessionStatus.STARTING
        assert session_with_run.session_url is None

    async def test_session_serialization(self, session):
        """Test Session serialization to API models."""
        # Create run first
        user = User(
            email="sesserialize@example.com", password_hash=SESSION_SERIALIZE_PASSWORD
        )
        flow = Flow(
            key="sesserialize-flow", name="Session Serialize Flow", created_by=user.id
        )
        run = Run(flow_id=flow.id, user_id=user.id)
        session.add_all([user, flow, run])
        await session.commit()

        # Create session
        db_session = DBSession(
            run_id=run.id,
            status="active",
            session_url="https://example.com/session/123",
        )
        session.add(db_session)
        await session.commit()
        await session.refresh(db_session)

        session_read = SessionRead.model_validate(db_session)

        assert session_read.id == db_session.id
        assert session_read.run_id == db_session.run_id
        assert session_read.status == db_session.status
        assert session_read.session_url == db_session.session_url
        assert session_read.created_at == db_session.created_at
        assert session_read.ended_at == db_session.ended_at
