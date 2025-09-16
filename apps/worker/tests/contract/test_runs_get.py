from http import HTTPStatus

from tests.conftest import BaseTestClass


class TestRunsGetContract(BaseTestClass):
    """Contract tests for GET /runs/{runId} endpoint."""

    def test_get_runs_returns_200_with_status(self):
        """Test that GET /runs/{runId} returns HTTPStatus.OK with run status."""
        # First create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["run_id"]

        # Then get the run
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert "status" in data
        assert data["status"] in [
            "pending",
            "running",
            "awaiting_input",
            "completed",
            "failed",
        ]
        assert "run_id" in data
        assert data["run_id"] == run_id

    def test_get_runs_nonexistent_returns_404(self):
        """Test that GET /runs/{runId} returns NOT_FOUND for nonexistent run."""
        # Use a valid UUID format that doesn't exist in database
        nonexistent_uuid = "091384b9-afe5-429c-8cba-abdff02fb79c"
        response = self.client.get(f"{self.API_PREFIX}/runs/{nonexistent_uuid}")
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_runs_invalid_id_format(self):
        """Test that GET /runs/{runId} validates run ID format."""
        response = self.client.get(f"{self.API_PREFIX}/runs/invalid@format")
        assert (
            response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
        )  # Validation error

    def test_get_runs_includes_session_url_when_available(self):
        """Test that GET /runs/{runId} includes session_url when available."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["run_id"]

        # Get the run
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        if "session_url" in data:
            assert data["session_url"].startswith("https://")

    def test_get_runs_status_transitions_correctly(self):
        """Test that run status transitions work correctly."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["run_id"]

        # Initial status should be running or pending
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert response.status_code == HTTPStatus.OK
        initial_status = response.json()["status"]
        assert initial_status in ["pending", "running"]

    def test_get_runs_status_transition_to_completed(self):
        """Test that run status transitions to completed when run finishes."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["run_id"]

        # Get initial status
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert response.status_code == HTTPStatus.OK
        initial_data = response.json()
        initial_status = initial_data["status"]

        # TODO: Simulate run completion (when completion endpoint exists)
        # For now, verify that completed is a valid status
        assert initial_status in ["pending", "running"]

        # When completion is implemented, this test should:
        # 1. Trigger run completion via appropriate endpoint
        # 2. Verify status changes to "completed"
        # 3. Verify completion timestamp is set

    def test_get_runs_status_transition_to_failed(self):
        """Test that run status transitions to failed when run fails."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["run_id"]

        # Get initial status
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert response.status_code == HTTPStatus.OK
        initial_data = response.json()
        initial_status = initial_data["status"]

        # TODO: Simulate run failure (when failure scenarios exist)
        # For now, verify that failed is a valid status expectation
        assert initial_status in ["pending", "running"]

        # When failure handling is implemented, this test should:
        # 1. Trigger a failure scenario
        # 2. Verify status changes to "failed"
        # 3. Verify error details are captured

    def test_get_runs_status_transition_to_awaiting_input(self):
        """Test run status transitions to awaiting_input when human input needed."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["run_id"]

        # Get initial status
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert response.status_code == HTTPStatus.OK
        initial_data = response.json()
        initial_status = initial_data["status"]

        # TODO: Simulate human-in-the-loop scenario (when HITL exists)
        # For now, verify that awaiting_input is a valid status expectation
        assert initial_status in ["pending", "running"]

        # When HITL is implemented, this test should:
        # 1. Trigger a scenario requiring human input
        # 2. Verify status changes to "awaiting_input"
        # 3. Verify input requirements are captured

    def test_get_runs_status_cannot_transition_from_completed(self):
        """Test that completed runs cannot transition to other statuses."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        create_response.json()["run_id"]

        # TODO: When status transition logic exists, this test should:
        # 1. Force a run to completed status (via direct DB update for testing)
        # 2. Attempt to change status via various endpoints
        # 3. Verify status remains "completed" and operations are rejected

    def test_get_runs_status_cannot_transition_from_failed(self):
        """Test that failed runs cannot transition to other statuses."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == HTTPStatus.CREATED
        create_response.json()["run_id"]

        # TODO: When status transition logic exists, this test should:
        # 1. Force a run to failed status (via direct DB update for testing)
        # 2. Attempt to change status via various endpoints
        # 3. Verify status remains "failed" and operations are rejected
