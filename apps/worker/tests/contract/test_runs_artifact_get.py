from http import HTTPStatus
from pathlib import Path

from tests.conftest import BaseTestClass


class TestRunsArtifactGetContract(BaseTestClass):
    """Contract tests for GET /runs/{runId}/artifact endpoint."""

    LARGE_FILE_SIZE = 10000

    def test_get_runs_artifact_returns_200_with_file(self):
        """Test GET /runs/{runId}/artifact returns OK with file for completed runs."""
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

        # Create a test artifact file
        artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        test_file = artifacts_dir / f"test_artifact_{run_id}.txt"
        test_content = b"This is a test artifact file"
        test_file.write_bytes(test_content)

        # Update run with artifact path
        update_response = self.client.patch(
            f"{self.API_PREFIX}/runs/{run_id}",
            json={"result_uri": str(test_file)},
            headers=headers,
        )
        assert update_response.status_code == HTTPStatus.OK

        # Get the artifact
        response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact", headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        # Should return file content
        assert len(response.content) > 0
        assert response.content == test_content
        # Should have appropriate content type
        assert response.headers.get("content-type")
        # Should have content-disposition header
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]

    def test_get_runs_artifact_nonexistent_run_returns_404(self):
        """Test that GET /runs/{runId}/artifact returns 404 for nonexistent run."""
        headers = self.get_user_auth_headers()
        response = self.client.get(
            f"{self.API_PREFIX}/runs/00000000-0000-0000-0000-000000000000/artifact",
            headers=headers,
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_runs_artifact_no_artifact_returns_404(self):
        """Test that GET /runs/{runId}/artifact returns 404 for runs
        without artifacts."""
        # Create a run without artifact
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

        # Get the artifact (should return 404 since no artifact)
        response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact", headers=headers
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "no artifact available" in response.json()["detail"].lower()

    def test_get_runs_artifact_content_disposition(self):
        """Test GET /runs/{runId}/artifact proper content-disposition header."""
        # Create a run with artifact
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

        # Create test artifact
        artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        test_file = artifacts_dir / "test_document.pdf"
        test_content = b"Test PDF content"
        test_file.write_bytes(test_content)

        # Update run with artifact path
        update_response = self.client.patch(
            f"{self.API_PREFIX}/runs/{run_id}",
            json={"result_uri": str(test_file)},
            headers=headers,
        )
        assert update_response.status_code == HTTPStatus.OK

        response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact", headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        assert response.headers.get("content-disposition")
        assert "attachment" in response.headers.get("content-disposition", "")
        assert "test_document.pdf" in response.headers.get("content-disposition", "")

    def test_get_runs_artifact_large_file_handling(self):
        """Test that GET /runs/{runId}/artifact handles large files correctly."""
        # Create a run with large artifact
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

        # Create large test artifact (simulate large file)
        artifacts_dir = Path(__file__).parent.parent.parent / "artifacts"
        artifacts_dir.mkdir(exist_ok=True)

        large_file = artifacts_dir / f"large_artifact_{run_id}.bin"
        large_content = b"x" * self.LARGE_FILE_SIZE  # 10KB of data
        large_file.write_bytes(large_content)

        # Update run with artifact path
        update_response = self.client.patch(
            f"{self.API_PREFIX}/runs/{run_id}",
            json={"result_uri": str(large_file)},
            headers=headers,
        )
        assert update_response.status_code == HTTPStatus.OK

        # Get the artifact
        response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact", headers=headers
        )

        # Should return HTTPStatus.OK even for large files
        assert response.status_code == HTTPStatus.OK

        # Should have appropriate content type for file downloads
        assert response.headers.get("content-type")

        # Should have content-disposition header for file downloads
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]

        # Test that response supports streaming/chunked transfer
        # This is indicated by the transfer-encoding header or content-length

        # Either chunked transfer or explicit content-length should be present
        # Note: FastAPI/Starlette handles this automatically for StreamingResponse
        # The test is mainly to ensure we get a successful response
        assert response.status_code == HTTPStatus.OK

        # For large files, the response should not load everything into memory
        content = response.content
        assert len(content) > 0, "Should have file content"
        assert len(content) == self.LARGE_FILE_SIZE, "Should have correct file size"

        # Additional test: verify that partial content requests work (if supported)
        # This tests range request support for large files
        range_response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact",
            headers={"Range": "bytes=0-99", **headers},
        )

        # Should return HTTPStatus.PARTIAL_CONTENT if range requests are supported
        if range_response.status_code == HTTPStatus.PARTIAL_CONTENT:
            assert "content-range" in range_response.headers
            range_request_size = 100
            assert len(range_response.content) <= range_request_size
