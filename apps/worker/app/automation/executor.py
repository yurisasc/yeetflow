"""Action executor that maps first-principles actions to a BrowserAgent."""

from __future__ import annotations

import logging
from typing import Any

from app.runtime.context import RunContext
from app.runtime.events import EventEmitter

from .agents.base import BrowserAgent

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes action steps against a BrowserAgent and emits events."""

    def __init__(self, agent: BrowserAgent, events: EventEmitter):
        self.agent = agent
        self.events = events

    async def execute_action(self, context: RunContext, step: dict[str, Any]) -> None:
        action = dict(step.get("action", {}))
        action_type = (action.get("type") or "").lower()

        # Common aliases
        if action_type == "navigate":
            action_type = "open_url"

        try:
            await self._dispatch_action(context, action, action_type, step)
        except Exception:
            logger.exception("Failed to execute action: %s", action)
            raise

    async def _dispatch_action(
        self,
        context: RunContext,
        action: dict[str, Any],
        action_type: str,
        step: dict[str, Any],
    ) -> None:
        """Dispatch action to appropriate handler."""
        if action_type == "open_url":
            await self._execute_open_url(action)
        elif action_type == "click":
            await self._execute_click(action)
        elif action_type == "type":
            await self._execute_type(action)
        elif action_type == "wait_for":
            await self._execute_wait_for(action)
        elif action_type == "extract":
            await self._execute_extract(context, action)
        elif action_type == "screenshot":
            await self._execute_screenshot(context, action, step)
        elif action_type == "log":
            await self._execute_log(context, action)
        else:
            self._raise_unknown_action_type(action_type)

    async def _execute_open_url(self, action: dict[str, Any]) -> None:
        url = self._require(action, "url")
        await self.agent.open_url(url)

    async def _execute_click(self, action: dict[str, Any]) -> None:
        selector = self._require(action, "selector")
        await self.agent.click(selector)

    async def _execute_type(self, action: dict[str, Any]) -> None:
        selector = self._require(action, "selector")
        text = self._require(action, "text")
        clear = bool(action.get("clear", False))
        await self.agent.type(selector, text, clear=clear)

    async def _execute_wait_for(self, action: dict[str, Any]) -> None:
        selector = self._require(action, "selector")
        timeout_ms = int(action.get("timeout_ms", 10000))
        await self.agent.wait_for(selector, timeout_ms=timeout_ms)

    async def _execute_extract(
        self, context: RunContext, action: dict[str, Any]
    ) -> None:
        selector = self._require(action, "selector")
        attr = action.get("attr")
        var = action.get("var")
        value = await self.agent.extract(selector, attr=attr)
        if var:
            context.set_variable(var, value)

    async def _execute_screenshot(
        self, context: RunContext, action: dict[str, Any], step: dict[str, Any]
    ) -> None:
        name = action.get("name") or step.get("name") or "screenshot"
        ref = await self.agent.screenshot(name)
        await self.events.emit_screenshot_taken(context, name, ref)

    async def _execute_log(self, context: RunContext, action: dict[str, Any]) -> None:
        message = self._require(action, "message")
        level = action.get("level", "info")
        await self.events.emit_log(context, message, level)

    def _raise_unknown_action_type(self, action_type: str) -> None:
        """Raise ValueError for unknown action types."""
        msg = "Unknown action type: %s" % (action_type or "<empty>")
        raise ValueError(msg)

    @staticmethod
    def _require(d: dict[str, Any], key: str) -> Any:
        if key not in d or d[key] in (None, ""):
            msg = f"Missing required action param: {key}"
            raise ValueError(msg)
        return d[key]
