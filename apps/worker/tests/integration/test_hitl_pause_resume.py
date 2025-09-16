import pytest
import time
from tests.conftest import BaseTestClass


class TestHITLPauseResumeIntegration(BaseTestClass):
    """Integration tests for human-in-the-loop pause and resume functionality."""

    def test_hitl_flow_pauses_on_user_input_required(self):
        """Test that flow pauses when user input is required."""
        # Start a flow that will require user input
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "hitl-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # Wait for the flow to reach awaiting_input state
        max_attempts = 10
        for attempt in range(max_attempts):
            get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
            assert get_response.status_code == 200
            status = get_response.json()["status"]

            if status == "awaiting_input":
                break

            time.sleep(0.5)

        # Verify the run is now awaiting input
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] == "awaiting_input"

    def test_hitl_resume_after_user_action(self):
        """Test that flow resumes after user provides action."""
        # Start a flow that requires user input
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "hitl-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # Wait for awaiting_input state
        self._wait_for_status(run_id, "awaiting_input")

        # Resume the flow with user action
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "click_button"}
        )
        assert resume_response.status_code == 200

        # Verify status changes to running
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] == "running"

    def test_hitl_multiple_pause_resume_cycles(self):
        """Test multiple pause/resume cycles in a single flow."""
        # Start a flow with multiple user interaction points
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "multi-hitl-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # First pause
        self._wait_for_status(run_id, "awaiting_input")
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "fill_form"}
        )
        assert resume_response.status_code == 200

        # Second pause
        self._wait_for_status(run_id, "awaiting_input")
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "submit_form"}
        )
        assert resume_response.status_code == 200

        # Verify final status
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] in ["running", "completed"]

    def test_hitl_resume_with_invalid_action(self):
        """Test resume with invalid action data."""
        # Start a flow that requires user input
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "hitl-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # Wait for awaiting_input state
        self._wait_for_status(run_id, "awaiting_input")

        # Try to resume with invalid action
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"action": "invalid_action"},
        )
        assert resume_response.status_code == 400

        # Verify status remains awaiting_input
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] == "awaiting_input"

    def test_hitl_resume_preserves_session_state(self):
        """Test that session state is preserved across pause/resume."""
        # Start a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "hitl-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]
        original_session_url = response.json()["session_url"]

        # Wait for pause
        self._wait_for_status(run_id, "awaiting_input")

        # Get run data before resume
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data_before = get_response.json()

        # Resume
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue", json={"action": "proceed"}
        )
        assert resume_response.status_code == 200

        # Verify session URL is preserved
        get_response_after = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data_after = get_response_after.json()
        assert run_data_after["session_url"] == original_session_url

    def _wait_for_status(self, run_id: str, target_status: str, timeout: int = 10):
        """Helper method to wait for a specific run status."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
            assert get_response.status_code == 200
            if get_response.json()["status"] == target_status:
                return
            time.sleep(0.5)

        # If we reach here, the status didn't change
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        current_status = get_response.json()["status"]
        pytest.fail(
            f"Run {run_id} did not reach status {target_status}, current status: {current_status}"
        )
