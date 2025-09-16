from tests.conftest import BaseTestClass


class TestRunsPostContract(BaseTestClass):
    """Contract tests for POST /runs endpoint."""

    def test_post_runs_returns_201_with_run_id(self):
        """Test that POST /runs returns 201 with run ID."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201
        data = response.json()
        assert "run_id" in data
        assert "session_url" in data
        assert data["status"] == "running"

    def test_post_runs_requires_flow_id(self):
        """Test that POST /runs requires flow_id."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs", json={"user_id": "test-user"}
        )
        assert response.status_code == 422  # Validation error

    def test_post_runs_requires_user_id(self):
        """Test that POST /runs requires user_id."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs", json={"flow_id": "test-flow"}
        )
        assert response.status_code == 422  # Validation error

    def test_post_runs_invalid_flow_id(self):
        """Test that POST /runs validates flow_id exists."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "nonexistent", "user_id": "test-user"},
        )
        assert response.status_code == 400
        assert "flow not found" in response.json()["detail"].lower()

    def test_post_runs_creates_browser_session(self):
        """Test that POST /runs creates a browser session."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201
        data = response.json()
        # Should have a valid session URL
        assert data["session_url"].startswith("https://")
