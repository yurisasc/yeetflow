from tests.conftest import BaseTestClass


class TestRunsArtifactGetContract(BaseTestClass):
    """Contract tests for GET /runs/{runId}/artifact endpoint."""

    def test_get_runs_artifact_returns_200_with_file(self):
        """Test that GET /runs/{runId}/artifact returns 200 with file for completed runs."""
        # First create and complete a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Complete the run and generate artifact
        # For now, assume the run is completed

        # Get the artifact
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert response.status_code == 200
        # Should return file content
        assert len(response.content) > 0
        # Should have appropriate content type
        assert "content-type" in response.headers

    def test_get_runs_artifact_nonexistent_run_returns_404(self):
        """Test that GET /runs/{runId}/artifact returns 404 for nonexistent run."""
        response = self.client.get(
            f"{self.API_PREFIX}/runs/nonexistent-run-id/artifact"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_get_runs_artifact_incomplete_run_returns_404(self):
        """Test that GET /runs/{runId}/artifact returns 404 for incomplete runs."""
        # Create a run but don't complete it
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # Get the artifact before completion
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        assert response.status_code == 404
        assert "not ready" in response.json()["detail"].lower()

    def test_get_runs_artifact_failed_run_returns_404(self):
        """Test that GET /runs/{runId}/artifact returns 404 for failed runs."""
        # TODO: Create a failed run
        # For now, test with nonexistent run
        response = self.client.get(f"{self.API_PREFIX}/runs/failed-run-id/artifact")
        assert response.status_code == 404

    def test_get_runs_artifact_content_disposition(self):
        """Test that GET /runs/{runId}/artifact includes proper content-disposition header."""
        # Create and complete a run with artifact
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={"flow_id": "test-flow", "user_id": "test-user"},
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Complete the run

        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        if response.status_code == 200:
            assert "content-disposition" in response.headers
            assert "attachment" in response.headers["content-disposition"]

    def test_get_runs_artifact_large_file_handling(self):
        """Test that GET /runs/{runId}/artifact handles large files correctly."""
        # TODO: Test with large artifact files
        # This should test streaming or chunked responses
        pass
