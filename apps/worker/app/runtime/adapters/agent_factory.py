"""Factory for creating Agents from a SessionProvider.

This decouples Runner from websocket/transport details.
"""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.runtime.agents import NoopAgent
from app.runtime.core import Agent, SessionProvider


class AgentFactory:
    @staticmethod
    async def create(session_provider: SessionProvider, run_id: UUID) -> Agent:
        """Create and start an Agent for a run.

        Currently returns a NoopAgent. In the future, use websocket_url or other
        transport hints from the session to instantiate a real browser agent.
        """
        session_info: dict[str, Any] = session_provider.get_session_info(run_id) or {}
        _websocket_url = session_info.get("websocket_url")

        # TODO: instantiate a real agent when websocket_url is provided
        agent: Agent = NoopAgent()
        await agent.start()
        return agent
