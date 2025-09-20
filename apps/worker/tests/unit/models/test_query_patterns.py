import itertools

import pytest
from sqlalchemy import select

from app.models import Flow, Run, RunStatus, User

# Test constants
PAGINATION_USER_PASSWORD = "pagination_password_hash"
FILTER_USER_PASSWORD = "filter_password_hash"

# Magic value constants
EXPECTED_RUN_COUNT = 3
PAGINATION_LIMIT = 2


@pytest.mark.unit
class TestQueryPatterns:
    """Unit tests for common query patterns."""

    async def test_run_pagination_query(self, session):
        """Test pagination query pattern for Run listings."""
        # Create multiple runs
        user = User(
            email="pagination@example.com", password_hash=PAGINATION_USER_PASSWORD
        )
        flow = Flow(key="pagination-flow", name="Pagination Flow", created_by=user.id)
        session.add_all([user, flow])
        await session.commit()

        runs = []
        for _ in range(5):
            run = Run(flow_id=flow.id, user_id=user.id)
            runs.append(run)
        session.add_all(runs)
        await session.commit()

        # Test pagination
        stmt = (
            select(Run)
            .order_by(Run.created_at.desc(), Run.id.desc())
            .limit(PAGINATION_LIMIT)
            .offset(1)
        )
        result = await session.execute(stmt)
        paginated_runs = result.scalars().all()

        assert len(paginated_runs) == PAGINATION_LIMIT

    async def test_run_filtering_and_ordering(self, session):
        """Test filtering and ordering queries for Runs."""
        user = User(email="filter@example.com", password_hash=FILTER_USER_PASSWORD)
        flow = Flow(key="filter-flow", name="Filter Flow", created_by=user.id)
        session.add_all([user, flow])
        await session.commit()

        # Create runs with different statuses
        run1 = Run(flow_id=flow.id, user_id=user.id, status=RunStatus.PENDING)
        run2 = Run(flow_id=flow.id, user_id=user.id, status=RunStatus.RUNNING)
        run3 = Run(flow_id=flow.id, user_id=user.id, status=RunStatus.COMPLETED)
        session.add_all([run1, run2, run3])
        await session.commit()

        # Filter by status and user to avoid interference from other tests
        stmt = select(Run).where(
            Run.status == RunStatus.RUNNING, Run.user_id == user.id
        )
        result = await session.execute(stmt)
        running_runs = result.scalars().all()

        assert len(running_runs) == 1
        assert running_runs[0].status == RunStatus.RUNNING
        assert running_runs[0].user_id == user.id

        # Order by creation time and filter by user and flow
        stmt = (
            select(Run)
            .where(Run.user_id == user.id, Run.flow_id == flow.id)
            .order_by(Run.created_at.desc(), Run.id.desc())
        )
        result = await session.execute(stmt)
        ordered_runs = result.scalars().all()

        assert len(ordered_runs) == EXPECTED_RUN_COUNT
        # Should be ordered newest first with proper tie-breaking
        for prev, curr in itertools.pairwise(ordered_runs):
            assert (prev.created_at, prev.id) >= (curr.created_at, curr.id)

        # Ensure we got the exact expected runs
        expected_ids = {run1.id, run2.id, run3.id}
        assert {r.id for r in ordered_runs} == expected_ids
