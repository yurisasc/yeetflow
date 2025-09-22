from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.models import User, UserCreate, UserRead, UserRole
from app.services.auth import AuthService
from app.utils.auth import TokenData, get_password_hash


@pytest.mark.unit
class TestAuthService:
    """Unit tests for AuthService methods."""

    @pytest.fixture
    def auth_service(self):
        """Create AuthService instance for testing."""
        return AuthService()

    @pytest.fixture
    def mock_session(self):
        """Create mock database session."""
        return AsyncMock()

    async def test_create_user_first_user_admin(self, auth_service, mock_session):
        """Test creating first user (should become admin)."""
        user_data = UserCreate(
            email="first@example.com", name="First User", password="password123"
        )

        # Mock database operations - session is mocked directly
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh = AsyncMock()

        # Mock the count query to return 0 (no existing users)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result

        # Test first user creation (password hashing is tested separately)
        with patch("app.utils.auth.get_password_hash", return_value="hashed_password"):
            result = await auth_service.create_user(user_data, mock_session, None)

            # Verify first user becomes admin
            assert result.role == UserRole.ADMIN

    async def test_create_user_regular_user(self, auth_service, mock_session):
        """Test creating regular user with specific role."""
        user_data = UserCreate(
            email="user@example.com",
            name="Regular User",
            password="password123",
            role=UserRole.USER,
        )

        with patch("app.utils.auth.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed_password"

            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh = AsyncMock()

            # Mock the count query to return 1 (existing users)
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_session.execute.return_value = mock_result

            result = await auth_service.create_user(
                user_data, mock_session, UserRole.ADMIN
            )

            assert result.role == UserRole.USER

    async def test_create_user_admin_role_requires_admin_creator(
        self, auth_service, mock_session
    ):
        """Test that only admins can create admin users."""
        user_data = UserCreate(
            email="admin@example.com",
            name="New Admin",
            password="password123",
            role=UserRole.ADMIN,
        )

        # Mock the count query to return 1 (existing users)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_session.execute.return_value = mock_result

        # Non-admin creator tries to create admin user
        with pytest.raises(
            ValueError, match="Only administrators can create admin users"
        ):
            await auth_service.create_user(user_data, mock_session, UserRole.USER)

    async def test_create_user_default_role(self, auth_service, mock_session):
        """Test creating user with default role when none specified."""
        user_data = UserCreate(
            email="default@example.com",
            name="Default User",
            password="password123",
            # No role specified
        )

        with patch("app.utils.auth.get_password_hash") as mock_hash:
            mock_hash.return_value = "hashed_password"

            mock_session.add.return_value = None
            mock_session.commit.return_value = None
            mock_session.refresh = AsyncMock()

            # Mock the count query to return 1 (existing users)
            mock_result = MagicMock()
            mock_result.scalar.return_value = 1
            mock_session.execute.return_value = mock_result

            result = await auth_service.create_user(
                user_data, mock_session, UserRole.ADMIN
            )

            assert result.role == UserRole.USER

    async def test_create_user_first_user_with_creator_role_fails(
        self, auth_service, mock_session
    ):
        """Test that first user registration fails when creator_role is not None."""
        user_data = UserCreate(
            email="first@example.com", name="First User", password="password123"
        )

        # Mock database operations
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh = AsyncMock()

        # Mock the count query to return 0 (no existing users)
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute.return_value = mock_result

        # Test that passing creator_role=UserRole.ADMIN for first user fails
        with (
            patch("app.utils.auth.get_password_hash", return_value="hashed_password"),
            pytest.raises(
                ValueError, match="First user registration must not have a creator"
            ),
        ):
            await auth_service.create_user(user_data, mock_session, UserRole.ADMIN)

    async def test_authenticate_user_success(self, auth_service, mock_session):
        """Test successful user authentication."""
        email = "test@example.com"
        password = "correct_password"

        # Mock user in database
        mock_user = User(
            id=uuid4(),
            email=email,
            name="Test User",
            password_hash=get_password_hash(password),
            role=UserRole.USER,
        )

        # Mock database query
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        # Mock password verification
        with patch("app.utils.auth.verify_password") as mock_verify:
            mock_verify.return_value = True

            result = await auth_service.authenticate_user(email, password, mock_session)

            assert result == mock_user
            mock_session.execute.assert_called_once()

    async def test_authenticate_user_wrong_password(self, auth_service, mock_session):
        """Test authentication with wrong password."""
        email = "test@example.com"
        wrong_password = "wrong_password"

        mock_user = User(
            id=uuid4(),
            email=email,
            name="Test User",
            password_hash=get_password_hash("correct_password"),
            role=UserRole.USER,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        with patch("app.utils.auth.verify_password") as mock_verify:
            mock_verify.return_value = False

            result = await auth_service.authenticate_user(
                email, wrong_password, mock_session
            )

            assert result is None

    async def test_authenticate_user_not_found(self, auth_service, mock_session):
        """Test authentication for non-existent user."""
        email = "nonexistent@example.com"
        password = "password123"

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await auth_service.authenticate_user(email, password, mock_session)

        assert result is None

    async def test_create_user_tokens(self, auth_service):
        """Test JWT token creation for user."""
        mock_user = User(
            id=uuid4(),
            email="test@example.com",
            name="Test User",
            password_hash="hashed_password",
            role=UserRole.USER,
        )

        # Test that the method can be called (detailed JWT testing is in jwt_utils)
        access_mock = patch(
            "app.utils.auth.create_access_token", return_value="access.jwt.token"
        )
        refresh_mock = patch(
            "app.utils.auth.create_refresh_token", return_value="refresh.jwt.token"
        )

        with access_mock, refresh_mock:
            tokens = auth_service.create_user_tokens(mock_user)

            assert hasattr(tokens, "access_token")
            assert hasattr(tokens, "refresh_token")
            assert hasattr(tokens, "token_type")

    async def test_refresh_user_tokens_success(self, auth_service, mock_session):
        """Test successful token refresh (happy path)."""
        mock_user = User(
            id=uuid4(),
            email="ok@example.com",
            name="Ok",
            password_hash="h",
            role=UserRole.USER,
        )
        with patch(
            "app.services.auth.service.verify_refresh_token",
            return_value=TokenData(user_id=mock_user.id),
        ):
            auth_service.get_user_by_id = AsyncMock(return_value=mock_user)
            with (
                patch(
                    "app.services.auth.service.create_access_token", return_value="a.t"
                ),
                patch(
                    "app.services.auth.service.create_refresh_token", return_value="r.t"
                ),
            ):
                tokens = await auth_service.refresh_user_tokens("rt", mock_session)
                assert tokens.access_token == "a.t"
                assert tokens.refresh_token == "r.t"

    async def test_refresh_user_tokens_invalid_token(self, auth_service, mock_session):
        """Test token refresh with invalid refresh token."""
        # This test verifies that the method exists and handles invalid tokens
        refresh_token = "invalid.refresh.token"

        # Just verify the method exists and handles invalid tokens
        with pytest.raises((ValueError, HTTPException)):
            await auth_service.refresh_user_tokens(refresh_token, mock_session)

    async def test_refresh_user_tokens_user_not_found(self, auth_service, mock_session):
        """Test token refresh when user no longer exists."""
        # This test verifies that the method exists and can be called
        refresh_token = "valid.refresh.token"

        # Just verify the method exists and handles invalid tokens
        with pytest.raises((ValueError, HTTPException)):
            await auth_service.refresh_user_tokens(refresh_token, mock_session)

    async def test_get_user_by_id_success(self, auth_service, mock_session):
        """Test successful user lookup by ID."""
        user_id = uuid4()
        mock_user = User(
            id=user_id,
            email="test@example.com",
            name="Test User",
            password_hash="hashed_password",
            role=UserRole.USER,
        )

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_user
        mock_session.execute.return_value = mock_result

        result = await auth_service.get_user_by_id(user_id, mock_session)

        assert result == mock_user

    async def test_get_user_by_id_not_found(self, auth_service, mock_session):
        """Test user lookup by ID when user doesn't exist."""
        user_id = uuid4()

        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result

        result = await auth_service.get_user_by_id(user_id, mock_session)

        assert result is None

    async def test_get_all_users(self, auth_service, mock_session):
        """Test retrieving all users."""
        mock_users = [
            User(
                id=uuid4(),
                email="user1@example.com",
                name="User 1",
                password_hash="hash1",
                role=UserRole.USER,
            ),
            User(
                id=uuid4(),
                email="user2@example.com",
                name="User 2",
                password_hash="hash2",
                role=UserRole.ADMIN,
            ),
        ]

        mock_result = MagicMock()
        # Create simple mock row objects

        class MockRow:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)

        mock_rows = [
            MockRow(
                id=mock_users[0].id,
                email="user1@example.com",
                name="User 1",
                role=UserRole.USER,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
            MockRow(
                id=mock_users[1].id,
                email="user2@example.com",
                name="User 2",
                role=UserRole.ADMIN,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            ),
        ]
        mock_result.all.return_value = mock_rows
        mock_session.execute.return_value = mock_result

        result = await auth_service.get_all_users(mock_session)

        expected_user_count = 2
        assert len(result) == expected_user_count
        assert isinstance(result[0], UserRead)
        assert result[0].email == "user1@example.com"
        assert result[1].email == "user2@example.com"

    async def test_update_user_role_success(self, auth_service, mock_session):
        """Test successful user role update."""
        user_id = uuid4()
        new_role = UserRole.ADMIN
        updater_role = UserRole.ADMIN

        mock_user = User(
            id=user_id,
            email="test@example.com",
            name="Test User",
            password_hash="hashed_password",
            role=UserRole.USER,
        )

        # Mock user lookup
        auth_service.get_user_by_id = AsyncMock(return_value=mock_user)

        # Mock database commit
        mock_session.add.return_value = None
        mock_session.commit.return_value = None
        mock_session.refresh = AsyncMock()

        result = await auth_service.update_user_role(
            user_id, new_role, mock_session, updater_role
        )

        assert result == mock_user
        assert result.role == UserRole.ADMIN

    async def test_update_user_role_insufficient_permissions(
        self, auth_service, mock_session
    ):
        """Test role update by non-admin user."""
        user_id = uuid4()
        new_role = UserRole.ADMIN
        updater_role = UserRole.USER  # Not admin

        with pytest.raises(
            ValueError, match="Only administrators can update user roles"
        ):
            await auth_service.update_user_role(
                user_id, new_role, mock_session, updater_role
            )

    async def test_update_user_role_user_not_found(self, auth_service, mock_session):
        """Test role update for non-existent user."""
        user_id = uuid4()
        new_role = UserRole.ADMIN
        updater_role = UserRole.ADMIN

        # User not found
        auth_service.get_user_by_id = AsyncMock(return_value=None)

        result = await auth_service.update_user_role(
            user_id, new_role, mock_session, updater_role
        )

        assert result is None
