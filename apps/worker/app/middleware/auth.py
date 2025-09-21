import logging
from collections.abc import Callable
from http import HTTPStatus

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.auth import verify_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware for JWT token validation and user context injection."""

    def __init__(self, app: Callable, exclude_paths: list[str] | None = None):
        """Initialize the auth middleware.

        Args:
            app: The FastAPI application
            exclude_paths: List of paths to exclude from authentication
        """
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/auth/refresh",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and validate JWT tokens if needed."""
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Extract Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"detail": "Authorization header missing"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Extract token from "Bearer <token>" format
        def _validate_scheme():
            scheme, token = auth_header.split(" ", 1)
            if scheme.lower() != "bearer":
                error_msg = "Invalid scheme"
                raise ValueError(error_msg)
            return token

        try:
            token = _validate_scheme()
        except ValueError:
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"detail": "Invalid authorization header format"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate token
        try:
            token_data = verify_token(token)

            # Add user information to request state
            request.state.user_id = token_data.user_id
            request.state.user_role = token_data.role

        except HTTPException as e:
            logger.warning("Token validation failed: %s", e)
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Continue with the request
        return await call_next(request)


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS middleware for cross-origin requests."""

    def __init__(self, app: Callable):
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add CORS headers to responses."""
        if request.method == "OPTIONS":
            # Handle preflight requests
            response = Response()
        else:
            response = await call_next(request)

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, PATCH, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"
        response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours

        return response
