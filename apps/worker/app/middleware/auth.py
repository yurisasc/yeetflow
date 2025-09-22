import logging
from collections.abc import Callable
from http import HTTPStatus

from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_cors_config
from app.constants import API_V1_PREFIX
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
            f"{API_V1_PREFIX}/auth/",
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
            return token.strip()

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
    """Secure CORS middleware with origin validation and credential support."""

    def __init__(self, app: Callable):
        super().__init__(app)
        # Get CORS configuration
        cors_config = get_cors_config()
        self.allow_origins = cors_config["allow_origins"]
        self.allow_credentials = cors_config.get("allow_credentials", False)
        self.allowed_methods = cors_config["allow_methods"]
        self.allowed_headers = cors_config["allow_headers"]
        self.expose_headers = cors_config.get("expose_headers", [])
        self.max_age = cors_config["max_age"]

        # Determine if we allow all origins
        self.allow_all_origins = self.allow_origins == ["*"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add secure CORS headers to responses with origin validation."""
        origin = request.headers.get("origin")

        # Validate origin if present
        if origin and not self._is_origin_allowed(origin):
            # If origin is not allowed, don't add CORS headers
            return await call_next(request)

        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)

        # Add CORS headers only if origin is allowed or allow_all_origins is True
        if self.allow_all_origins:
            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Credentials"] = "false"
        elif origin and self._is_origin_allowed(origin):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Vary"] = "Origin"

        # Add common CORS headers
        response.headers["Access-Control-Allow-Methods"] = ", ".join(
            self.allowed_methods
        )
        response.headers["Access-Control-Allow-Headers"] = ", ".join(
            self.allowed_headers
        )
        if self.expose_headers:
            response.headers["Access-Control-Expose-Headers"] = ", ".join(
                self.expose_headers
            )
        response.headers["Access-Control-Max-Age"] = str(self.max_age)

        return response

    def _is_origin_allowed(self, origin: str) -> bool:
        """Check if the origin is in the allowed list."""
        if self.allow_all_origins:
            return True
        return origin in self.allow_origins
