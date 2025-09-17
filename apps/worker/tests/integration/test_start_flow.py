import time
from http import HTTPStatus

import pytest

from tests.conftest import BaseTestClass


class TestStartFlowIntegration(BaseTestClass):
    """Integration tests for starting a flow and verifying session creation."""

    def test_start_flow_creates_run_with_session_url(self):
        """Test that starting a flow creates a run with session URL."""
        # Start a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        data = response.json()
        assert "run_id" in data
        assert "session_url" in data
        assert "status" in data

        run_id = data["run_id"]
        session_url = data["session_url"]

        # Verify the run was created
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert get_response.status_code == HTTPStatus.OK
        run_data = get_response.json()
        assert run_data["run_id"] == run_id
        assert run_data["status"] in ["pending", "running"]

        # Verify session URL is valid
        assert session_url.startswith("https://")

    def test_start_flow_status_transitions_to_running(self):
        """Test that flow status transitions to running after creation."""
        # Start a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        run_id = response.json()["run_id"]

        # Poll for status update with timeout
        deadline = time.monotonic() + 5.0
        while time.monotonic() < deadline:
            get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
            assert get_response.status_code == HTTPStatus.OK
            if get_response.json().get("status") == "running":
                break
            time.sleep(0.05)
        else:
            pytest.fail("Status did not transition to 'running' within 5.0 seconds")

        # Check status
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert get_response.status_code == HTTPStatus.OK
        run_data = get_response.json()
        assert run_data["status"] == "running"

    def test_start_flow_creates_unique_run_ids(self):
        """Test that starting multiple flows creates unique run IDs."""
        # Start first flow
        response1 = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response1.status_code == HTTPStatus.CREATED
        run_id1 = response1.json()["run_id"]

        # Start second flow
        response2 = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response2.status_code == HTTPStatus.CREATED
        run_id2 = response2.json()["run_id"]

        # Verify they are different
        assert run_id1 != run_id2

    def test_start_flow_initializes_browser_session(self):
        """Test that starting a flow initializes a browser session via Steel.dev."""
        # Start a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED
        session_url = response.json()["session_url"]

        assert "steel.dev" in session_url or "localhost" in session_url

    def test_start_flow_handles_concurrent_requests(self):
        """Test that the system handles concurrent flow starts correctly."""
        # TODO: Test concurrent requests
        # This would require async testing or multiple clients

        # For now, test sequential requests
        responses = []
        for _i in range(3):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                },
            )
            responses.append(response)
            assert response.status_code == HTTPStatus.CREATED

        # Verify all runs are created
        run_ids = [r.json()["run_id"] for r in responses]
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
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": flow_id,
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        data = response.json()
        assert "run_id" in data
        assert "session_url" in data

        # Verify the run
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{data['run_id']}")
        assert get_response.status_code == HTTPStatus.OK
