from http import HTTPStatus

from app.models import RunStatus
from tests.conftest import BaseTestClass


class TestRunsContinuePostContract(BaseTestClass):
    """Contract tests for POST /runs/{runId}/continue endpoint."""

    def test_post_runs_continue_returns_200_for_awaiting_input(self):
        """Test that POST /runs/{runId}/continue returns OK for runs awaiting input."""
        # Create a run that will go into awaiting_input state
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["id"]

        # Put the run into awaiting_input state
        self.set_run_status(run_id, RunStatus.AWAITING_INPUT)

        # Continue the run
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"input_payload": {"action": "continue"}},
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "status" in data
        assert data["status"] == "running"

    def test_post_runs_continue_nonexistent_run_returns_404(self):
        """Test that POST /runs/{runId}/continue returns 404 for nonexistent run."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs/550e8400-e29b-41d4-a716-446655440001/continue",
            json={"input_payload": {"action": "continue"}},
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_post_runs_continue_not_awaiting_input_returns_400(self):
        """Test POST /runs/{runId}/continue returns 400 for runs not awaiting input."""
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

        # Ensure the run is in running state (not awaiting_input)
        self.set_run_status(run_id, RunStatus.RUNNING)

        # Try to continue a running run
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"input_payload": {"action": "continue"}},
        )
        assert response.status_code == HTTPStatus.BAD_REQUEST
        assert "not awaiting input" in response.json()["detail"].lower()

    def test_post_runs_continue_requires_action_data(self):
        """Test that POST /runs/{runId}/continue requires action data."""
        # Create and pause a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["id"]

        # Put run into awaiting_input state
        self.set_run_status(run_id, RunStatus.AWAITING_INPUT)

        # Try without action data
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={},
        )
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # Validation error

    def test_post_runs_continue_validates_action_format(self):
        """Test that POST /runs/{runId}/continue validates action format."""
        # Create and pause a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["id"]

        # Put run into awaiting_input state
        self.set_run_status(run_id, RunStatus.AWAITING_INPUT)

        # Try with invalid action
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"input_payload": {"action": "invalid"}},
        )
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # Pydantic validation error

    def test_post_runs_continue_updates_status_to_running(self):
        """Test that POST /runs/{runId}/continue updates status to running."""
        # Create and pause a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["id"]

        # Put run into awaiting_input state
        self.set_run_status(run_id, RunStatus.AWAITING_INPUT)

        # Verify initial status
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert get_response.status_code == HTTPStatus.OK

        # Continue the run
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"input_payload": {"action": "continue"}},
        )
        assert response.status_code == HTTPStatus.OK

        # Verify status changed to running
        get_response_after = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert get_response_after.status_code == HTTPStatus.OK
        new_status = get_response_after.json()["status"]
        assert new_status == RunStatus.RUNNING
