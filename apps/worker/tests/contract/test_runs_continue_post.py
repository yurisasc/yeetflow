from tests.conftest import BaseTestClass


class TestRunsContinuePostContract(BaseTestClass):
    """Contract tests for POST /runs/{runId}/continue endpoint."""

    def test_post_runs_continue_returns_200_for_awaiting_input(self):
        """Test that POST /runs/{runId}/continue returns 200 for runs awaiting input."""
        # Create a run that will go into awaiting_input state
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Put the run into awaiting_input state
        # For now, assume we have a run in awaiting_input state

        # Continue the run
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "continue"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "running"

    def test_post_runs_continue_nonexistent_run_returns_404(self):
        """Test that POST /runs/{runId}/continue returns 404 for nonexistent run."""
        response = self.client.post(
            f"{self.API_PREFIX}/runs/nonexistent-run-id/continue",
            json={"action": "continue"},
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_post_runs_continue_not_awaiting_input_returns_400(self):
        """Test that POST /runs/{runId}/continue returns 400 for runs not awaiting input."""
        # Create a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # Try to continue a running run
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "continue"}
        )
        assert response.status_code == 400
        assert "not awaiting input" in response.json()["detail"].lower()

    def test_post_runs_continue_requires_action_data(self):
        """Test that POST /runs/{runId}/continue requires action data."""
        # Create and pause a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Put run into awaiting_input state

        # Try without action data
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={}
        )
        assert response.status_code == 422  # Validation error

    def test_post_runs_continue_validates_action_format(self):
        """Test that POST /runs/{runId}/continue validates action format."""
        # Create and pause a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Put run into awaiting_input state

        # Try with invalid action
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "invalid"}
        )
        assert response.status_code == 400

    def test_post_runs_continue_updates_status_to_running(self):
        """Test that POST /runs/{runId}/continue updates status to running."""
        # Create and pause a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Put run into awaiting_input state
        # Verify initial status
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert get_response.status_code == 200
        initial_status = get_response.json()["status"]

        # Continue the run
        response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "continue"}
        )
        assert response.status_code == 200

        # Verify status changed
        get_response_after = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert get_response_after.status_code == 200
        new_status = get_response_after.json()["status"]
        if initial_status == "awaiting_input":
            assert new_status == "running"
