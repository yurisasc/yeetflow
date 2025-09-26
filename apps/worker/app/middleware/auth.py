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

        # Extract token from multiple sources (hybrid authentication)
        token = self._extract_token(request)

        if not token:
            # Check for specific error conditions
            if (
                hasattr(request.state, "invalid_auth_scheme")
                and request.state.invalid_auth_scheme
            ) or (
                hasattr(request.state, "malformed_auth_header")
                and request.state.malformed_auth_header
            ):
                return JSONResponse(
                    status_code=HTTPStatus.UNAUTHORIZED,
                    content={"detail": "Invalid authorization header format"},
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"detail": "Authentication credentials missing"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Validate token
        try:
            token_data = verify_token(token)

            # Add user information to request state
            request.state.user_id = token_data.user_id
            request.state.user_role = token_data.role

        except HTTPException as e:
            logger.debug("Token validation failed: %s", e)
            return JSONResponse(
                status_code=HTTPStatus.UNAUTHORIZED,
                content={"detail": "Invalid or expired token"},
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Continue with the request
        return await call_next(request)

    def _extract_token(self, request: Request) -> str | None:
        """Extract JWT token from multiple sources for hybrid authentication.

        Priority order:
        1. Authorization: Bearer <token> header (mobile clients)
        2. HttpOnly access_token cookie (web clients)
        """
        # First, try Authorization header (mobile clients)
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                scheme, token = auth_header.split(" ", 1)
                if scheme.lower() == "bearer":
                    return token.strip()
                # Invalid scheme - set flag for error message
                request.state.invalid_auth_scheme = True
            except ValueError:
                # Malformed header - set flag for error message
                request.state.malformed_auth_header = True
                return None
            else:
                return None

        # Second, try HttpOnly cookie (web clients)
        access_token_cookie = request.cookies.get("access_token")
        if access_token_cookie:
            return access_token_cookie

        # No valid token found
        return None


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
