import asyncio
import time
from http import HTTPStatus
from threading import Event
from unittest.mock import patch
from uuid import UUID

import pytest

from app.dependencies.run_scheduler import get_run_scheduler
from app.runtime.core import RunnerCoordinator
from app.runtime.scheduler import RunScheduler
from tests.conftest import BaseTestClass


@pytest.mark.integration
class TestStartFlowIntegration(BaseTestClass):
    """Integration tests for starting a flow and verifying session creation."""

    def test_start_flow_creates_run_with_session_url(self):
        """Test that starting a flow creates a run with session URL."""
        # Start a flow with authentication
        headers = self.get_user_auth_headers()
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
            },
            headers=headers,
        )
        assert response.status_code == HTTPStatus.CREATED

        data = response.json()
        assert "id" in data
        assert "status" in data

        run_id = data["id"]

        # Verify the run was created
        get_response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}", headers=headers
        )
        assert get_response.status_code == HTTPStatus.OK
        run_data = get_response.json()
        assert run_data["id"] == run_id
        assert run_data["status"] in ["pending", "running"]

        # Check that sessions were created for this run
        sessions_response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/sessions", headers=headers
        )
        assert sessions_response.status_code == HTTPStatus.OK
        sessions = sessions_response.json()
        assert len(sessions) > 0  # Should have at least one session
        session_url = sessions[0]["session_url"]
        assert session_url.startswith("https://")

    def test_start_flow_status_transitions_to_running(self):
        """Test that flow status transitions to running after creation."""
        # Start a flow with authentication
        headers = self.get_user_auth_headers()
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
            },
            headers=headers,
        )
        assert response.status_code == HTTPStatus.CREATED

        run_id = response.json()["id"]

        # Poll for status update with timeout
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            get_response = self.client.get(
                f"{self.API_PREFIX}/runs/{run_id}", headers=headers
            )
            assert get_response.status_code == HTTPStatus.OK
            if get_response.json().get("status") == "running":
                break
            time.sleep(0.05)
        else:
            pytest.fail("Status did not transition to 'running' within 5.0 seconds")

        # Check status
        get_response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}", headers=headers
        )
        assert get_response.status_code == HTTPStatus.OK
        run_data = get_response.json()
        assert run_data["status"] == "running"

    def test_start_flow_creates_unique_run_ids(self):
        """Test that starting multiple flows creates unique run IDs."""
        headers = self.get_user_auth_headers()

        # Start first flow
        response1 = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
            },
            headers=headers,
        )
        assert response1.status_code == HTTPStatus.CREATED
        run_id1 = response1.json()["id"]

        # Start second flow
        response2 = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
            },
            headers=headers,
        )
        assert response2.status_code == HTTPStatus.CREATED
        run_id2 = response2.json()["id"]

        # Verify they are different
        assert run_id1 != run_id2

    def test_start_flow_initializes_browser_session(self):
        """Test that starting a flow initializes a browser session via Steel.dev."""
        # Start a flow with authentication
        headers = self.get_user_auth_headers()
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
            },
            headers=headers,
        )
        assert response.status_code == HTTPStatus.CREATED
        run_id = response.json()["id"]

        # Check that sessions were created for this run
        sessions_response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/sessions", headers=headers
        )
        assert sessions_response.status_code == HTTPStatus.OK
        sessions = sessions_response.json()
        assert len(sessions) > 0  # Should have at least one session
        session_url = sessions[0]["session_url"]

        assert "steel.dev" in session_url or "localhost" in session_url

    def test_start_flow_handles_concurrent_requests(self):
        """Test that the system handles concurrent flow starts correctly."""
        # TODO: Test concurrent requests
        # This would require async testing or multiple clients

        # For now, test sequential requests
        headers = self.get_user_auth_headers()
        responses = []
        for _i in range(3):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                },
                headers=headers,
            )
            responses.append(response)
            assert response.status_code == HTTPStatus.CREATED

        # Verify all runs are created
        run_ids = [r.json()["id"] for r in responses]
        assert len(set(run_ids)) == len(run_ids)  # All unique

    @pytest.mark.parametrize(
        "flow_id",
        [
            "550e8400-e29b-41d4-a716-446655440000",
            "550e8400-e29b-41d4-a716-446655440001",
            "550e8400-e29b-41d4-a716-446655440002",
        ],
    )
    def test_start_flow_works_with_different_flows(self, flow_id):
        """Test that starting works with different flow configurations."""
        headers = self.get_user_auth_headers()
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": flow_id,
            },
            headers=headers,
        )
        assert response.status_code == HTTPStatus.CREATED

        data = response.json()
        assert "id" in data
        assert "status" in data

        # Verify the run
        get_response = self.client.get(
            f"{self.API_PREFIX}/runs/{data['id']}", headers=headers
        )
        assert get_response.status_code == HTTPStatus.OK

    def test_start_flow_schedules_background_task_via_coordinator(self):
        """Verify RunScheduler registers a coordinator task on run creation."""

        class RecordingCoordinator(RunnerCoordinator):
            def __init__(self) -> None:
                super().__init__()
                self.started_event = Event()
                self.started_runs: set[UUID] = set()

            async def start(self, run_id, coro):  # type: ignore[override]
                self.started_runs.add(run_id)
                await super().start(run_id, coro)
                self.started_event.set()

        coordinator = RecordingCoordinator()
        scheduler = RunScheduler(
            coordinator=coordinator,
            session_factory=self.TestAsyncSessionLocal,
        )

        # Override the API dependency so the router uses our recording scheduler.
        self.client.app.dependency_overrides[get_run_scheduler] = lambda: scheduler

        # Track that the coordinator-run coroutine actually starts executing.
        run_started = Event()

        async def stub_run(*_args, **_kwargs):  # type: ignore[override]
            # Mark the coroutine as running, but exit quickly to keep the task short.
            run_started.set()
            await asyncio.sleep(0.01)

        headers = self.get_user_auth_headers()

        try:
            with patch(
                "app.runtime.engine.flow_engine.FlowEngine._run",
                new=stub_run,
            ):
                response = self.client.post(
                    f"{self.API_PREFIX}/runs",
                    json={"flow_id": "550e8400-e29b-41d4-a716-446655440000"},
                    headers=headers,
                )

            assert response.status_code == HTTPStatus.CREATED
            run_id = UUID(response.json()["id"])

            assert coordinator.started_event.wait(timeout=1.0)
            assert run_id in coordinator.started_runs

            assert run_started.wait(timeout=1.0)
        finally:
            # Ensure we restore the original dependency wiring even if the test fails.
            self.client.app.dependency_overrides.pop(get_run_scheduler, None)
