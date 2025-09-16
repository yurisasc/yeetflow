import httpx
import os
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class SteelService:
    """Service for managing Steel.dev browser sessions."""

    def __init__(self):
        self.api_key = os.getenv("STEEL_API_KEY")
        if not self.api_key:
            raise ValueError("STEEL_API_KEY environment variable is not set")
        self.base_url = "https://api.steel.dev/v1"

    async def create_session(self) -> Optional[dict]:
        """Create a new Steel.dev browser session."""
        try:
            async with httpx.AsyncClient() as client:
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

                if response.status_code == 201:
                    session_data = response.json()
                    return session_data
                else:
                    logger.error(
                        f"Failed to create Steel session: {response.status_code} - {response.text}"
                    )
                    return None

        except Exception as e:
            logger.error(f"Error creating Steel session: {e}")
            return None

    async def release_session(self, session_id: str) -> bool:
        """Release a Steel.dev browser session."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/sessions/{session_id}/release",
                    headers={"steel-api-key": self.api_key},
                )

                return response.status_code == 200

        except Exception as e:
            logger.error(f"Error closing Steel session: {e}")
            return False
