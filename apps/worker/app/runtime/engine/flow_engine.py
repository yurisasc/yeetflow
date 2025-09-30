"""FlowEngine: declarative orchestrator for flow runs.

This class owns the flow lifecycle and coordinates:
- session attach/close via SessionProvider
- agent create/start/stop via AgentFactory
- run status updates via RunService and RunStateMachine
- step execution via ActionExecutor + Middleware
- checkpoint pause/resume via RunnerCoordinator and context mementos

Controllers should depend on this engine instead of runner.py.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Run, RunStatus
from app.runtime.adapters import AgentFactory
from app.runtime.core import (
    ActionStep,
    Agent,
    CheckpointStep,
    RunContext,
    RunnerCoordinator,
    RunStateMachine,
    SessionProvider,
    merge_inputs,
    parse_manifest_steps,
    restore_context,
    snapshot_context,
)
from app.runtime.engine import ActionExecutor, EventEmitter
from app.services.run.service import RunService

logger = logging.getLogger(__name__)


class FlowEngine:
    def __init__(
        self,
        run_service: RunService,
        session_provider: SessionProvider,
        session: AsyncSession,
        event_emitter: EventEmitter,
        coordinator: RunnerCoordinator | None = None,
    ) -> None:
        self.run_service = run_service
        self.session = session
        self.event_emitter = event_emitter
        self.session_provider = session_provider
        self._coordinator = coordinator or RunnerCoordinator()

        self._agents: dict[UUID, Agent] = {}
        self._executors: dict[UUID, ActionExecutor] = {}
        self._fsms: dict[UUID, RunStateMachine] = {}

    async def start(
        self, run: Run, manifest: dict[str, Any], input_payload: dict[str, Any]
    ) -> None:
        """Start a flow. Launches a background task via the coordinator."""
        context = self._make_context(run, manifest, input_payload)
        await self._coordinator.start(run.id, self._run(context))

    async def resume(self, run_id: UUID, latest_input: dict[str, Any]) -> None:
        """Signal resume with latest input."""
        if not self._coordinator.has_task(run_id) or not self._coordinator.has_event(
            run_id
        ):
            msg = (
                "Run coordinator state missing; background task is not active for "
                "resume"
            )
            raise RuntimeError(msg)
        await self._update_run_status(run_id, RunStatus.RUNNING)
        self._coordinator.resume(run_id, latest_input)

    async def _run(self, context: RunContext) -> None:
        flow_completed = False
        failed = False
        try:
            self._init_fsm(context.run_id)
            await self._attach_session(context.run_id)
            await self._setup_agent_and_executor(context.run_id)
            await self._update_run_status(context.run_id, RunStatus.RUNNING)
            await self.event_emitter.emit_run_started(context)

            flow_completed = await self._execute_steps(context)
            if flow_completed:
                await self._handle_completion(context)
        except Exception as e:  # noqa: BLE001
            failed = True
            await self._handle_error(context, e)
        finally:
            await self._cleanup(
                context.run_id, failed=failed, flow_completed=flow_completed
            )

    def _make_context(
        self, run: Run, manifest: dict[str, Any], input_payload: dict[str, Any]
    ) -> RunContext:
        return RunContext(
            run_id=run.id,
            flow_id=run.flow_id,
            user_id=run.user_id,
            input_payload=input_payload,
            manifest=manifest,
        )

    async def _attach_session(self, run_id: UUID) -> None:
        await self.session_provider.attach_to_session(run_id)

    async def _setup_agent_and_executor(self, run_id: UUID) -> None:
        agent: Agent = await AgentFactory.create(self.session_provider, run_id)
        executor = ActionExecutor(agent, self.event_emitter)
        self._agents[run_id] = agent
        self._executors[run_id] = executor

    async def _execute_steps(self, context: RunContext) -> bool:
        steps = parse_manifest_steps(context.manifest or {})
        for i, step in enumerate(steps):
            step_name = (
                getattr(step, "name", None)
                or (
                    getattr(step, "id", None)
                    if isinstance(step, CheckpointStep)
                    else None
                )
                or f"Step {i + 1}"
            )
            context.current_step = i + 1
            should_continue = await self._execute_step(context, step, step_name)
            if not should_continue:
                return False
        return True

    async def _execute_step(
        self, context: RunContext, step: ActionStep | CheckpointStep, step_name: str
    ) -> bool:
        if isinstance(step, CheckpointStep):
            checkpoint_id = step.id or step.name or "checkpoint"
            reason = step.reason or "Awaiting human input"
            expected_action = step.expected_action or "continue"
            timeout_seconds = int(step.timeout or 900)
            expires_at = datetime.now(UTC) + timedelta(seconds=timeout_seconds)

            # Snapshot memento for deterministic resume
            context.add_checkpoint(checkpoint_id, {})
            memento = snapshot_context(context)
            context.add_checkpoint(checkpoint_id, memento)

            await self._update_run_status(context.run_id, RunStatus.AWAITING_INPUT)
            await self.event_emitter.emit_checkpoint_reached(
                context, checkpoint_id, reason, expected_action, expires_at
            )

            resumed = await self._coordinator.await_resume(
                context.run_id, timeout_s=timeout_seconds
            )
            if resumed:
                restore_context(context, memento)
                latest = self._coordinator.latest_input(context.run_id)
                context.input_payload = merge_inputs(context.input_payload, latest)
                await self._update_run_status(context.run_id, RunStatus.RUNNING)
                return True
            logger.info(
                "Run %s checkpoint %s timed out waiting for resume",
                context.run_id,
                checkpoint_id,
            )
            self._coordinator.cleanup(context.run_id)
            timeout_error = TimeoutError(
                f"Run {context.run_id} checkpoint {checkpoint_id} timed out"
            )
            raise timeout_error

        # Action step
        executor = self._executors.get(context.run_id)
        if executor is None:
            msg = f"No executor registered for run {context.run_id}"
            raise RuntimeError(msg)
        await executor.execute_action(context, step, step_name)
        return True

    async def _handle_completion(self, context: RunContext) -> None:
        await self._update_run_status(context.run_id, RunStatus.COMPLETED)
        await self.event_emitter.emit_run_completed(context)

    async def _handle_error(self, context: RunContext, error: Exception) -> None:
        logger.exception("Flow execution failed for run %s", context.run_id)
        error_message = (
            "Run execution timed out" if isinstance(error, TimeoutError) else str(error)
        )
        await self.run_service.update_run(
            context.run_id,
            {
                "status": RunStatus.FAILED,
                "error": error_message,
            },
            self.session,
        )
        try:
            await self.event_emitter.emit_run_failed(context, error_message)
        except Exception as emit_error:
            logger.exception(
                "Failed to emit run_failed event for run %s | original error: %s",
                context.run_id,
                error,
                exc_info=emit_error,
            )

    async def _cleanup(
        self, run_id: UUID, *, failed: bool, flow_completed: bool
    ) -> None:
        paused = not failed and not flow_completed
        if paused:
            logger.info(
                "Run %s paused; keeping agent and browser session open for resume",
                run_id,
            )
            return
        try:
            agent = self._agents.get(run_id)
            if agent is not None:
                stop_fn = getattr(agent, "stop", None)
                if stop_fn is not None:
                    try:
                        await asyncio.wait_for(stop_fn(), timeout=10.0)
                    except TimeoutError:
                        logger.warning("Agent stop timed out for run %s", run_id)
                    except Exception as agent_error:
                        logger.exception(
                            "Agent stop failed for run %s", run_id, exc_info=agent_error
                        )
                else:
                    logger.debug("Agent for run %s has no stop() method", run_id)
        finally:
            try:
                close_session = getattr(self.session_provider, "close_session", None)
                if close_session is not None:
                    await asyncio.wait_for(close_session(run_id), timeout=10.0)
            except TimeoutError:
                logger.warning("Session close timed out for run %s", run_id)
            except Exception as session_error:
                logger.exception(
                    "Session close failed for run %s", run_id, exc_info=session_error
                )
            finally:
                self._coordinator.cleanup(run_id)
                self._agents.pop(run_id, None)
                self._executors.pop(run_id, None)
                self._fsms.pop(run_id, None)

    async def _update_run_status(self, run_id: UUID, status: RunStatus) -> None:
        fsm = self._fsms.get(run_id)
        if fsm is not None:
            fsm.transition(status.value)
        await self.run_service.update_run(run_id, {"status": status}, self.session)

    def _init_fsm(self, run_id: UUID) -> None:
        self._fsms[run_id] = RunStateMachine("pending")
