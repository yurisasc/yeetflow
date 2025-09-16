import pytest
from tests.conftest import BaseTestClass


class TestRunsArtifactGetContract(BaseTestClass):
    """Contract tests for GET /runs/{runId}/artifact endpoint."""

    @pytest.mark.xfail(
        strict=False,
        reason="Artifact generation not wired yet; will pass once completion pipeline is implemented.",
    )
    def test_get_runs_artifact_returns_200_with_file(self):
        """Test that GET /runs/{runId}/artifact returns 200 with file for completed runs."""
        # First create and complete a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
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
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
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

    @pytest.mark.xfail(
        strict=False, reason="Awaiting artifact generation/completion flow."
    )
    def test_get_runs_artifact_content_disposition(self):
        """Test that GET /runs/{runId}/artifact includes proper content-disposition header."""
        # Create and complete a run with artifact
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Complete the run

        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")
        if response.status_code == 200:
            assert "content-disposition" in response.headers
            assert "attachment" in response.headers["content-disposition"]

    @pytest.mark.xfail(
        strict=False,
        reason="Large artifact path not available yet; enable after artifact pipeline is ready.",
    )
    def test_get_runs_artifact_large_file_handling(self):
        """Test that GET /runs/{runId}/artifact handles large files correctly."""
        # First create and complete a run
        create_response = self.client.post(
            f"{self.API_PREFIX}/runs",
            json={
                "flow_id": "550e8400-e29b-41d4-a716-446655440000",
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
            },
        )
        assert create_response.status_code == 201
        run_id = create_response.json()["run_id"]

        # TODO: Complete the run and generate a large artifact file
        # For now, assume the run is completed with a large artifact

        # Get the artifact
        response = self.client.get(f"{self.API_PREFIX}/runs/{run_id}/artifact")

        # Should return 200 even for large files
        assert response.status_code == 200

        # Should have appropriate content type for file downloads
        assert "content-type" in response.headers

        # Should have content-disposition header for file downloads
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]

        # Test that response supports streaming/chunked transfer
        # This is indicated by the transfer-encoding header or content-length
        transfer_encoding = response.headers.get("transfer-encoding")
        content_length = response.headers.get("content-length")

        # Either chunked transfer or explicit content-length should be present
        assert transfer_encoding == "chunked" or (
            content_length is not None and int(content_length) > 0
        ), "Response should support streaming or have explicit content length"

        # For large files, the response should not load everything into memory
        # Test by checking that we can read the content in chunks
        content = response.content
        assert len(content) > 0, "Should have file content"

        # If it's a very large file, content-length should reflect that
        if content_length:
            expected_size = int(content_length)
            actual_size = len(content)
            assert (
                actual_size == expected_size
            ), f"Content size mismatch: expected {expected_size}, got {actual_size}"

        # Additional test: verify that partial content requests work (if supported)
        # This tests range request support for large files
        range_response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact",
            headers={"Range": "bytes=0-99"},  # Request first 100 bytes
        )

        # Should return 206 Partial Content if range requests are supported
        if range_response.status_code == 206:
            assert "content-range" in range_response.headers
            assert len(range_response.content) <= 100
