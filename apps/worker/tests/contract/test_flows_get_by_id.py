from http import HTTPStatus

from tests.conftest import BaseTestClass


class TestFlowsGetByIdContract(BaseTestClass):
    """Contract tests for GET /api/v1/flows/{flow_id} endpoint."""

    def test_get_flow_by_id_returns_200_with_flow_data(self):
        """Test that GET /api/v1/flows/{flow_id} returns OK with flow data."""
        # Use the test flow created in conftest.py
        flow_id = "550e8400-e29b-41d4-a716-446655440000"
        headers = self.get_user_auth_headers()

        response = self.client.get(
            f"{self.API_PREFIX}/flows/{flow_id}", headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Verify expected fields from FlowRead model
        assert "id" in data
        assert data["id"] == flow_id
        assert "key" in data
        assert data["key"] == "test-flow"
        assert "name" in data
        assert data["name"] == "Test Flow"
        assert "description" in data
        assert data["description"] == "A test flow for development and testing"
        assert "created_by" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_get_flow_by_id_nonexistent_returns_404(self):
        """Test that GET /api/v1/flows/{flow_id} returns NOT_FOUND for nonexistent."""
        # Use a valid UUID format that doesn't exist in database
        headers = self.get_user_auth_headers()
        nonexistent_uuid = "091384b9-afe5-429c-8cba-abdff02fb79c"
        response = self.client.get(
            f"{self.API_PREFIX}/flows/{nonexistent_uuid}", headers=headers
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_flow_by_id_unauthenticated_returns_401(self):
        """Test that GET /api/v1/flows/{flow_id} requires authentication."""
        flow_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self.client.get(f"{self.API_PREFIX}/flows/{flow_id}")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_flow_by_id_access_denied_returns_404(self):
        """Test that GET /api/v1/flows/{flow_id} returns 404 when user lacks access."""
        # Use an admin-owned flow that regular users shouldn't be able to access
        admin_flow_id = "550e8400-e29b-41d4-a716-446655440007"
        headers = self.get_user_auth_headers()  # Regular user, not admin

        response = self.client.get(
            f"{self.API_PREFIX}/flows/{admin_flow_id}", headers=headers
        )
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert "not found" in response.json()["detail"].lower()
