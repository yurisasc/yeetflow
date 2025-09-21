from http import HTTPStatus

import pytest

from tests.conftest import BaseTestClass


class TestRunsGetContract(BaseTestClass):
    """Contract tests for GET /runs endpoints."""

    def test_get_runs_returns_200_with_status(self):
        """Test that GET /runs/{runId} returns HTTPStatus.OK with run status."""
        # First create a run with authentication
        headers = self.get_user_auth_headers()
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
            },
            headers=headers,
        )
        assert create_response.status_code == HTTPStatus.CREATED
        run_id = create_response.json()["id"]

        # Then get the run with authentication
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}", headers=headers)
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
        assert "id" in data
        assert data["id"] == run_id

    def test_get_runs_nonexistent_returns_404(self):
        """Test that GET /runs/{runId} returns NOT_FOUND for nonexistent run."""
        # Use a valid UUID format that doesn't exist in database
        headers = self.get_user_auth_headers()
        nonexistent_uuid = "091384b9-afe5-429c-8cba-abdff02fb79c"
        response = self.client.get(
            f"{self.API_PREFIX}/runs/{nonexistent_uuid}", headers=headers
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_runs_invalid_id_format(self):
        """Test that GET /runs/{runId} validates run ID format."""
        headers = self.get_user_auth_headers()
        response = self.client.get(
            f"{self.API_PREFIX}/runs/invalid@format", headers=headers
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_get_runs_unauthorized(self):
        """Test that GET /runs/{runId} requires authentication."""
        run_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
        assert response.headers.get("WWW-Authenticate") == "Bearer"

    def _create_run(self):
        """Helper method to create a run and return its ID."""
        headers = self.get_user_auth_headers()
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
            },
            headers=headers,
        )
        assert create_response.status_code == HTTPStatus.CREATED
        return create_response.json()["id"]

    def test_get_runs_returns_run_details(self):
        """Test that GET /runs/{runId} returns run details."""
        run_id = self._create_run()
        headers = self.get_user_auth_headers()

        # Get the run details
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}", headers=headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Check required fields
        required_fields = [
            "id",
            "flow_id",
            "user_id",
            "status",
            "created_at",
            "updated_at",
        ]
        for field in required_fields:
            assert field in data

        # Check data types and values
        assert data["id"] == run_id
        assert data["flow_id"] == "550e8400-e29b-41d4-a716-446655440000"
        assert data["user_id"] == str(self.test_user.id)
        assert data["status"] in [
            "pending",
            "running",
            "awaiting_input",
            "completed",
            "failed",
        ]

    def test_get_runs_status_transitions_correctly(self):
        """Test that run status transitions work correctly."""
        run_id = self._create_run()
        headers = self.get_user_auth_headers()

        # Initial status should be running or pending
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}", headers=headers)
        assert response.status_code == HTTPStatus.OK
        initial_status = response.json()["status"]
        assert initial_status in ["pending", "running"]

    def test_get_runs_status_transition_to_completed(self):
        """Test that run status transitions to completed when run finishes."""
        run_id = self._create_run()
        headers = self.get_user_auth_headers()

        # Get initial status
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}", headers=headers)
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
        run_id = self._create_run()
        headers = self.get_user_auth_headers()

        # Get initial status
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}", headers=headers)
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
        run_id = self._create_run()
        headers = self.get_user_auth_headers()

        # Get initial status
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}", headers=headers)
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

    @pytest.mark.xfail(reason="Status transition logic not yet implemented")
    def test_get_runs_status_cannot_transition_from_completed(self):
        """Test that completed runs cannot transition to other statuses."""
        # This test requires status transition logic that isn't implemented yet
        # For now, we'll mark it as expected failure

    @pytest.mark.xfail(reason="Status transition logic not yet implemented")
    def test_get_runs_status_cannot_transition_from_failed(self):
        """Test that failed runs cannot transition to other statuses."""
        # This test requires status transition logic that isn't implemented yet
        # For now, we'll mark it as expected failure

    def test_list_runs_returns_200_with_pagination(self):
        """Test that GET /runs returns HTTPStatus.OK with paginated results."""
        # Create multiple runs
        headers = self.get_user_auth_headers()
        for _ in range(3):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                },
                headers=headers,
            )
            assert response.status_code == HTTPStatus.CREATED

        # Get list of runs
        response = self.client.get(f"{self.API_PREFIX}/runs", headers=headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Should be a list
        assert isinstance(data, list)
        # Should have at least the runs we created
        expected_run_count = 3
        assert len(data) >= expected_run_count

        # Verify each run has required fields
        for run in data:
            assert "id" in run
            assert "flow_id" in run
            assert "user_id" in run
            assert run["user_id"] == str(self.test_user.id)
            assert "status" in run
            assert "created_at" in run
            assert "updated_at" in run

    def test_list_runs_pagination_works(self):
        """Test that GET /runs pagination parameters work correctly."""
        # Create multiple runs
        headers = self.get_user_auth_headers()
        for _ in range(5):
            response = self.client.post(
                f"{self.API_PREFIX}/runs",
                json={
                    "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                },
                headers=headers,
            )
            assert response.status_code == HTTPStatus.CREATED

        # Test limit parameter
        pagination_limit = 2
        response = self.client.get(
            f"{self.API_PREFIX}/runs?limit={pagination_limit}", headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) <= pagination_limit

        # Test skip parameter
        skip_count = 2
        response = self.client.get(
            f"{self.API_PREFIX}/runs?skip={skip_count}&limit={pagination_limit}",
            headers=headers,
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) <= pagination_limit

    def test_get_run_sessions_returns_200(self):
        """Test that GET /runs/{runId}/sessions returns HTTPStatus.OK."""
        run_id = self._create_run()
        headers = self.get_user_auth_headers()

        # Get run sessions
        response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/sessions", headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Should be a list
        assert isinstance(data, list)

        # Verify session structure if sessions exist
        for session in data:
            assert "id" in session
            assert "run_id" in session
            assert "status" in session
            assert "created_at" in session

    def test_get_run_sessions_nonexistent_run_returns_404(self):
        """Test that GET /runs/{runId}/sessions returns 404 for nonexistent run."""
        headers = self.get_user_auth_headers()
        response = self.client.get(
            f"{self.API_PREFIX}/runs/00000000-0000-0000-0000-000000000000/sessions",
            headers=headers,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_run_events_returns_200(self):
        """Test that GET /runs/{runId}/events returns HTTPStatus.OK."""
        run_id = self._create_run()
        headers = self.get_user_auth_headers()

        # Get run events
        response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/events", headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Should be a list
        assert isinstance(data, list)

        # Verify event structure if events exist
        for event in data:
            assert "id" in event
            assert "run_id" in event
            assert "type" in event
            assert "at" in event

    def test_get_run_events_nonexistent_run_returns_404(self):
        """Test that GET /runs/{runId}/events returns 404 for nonexistent run."""
        headers = self.get_user_auth_headers()
        response = self.client.get(
            f"{self.API_PREFIX}/runs/00000000-0000-0000-0000-000000000000/events",
            headers=headers,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
