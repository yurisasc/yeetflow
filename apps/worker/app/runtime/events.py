"""Event system for flow execution and monitoring."""

import logging
from collections.abc import Callable
from contextlib import AbstractAsyncContextManager
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Event, EventType
from app.runtime.context import RunContext
from app.services.event.service import EventService

logger = logging.getLogger(__name__)


def _redact(obj):
    sensitive = [
        "api_key",
        "apikey",
        "password",
        "secret",
        "token",
        "authorization",
        "cookie",
        "set-cookie",
    ]
    if isinstance(obj, dict):
        return {
            k: ("***" if k.lower() in sensitive else _redact(v)) for k, v in obj.items()
        }
    if isinstance(obj, list):
        return [_redact(v) for v in obj]
    return obj


class EventEmitter:
    """Emits events during flow execution."""

    def __init__(
        self,
        event_service: EventService | None = None,
        session_getter: (
            Callable[[], AbstractAsyncContextManager[AsyncSession]] | None
        ) = None,
    ):
        self.event_service = event_service
        self.session_getter = session_getter

    async def emit_run_started(self, context: RunContext) -> None:
        """Emit run started event."""
        await self._emit_event(
            context.run_id, EventType.STATUS, "run_started", {"status": "running"}
        )

    async def emit_run_completed(self, context: RunContext) -> None:
        """Emit run completed event."""
        await self._emit_event(
            context.run_id,
            EventType.STATUS,
            "run_completed",
            {"status": "completed"},
        )

    async def emit_run_failed(self, context: RunContext, error: str) -> None:
        """Emit run failed event."""
        await self._emit_event(
            context.run_id,
            EventType.ERROR,
            "run_failed",
            {"status": "failed", "error": error},
        )

    async def emit_step_started(self, context: RunContext, step_name: str) -> None:
        """Emit step started event."""
        await self._emit_event(
            context.run_id,
            EventType.STEP_START,
            f"step_started: {step_name}",
            {"step": step_name, "index": context.current_step, "status": "running"},
        )

    async def emit_step_completed(self, context: RunContext, step_name: str) -> None:
        """Emit step completed event."""
        await self._emit_event(
            context.run_id,
            EventType.STEP_END,
            f"step_completed: {step_name}",
            {"step": step_name, "index": context.current_step, "status": "completed"},
        )

    async def emit_step_failed(
        self, context: RunContext, step_name: str, error: str
    ) -> None:
        """Emit step failed event."""
        await self._emit_event(
            context.run_id,
            EventType.ERROR,
            f"step_failed: {step_name}",
            {
                "step": step_name,
                "index": context.current_step,
                "status": "failed",
                "error": error,
            },
        )

    async def emit_checkpoint_reached(
        self,
        context: RunContext,
        checkpoint_id: str,
        reason: str,
        expected_action: str,
        expires_at: datetime,
    ) -> None:
        """Emit checkpoint reached event with full checkpoint data."""
        # Create checkpoint payload matching data model
        checkpoint_payload = {
            "id": checkpoint_id,
            "reason": reason,
            "expected_action": expected_action,
            "expires_at": expires_at.astimezone(
                timezone.utc  # noqa: UP017
            ).isoformat(),
            "status": "awaiting_input",
        }

        await self._emit_event(
            context.run_id,
            EventType.CHECKPOINT,
            f"checkpoint_reached: {checkpoint_id}",
            {"checkpoint": checkpoint_payload},
        )

    async def emit_prompt_required(
        self,
        context: RunContext,
        prompt_id: str,
        prompt_message: str,
        response_options: list[str] | None = None,
    ) -> None:
        """Emit prompt required event for human input."""
        prompt_payload = {
            "id": prompt_id,
            "message": prompt_message,
            "response_options": response_options or [],
            "status": "awaiting_input",
        }

        await self._emit_event(
            context.run_id,
            EventType.PROMPT,
            f"prompt_required: {prompt_id}",
            {"prompt": prompt_payload},
        )

    async def emit_log(
        self, context: RunContext, message: str, level: str = "info"
    ) -> None:
        """Emit a log event."""
        await self._emit_event(
            context.run_id,
            EventType.LOG,
            message,
            {"level": level},
        )

    async def emit_artifact_created(
        self, context: RunContext, artifact_name: str, artifact_type: str
    ) -> None:
        """Emit artifact created event."""
        await self._emit_event(
            context.run_id,
            EventType.ARTIFACT,
            f"artifact_created: {artifact_name}",
            {"artifact": artifact_name, "type": artifact_type},
        )

    async def emit_screenshot_taken(
        self, context: RunContext, screenshot_id: str, reference_id: str
    ) -> None:
        """Emit screenshot taken event."""
        await self._emit_event(
            context.run_id,
            EventType.SCREENSHOT,
            f"screenshot_taken: {screenshot_id}",
            {"screenshot": screenshot_id, "reference_id": reference_id},
        )

    async def _emit_event(
        self, run_id: UUID, event_type: EventType, message: str, payload: dict[str, Any]
    ) -> Event | None:
        """Emit an event through the event service."""
        # Redact sensitive data before emitting
        safe_message = _redact(message)
        safe_payload = _redact(payload)

        try:
            if self.event_service and self.session_getter:
                async with self.session_getter() as session:
                    return await self.event_service.create_event(
                        run_id=run_id,
                        event_type=event_type,
                        message=safe_message,
                        payload=safe_payload,
                        session=session,
                    )
            else:
                # Log to console if no event service or session getter available
                logger.info(
                    "Event [%s]: %s - %s", event_type.value, safe_message, safe_payload
                )

        except Exception:
            logger.exception("Failed to emit event")
        return None
