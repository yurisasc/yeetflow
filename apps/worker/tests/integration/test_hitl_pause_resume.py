import time
from http import HTTPStatus

import pytest

from app.models import RunStatus
from tests.conftest import BaseTestClass


@pytest.mark.integration
class TestHITLPauseResumeIntegration(BaseTestClass):
    """Integration tests for human-in-the-loop pause and resume functionality."""

    @pytest.mark.xfail(strict=False, reason="HITL functionality not implemented yet")
    def test_hitl_flow_pauses_on_user_input_required(self):
        """Test that flow pauses when user input is required."""
        # Start a flow that will require user input
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        run_id = response.json()["id"]

        # Wait for the flow to reach awaiting_input state
        self._wait_for_status(run_id, RunStatus.AWAITING_INPUT.value)

        # Verify the run is now awaiting input
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] == RunStatus.AWAITING_INPUT.value

    @pytest.mark.xfail(strict=False, reason="Continue endpoint not implemented yet")
    def test_hitl_resume_after_user_action(self):
        """Test that flow resumes after user provides action."""
        # Start a flow that requires user input
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        run_id = response.json()["id"]

        # Wait for awaiting_input state
        self._wait_for_status(run_id, RunStatus.AWAITING_INPUT.value)

        # Resume the flow with user action
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"action": "click_button"},
        )
        assert resume_response.status_code == HTTPStatus.OK

        # Verify status changes to running
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] == RunStatus.RUNNING.value

    @pytest.mark.xfail(strict=False, reason="Continue endpoint not implemented yet")
    def test_hitl_multiple_pause_resume_cycles(self):
        """Test multiple pause/resume cycles in a single flow."""
        # Start a flow with multiple user interaction points
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440005",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        run_id = response.json()["id"]

        # First pause
        self._wait_for_status(run_id, RunStatus.AWAITING_INPUT.value)
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"action": "fill_form"},
        )
        assert resume_response.status_code == HTTPStatus.OK

        # Second pause
        self._wait_for_status(run_id, RunStatus.AWAITING_INPUT.value)
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"action": "submit_form"},
        )
        assert resume_response.status_code == HTTPStatus.OK

        # Verify final status
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] in {
            RunStatus.RUNNING.value,
            RunStatus.COMPLETED.value,
        }

    @pytest.mark.xfail(strict=False, reason="Continue endpoint not implemented yet")
    def test_hitl_resume_with_invalid_action(self):
        """Test resume with invalid action data."""
        # Start a flow that requires user input
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        run_id = response.json()["id"]

        # Wait for awaiting_input state
        self._wait_for_status(run_id, RunStatus.AWAITING_INPUT.value)

        # Try to resume with invalid action
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"action": "invalid_action"},
        )
        assert resume_response.status_code == HTTPStatus.BAD_REQUEST

        # Verify status remains awaiting_input
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        run_data = get_response.json()
        assert run_data["status"] == RunStatus.AWAITING_INPUT.value

    @pytest.mark.xfail(strict=False, reason="Continue endpoint not implemented yet")
    def test_hitl_resume_preserves_session_state(self):
        """Test that session state is preserved across pause/resume."""
        # Start a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440001",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert response.status_code == HTTPStatus.CREATED

        run_id = response.json()["id"]

        # Get session URL from sessions endpoint
        sessions_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/sessions")
        assert sessions_response.status_code == HTTPStatus.OK
        sessions = sessions_response.json()
        assert len(sessions) > 0
        original_session_url = sessions[0]["session_url"]

        # Wait for pause
        self._wait_for_status(run_id, "awaiting_input")

        # Resume
        resume_response = self.client.post(
            f"{self.API_PREFIX}/runs/{run_id}/continue",
            json={"action": "proceed"},
        )
        assert resume_response.status_code == HTTPStatus.OK

        # Verify session URL is preserved
        sessions_response_after = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/sessions"
        )
        assert sessions_response_after.status_code == HTTPStatus.OK
        sessions_after = sessions_response_after.json()
        assert len(sessions_after) > 0
        assert sessions_after[0]["session_url"] == original_session_url

    def _wait_for_status(self, run_id: str, target_status: str, timeout: int = 10):
        """Helper method to wait for a specific run status."""
        start = time.monotonic()
        while time.monotonic() - start < timeout:
            get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
            assert get_response.status_code == HTTPStatus.OK
            if get_response.json()["status"] == target_status:
                return
            time.sleep(0.2)

        # If we reach here, the status didn't change
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        current_status = get_response.json()["status"]
        pytest.fail(
            f"Run {run_id} did not reach status {target_status}, "
            f"current status: {current_status}",
        )
