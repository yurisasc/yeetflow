"""Steel.dev browser automation adapter implementing SessionProvider port."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.runtime.core import SessionProvider
from app.services.run.repository import RunRepository
from app.services.steel_service import SteelService

logger = logging.getLogger(__name__)


class SteelBrowserAdapter(SessionProvider):
    """Adapter for Steel.dev browser automation."""

    def __init__(self, db: AsyncSession, steel_service: SteelService):
        """Dependencies:

        - db: direct DB session for queries
        - steel_service: API client for Steel.dev
        """
        self.db = db
        self.steel_service = steel_service
        self.sessions: dict[UUID, dict[str, Any]] = {}

    async def attach_to_session(self, run_id: UUID) -> None:
        """Attach to an existing Steel session persisted in the DB for this run.

        Looks up the active Session row for the run and caches essential info in
        `self.sessions[run_id]`. This avoids creating duplicate sessions and keeps
        the runtime attach-only per the plan.
        """
        # If already attached, nothing to do
        if run_id in self.sessions:
            return
        try:
            repo = RunRepository()
            sessions = await repo.get_sessions(self.db, run_id)
            active = next((s for s in sessions if s.ended_at is None), None)
        except Exception:
            logger.exception("Failed to attach to session for run %s", run_id)
            raise

        if not active:
            msg = f"No persisted browser session found for run {run_id}"
            raise RuntimeError(msg)

        # Seed mapping from DB
        mapping: dict[str, Any] = {
            "session_id": active.browser_provider_session_id,
            "session_url": active.session_url,
            "websocket_url": None,
            "status": (
                active.status.value
                if hasattr(active.status, "value")
                else str(active.status)
            ),
            "created_at": (
                active.created_at.isoformat() if active.created_at else None
            ),
        }

        # Try to enrich with provider info (websocketUrl/connectUrl)
        provider_id = active.browser_provider_session_id
        if provider_id:
            try:
                info = await self.steel_service.get_session_info(provider_id)
            except Exception:  # network failures shouldn't break attach
                logger.exception(
                    "Failed to fetch Steel session info for %s", provider_id
                )
                info = None
            if isinstance(info, dict):
                ws = (
                    info.get("websocketUrl")
                    or info.get("connectUrl")
                    or info.get("wsUrl")
                )
                if ws:
                    mapping["websocket_url"] = ws

        self.sessions[run_id] = mapping
        logger.info("Attached to existing browser session for run %s", run_id)

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
