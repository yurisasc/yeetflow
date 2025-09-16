from http import HTTPStatus

from tests.conftest import BaseTestClass


class TestRunsPostContract(BaseTestClass):
    """Contract tests for POST /runs endpoint."""

    def test_post_runs_returns_201_with_run_id(self):
        """Test that POST /runs returns HTTPStatus.CREATED with run ID."""
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
        assert data["status"] == "running"

    def test_post_runs_requires_flow_id(self):
        """Test that POST /runs requires flow_id."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"user_id": "550e8400-e29b-41d4-a716-446655440000"},
        )
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # Validation error

    def test_post_runs_requires_user_id(self):
        """Test that POST /runs requires user_id."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "550e8400-e29b-41d4-a716-446655440000"},
        )
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # Validation error

    def test_post_runs_invalid_flow_id(self):
        """Test that POST /runs validates flow_id exists."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "00000000-0000-0000-0000-000000000000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "flow not found" in response.json()["detail"].lower()

    def test_post_runs_creates_browser_session(self):
        """Test that POST /runs creates a browser session."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        # Should have a valid session URL
        assert data["session_url"].startswith("https://")
