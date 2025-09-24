from http import HTTPStatus

from tests.conftest import BaseTestClass

# Number of test flows created for test_user in conftest.py
TEST_USER_FLOW_COUNT = 6


class TestFlowsGetContract(BaseTestClass):
    """Contract tests for GET /api/v1/flows list endpoint."""

    def test_get_flows_returns_200_with_flows_list(self):
        """Test that GET /api/v1/flows returns OK with list of visible flows."""
        headers = self.get_user_auth_headers()

        response = self.client.get(f"{self.API_PREFIX}/flows", headers=headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Should have 'flows' key with array
        assert "flows" in data
        assert isinstance(data["flows"], list)

        # Should have at least the test flows created in conftest
        assert len(data["flows"]) >= TEST_USER_FLOW_COUNT

        # Check structure of first flow
        if data["flows"]:
            flow = data["flows"][0]
            assert "id" in flow
            assert "key" in flow
            assert "name" in flow
            assert "description" in flow
            assert "created_by" in flow
            assert "created_at" in flow
            assert "updated_at" in flow

    def test_get_flows_admin_sees_all_flows(self):
        """Test that admin users can see all flows."""
        headers = self.get_admin_auth_headers()

        response = self.client.get(f"{self.API_PREFIX}/flows", headers=headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Admin should see all flows (same as user in this case since all flows
        # are created by user)
        assert "flows" in data
        assert isinstance(data["flows"], list)
        assert len(data["flows"]) >= TEST_USER_FLOW_COUNT

    def test_get_flows_unauthenticated_returns_401(self):
        """Test that GET /api/v1/flows requires authentication."""
        response = self.client.get(f"{self.API_PREFIX}/flows")
        assert response.status_code == HTTPStatus.UNAUTHORIZED
