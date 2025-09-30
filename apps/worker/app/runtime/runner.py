"""Flow runner for executing automation flows."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Run
from app.runtime.agents import NoopAgent
from app.runtime.context import RunContext
from app.runtime.events import EventEmitter
from app.runtime.executor import ActionExecutor
from app.runtime.steel import SteelBrowserAdapter
from app.services.run.service import RunService


# Fallback symbol so tests can patch `app.runtime.runner.create_browser_use_agent`
def create_browser_use_agent(_ws_url: str | None):  # pragma: no cover - shim
    return None


logger = logging.getLogger(__name__)


class FlowRunner:
    """Executes automation flows with human-in-the-loop support.

    Dependencies:
    - run_service: business logic for run updates (injected)
    - steel_adapter: browser adapter
    - session: direct DB session for this flow execution
    - session_getter: callable db context (fallback when session not provided)
    - event_emitter: event emitter
    """

    def __init__(
        self,
        run_service: RunService,
        steel_adapter: SteelBrowserAdapter,
        session: AsyncSession,
        event_emitter: EventEmitter,
    ):
        self.run_service = run_service
        self.session = session
        self.event_emitter = event_emitter
        self.steel_adapter = steel_adapter
        self._agent = None
        self._executor: ActionExecutor | None = None

    async def execute_flow(
        self, run: Run, flow_manifest: dict[str, Any], input_payload: dict[str, Any]
    ) -> None:
        """Execute a flow with the given inputs."""
        context = self._setup_execution_context(run, flow_manifest, input_payload)
        flow_completed = False
        failed = False

        try:
            await self._setup_agent_and_executor(run.id)
            await self._update_run_status(run.id, "running")
            await self.event_emitter.emit_run_started(context)

            flow_completed = await self._execute_flow_steps(context)

            if flow_completed:
                await self._handle_flow_completion(run.id, context)

        except Exception as e:  # noqa: BLE001
            failed = True
            await self._handle_execution_error(run.id, context, e)
        finally:
            await self._cleanup_after_execution(
                run.id, failed=failed, flow_completed=flow_completed
            )

    def _setup_execution_context(
        self, run: Run, flow_manifest: dict[str, Any], input_payload: dict[str, Any]
    ) -> RunContext:
        """Create and return the execution context for the flow."""
        return RunContext(
            run_id=run.id,
            flow_id=run.flow_id,
            user_id=run.user_id,
            input_payload=input_payload,
            manifest=flow_manifest,
        )

    async def _setup_agent_and_executor(self, run_id: UUID) -> None:
        """Attach to session and initialize browser agent and executor."""
        await self.steel_adapter.attach_to_session(run_id)
        session_info = self.steel_adapter.get_session_info(run_id) or {}
        websocket_url = session_info.get("websocket_url")
        agent = create_browser_use_agent(websocket_url) or NoopAgent()
        await agent.start()
        self._agent = agent
        self._executor = ActionExecutor(agent, self.event_emitter)

    async def _update_run_status(self, run_id: UUID, status: str) -> None:
        """Update the run status in the database."""
        await self.run_service.update_run(run_id, {"status": status}, self.session)

    async def _handle_flow_completion(self, run_id: UUID, context: RunContext) -> None:
        """Handle successful flow completion."""
        await self._update_run_status(run_id, "completed")
        await self.event_emitter.emit_run_completed(context)

    async def _handle_execution_error(
        self, run_id: UUID, context: RunContext, error: Exception
    ) -> None:
        """Handle execution errors."""
        logger.exception("Flow execution failed for run %s", run_id)
        await self.run_service.update_run(
            run_id, {"status": "failed", "error": str(error)}, self.session
        )
        await self.event_emitter.emit_run_failed(context, str(error))

    async def _cleanup_after_execution(
        self, run_id: UUID, *, failed: bool, flow_completed: bool
    ) -> None:
        """Clean up resources after execution."""
        paused = not failed and not flow_completed
        if paused:
            logger.info(
                "Run %s paused; keeping agent and browser session open for resume",
                run_id,
            )
        else:
            try:
                if self._agent:
                    try:
                        await asyncio.wait_for(self._agent.stop(), timeout=10.0)
                    except TimeoutError:
                        logger.warning("Agent stop timed out for run %s", run_id)
            finally:
                try:
                    await asyncio.wait_for(
                        self.steel_adapter.close_session(run_id), timeout=10.0
                    )
                except TimeoutError:
                    logger.warning("Session close timed out for run %s", run_id)

    async def _execute_flow_steps(self, context: RunContext) -> bool:
        """Execute individual flow steps (placeholder implementation).

        Returns:
            bool: True if all steps completed, False if paused at checkpoint
        """
        # This is where the actual flow execution logic would go
        # For now, just emit some sample events

        manifest_data = context.manifest or {}
        steps = manifest_data.get("steps") or manifest_data.get("config", {}).get(
            "steps", []
        )

        for i, step in enumerate(steps):
            step_name = step.get("name", f"Step {i + 1}")

            context.current_step = i + 1  # 1-based indexing for traceability

            # Emit step start
            await self.event_emitter.emit_step_started(context, step_name)

            try:
                # Execute step
                should_continue = await self._execute_step(context, step)
                if not should_continue:
                    return False  # Paused at checkpoint

                # Emit step completion
                await self.event_emitter.emit_step_completed(context, step_name)

            except Exception as e:
                # Emit step failure
                await self.event_emitter.emit_step_failed(context, step_name, str(e))
                raise

        return True  # All steps completed

    async def _execute_step(self, context: RunContext, step: dict[str, Any]) -> bool:
        """Execute a single step using first-principles primitives."""
        step_type = (step.get("type") or "").lower()

        if step_type == "checkpoint":
            # Pause for human input
            checkpoint_id = step.get("id") or step.get("name") or "checkpoint"
            reason = step.get("reason") or "Awaiting human input"
            expected_action = step.get("expected_action") or "continue"
            timeout_seconds = int(step.get("timeout", 900))  # default 15m
            expires_at = datetime.now(UTC) + timedelta(seconds=timeout_seconds)

            await self.event_emitter.emit_checkpoint_reached(
                context, checkpoint_id, reason, expected_action, expires_at
            )
            if self.session is not None:
                await self.run_service.update_run(
                    context.run_id, {"status": "awaiting_input"}, self.session
                )
            else:
                async with self.session_getter() as db:
                    await self.run_service.update_run(
                        context.run_id, {"status": "awaiting_input"}, db
                    )
            return False

        if step_type == "action":
            # Execute an action via executor
            await self._execute_action(context, step)

        # Simulate some execution time (placeholder)
        await asyncio.sleep(0.1)
        return True

    async def _execute_action(self, context: RunContext, step: dict[str, Any]) -> None:
        """Execute an action step via the ActionExecutor."""
        await self._executor.execute_action(context, step)

    async def resume_flow(self, run_id: UUID, user_input: dict[str, Any]) -> None:
        """Resume a paused flow with user input."""
        # Update run status back to running
        await self.run_service.update_run(run_id, {"status": "running"}, self.session)

        # Continue execution (placeholder)
        logger.info("Resuming flow %s with user input: %s", run_id, user_input)

        # In a real implementation, this would continue from the checkpoint
