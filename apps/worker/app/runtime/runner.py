"""Flow runner for executing automation flows."""

import asyncio
import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from app.automation.agents.browser_use_agent import (
    create_browser_use_agent,
)
from app.automation.agents.noop import NoopAgent
from app.automation.executor import ActionExecutor
from app.db import get_session
from app.models import Run
from app.runtime.context import RunContext
from app.runtime.events import EventEmitter
from app.runtime.steel import SteelBrowserAdapter
from app.services.run.service import RunService

logger = logging.getLogger(__name__)


class FlowRunner:
    """Executes automation flows with human-in-the-loop support."""

    def __init__(
        self, run_service: RunService, steel_adapter: SteelBrowserAdapter | None = None
    ):
        self.run_service = run_service
        self.event_emitter = EventEmitter(session_getter=get_session)
        self.steel_adapter = steel_adapter or SteelBrowserAdapter()
        self._agent = None
        self._executor: ActionExecutor | None = None

    async def execute_flow(
        self, run: Run, flow_manifest: dict[str, Any], input_payload: dict[str, Any]
    ) -> None:
        """Execute a flow with the given inputs."""
        context = RunContext(
            run_id=run.id,
            flow_id=run.flow_id,
            user_id=run.user_id,
            input_payload=input_payload,
            manifest=flow_manifest,
        )

        try:
            # Initialize browser session via Steel.dev
            await self.steel_adapter.create_session(run.id)

            # Initialize browser agent (browser-use if available, fallback to noop)
            session_info = self.steel_adapter.get_session_info(run.id) or {}
            websocket_url = session_info.get("websocket_url")
            agent = create_browser_use_agent(websocket_url) or NoopAgent()
            await agent.start()
            self._agent = agent
            self._executor = ActionExecutor(agent, self.event_emitter)

            # Update run status to running
            await self.run_service.update_run_status(run.id, "running")

            # Emit start event
            await self.event_emitter.emit_run_started(context)

            # Execute the flow
            flow_completed = await self._execute_flow_steps(context)

            # Only mark as completed if all steps finished
            if flow_completed:
                # Update run status to completed
                await self.run_service.update_run_status(run.id, "completed")

                # Emit completion event
                await self.event_emitter.emit_run_completed(context)

        except Exception as e:
            logger.exception("Flow execution failed for run %s", run.id)

            # Update run status to failed
            await self.run_service.update_run_status(run.id, "failed", error=str(e))

            # Emit failure event
            await self.event_emitter.emit_run_failed(context, str(e))
        finally:
            # Cleanup agent and Steel session
            try:
                if self._agent:
                    try:
                        await asyncio.wait_for(self._agent.stop(), timeout=10.0)
                    except TimeoutError:
                        logger.warning("Agent stop timed out for run %s", run.id)
            finally:
                try:
                    await asyncio.wait_for(
                        self.steel_adapter.close_session(run.id), timeout=10.0
                    )
                except TimeoutError:
                    logger.warning("Session close timed out for run %s", run.id)

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
            await self.run_service.update_run_status(context.run_id, "awaiting_input")
            return False

        if step_type == "action":
            # Execute an action via executor
            await self._execute_action(context, step)

        # Simulate some execution time (placeholder)
        await asyncio.sleep(0.1)
        return True

    async def _execute_action(self, context: RunContext, step: dict[str, Any]) -> None:
        """Execute an action step via the ActionExecutor."""
        if not self._executor:
            logger.warning("ActionExecutor not initialized; skipping action")
            return
        await self._executor.execute_action(context, step)

    async def resume_flow(self, run_id: UUID, user_input: dict[str, Any]) -> None:
        """Resume a paused flow with user input."""
        # Update run status back to running
        await self.run_service.update_run_status(run_id, "running")

        # Continue execution (placeholder)
        logger.info("Resuming flow %s with user input: %s", run_id, user_input)

        # In a real implementation, this would continue from the checkpoint
