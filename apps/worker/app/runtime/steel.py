"""Steel.dev browser automation adapter."""

import logging
from typing import Any
from uuid import UUID

from app.services.steel_service import SteelService

logger = logging.getLogger(__name__)


class SteelBrowserAdapter:
    """Adapter for Steel.dev browser automation."""

    def __init__(self, steel_service: SteelService | None = None):
        self.steel_service = steel_service or SteelService()
        self.sessions: dict[UUID, dict[str, Any]] = {}

    async def create_session(self, run_id: UUID) -> str:
        """Create a new browser session and return the session URL."""
        session_data = await self.steel_service.create_session()

        if not session_data:
            msg = f"Failed to create Steel session for run {run_id}"
            raise RuntimeError(msg)

        session_id = session_data.get("id")
        session_url = session_data.get("debugUrl") or session_data.get(
            "sessionViewerUrl"
        )

        if not session_url:
            msg = f"Steel session created but missing URL for run {run_id}"
            raise RuntimeError(msg)

        # Store session mapping
        self.sessions[run_id] = {
            "session_id": session_id,
            "session_url": session_url,
            "websocket_url": session_data.get("websocketUrl"),
            "status": session_data.get("status", "active"),
            "created_at": session_data.get("createdAt"),
        }

        logger.info("Created browser session for run %s: %s", run_id, session_url)
        return session_url

    async def execute_action(
        self, run_id: UUID, action_type: str, action_params: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a browser action."""
        session = self.sessions.get(run_id)
        if not session:
            msg = f"No active session for run {run_id}"
            raise ValueError(msg)

        try:
            # TODO: Implement actual Steel.dev action execution
            # This would require additional Steel API endpoints for actions
            # For now, return a placeholder result

            result = {
                "action": action_type,
                "params": action_params,
                "status": "completed",
                "timestamp": None,  # Would be set by Steel API
            }

        except Exception:
            logger.exception(
                "Failed to execute action %s for run %s", action_type, run_id
            )
            raise
        else:
            logger.info("Executed action %s for run %s", action_type, run_id)
            return result

    async def take_screenshot(self, run_id: UUID, name: str) -> str:
        """Take a screenshot and return the artifact reference."""
        session = self.sessions.get(run_id)
        if not session:
            msg = f"No active session for run {run_id}"
            raise ValueError(msg)

        try:
            # TODO: Implement actual Steel.dev screenshot capture
            # This would require Steel API screenshot endpoint
            # For now, return a placeholder reference

            screenshot_ref = f"screenshot_{name}_{run_id}"

        except Exception:
            logger.exception("Failed to take screenshot for run %s", run_id)
            raise
        else:
            logger.info("Took screenshot '%s' for run %s", name, run_id)
            return screenshot_ref

    async def close_session(self, run_id: UUID) -> None:
        """Close a browser session."""
        session = self.sessions.get(run_id)
        if not session:
            logger.warning("No session found for run %s", run_id)
            return

        session_id = session.get("session_id")
        if session_id:
            success = await self.steel_service.release_session(session_id)
            if not success:
                logger.warning("Failed to release Steel session %s", session_id)
                return

        self.sessions.pop(run_id, None)
        logger.info("Closed browser session for run %s", run_id)

    def get_session_status(self, run_id: UUID) -> dict[str, Any] | None:
        """Get the status of a browser session."""
        return self.sessions.get(run_id)

    def get_session_info(self, run_id: UUID) -> dict[str, Any] | None:
        """Return the stored session mapping for a run, if available."""
        return self.sessions.get(run_id)
