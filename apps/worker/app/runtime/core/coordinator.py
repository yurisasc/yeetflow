"""RunnerCoordinator for handling pause/resume orchestration."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable
from typing import Any
from uuid import UUID

logger = logging.getLogger(__name__)


class RunnerCoordinator:
    def __init__(self) -> None:
        self._events: dict[UUID, asyncio.Event] = {}
        self._latest_inputs: dict[UUID, dict[str, Any]] = {}
        self._tasks: dict[UUID, asyncio.Task] = {}

    def _get_event(self, run_id: UUID) -> asyncio.Event:
        evt = self._events.get(run_id)
        if not evt:
            evt = asyncio.Event()
            self._events[run_id] = evt
        return evt

    def set_task(self, run_id: UUID, task: asyncio.Task) -> None:
        self._tasks[run_id] = task

    async def start(self, run_id: UUID, coro: Awaitable[None]) -> None:
        """Start a background task for a run."""
        task = asyncio.create_task(coro)
        self.set_task(run_id, task)
        task.add_done_callback(lambda t: self._handle_task_completion(run_id, t))

    async def await_resume(self, run_id: UUID, timeout_s: int = 900) -> bool:
        """Wait for resume signal or timeout.

        Returns True if resumed, False if timeout.
        """
        evt = self._get_event(run_id)
        try:
            await asyncio.wait_for(evt.wait(), timeout=timeout_s)
            evt.clear()
        except TimeoutError:
            return False
        return True

    def resume(self, run_id: UUID, input_payload: dict[str, Any] | None = None) -> None:
        """Signal resume for a run and store latest input payload."""
        if input_payload is not None:
            self._latest_inputs[run_id] = input_payload
        self._get_event(run_id).set()

    def latest_input(self, run_id: UUID) -> dict[str, Any] | None:
        return self._latest_inputs.get(run_id)

    def has_task(self, run_id: UUID) -> bool:
        return run_id in self._tasks

    def has_event(self, run_id: UUID) -> bool:
        return run_id in self._events

    def cleanup(self, run_id: UUID) -> None:
        """Remove stored state for a finished run."""
        self._events.pop(run_id, None)
        self._latest_inputs.pop(run_id, None)
        task = self._tasks.pop(run_id, None)
        if task is not None and not task.done():
            current = asyncio.current_task()
            if task is not current:
                task.cancel()

    def _handle_task_completion(self, run_id: UUID, task: asyncio.Task) -> None:
        if task.cancelled():
            logger.info("Run %s task cancelled", run_id)
            return
        exc = task.exception()
        if exc is not None:
            logger.exception("Run %s task failed", run_id, exc_info=exc)
