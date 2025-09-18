"""
Centralized configuration management for the YeetFlow worker application.
All environment variables are loaded and validated here.
"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database configuration
    database_url: str = Field(
        default="sqlite:///yeetflow.db",
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
        default="0.0.0.0",  # noqa: S104
        description="Host to bind the server to",
    )

    port: int = Field(
        default=8000,
        description="Port to bind the server to",
    )

    # Logging configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    # Security settings
    secret_key: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens and encryption",
    )

    # Retry configuration
    retry_max_attempts: int = Field(
        default=3,
        description="Maximum retry attempts for network operations",
    )

    retry_base_delay: float = Field(
        default=1.0,
        description="Base delay for exponential backoff in seconds",
    )

    retry_max_delay: float = Field(
        default=30.0,
        description="Maximum delay for exponential backoff in seconds",
    )

    # Additional configuration
    api_token: str = Field(
        default="",
        description="API token for authentication",
    )

    artifacts_dir: str = Field(
        default="./artifacts",
        description="Directory for storing artifacts",
    )

    # Socket.IO configuration
    socketio_cors: str = Field(
        default="*",
        description="CORS allowed origins for Socket.IO (comma-separated)",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Helper functions for specific configurations
def get_database_url() -> str:
    """Get the database URL, converting SQLite to async format if needed."""
    url = settings.database_url
    if url.startswith("sqlite:///"):
        return url.replace("sqlite:///", "sqlite+aiosqlite:///")
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
    return {
        "cors_allowed_origins": settings.socketio_cors.split(","),
        "cors_enabled": True,
    }
