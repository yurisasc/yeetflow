import pytest
import time
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi.testclient import TestClient

from app.main import app


class TestStartFlowIntegration:
    """Integration tests for starting a flow and verifying session creation."""

    @pytest.fixture(autouse=True)
    def mock_steel_service(self):
        """Mock the Steel service to avoid hitting API limits during tests."""
        mock_session_data = {
            "id": "test-session-123",
            "createdAt": "2025-09-16T02:11:28.027Z",
            "status": "live",
            "sessionViewerUrl": "https://app.steel.dev/sessions/test-session-123",
            "websocketUrl": "wss://api.steel.dev/sessions/test-session-123/ws",
            "debugUrl": "https://debug.steel.dev/sessions/test-session-123"
        }

        with patch('app.routers.runs.SteelService') as mock_service_class:
            mock_service_instance = MagicMock()
            # Use AsyncMock for the async create_session method
            mock_service_instance.create_session = AsyncMock(return_value=mock_session_data)
            mock_service_class.return_value = mock_service_instance
            yield

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_start_flow_creates_run_with_session_url(self):
        """Test that starting a flow creates a run with session URL."""
        # Start a flow
        response = self.client.post("/api/v1/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert response.status_code == 201

        data = response.json()
        assert "run_id" in data
        assert "session_url" in data
        assert "status" in data

        run_id = data["run_id"]
        session_url = data["session_url"]

        # Verify the run was created
        get_response = self.client.get(f"/api/v1/runs/{run_id}")
        assert get_response.status_code == 200
        run_data = get_response.json()
        assert run_data["run_id"] == run_id
        assert run_data["status"] in ["pending", "running"]

        # Verify session URL is valid
        assert session_url.startswith("https://")

    def test_start_flow_status_transitions_to_running(self):
        """Test that flow status transitions to running after creation."""
        # Start a flow
        response = self.client.post("/api/v1/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # Wait a bit for status to update
        time.sleep(0.1)

        # Check status
        get_response = self.client.get(f"/api/v1/runs/{run_id}")
        assert get_response.status_code == 200
        run_data = get_response.json()
        assert run_data["status"] == "running"

    def test_start_flow_creates_unique_run_ids(self):
        """Test that starting multiple flows creates unique run IDs."""
        # Start first flow
        response1 = self.client.post("/api/v1/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert response1.status_code == 201
        run_id1 = response1.json()["run_id"]

        # Start second flow
        response2 = self.client.post("/api/v1/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert response2.status_code == 201
        run_id2 = response2.json()["run_id"]

        # Verify they are different
        assert run_id1 != run_id2

    def test_start_flow_initializes_browser_session(self):
        """Test that starting a flow initializes a browser session via Steel.dev."""
        # Start a flow
        response = self.client.post("/api/v1/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert response.status_code == 201

        run_id = response.json()["run_id"]
        session_url = response.json()["session_url"]

        # TODO: Verify that Steel.dev session was created
        # This would require mocking Steel.dev API or checking internal state

        # For now, verify the session URL format
        assert "steel.dev" in session_url or "localhost" in session_url

    def test_start_flow_handles_concurrent_requests(self):
        """Test that the system handles concurrent flow starts correctly."""
        # TODO: Test concurrent requests
        # This would require async testing or multiple clients

        # For now, test sequential requests
        responses = []
        for i in range(3):
            response = self.client.post("/api/v1/runs", json={"flow_id": f"test-flow-{i}", "user_id": "test-user"})
            responses.append(response)
            assert response.status_code == 201

        # Verify all runs are created
        run_ids = [r.json()["run_id"] for r in responses]
        assert len(set(run_ids)) == len(run_ids)  # All unique

    @pytest.mark.parametrize("flow_id", ["simple-flow", "complex-flow", "automation-flow"])
    def test_start_flow_works_with_different_flows(self, flow_id):
        """Test that starting works with different flow configurations."""
        response = self.client.post("/api/v1/runs", json={"flow_id": flow_id, "user_id": "test-user"})
        assert response.status_code == 201

        data = response.json()
        assert "run_id" in data
        assert "session_url" in data

        # Verify the run
        get_response = self.client.get(f"/api/v1/runs/{data['run_id']}")
        assert get_response.status_code == 200
