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
        assert "id" in data
        assert data["status"] == "running"
        assert data["flow_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert data["user_id"] == "550e8400-e29b-41d4-a716-446655440000"

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
        """Test that POST /runs returns BAD_REQUEST for invalid flow_id."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "00000000-0000-0000-0000-000000000000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        # Should return BAD_REQUEST for invalid flow_id
        assert response.status_code == HTTPStatus.BAD_REQUEST
        data = response.json()
        assert "detail" in data
        assert "does not exist" in data["detail"]

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
        run_id = data["id"]

        # Verify the run was created and is in running state
        assert data["status"] == "running"

        # Check that sessions were created for this run
        sessions_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/sessions")
        assert sessions_response.status_code == HTTPStatus.OK
        sessions = sessions_response.json()
        assert len(sessions) > 0  # Should have at least one session
