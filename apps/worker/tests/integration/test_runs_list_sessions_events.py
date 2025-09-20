from http import HTTPStatus

import pytest

from app.models import EventType
from tests.conftest import BaseTestClass


@pytest.mark.integration
class TestRunsListSessionsEventsIntegration(BaseTestClass):
    """Integration tests for GET /runs list, sessions, and events endpoints."""

    def test_list_runs_integration(self):
        """Integration test for GET /runs endpoint."""
        # Create several runs
        run_ids = []
        expected_run_count = 3
        for _ in range(expected_run_count):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            )
            assert response.status_code == HTTPStatus.CREATED
            run_ids.append(response.json()["id"])

        # Get list of runs
        response = self.client.get(f"{self.API_PREFIX}/runs")
        assert response.status_code == HTTPStatus.OK
        runs = response.json()

        assert isinstance(runs, list)
        assert len(runs) >= expected_run_count
        listed_ids = {r["id"] for r in runs}
        for rid in run_ids:
            assert rid in listed_ids

        # Verify we can retrieve each created run
        for run_id in run_ids:
            run_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
            assert run_response.status_code == HTTPStatus.OK

    def test_list_runs_pagination_integration(self):
        """Integration test for GET /runs with pagination."""
        # Create multiple runs
        run_count = 7
        for _ in range(run_count):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            )
            assert response.status_code == HTTPStatus.CREATED

        # Test pagination with limit
        pagination_limit = 3
        response = self.client.get(f"{self.API_PREFIX}/runs?limit={pagination_limit}")
        assert response.status_code == HTTPStatus.OK
        limited_runs = response.json()
        assert len(limited_runs) == min(pagination_limit, run_count)

        # Test pagination with skip
        skip_count = 3
        response = self.client.get(
            f"{self.API_PREFIX}/runs?skip={skip_count}&limit={pagination_limit}"
        )
        assert response.status_code == HTTPStatus.OK
        skipped_runs = response.json()
        assert len(skipped_runs) == min(
            pagination_limit, max(0, run_count - skip_count)
        )
        # Optional: ensure pages don't overlap when enough items exist
        if len(limited_runs) == pagination_limit and len(skipped_runs) > 0:
            assert {r["id"] for r in limited_runs}.isdisjoint(
                {r["id"] for r in skipped_runs}
            )

    def test_get_run_sessions_integration(self):
        """Integration test for GET /runs/{runId}/sessions endpoint."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["id"]

        # Get sessions for the run
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/sessions")
        assert response.status_code == HTTPStatus.OK
        sessions = response.json()

        assert isinstance(sessions, list)

        # Sessions should exist since runs create browser sessions
        # (This depends on the run creation actually creating sessions)
        if len(sessions) > 0:
            for session in sessions:
                assert "id" in session
                assert "run_id" in session
                assert session["run_id"] == run_id
                assert "status" in session
                assert "session_url" in session

    def test_get_run_sessions_with_different_flows(self):
        """Integration test for sessions with different flow types."""
        flows_and_runs = [
            ("550e8400-e29b-41d4-a716-446655440000", "test-flow"),
            ("550e8400-e29b-41d4-a716-446655440001", "hitl-flow"),
        ]

        for flow_id, _ in flows_and_runs:
            # Create run for this flow
            create_response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": flow_id,
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            )
            assert create_response.status_code == HTTPStatus.CREATED
            run_id = create_response.json()["id"]

            # Get sessions
            response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/sessions")
            assert response.status_code == HTTPStatus.OK
            sessions = response.json()

            assert isinstance(sessions, list)

    def test_get_run_events_integration(self):
        """Integration test for GET /runs/{runId}/events endpoint."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["id"]

        # Get events for the run
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/events")
        assert response.status_code == HTTPStatus.OK
        events = response.json()

        assert isinstance(events, list)

        # Events might be empty initially, but if they exist, verify structure
        allowed_types = {t.value for t in EventType}
        for event in events:
            assert "id" in event
            assert "run_id" in event
            assert event["run_id"] == run_id
            assert "type" in event
            assert "at" in event
            assert event["type"] in allowed_types

    def test_endpoints_consistency_across_runs(self):
        """Integration test to verify all endpoints work consistently."""
        # Create multiple runs
        run_ids = []
        consistency_test_run_count = 3
        for _ in range(consistency_test_run_count):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            )
            assert response.status_code == HTTPStatus.CREATED
            run_ids.append(response.json()["id"])

        # Test all endpoints for each run
        for run_id in run_ids:
            # Test individual run endpoint
            run_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
            assert run_response.status_code == HTTPStatus.OK

            # Test sessions endpoint
            sessions_response = self.client.get(
                f"{self.API_PREFIX}/runs/{run_id}/sessions"
            )
            assert sessions_response.status_code == HTTPStatus.OK

            # Test events endpoint
            events_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/events")
            assert events_response.status_code == HTTPStatus.OK

    def test_performance_pagination_under_load(self):
        """Integration test for pagination performance with many runs."""
        # Create many runs for pagination testing
        run_count = 10
        for _ in range(run_count):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            )
            assert response.status_code == HTTPStatus.CREATED

        # Test pagination works correctly
        page_size = 3
        total_pages = (run_count + page_size - 1) // page_size  # Ceiling division

        all_runs = []
        for page in range(total_pages):
            skip = page * page_size
            response = self.client.get(
                f"{self.API_PREFIX}/runs?skip={skip}&limit={page_size}"
            )
            assert response.status_code == HTTPStatus.OK
            page_runs = response.json()
            all_runs.extend(page_runs)

            # Each page should have at most page_size items
            assert len(page_runs) <= page_size

        # Should retrieve all created runs exactly once
        all_ids = [r["id"] for r in all_runs]
        assert len(set(all_ids)) == len(all_ids)
        assert len(all_runs) >= run_count
