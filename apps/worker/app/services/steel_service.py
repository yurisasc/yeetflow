import httpx
import os
from typing import Optional
import logging

from ..utils.retry import retry_network_operation

logger = logging.getLogger(__name__)


class SteelService:
    """Service for managing Steel.dev browser sessions."""

    def __init__(self):
        self.api_key = os.getenv("STEEL_API_KEY")
        if not self.api_key:
            raise ValueError("Missing required STEEL_API_KEY environment variable")
        self.base_url = "https://api.steel.dev/v1"

    @retry_network_operation(max_attempts=5, base_delay=1.0, max_delay=30.0)
    async def create_session(self) -> Optional[dict]:
        """Create a new Steel.dev browser session with retry logic."""
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

            if response.status_code == 201:
                session_data = response.json()
                logger.info(f"Successfully created Steel session: {session_data.get('id')}")
                return session_data
            else:
                logger.error(
                    f"Failed to create Steel session: {response.status_code} - {response.text}"
                )
                return None

    @retry_network_operation(max_attempts=3, base_delay=0.5, max_delay=10.0)
    async def release_session(self, session_id: str) -> bool:
        """Release a Steel.dev browser session with retry logic."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/sessions/{session_id}/release",
                headers={"steel-api-key": self.api_key},
            )

            success = response.status_code == 200
            if success:
                logger.info(f"Successfully released Steel session: {session_id}")
            else:
                logger.warning(
                    f"Failed to release Steel session {session_id}: {response.status_code}"
                )
            return success
