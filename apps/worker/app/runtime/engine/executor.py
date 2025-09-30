"""Action executor that maps first-principles actions to a BrowserAgent."""

from __future__ import annotations

import logging
from typing import Any

from app.runtime.actions import registry as action_registry
from app.runtime.actions.base import ActionExecution
from app.runtime.core import ActionStep, Agent, RunContext

from .events import EventEmitter
from .middleware import (
    ErrorScreenshotMiddleware,
    EventMiddleware,
    LoggingMiddleware,
    MiddlewareChain,
    StepExecution,
    StepExecutionResult,
)

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes action steps against a BrowserAgent and emits events."""

    def __init__(self, agent: Agent, events: EventEmitter):
        self.agent = agent
        self.events = events
        self._mw = MiddlewareChain()
        self._mw.add(EventMiddleware())
        self._mw.add(LoggingMiddleware())
        self._mw.add(ErrorScreenshotMiddleware())

    async def execute_action(
        self, context: RunContext, step: ActionStep, step_name: str
    ) -> None:
        """Execute an action step."""
        try:
            params = dict(step.action or {})
            action_type = (params.get("type") or "").lower()
            await self._execute_with_middleware(context, action_type, params, step_name)
        except Exception:
            logger.exception("Failed to execute action step: %s", step)
            raise

    async def _execute_via_registry(self, execution: ActionExecution) -> None:
        action_cmd = action_registry.create(execution.action_type, execution.params)
        await action_cmd.execute(execution)

    async def _execute_with_middleware(
        self,
        context: RunContext,
        action_type: str,
        params: dict[str, Any],
        step_name: str,
    ) -> None:
        error: Exception | None = None
        execution = StepExecution(
            context=context,
            action_type=action_type,
            params=params,
            agent=self.agent,
            events=self.events,
            step_name=step_name,
        )
        await self._mw.run_before(execution)
        try:
            action_exec = ActionExecution(**vars(execution))
            await self._execute_via_registry(action_exec)
        except Exception as exc:
            error = exc
            raise
        finally:
            await self._mw.run_after(
                StepExecutionResult(**vars(execution), error=error)
            )
