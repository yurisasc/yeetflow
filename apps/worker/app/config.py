"""
Centralized configuration management for the YeetFlow worker application.
All environment variables are loaded and validated here.
"""

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Default configuration values
DEFAULT_DATABASE_URL = "sqlite:///yeetflow.db"
DEFAULT_HOST = "0.0.0.0"  # noqa: S104
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_SECRET_KEY = "dev-secret-key-change-in-production"  # noqa: S105
DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS = 7
DEFAULT_RETRY_MAX_ATTEMPTS = 3
DEFAULT_RETRY_BASE_DELAY = 1.0
DEFAULT_RETRY_MAX_DELAY = 30.0
DEFAULT_API_TOKEN = ""
DEFAULT_ARTIFACTS_DIR = "./artifacts"
DEFAULT_SOCKETIO_CORS = "*"
DEFAULT_CORS_ALLOW_ORIGINS = "*"


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
        le=1440,  # <= 24h
        default=DEFAULT_ACCESS_TOKEN_EXPIRE_MINUTES,
        description="Access token expiration time in minutes",
    )

    refresh_token_expire_days: int = Field(
        ge=1,
        le=90,  # <= 90 days
        default=DEFAULT_REFRESH_TOKEN_EXPIRE_DAYS,
        description="Refresh token expiration time in days",
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

    @field_validator("cors_allow_origins")
    @classmethod
    def validate_cors_allow_origins(cls, v: str, info) -> str:
        """Validate CORS origins configuration."""
        # Get debug flag from the validation context
        debug = info.data.get("debug", False)

        # Allow wildcard only in debug mode
        if not debug and v.strip() == "*":
            msg = (
                "CORS wildcard '*' is not allowed in production. "
                "Please specify explicit origins (comma-separated) "
                "for CORS_ALLOW_ORIGINS."
            )
            raise ValueError(msg)

        # For comma-separated values, check if any is wildcard
        if not debug:
            origins = [origin.strip() for origin in v.split(",")]
            if "*" in origins:
                msg = (
                    "CORS wildcard '*' is not allowed in production. "
                    "Please specify explicit origins (comma-separated) "
                    "for CORS_ALLOW_ORIGINS."
                )
                raise ValueError(msg)

        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def model_post_init(self, _) -> None:
        if not self.secret_key or not self.secret_key.strip():
            msg = "SECRET_KEY must be set and non-empty"
            raise ValueError(msg)
        if not self.debug and self.secret_key == DEFAULT_SECRET_KEY:
            msg = "SECRET_KEY must be set in production"
            raise ValueError(msg)


# Global settings instance
settings = Settings()


# Helper functions for specific configurations
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
    origins = "*" if raw == "*" else [o.strip() for o in raw.split(",") if o.strip()]
    return {"cors_allowed_origins": origins, "cors_enabled": True}


def get_cors_config() -> dict:
    """Get CORS configuration for the API."""
    raw = settings.cors_allow_origins.strip()
    if raw == "*":
        return {
            "allow_origins": ["*"],
            "allow_methods": [
                "GET",
                "POST",
                "PUT",
                "DELETE",
                "PATCH",
                "OPTIONS",
                "HEAD",
            ],
            "allow_headers": [
                "Authorization",
                "Content-Type",
                "Accept",
                "Accept-Language",
            ],
            "expose_headers": ["WWW-Authenticate", "Authorization"],
            "max_age": 86400,
        }
    origins = [o.strip() for o in raw.split(",") if o.strip()]
    return {
        "allow_origins": origins,
        "allow_credentials": True,
        "allow_methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
        "allow_headers": [
            "Authorization",
            "Content-Type",
            "Accept",
            "Accept-Language",
        ],
        "expose_headers": ["WWW-Authenticate", "Authorization"],
        "max_age": 86400,
    }
