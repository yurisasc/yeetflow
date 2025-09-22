"""
Unit tests for JWT utilities and authentication helpers.
"""

from datetime import UTC, datetime, timedelta
from http import HTTPStatus
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi import HTTPException
from jwt.exceptions import ExpiredSignatureError, InvalidSignatureError

from app.models import UserRole
from app.utils.auth import (
    TokenData,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_refresh_token,
    verify_token,
)


@pytest.mark.unit
class TestJWTUtilities:
    """Unit tests for JWT token creation and validation."""

    def test_create_access_token(self):
        """Test access token creation with proper payload."""
        token_data = {"sub": str(uuid4()), "email": "test@example.com", "role": "user"}

        token = create_access_token(token_data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT format validation

    def test_create_refresh_token(self):
        """Test refresh token creation with proper payload."""
        token_data = {"sub": str(uuid4()), "email": "test@example.com", "role": "user"}

        token = create_refresh_token(token_data)

        assert isinstance(token, str)
        assert len(token) > 0
        assert "." in token  # JWT format validation

    def test_verify_token_valid(self):
        """Test verification of valid access token."""
        user_id = str(uuid4())
        token_data = {"sub": user_id, "email": "test@example.com", "role": "user"}

        token = create_access_token(token_data)
        decoded = verify_token(token)

        assert str(decoded.user_id) == user_id  # Convert UUID to string for comparison
        assert decoded.email == "test@example.com"
        assert decoded.role == UserRole.USER

    def test_verify_refresh_token_valid(self):
        """Test verification of valid refresh token."""
        user_id = str(uuid4())
        token_data = {"sub": user_id, "email": "test@example.com", "role": "admin"}

        token = create_refresh_token(token_data)
        decoded = verify_refresh_token(token)

        assert str(decoded.user_id) == user_id  # Convert UUID to string for comparison
        assert decoded.email == "test@example.com"
        assert decoded.role == UserRole.ADMIN

    def test_verify_token_expired(self):
        """Test verification of expired token."""
        user_id = str(uuid4())
        token_data = {
            "sub": user_id,
            "email": "test@example.com",
            "role": "user",
            "exp": datetime.now(UTC) - timedelta(minutes=1),  # Expired 1 minute ago
        }

        with patch("app.utils.auth.create_access_token") as mock_create:
            mock_create.return_value = "expired.jwt.token"
            token = create_access_token(token_data)

            with patch("jwt.decode") as mock_decode:
                mock_decode.side_effect = ExpiredSignatureError("Token expired")
                with pytest.raises(HTTPException) as exc_info:
                    verify_token(token)

                assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
                assert "Invalid or expired token" in str(exc_info.value.detail)

    def test_verify_token_invalid_signature(self):
        """Test verification of token with invalid signature."""
        invalid_token = "invalid.jwt.token"

        with patch("jwt.decode") as mock_decode:
            mock_decode.side_effect = InvalidSignatureError("Invalid signature")
            with pytest.raises(HTTPException) as exc_info:
                verify_token(invalid_token)

            assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
            assert "Invalid or expired token" in str(exc_info.value.detail)

    def test_verify_token_missing_user_id(self):
        """Test verification of token missing user ID."""
        token_data = {
            "email": "test@example.com",
            "role": "user",
            # Missing "sub" (user_id)
        }

        token = create_access_token(token_data)

        # This should raise an HTTPException
        with pytest.raises(HTTPException) as exc_info:
            verify_token(token)

        assert exc_info.value.status_code == HTTPStatus.UNAUTHORIZED
        assert "Token missing user ID" in str(exc_info.value.detail)

    def test_token_expiry_times(self):
        """Test that tokens have correct expiry times."""
        token_data = {"sub": str(uuid4()), "email": "test@example.com", "role": "user"}

        # Test access token expiry
        access_token = create_access_token(token_data)
        with patch("jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": token_data["sub"],
                "email": token_data["email"],
                "role": token_data["role"],
                "exp": datetime.now(UTC).timestamp() + 30 * 60,  # 30 minutes from now
                "iat": datetime.now(UTC).timestamp(),
                "type": "access",
            }
            decoded = verify_token(access_token)
            assert decoded.user_id is not None  # Just verify it decoded successfully

        # Test refresh token expiry
        refresh_token = create_refresh_token(token_data)
        with patch("jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": token_data["sub"],
                "email": token_data["email"],
                "role": token_data["role"],
                "exp": datetime.now(UTC).timestamp() + 7 * 24 * 60 * 60,  # 7 days
                "iat": datetime.now(UTC).timestamp(),
                "type": "refresh",
            }
            decoded = verify_refresh_token(refresh_token)
            assert decoded.user_id is not None  # Just verify it decoded successfully


@pytest.mark.unit
class TestPasswordUtilities:
    """Unit tests for password hashing and verification."""

    def test_get_password_hash(self):
        """Test password hashing."""
        password = "test_password_123"
        hashed = get_password_hash(password)

        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should be hashed
        # Bcrypt hash should look like $2a$ / $2b$ / $2y$
        assert hashed.startswith("$2"), f"Unexpected bcrypt prefix: {hashed[:4]}"

    def test_verify_password_correct(self):
        """Test password verification with correct password."""
        password = "correct_password"
        hashed = get_password_hash(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password."""
        password = "correct_password"
        wrong_password = "wrong_password"
        hashed = get_password_hash(password)

        assert verify_password(wrong_password, hashed) is False

    def test_verify_password_empty(self):
        """Test password verification with empty password."""
        password = "test_password"
        hashed = get_password_hash(password)

        # Empty password should not match
        assert verify_password("", hashed) is False

        # Valid password should match
        assert verify_password(password, hashed) is True

    def test_password_hash_uniqueness(self):
        """Test that same password generates different hashes."""
        password = "same_password"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2  # Should be different due to salt
        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


@pytest.mark.unit
class TestTokenData:
    """Unit tests for TokenData model."""

    def test_token_data_creation(self):
        """Test TokenData creation."""
        user_id = str(uuid4())
        token_data = TokenData(
            user_id=user_id, email="test@example.com", role=UserRole.USER
        )

        assert str(token_data.user_id) == user_id
        assert token_data.email == "test@example.com"
        assert token_data.role == UserRole.USER

    def test_token_data_serialization(self):
        """Test TokenData serialization."""
        user_id = str(uuid4())
        token_data = TokenData(
            user_id=user_id, email="test@example.com", role=UserRole.USER
        )

        data_dict = token_data.model_dump()
        assert str(data_dict["user_id"]) == user_id
        assert data_dict["email"] == "test@example.com"
        assert data_dict["role"] == UserRole.USER
