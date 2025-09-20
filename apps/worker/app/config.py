"""
Centralized configuration management for the YeetFlow worker application.
All environment variables are loaded and validated here.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Default configuration values
DEFAULT_DATABASE_URL = "sqlite:///yeetflow.db"
DEFAULT_HOST = "0.0.0.0"  # noqa: S104
DEFAULT_PORT = 8000
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_SECRET_KEY = "dev-secret-key-change-in-production"  # noqa: S105
DEFAULT_RETRY_MAX_ATTEMPTS = 3
DEFAULT_RETRY_BASE_DELAY = 1.0
DEFAULT_RETRY_MAX_DELAY = 30.0
DEFAULT_API_TOKEN = ""
DEFAULT_ARTIFACTS_DIR = "./artifacts"
DEFAULT_SOCKETIO_CORS = "*"


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

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    def model_post_init(self, _) -> None:
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
