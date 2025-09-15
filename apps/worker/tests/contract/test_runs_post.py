import pytest
from httpx import AsyncClient
from fastapi.testclient import TestClient

from app.main import app


class TestRunsPostContract:
    """Contract tests for POST /runs endpoint."""

    def setup_method(self):
        """Set up test client before each test."""
        self.client = TestClient(app)

    def test_post_runs_returns_201_with_run_id(self):
        """Test that POST /runs returns 201 with run ID."""
        # TODO: Implement when endpoint exists
        response = self.client.post("/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert response.status_code == 201
        data = response.json()
        assert "run_id" in data
        assert "session_url" in data
        assert data["status"] == "running"

    def test_post_runs_requires_flow_id(self):
        """Test that POST /runs requires flow_id."""
        response = self.client.post("/runs", json={"user_id": "test-user"})
        assert response.status_code == 422  # Validation error

    def test_post_runs_requires_user_id(self):
        """Test that POST /runs requires user_id."""
        response = self.client.post("/runs", json={"flow_id": "test-flow"})
        assert response.status_code == 422  # Validation error

    def test_post_runs_invalid_flow_id(self):
        """Test that POST /runs validates flow_id exists."""
        response = self.client.post("/runs", json={"flow_id": "nonexistent", "user_id": "test-user"})
        assert response.status_code == 400
        assert "flow not found" in response.json()["detail"].lower()

    def test_post_runs_creates_session(self):
        """Test that POST /runs creates a browser session."""
        response = self.client.post("/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
        assert response.status_code == 201
        data = response.json()
        # Should have a valid session URL
        assert data["session_url"].startswith("https://")

    @pytest.mark.asyncio
    async def test_post_runs_async_handling(self):
        """Test that POST /runs handles async operations correctly."""
        async with AsyncClient(app=app, base_url="http://testserver") as client:
            response = await client.post("/runs", json={"flow_id": "test-flow", "user_id": "test-user"})
            assert response.status_code == 201
