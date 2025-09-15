import pytest
from fastapi.testclient import TestClient

from app.main import app


class TestRunsGetContract:
    """Contract tests for GET /runs/{runId} endpoint."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_get_runs_returns_200_with_status(self):
        """Test that GET /runs/{runId} returns 200 with run status."""
        # First create a run
        create_response = self.client.post("/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # Then get the run
        response = self.client.get(f"/runs/{run_id}")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["pending", "running", "awaiting_input", "completed", "failed"]
        assert "run_id" in data
        assert data["run_id"] == run_id

    def test_get_runs_nonexistent_returns_404(self):
        """Test that GET /runs/{runId} returns 404 for nonexistent run."""
        response = self.client.get("/runs/nonexistent-run-id")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_runs_invalid_id_format(self):
        """Test that GET /runs/{runId} validates run ID format."""
        response = self.client.get("/runs/invalid@format")
        assert response.status_code == 422  # Validation error

    def test_get_runs_includes_session_url_when_available(self):
        """Test that GET /runs/{runId} includes session_url when available."""
        # Create a run
        create_response = self.client.post("/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # Get the run
        response = self.client.get(f"/runs/{run_id}")
        assert response.status_code == 200
        data = response.json()
        if "session_url" in data:
            assert data["session_url"].startswith("https://")

    def test_get_runs_status_transitions_correctly(self):
        """Test that run status transitions work correctly."""
        # Create a run
        create_response = self.client.post("/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # Initial status should be running or pending
        response = self.client.get(f"/runs/{run_id}")
        assert response.status_code == 200
        initial_status = response.json()["status"]
        assert initial_status in ["pending", "running"]

        # TODO: Test status transitions when implementation exists
