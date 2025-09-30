"""Executor middleware interfaces and defaults."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol

from app.runtime.core import Agent, RunContext

from .events import EventEmitter


@dataclass
class StepExecution:
    context: RunContext
    action_type: str
    params: dict[str, Any]
    agent: Agent
    events: EventEmitter
    step_name: str


@dataclass
class StepExecutionResult(StepExecution):
    error: Exception | None = None


class ExecutorMiddleware(Protocol):
    async def before_execute(
        self, execution: StepExecution
    ) -> None:  # pragma: no cover - interface only
        ...

    async def after_execute(
        self, execution: StepExecutionResult
    ) -> None:  # pragma: no cover - interface only
        ...


class MiddlewareChain:
    """A simple chain to call middlewares sequentially."""

    def __init__(self) -> None:
        self._middlewares: list[ExecutorMiddleware] = []

    def add(self, mw: ExecutorMiddleware) -> None:
        self._middlewares.append(mw)

    async def run_before(self, execution: StepExecution) -> None:
        for mw in self._middlewares:
            await mw.before_execute(execution)

    async def run_after(self, execution: StepExecutionResult) -> None:
        for mw in self._middlewares:
            await mw.after_execute(execution)


class EventMiddleware:
    """Emits step start/completion/failure events around action execution."""

    async def before_execute(self, execution: StepExecution) -> None:
        await execution.events.emit_step_started(execution.context, execution.step_name)

    async def after_execute(self, execution: StepExecutionResult) -> None:
        if execution.error is None:
            await execution.events.emit_step_completed(
                execution.context, execution.step_name
            )
        else:
            await execution.events.emit_step_failed(
                execution.context, execution.step_name, str(execution.error)
            )


class LoggingMiddleware:
    """Logs action start/end with status."""

    def __init__(self) -> None:
        self._log = logging.getLogger(__name__)

    async def before_execute(self, execution: StepExecution) -> None:
        self._log.info(
            "Action start: %s | Run: %s | Step: %s",
            execution.action_type,
            execution.context.run_id,
            execution.context.current_step,
        )

    async def after_execute(self, execution: StepExecutionResult) -> None:
        status = "error" if execution.error else "ok"
        self._log.info(
            "Action end: %s | status=%s | Run: %s | Step: %s",
            execution.action_type,
            status,
            execution.context.run_id,
            execution.context.current_step,
        )


class ErrorScreenshotMiddleware:
    """Takes a screenshot and emits an event if action errors."""

    async def before_execute(
        self, _execution: StepExecution
    ) -> None:  # pragma: no cover - no-op
        return

    async def after_execute(self, execution: StepExecutionResult) -> None:
        if execution.error is None:
            return
        try:
            name = f"error_step_{execution.context.current_step}"
            ref = await execution.agent.screenshot(name)
            await execution.events.emit_screenshot_taken(execution.context, name, ref)
        except Exception:  # pragma: no cover - best effort
            logging.getLogger(__name__).exception("ErrorScreenshotMiddleware failed")
