from http import HTTPStatus
from unittest.mock import patch

from tests.conftest import BaseTestClass, MockStorageBackend


class TestRunsArtifactGetContract(BaseTestClass):
    """Contract tests for GET /runs/{runId}/artifact endpoint."""

    LARGE_FILE_SIZE = 10000
    RANGE_REQUEST_SIZE = 100

    @patch("app.services.artifact.service.get_storage")
    def test_get_runs_artifact_returns_200_with_file(self, mock_get_storage, tmp_path):
        """Test that GET /runs/{runId}/artifact returns 200 with file content."""
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

        # Create a test artifact file using tmp_path
        test_file = tmp_path / f"test_artifact_{run_id}.txt"
        test_content = b"This is a test artifact file"
        test_file.write_bytes(test_content)

        # Mock the storage backend to serve files from tmp_path
        mock_storage = MockStorageBackend({str(test_file): test_file})
        mock_get_storage.return_value = mock_storage

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

    @patch("app.services.artifact.service.get_storage")
    def test_get_runs_artifact_content_disposition(self, mock_get_storage, tmp_path):
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

        # Create test artifact using tmp_path
        test_file = tmp_path / "test_document.pdf"
        test_content = b"Test PDF content"
        test_file.write_bytes(test_content)

        # Mock the storage backend to serve files from tmp_path
        mock_storage = MockStorageBackend({str(test_file): test_file})
        mock_get_storage.return_value = mock_storage

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

    @patch("app.services.artifact.service.get_storage")
    def test_get_runs_artifact_large_file_handling(self, mock_get_storage, tmp_path):
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

        # Create large test artifact using tmp_path
        large_file = tmp_path / f"large_artifact_{run_id}.bin"
        large_content = b"x" * self.LARGE_FILE_SIZE  # 10KB of data
        large_file.write_bytes(large_content)

        # Mock the storage backend to serve files from tmp_path
        mock_storage = MockStorageBackend({str(large_file): large_file})
        mock_get_storage.return_value = mock_storage

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

        # Accept either Content-Length (exact) or Transfer-Encoding
        if "content-length" in response.headers:
            assert response.headers["content-length"] == str(self.LARGE_FILE_SIZE)
        else:
            assert response.headers.get("transfer-encoding", "").lower() == "chunked"
        # Verify we can access content without loading everything at once in test
        # (In real usage, this would be streamed chunk by chunk)
        assert hasattr(response, "content"), "Response should have content"
        # The content length should match what we expect for streaming validation
        assert len(response.content) == self.LARGE_FILE_SIZE

        # Test that the response supports range requests (partial content)
        # This is important for large file handling and streaming validation
        range_response = self.client.get(
            f"{self.API_PREFIX}/runs/{run_id}/artifact",
            headers={"Range": f"bytes=0-{self.RANGE_REQUEST_SIZE - 1}", **headers},
        )

        # Should be 206 when supported; otherwise at least 200 OK
        assert range_response.status_code in (HTTPStatus.PARTIAL_CONTENT, HTTPStatus.OK)
        if range_response.status_code == HTTPStatus.PARTIAL_CONTENT:
            assert "content-range" in range_response.headers
            assert "content-length" in range_response.headers
            # Should return exactly RANGE_REQUEST_SIZE bytes
            # (0 to RANGE_REQUEST_SIZE-1 inclusive)
            assert len(range_response.content) == self.RANGE_REQUEST_SIZE
            assert range_response.content == large_content[: self.RANGE_REQUEST_SIZE]
