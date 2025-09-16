import pytest
import time
from tests.conftest import BaseTestClass


class TestCompletionArtifactIntegration(BaseTestClass):
    """Integration tests for flow completion and artifact generation."""

    def test_flow_completion_generates_artifact(self):
        """Test that completed flow generates downloadable artifact."""
        # Start a flow that will complete automatically
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "auto-complete-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # Wait for completion
        self._wait_for_status(run_id, "completed")

        # Verify artifact is available
        artifact_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert artifact_response.status_code == 200

        # Verify artifact has content
        assert len(artifact_response.content) > 0

        # Verify proper headers
        assert "content-disposition" in artifact_response.headers
        assert "attachment" in artifact_response.headers["content-disposition"]

    def test_flow_completion_updates_status_correctly(self):
        """Test that flow status updates to completed when finished."""
        # Start a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "quick-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # Initially should be running or pending
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        initial_status = get_response.json()["status"]
        assert initial_status in ["pending", "running"]

        # Wait for completion
        self._wait_for_status(run_id, "completed")

        # Verify final status
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        final_data = get_response.json()
        assert final_data["status"] == "completed"

    def test_completed_flow_artifact_persistence(self):
        """Test that artifacts persist after flow completion."""
        # Start and complete a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "auto-complete-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]
        self._wait_for_status(run_id, "completed")

        # Get artifact
        artifact_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert artifact_response.status_code == 200
        original_content = artifact_response.content

        # Wait a bit and get artifact again
        time.sleep(1)
        artifact_response2 = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact"
        )
        assert artifact_response2.status_code == 200
        assert artifact_response2.content == original_content

    def test_failed_flow_does_not_generate_artifact(self):
        """Test that failed flows do not generate artifacts."""
        # Start a flow that will fail
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "failing-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]

        # Wait for failure
        self._wait_for_status(run_id, "failed")

        # Verify no artifact available
        artifact_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert artifact_response.status_code == 404

    def test_artifact_content_type_based_on_flow_type(self):
        """Test that artifact content type matches flow output type."""
        # Start a flow that generates PDF
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "pdf-generation-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]
        self._wait_for_status(run_id, "completed")

        # Check artifact content type
        artifact_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert artifact_response.status_code == 200

        # Should have appropriate content type for PDF
        if "content-type" in artifact_response.headers:
            assert (
                "pdf" in artifact_response.headers["content-type"].lower()
                or "application" in artifact_response.headers["content-type"].lower()
            )

    def test_large_artifact_handling(self):
        """Test that large artifacts are handled correctly."""
        # Start a flow that generates large output
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "large-output-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]
        self._wait_for_status(run_id, "completed")

        # Get artifact
        artifact_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert artifact_response.status_code == 200

        # Verify reasonable size (should be > 1KB for "large" output)
        assert len(artifact_response.content) > 1024

    def test_artifact_filename_includes_run_id(self):
        """Test that artifact filename includes run ID."""
        # Start and complete a flow
        response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "auto-complete-flow", "user_id": "test-user"},
        )
        assert response.status_code == 201

        run_id = response.json()["run_id"]
        self._wait_for_status(run_id, "completed")

        # Get artifact
        artifact_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert artifact_response.status_code == 200

        # Check filename in content-disposition
        content_disposition = artifact_response.headers.get("content-disposition", "")
        assert run_id in content_disposition

    def _wait_for_status(self, run_id: str, target_status: str, timeout: int = 30):
        """Helper method to wait for a specific run status."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
            assert get_response.status_code == 200
            if get_response.json()["status"] == target_status:
                return
            time.sleep(1)

        # If we reach here, the status didn't change
        get_response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}")
        current_status = get_response.json()["status"]
        pytest.fail(
            f"Run {run_id} did not reach status {target_status}, current status: {current_status}"
        )
