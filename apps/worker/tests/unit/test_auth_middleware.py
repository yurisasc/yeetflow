from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse

from app.middleware.auth import AuthMiddleware
from app.models import UserRole


@pytest.mark.unit
class TestAuthMiddleware:
    """Unit tests for authentication middleware."""

    @pytest.fixture
    def middleware(self):
        """Create AuthMiddleware instance for testing."""
        return AuthMiddleware(None)

    @pytest.fixture
    def mock_request(self):
        """Create mock request object."""
        request = MagicMock(spec=Request)
        request.url = MagicMock()
        request.headers = MagicMock()
        request.state = MagicMock()
        return request

    @pytest.fixture
    def mock_call_next(self):
        """Create mock call_next function."""
        return AsyncMock(return_value=Response())

    async def test_excluded_paths_bypass_auth(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that excluded paths bypass authentication."""
        # Test login endpoint (excluded)
        mock_request.url.path = "/api/v1/auth/login"
        mock_request.headers.get.return_value = None

        await middleware.dispatch(mock_request, mock_call_next)

        # Should call next without authentication checks
        mock_call_next.assert_called_once_with(mock_request)
        # Should not check Authorization header
        mock_request.headers.get.assert_not_called()

    async def test_register_endpoint_excluded(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that register endpoint is excluded from auth."""
        mock_request.url.path = "/api/v1/auth/register"
        mock_request.headers.get.return_value = None

        await middleware.dispatch(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

    async def test_protected_endpoint_requires_auth_header(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that protected endpoints require Authorization header."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = None  # No Authorization header

        result = await middleware.dispatch(mock_request, mock_call_next)

        # Should not call next
        mock_call_next.assert_not_called()
        # Should return 401 response
        assert isinstance(result, JSONResponse)
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        assert "Authorization header missing" in result.body.decode()

    async def test_invalid_auth_header_format(
        self, middleware, mock_request, mock_call_next
    ):
        """Test handling of malformed Authorization header."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = "InvalidFormat"  # Missing Bearer

        result = await middleware.dispatch(mock_request, mock_call_next)

        mock_call_next.assert_not_called()
        assert isinstance(result, JSONResponse)
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        assert "Invalid authorization header format" in result.body.decode()

    async def test_invalid_scheme_in_auth_header(
        self, middleware, mock_request, mock_call_next
    ):
        """Test handling of invalid scheme in Authorization header."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = "Basic token123"  # Wrong scheme

        result = await middleware.dispatch(mock_request, mock_call_next)

        mock_call_next.assert_not_called()
        assert isinstance(result, JSONResponse)
        assert result.status_code == HTTPStatus.UNAUTHORIZED
        assert "Invalid authorization header format" in result.body.decode()

    async def test_valid_token_authenticates_user(
        self, middleware, mock_request, mock_call_next
    ):
        """Test successful authentication with valid token."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = "Bearer valid.jwt.token"

        # Mock token verification
        with patch("app.middleware.auth.verify_token") as mock_verify:
            mock_token_data = MagicMock()
            mock_token_data.user_id = "user-123"
            mock_token_data.role = UserRole.USER
            mock_verify.return_value = mock_token_data

            await middleware.dispatch(mock_request, mock_call_next)

            # Should call next
            mock_call_next.assert_called_once_with(mock_request)
            # Should set user context
            assert mock_request.state.user_id == "user-123"
            assert mock_request.state.user_role == UserRole.USER

    async def test_invalid_token_returns_401(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that invalid tokens return 401."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = "Bearer invalid.jwt.token"

        with patch("app.middleware.auth.verify_token") as mock_verify:
            mock_verify.side_effect = HTTPException(
                status_code=401, detail="Invalid token"
            )

            result = await middleware.dispatch(mock_request, mock_call_next)

            mock_call_next.assert_not_called()
            assert isinstance(result, JSONResponse)
            assert result.status_code == HTTPStatus.UNAUTHORIZED
            assert "Invalid or expired token" in result.body.decode()

    async def test_expired_token_returns_401(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that expired tokens return 401."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = "Bearer expired.jwt.token"

        with patch("app.middleware.auth.verify_token") as mock_verify:
            mock_verify.side_effect = HTTPException(
                status_code=401, detail="Token expired"
            )

            result = await middleware.dispatch(mock_request, mock_call_next)

            mock_call_next.assert_not_called()
            assert isinstance(result, JSONResponse)
            assert result.status_code == HTTPStatus.UNAUTHORIZED

    async def test_middleware_calls_next_with_valid_request(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that middleware passes through valid requests."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = "Bearer valid.jwt.token"

        with patch("app.middleware.auth.verify_token") as mock_verify:
            mock_token_data = MagicMock()
            mock_token_data.user_id = "user-123"
            mock_token_data.role = UserRole.ADMIN
            mock_verify.return_value = mock_token_data

            mock_response = Response(status_code=200)
            mock_call_next.return_value = mock_response

            result = await middleware.dispatch(mock_request, mock_call_next)

            assert result == mock_response
            assert mock_request.state.user_id == "user-123"
            assert mock_request.state.user_role == UserRole.ADMIN

    async def test_health_endpoint_excluded(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that health endpoint is excluded from auth."""
        mock_request.url.path = "/health"
        mock_request.headers.get.return_value = None

        await middleware.dispatch(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

    async def test_docs_endpoints_excluded(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that documentation endpoints are excluded from auth."""
        excluded_paths = ["/docs", "/redoc", "/openapi.json"]

        for path in excluded_paths:
            mock_request.url.path = path
            mock_request.headers.get.return_value = None

            await middleware.dispatch(mock_request, mock_call_next)

            # Each should call next without auth checks
            assert mock_call_next.call_count == excluded_paths.index(path) + 1

    async def test_refresh_endpoint_excluded(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that refresh endpoint is excluded from auth."""
        mock_request.url.path = "/api/v1/auth/refresh"
        mock_request.headers.get.return_value = None

        await middleware.dispatch(mock_request, mock_call_next)

        mock_call_next.assert_called_once_with(mock_request)

    async def test_nested_api_paths_handled_correctly(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that nested API paths are handled correctly."""
        # This should require auth (not excluded)
        mock_request.url.path = "/api/v1/runs/123/sessions"
        mock_request.headers.get.return_value = "Bearer valid.jwt.token"

        with patch("app.middleware.auth.verify_token") as mock_verify:
            mock_token_data = MagicMock()
            mock_token_data.user_id = "user-123"
            mock_token_data.role = UserRole.USER
            mock_verify.return_value = mock_token_data

            await middleware.dispatch(mock_request, mock_call_next)

            mock_call_next.assert_called_once_with(mock_request)
            assert mock_request.state.user_id == "user-123"

    async def test_middleware_preserves_request_state(
        self, middleware, mock_request, mock_call_next
    ):
        """Test that middleware preserves existing request state."""
        mock_request.url.path = "/api/v1/protected/endpoint"
        mock_request.headers.get.return_value = "Bearer valid.jwt.token"
        mock_request.state.existing_data = "preserved"

        with patch("app.middleware.auth.verify_token") as mock_verify:
            mock_token_data = MagicMock()
            mock_token_data.user_id = "user-123"
            mock_token_data.role = UserRole.USER
            mock_verify.return_value = mock_token_data

            await middleware.dispatch(mock_request, mock_call_next)

            # Should preserve existing state
            assert mock_request.state.existing_data == "preserved"
            # Should add auth state
            assert mock_request.state.user_id == "user-123"
            assert mock_request.state.user_role == UserRole.USER

    async def test_middleware_handles_multiple_requests(self, middleware):
        """Test that middleware can handle multiple requests sequentially."""
        # Test first request (excluded path)
        mock_request1 = MagicMock(spec=Request)
        mock_request1.url = MagicMock()
        mock_request1.url.path = "/api/v1/auth/login"
        mock_request1.headers = MagicMock()
        mock_request1.headers.get.return_value = None
        mock_request1.state = MagicMock()

        mock_call_next1 = AsyncMock(return_value=Response())

        result1 = await middleware.dispatch(mock_request1, mock_call_next1)
        assert result1.status_code == HTTPStatus.OK
        mock_call_next1.assert_called_once_with(mock_request1)

        # Test second request (protected path with valid token)
        mock_request2 = MagicMock(spec=Request)
        mock_request2.url = MagicMock()
        mock_request2.url.path = "/api/v1/protected/endpoint"
        mock_request2.headers = MagicMock()
        mock_request2.headers.get.return_value = "Bearer valid.jwt.token"
        mock_request2.state = MagicMock()

        mock_call_next2 = AsyncMock(return_value=Response())

        with patch("app.middleware.auth.verify_token") as mock_verify:
            mock_token_data = MagicMock()
            mock_token_data.user_id = "user-123"
            mock_token_data.role = UserRole.USER
            mock_verify.return_value = mock_token_data

            await middleware.dispatch(mock_request2, mock_call_next2)

            mock_call_next2.assert_called_once_with(mock_request2)
            assert mock_request2.state.user_id == "user-123"
            assert mock_request2.state.user_role == UserRole.USER
