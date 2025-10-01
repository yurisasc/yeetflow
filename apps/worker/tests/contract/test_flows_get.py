from http import HTTPStatus

from app.models import FlowVisibility
from tests.conftest import BaseTestClass

# Number of test flows created for test_user in conftest.py
TEST_USER_FLOW_COUNT = 6

# Total flows created (user flows + admin flows)
TOTAL_FLOW_COUNT = 8

# Constants for pagination testing
SMALL_PAGE_LIMIT = 2
MEDIUM_PAGE_LIMIT = 3


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
            assert "visibility" in flow

    def test_get_flows_admin_sees_all_flows(self):
        """Test that admin users can see all flows, including those owned by others."""
        # First, get user flows count
        user_headers = self.get_user_auth_headers()
        user_response = self.client.get(
            f"{self.API_PREFIX}/flows", headers=user_headers
        )
        assert user_response.status_code == HTTPStatus.OK
        user_data = user_response.json()
        user_flow_count = len(user_data["flows"])

        # Then get admin flows count
        admin_headers = self.get_admin_auth_headers()
        admin_response = self.client.get(
            f"{self.API_PREFIX}/flows", headers=admin_headers
        )
        assert admin_response.status_code == HTTPStatus.OK
        admin_data = admin_response.json()

        # Admin should see all flows (including admin-owned flow)
        assert "flows" in admin_data
        assert isinstance(admin_data["flows"], list)
        assert len(admin_data["flows"]) == TOTAL_FLOW_COUNT

        # Admin should see more flows than regular user
        assert len(admin_data["flows"]) > user_flow_count
        assert user_flow_count == TEST_USER_FLOW_COUNT

        # Verify admin can see the admin-only flow
        admin_flow_ids = {flow["id"] for flow in admin_data["flows"]}
        assert "550e8400-e29b-41d4-a716-446655440006" in admin_flow_ids

        # Verify user cannot see the admin-only flow
        user_flow_ids = {flow["id"] for flow in user_data["flows"]}
        assert "550e8400-e29b-41d4-a716-446655440006" not in user_flow_ids

    def test_get_flows_includes_public_flows_from_other_users(self):
        """Regular users should see public flows owned by other users."""

        public_flow_id = "550e8400-e29b-41d4-a716-446655440006"
        self.set_flow_visibility(public_flow_id, FlowVisibility.PUBLIC)

        headers = self.get_user_auth_headers()
        response = self.client.get(f"{self.API_PREFIX}/flows", headers=headers)
        assert response.status_code == HTTPStatus.OK

        data = response.json()
        flow_ids = {flow["id"] for flow in data["flows"]}
        assert public_flow_id in flow_ids

        public_flow = next(
            flow for flow in data["flows"] if flow["id"] == public_flow_id
        )
        assert public_flow["visibility"] == FlowVisibility.PUBLIC.value

    def test_get_flows_limit_parameter_works(self):
        """Test that limit parameter works correctly."""
        headers = self.get_user_auth_headers()

        response = self.client.get(
            f"{self.API_PREFIX}/flows?limit={SMALL_PAGE_LIMIT}", headers=headers
        )
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Should return exactly 2 flows
        assert "flows" in data
        assert isinstance(data["flows"], list)
        assert len(data["flows"]) == SMALL_PAGE_LIMIT

    def test_get_flows_pagination_skip_works(self):
        """Test that skip parameter works correctly for pagination."""
        headers = self.get_user_auth_headers()

        # Get first page (skip=0, limit=2)
        response1 = self.client.get(
            f"{self.API_PREFIX}/flows?skip=0&limit={SMALL_PAGE_LIMIT}", headers=headers
        )
        assert response1.status_code == HTTPStatus.OK
        data1 = response1.json()
        assert len(data1["flows"]) == SMALL_PAGE_LIMIT

        # Get second page (skip=2, limit=2)
        response2 = self.client.get(
            f"{self.API_PREFIX}/flows?skip={SMALL_PAGE_LIMIT}&limit={SMALL_PAGE_LIMIT}",
            headers=headers,
        )
        assert response2.status_code == HTTPStatus.OK
        data2 = response2.json()
        assert len(data2["flows"]) == SMALL_PAGE_LIMIT

        # Ensure no duplication between pages
        first_page_ids = {flow["id"] for flow in data1["flows"]}
        second_page_ids = {flow["id"] for flow in data2["flows"]}
        assert first_page_ids.isdisjoint(second_page_ids), (
            "Pages should not have overlapping flows"
        )

    def test_get_flows_pagination_stable_ordering(self):
        """Test that pagination preserves stable ordering across multiple requests."""
        headers = self.get_user_auth_headers()

        # Get all flows in two requests
        response1 = self.client.get(
            f"{self.API_PREFIX}/flows?skip=0&limit={MEDIUM_PAGE_LIMIT}", headers=headers
        )
        assert response1.status_code == HTTPStatus.OK
        data1 = response1.json()

        response2 = self.client.get(
            f"{self.API_PREFIX}/flows?skip={MEDIUM_PAGE_LIMIT}&limit={MEDIUM_PAGE_LIMIT}",
            headers=headers,
        )
        assert response2.status_code == HTTPStatus.OK
        data2 = response2.json()

        # Combine results and verify ordering is preserved
        all_flows = data1["flows"] + data2["flows"]
        assert len(all_flows) >= TEST_USER_FLOW_COUNT

        # Verify ordering by created_at (should be descending)
        for i in range(len(all_flows) - 1):
            assert all_flows[i]["created_at"] >= all_flows[i + 1]["created_at"], (
                f"Flows not in descending order by created_at at index {i}"
            )

    def test_get_flows_default_pagination_parameters(self):
        """Test that default pagination parameters work correctly."""
        headers = self.get_user_auth_headers()

        response = self.client.get(f"{self.API_PREFIX}/flows", headers=headers)
        assert response.status_code == HTTPStatus.OK
        data = response.json()

        # Default limit should return at least the user's visible flows
        assert "flows" in data
        assert isinstance(data["flows"], list)
        assert len(data["flows"]) >= TEST_USER_FLOW_COUNT

    def test_get_flows_requires_auth(self):
        """GET /flows without auth should return 401."""
        response = self.client.get(f"{self.API_PREFIX}/flows")
        assert response.status_code == HTTPStatus.UNAUTHORIZED

    def test_get_flows_invalid_pagination_params_return_422(self):
        """Invalid skip/limit should yield 422."""
        headers = self.get_user_auth_headers()

        invalid_queries = [
            "?skip=-1",
            "?limit=0",
            "?skip=-5&limit=2",
            "?skip=0&limit=-2",
            "?skip=abc",
            "?limit=xyz",
        ]

        for q in invalid_queries:
            resp = self.client.get(f"{self.API_PREFIX}/flows{q}", headers=headers)
            msg = f"Query {q} should be 422"
            assert resp.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, msg
