"""
Centralized configuration management for the YeetFlow worker application.
All environment variables are loaded and validated here.
"""

from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Default configuration values
DEFAULT_DATABASE_URL = "sqlite:///yeetflow.db"
DEFAULT_HOST = "0.0.0.0"  # noqa: S104
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_SECRET_KEY = "dev-secret-key-change-in-production"  # noqa: S105
DEFAULT_SECRET_KEY_MIN_LENGTH = 32
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7
DEFAULT_RETRY_MAX_ATTEMPTS = 3
DEFAULT_RETRY_BASE_DELAY = 1.0
DEFAULT_RETRY_MAX_DELAY = 30.0
DEFAULT_API_TOKEN = ""
DEFAULT_ARTIFACTS_DIR = "./artifacts"
DEFAULT_SOCKETIO_CORS = "*"
DEFAULT_CORS_ALLOW_ORIGINS = "*"
DEFAULT_FLOWS_DIR = Path(__file__).parent / "flows"

# CORS configuration constants
ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"]
ALLOWED_HEADERS = ["Authorization", "Content-Type", "Accept", "Accept-Language"]
EXPOSE_HEADERS = ["WWW-Authenticate", "Authorization"]
MINUTES_PER_DAY = 24 * 60


def normalize_origins(raw: str) -> str | list[str]:
    """Normalize CORS origins from comma-separated string.
    - Returns "*" if any wildcard is present.
    - Else returns a sorted, de-duplicated list of normalized origins (scheme://host[:port]).
    - Rejects entries with paths, queries, or fragments.
    """
    cleaned: list[str] = []
    for o in raw.split(","):
        s = o.strip().rstrip("/")
        if not s:
            continue
        if s == "*":
            return "*"
        parts = urlsplit(s)
        if (
            parts.scheme not in {"http", "https"}
            or not parts.netloc
            or any([parts.path, parts.query, parts.fragment])
        ):
            msg = f"Invalid CORS origin: {s!r}"
            raise ValueError(msg)
        scheme = parts.scheme.lower()
        netloc = parts.netloc.lower()
        cleaned.append(f"{scheme}://{netloc}")
    return sorted(set(cleaned))


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    database_url: str = Field(
        default=DEFAULT_DATABASE_URL,
        description="Database URL (SQLite for MVP)",
    )

    # Steel.dev API configuration
    steel_api_key: str | None = Field(
        default=None,
        description="Steel.dev API key for browser automation",
    )

    # Application settings
    debug: bool = Field(
        default=False,
        description="Enable debug mode for development",
    )

    host: str = Field(
        default=DEFAULT_HOST,
        description="Host to bind the server to",
    )

    port: int = Field(
        default=DEFAULT_PORT,
        description="Port to bind the server to",
    )

    # Logging configuration
    log_level: str = Field(
        default=DEFAULT_LOG_LEVEL,
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Security settings
    secret_key: str = Field(
        default=DEFAULT_SECRET_KEY,
        description="Secret key for JWT tokens and encryption",
    )

    access_token_expire_minutes: int = Field(
        ge=1,
        le=120,  # <= 2h
        default=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        description="Access token expiration time in minutes",
    )

    refresh_token_expire_days: int = Field(
        ge=1,
        le=30,  # <= 30 days
        default=DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        description="Refresh token expiration time in days",
    )

    # Cookie configuration for web authentication
    cookie_secure: bool = Field(
        default=True,
        description="Set secure flag on cookies (HTTPS only in production)",
    )

    cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax",
        description="SameSite attribute for cookies ('lax' | 'strict' | 'none')",
    )

    # Retry configuration
    retry_max_attempts: int = Field(
        default=DEFAULT_RETRY_MAX_ATTEMPTS,
        description="Maximum retry attempts for network operations",
    )

    retry_base_delay: float = Field(
        default=DEFAULT_RETRY_BASE_DELAY,
        description="Base delay for exponential backoff in seconds",
    )

    retry_max_delay: float = Field(
        default=DEFAULT_RETRY_MAX_DELAY,
        description="Maximum delay for exponential backoff in seconds",
    )

    # Additional configuration
    api_token: str = Field(
        default=DEFAULT_API_TOKEN,
        description="API token for authentication",
    )

    artifacts_dir: str = Field(
        default=DEFAULT_ARTIFACTS_DIR,
        description="Directory for storing artifacts",
    )

    flows_dir: Path = Field(
        default=DEFAULT_FLOWS_DIR,
        description="Directory containing flow manifests",
    )

    # Storage configuration
    storage_backend: str = Field(
        default="local",
        description="Storage backend type (local, s3, gcs, etc.)",
    )

    # S3-compatible storage settings
    s3_endpoint_url: str | None = Field(
        default=None,
        description="S3-compatible endpoint URL",
    )
    s3_access_key: str | None = Field(
        default=None,
        description="S3 access key",
    )
    s3_secret_key: str | None = Field(
        default=None,
        description="S3 secret key",
    )
    s3_bucket: str | None = Field(
        default=None,
        description="S3 bucket name",
    )
    s3_region: str | None = Field(
        default=None,
        description="S3 region",
    )

    # Socket.IO configuration
    socketio_cors: str = Field(
        default=DEFAULT_SOCKETIO_CORS,
        description="CORS allowed origins for Socket.IO (comma-separated)",
    )

    # CORS configuration
    cors_allow_origins: str = Field(
        default=DEFAULT_CORS_ALLOW_ORIGINS,
        description=(
            "CORS allowed origins for API (comma-separated). "
            "Use '*' for development, explicit origins for production."
        ),
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_security(self) -> "Settings":
        self._validate_secret_key()
        self._validate_cors_settings()
        self._validate_token_expiry()
        self._validate_cookie_settings()
        return self

    def _validate_secret_key(self) -> None:
        """Validate secret key configuration."""
        if not self.secret_key or not self.secret_key.strip():
            msg = "SECRET_KEY must be set and non-empty"
            raise ValueError(msg)
        if not self.debug and len(self.secret_key) < DEFAULT_SECRET_KEY_MIN_LENGTH:
            msg = "SECRET_KEY must be at least 32 characters in production"
            raise ValueError(msg)
        if not self.debug and self.secret_key == DEFAULT_SECRET_KEY:
            msg = "SECRET_KEY must be set in production; set DEBUG=true for local dev"
            raise ValueError(msg)

    def _validate_cors_settings(self) -> None:
        """Validate CORS configuration."""
        cors_norm = normalize_origins(self.cors_allow_origins.strip())
        sio_norm = normalize_origins(self.socketio_cors.strip())

        if not self.debug and cors_norm == "*":
            msg = (
                "CORS_ALLOW_ORIGINS cannot contain '*' in production; "
                "set explicit origins"
            )
            raise ValueError(msg)
        if not self.debug and sio_norm == "*":
            msg = "SOCKETIO_CORS cannot contain '*' in production; set explicit origins"
            raise ValueError(msg)

        # Guard against commas-only/whitespace resulting in an empty list
        if not self.debug and isinstance(cors_norm, list) and len(cors_norm) == 0:
            msg = "CORS_ALLOW_ORIGINS cannot be empty (or commas-only) in production"
            raise ValueError(msg)
        if not self.debug and isinstance(sio_norm, list) and len(sio_norm) == 0:
            msg = "SOCKETIO_CORS cannot be empty (or commas-only) in production"
            raise ValueError(msg)

    def _validate_token_expiry(self) -> None:
        """Validate token expiry configuration."""
        refresh_minutes = self.refresh_token_expire_days * MINUTES_PER_DAY
        if refresh_minutes <= self.access_token_expire_minutes:
            msg = (
                f"REFRESH_TOKEN_EXPIRE_DAYS must be strictly greater than "
                f"ACCESS_TOKEN_EXPIRE_MINUTES/{MINUTES_PER_DAY} "
                f"(got {self.refresh_token_expire_days}d = {refresh_minutes}m vs "
                f"{self.access_token_expire_minutes}m)"
            )
            raise ValueError(msg)

    def _validate_cookie_settings(self) -> None:
        """Validate cookie configuration."""
        # Validate cookie SameSite value
        samesite = (self.cookie_samesite or "lax").lower()
        if samesite not in {"lax", "strict", "none"}:
            msg = "COOKIE_SAMESITE must be one of: lax, strict, none"
            raise ValueError(msg)

        # Enforce secure when SameSite=None (required by browsers)
        if not self.debug and samesite == "none" and not self.cookie_secure:
            msg = "COOKIE_SECURE must be true when COOKIE_SAMESITE=none in production"
            raise ValueError(msg)


# Global settings instance
settings = Settings()


def get_database_url() -> str:
    """Get the database URL, converting SQLite to async format if needed."""
    url = settings.database_url
    if url.startswith("sqlite:") and not url.startswith("sqlite+aiosqlite:"):
        return "sqlite+aiosqlite:" + url[len("sqlite:") :]
    return url


def is_development_mode() -> bool:
    """Check if we're running in development mode."""
    return settings.debug or not settings.steel_api_key


def get_steel_config() -> dict:
    """Get Steel.dev configuration."""
    return {
        "api_key": settings.steel_api_key,
        "base_url": "https://api.steel.dev/v1",
        "enabled": bool(settings.steel_api_key),
    }


def get_retry_config() -> dict:
    """Get retry configuration for network operations."""
    return {
        "max_attempts": settings.retry_max_attempts,
        "base_delay": settings.retry_base_delay,
        "max_delay": settings.retry_max_delay,
    }


def get_socketio_config() -> dict:
    """Get Socket.IO configuration."""
    raw = settings.socketio_cors.strip()
    origins = normalize_origins(raw)
    return {"cors_allowed_origins": origins, "cors_enabled": True}


def get_cors_config() -> dict:
    """Get CORS configuration for the API."""
    raw = settings.cors_allow_origins.strip()
    origins = normalize_origins(raw)

    base_config = {
        "allow_methods": ALLOWED_METHODS,
        "allow_headers": ALLOWED_HEADERS,
        "expose_headers": EXPOSE_HEADERS,
        "max_age": 86400,
    }

    if origins == "*":
        return base_config | {
            "allow_origins": ["*"],
            "allow_credentials": False,
        }

    return base_config | {
        "allow_origins": origins,
        "allow_credentials": True,
    }
