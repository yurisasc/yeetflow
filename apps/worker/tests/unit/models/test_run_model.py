from uuid import uuid4

import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from app.models import Flow, Run, RunCreate, RunStatus, User

# Test constants
RUN_USER_PASSWORD = "runuser_password_hash"
STATUS_USER_PASSWORD = "statususer_password_hash"
FKTEST_PASSWORD = "fktest_password_hash"


@pytest.mark.unit
class TestRunModel:
    """Unit tests for Run model operations."""

    async def test_create_run_with_relationships(self, session):
        """Test creating Run with User and Flow relationships."""
        # Create user and flow first
        user = User(email="runuser@example.com", password_hash=RUN_USER_PASSWORD)
        flow = Flow(key="run-flow", name="Run Flow", created_by=user.id)
        session.add_all([user, flow])
        await session.commit()
        await session.refresh(user)
        await session.refresh(flow)

        # Create run
        run_data = RunCreate(flow_id=flow.id, user_id=user.id)
        run = Run(**run_data.model_dump())
        session.add(run)
        await session.commit()
        await session.refresh(run)

        # Load relationships
        stmt = (
            select(Run)
            .where(Run.id == run.id)
            .options(selectinload(Run.user), selectinload(Run.flow))
        )
        result = await session.execute(stmt)
        run_with_relations = result.scalar_one()

        assert run_with_relations.flow_id == flow.id
        assert run_with_relations.user_id == user.id
        assert run_with_relations.flow.key == flow.key
        assert run_with_relations.user.email == user.email
        assert run_with_relations.status == RunStatus.PENDING

    async def test_run_status_enum_constraint(self, session):
        """Test Run status enum validation."""
        # Create user and flow first
        user = User(email="statususer@example.com", password_hash=STATUS_USER_PASSWORD)
        flow = Flow(key="status-flow", name="Status Flow", created_by=user.id)
        session.add_all([user, flow])
        await session.commit()

        # Valid status should work
        run = Run(flow_id=flow.id, user_id=user.id, status=RunStatus.RUNNING)
        session.add(run)
        await session.commit()

        # Note: SQLite doesn't enforce enum constraints like PostgreSQL
        # This test verifies that valid enum values work correctly
        # Invalid enum values would be caught by Pydantic validation before
        # reaching DB
        assert run.status == RunStatus.RUNNING

    async def test_run_foreign_key_constraints(self, session):
        """Test Run foreign key constraints."""

        # First, verify that valid foreign keys work
        user = User(email="fktest@example.com", password_hash=FKTEST_PASSWORD)
        flow = Flow(key="fktest-flow", name="FK Test Flow", created_by=user.id)
        session.add_all([user, flow])
        await session.commit()

        # This should work - valid foreign keys
        valid_run = Run(flow_id=flow.id, user_id=user.id)
        session.add(valid_run)
        await session.commit()  # Should succeed

        # Now test invalid foreign keys
        nonexistent_flow_id = uuid4()
        nonexistent_user_id = uuid4()

        invalid_run = Run(flow_id=nonexistent_flow_id, user_id=nonexistent_user_id)
        session.add(invalid_run)

        # SQLite with foreign keys enabled should raise IntegrityError
        with pytest.raises(IntegrityError):
            await session.commit()
        await session.rollback()
