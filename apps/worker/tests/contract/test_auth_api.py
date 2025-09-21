import asyncio

from fastapi import status
from sqlmodel import delete

from app.models import User
from tests.conftest import BaseTestClass


class TestAuthAPI(BaseTestClass):
    """Test authentication API endpoints."""

    def test_register_first_user_becomes_admin(self):
        """Test that the first user can register without auth and becomes admin."""
        # Ensure empty DB to exercise bootstrap behavior
        self._clear_all_users()
        user_data = {
            "email": "firstadmin@example.com",
            "name": "First Admin",
            "password": "securepassword123",
        }
        response = self.client.post("/api/v1/auth/register", json=user_data)

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["role"] == "admin"
        assert "id" in data

    def test_register_user_requires_admin_after_first(self):
        """Test that subsequent user registration requires admin privileges."""
        user_data = {
            "email": "newuser2@example.com",
            "name": "New User 2",
            "password": "securepassword123",
            "role": "admin",  # Trying to create admin user
        }

        # Register with regular user auth (should fail with 403, not 400)
        headers = self.get_user_auth_headers()
        response = self.client.post(
            "/api/v1/auth/register", json=user_data, headers=headers
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]

    def test_register_user_unauthorized_after_first_user(self):
        """Test that registration without auth fails after first user exists."""
        user_data = {
            "email": "unauth@example.com",
            "name": "Unauthorized User",
            "password": "password123",
        }

        # Since users already exist in test setup, this should require admin auth
        response = self.client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Authorization header missing" in response.json()["detail"]

    def test_register_user_success_with_admin(self):
        """Test successful user registration with admin authentication."""
        user_data = {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "securepassword123",
            "role": "user",
        }

        # Register with admin auth
        headers = self.get_admin_auth_headers()
        response = self.client.post(
            "/api/v1/auth/register", json=user_data, headers=headers
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == user_data["email"]
        assert data["name"] == user_data["name"]
        assert data["role"] == user_data["role"]
        assert "id" in data

    def test_first_user_registration_empty_database(self):
        """Test first user registration in an empty database scenario."""
        # Ensure the database has no users
        self._clear_all_users()
        user_data = {
            "email": "firstadmin@example.com",
            "name": "First Admin",
            "password": "securepassword123",
        }

        response = self.client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["role"] == "admin"

    def _clear_all_users(self):
        """Helper method to clear all users for first user testing."""

        # Use the test's session to clear users
        async def clear_users():
            async with self.TestAsyncSessionLocal() as session:
                await session.execute(delete(User))
                await session.commit()

        # Run the async function
        asyncio.run(clear_users())

    def test_login_success(self):
        """Test successful user login."""
        login_data = {"username": "user@example.com", "password": "userpass"}

        response = self.client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_200_OK

        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        login_data = {"username": "user@example.com", "password": "wrongpassword"}

        response = self.client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Incorrect email or password" in response.json()["detail"]

    def test_get_current_user(self):
        """Test getting current user information."""
        headers = self.get_user_auth_headers()
        response = self.client.get("/api/v1/auth/me", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "user@example.com"
        assert data["name"] == "Test User"
        assert data["role"] == "user"

    def test_get_current_user_unauthorized(self):
        """Test getting current user without authentication."""
        response = self.client.get("/api/v1/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_users_admin_only(self):
        """Test that only admins can list users."""
        # Admin can list users
        headers = self.get_admin_auth_headers()
        response = self.client.get("/api/v1/auth/users", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        expected_users_count = 2  # At least test_user and test_admin
        assert len(data) >= expected_users_count

    def test_list_users_regular_user_denied(self):
        """Test that regular users cannot list users."""
        headers = self.get_user_auth_headers()
        response = self.client.get("/api/v1/auth/users", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not enough permissions" in response.json()["detail"]

    def test_update_user_role_admin_only(self):
        """Test that only admins can update user roles."""
        # Admin can update role - send new_role as query parameter
        headers = self.get_admin_auth_headers()
        user_id = "550e8400-e29b-41d4-a716-446655440000"  # test_user id
        response = self.client.patch(
            f"/api/v1/auth/users/{user_id}/role?new_role=admin", headers=headers
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "admin"

    def test_update_user_role_regular_user_denied(self):
        """Test that regular users cannot update roles."""
        headers = self.get_user_auth_headers()
        user_id = "550e8400-e29b-41d4-a716-446655440001"  # test_admin id
        response = self.client.patch(
            f"/api/v1/auth/users/{user_id}/role?new_role=admin", headers=headers
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_update_user_role_invalid_user(self):
        """Test updating role for non-existent user."""
        headers = self.get_admin_auth_headers()
        response = self.client.patch(
            "/api/v1/auth/users/00000000-0000-0000-0000-000000000000/role?new_role=admin",
            headers=headers,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_refresh_token_success(self):
        """Test successful token refresh."""
        # First login to get tokens
        login_data = {
            "username": "user@example.com",  # OAuth2 uses 'username' not 'email'
            "password": "userpass",
        }

        login_response = self.client.post("/api/v1/auth/login", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK

        tokens = login_response.json()

        # Now refresh the tokens
        refresh_data = {"refresh_token": tokens["refresh_token"]}

        refresh_response = self.client.post("/api/v1/auth/refresh", json=refresh_data)

        assert refresh_response.status_code == status.HTTP_200_OK

        new_tokens = refresh_response.json()
        assert "access_token" in new_tokens
        assert "refresh_token" in new_tokens
        assert new_tokens["token_type"] == "bearer"

        # Verify new tokens are different from old ones
        assert new_tokens["access_token"] != tokens["access_token"], (
            "Access tokens should be different"
        )
        assert new_tokens["refresh_token"] != tokens["refresh_token"], (
            "Refresh tokens should be different"
        )

        # Verify new access token works
        headers = {"Authorization": f"Bearer {new_tokens['access_token']}"}
        me_response = self.client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == status.HTTP_200_OK

    def test_refresh_token_invalid(self):
        """Test refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid_refresh_token"}
        response = self.client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid refresh token" in response.json()["detail"]

    def test_refresh_token_missing(self):
        """Test refresh without token."""
        response = self.client.post("/api/v1/auth/refresh", json={})
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_refresh_token_wrong_type(self):
        """Test refresh with access token instead of refresh token."""
        # Get an access token
        login_data = {"username": "user@example.com", "password": "userpass"}
        login_response = self.client.post("/api/v1/auth/login", data=login_data)
        tokens = login_response.json()

        # Try to refresh with access token
        refresh_data = {"refresh_token": tokens["access_token"]}
        response = self.client.post("/api/v1/auth/refresh", json=refresh_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid token type" in response.json()["detail"]
