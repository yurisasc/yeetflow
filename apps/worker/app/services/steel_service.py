import logging
from http import HTTPStatus

import httpx

from app.config import settings
from app.utils.retry import retry_network_operation, should_retry_http_response

logger = logging.getLogger(__name__)


class SteelService:
    """Service for managing Steel.dev browser sessions."""

    def __init__(self):
        self.api_key = settings.steel_api_key
        self.dev_mode = not bool(self.api_key)
        self.base_url = "https://api.steel.dev/v1"
        if self.dev_mode:
            logger.warning("Running in development mode - using mock Steel sessions")

    @retry_network_operation()
    async def create_session(self) -> dict | None:
        """Create a new Steel.dev browser session with retry logic."""
        if self.dev_mode:
            # Development mode: return mock session data
            return {
                "id": "dev-session-123",
                "sessionViewerUrl": "https://dev.steel.dev/session/dev-session-123",
                "websocketUrl": "wss://dev.steel.dev/session/dev-session-123/ws",
                "debugUrl": "https://dev.steel.dev/debug/dev-session-123",
                "createdAt": "2025-09-18T11:00:00.000Z",
                "status": "live",
            }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/sessions",
                headers={
                    "steel-api-key": self.api_key,
                    "Content-Type": "application/json",
                },
                json={
                    "dimensions": {"width": 1280, "height": 720},
                    "timeout": 30000,
                },
            )

            if should_retry_http_response(response):
                response.raise_for_status()

            if response.status_code != HTTPStatus.CREATED:
                logger.error(
                    "Failed to create Steel session: %s - %s",
                    response.status_code,
                    response.text,
                )
                return None

            session_data = response.json()
            session_url = session_data.get("debugUrl")
            if not session_url:
                logger.error("Steel session created but missing 'debugUrl'")
                return None
            logger.info(
                "Successfully created Steel session: %s",
                session_data.get("id"),
            )
            return session_data

    @retry_network_operation()
    async def release_session(self, session_id: str) -> bool:
        """Release a Steel.dev browser session with retry logic."""
        if self.dev_mode:
            # Development mode: always return success
            logger.info("Development mode: mock releasing session %s", session_id)
            return True

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/sessions/{session_id}/release",
                headers={"steel-api-key": self.api_key},
            )

            if not should_retry_http_response(response):
                response.raise_for_status()

            success = response.status_code in (HTTPStatus.OK, HTTPStatus.NO_CONTENT)
            if success:
                logger.info("Successfully released Steel session: %s", session_id)
            else:
                logger.warning(
                    "Failed to release Steel session %s: %s",
                    session_id,
                    response.status_code,
                )
            return success
