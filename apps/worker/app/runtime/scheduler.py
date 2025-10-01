"""Runtime scheduling utilities for launching flow executions."""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Flow, Run
from app.runtime.adapters.steel import SteelBrowserAdapter
from app.runtime.core import RunnerCoordinator
from app.runtime.engine import EventEmitter
from app.runtime.engine.flow_engine import FlowEngine
from app.services.event.service import EventService
from app.services.run.service import RunService
from app.services.steel_service import SteelService

logger = logging.getLogger(__name__)


class RunScheduler:
    """Coordinates background execution of runs via FlowEngine."""

    def __init__(
        self,
        coordinator: RunnerCoordinator,
        session_factory: Callable[[], AsyncSession],
        run_service_factory: Callable[[], RunService] | None = None,
        steel_service_factory: Callable[[], SteelService] | None = None,
        event_service_factory: Callable[[], EventService] | None = None,
    ) -> None:
        self._coordinator = coordinator
        self._session_factory = session_factory
        self._run_service_factory = run_service_factory or RunService
        self._steel_service_factory = steel_service_factory or SteelService
        self._event_service_factory = event_service_factory or EventService

    async def schedule(
        self, run: Run, *, input_payload: dict[str, Any] | None = None
    ) -> None:
        """Start background execution for a run."""

        session = self._session_factory()
        try:
            flow = await session.get(Flow, run.flow_id)
            if flow is None:
                logger.warning(
                    "Skipping scheduling for run %s: flow %s not found",
                    run.id,
                    run.flow_id,
                )
                await session.close()
                return

            manifest_payload: dict[str, Any] = {
                "id": str(flow.id),
                "name": flow.name,
                "key": flow.key,
                "description": flow.description,
                "config": flow.config or {},
            }

            steel_adapter = SteelBrowserAdapter(session, self._steel_service_factory())
            event_emitter = EventEmitter(session, self._event_service_factory())
            flow_engine = FlowEngine(
                run_service=self._run_service_factory(),
                session_provider=steel_adapter,
                session=session,
                event_emitter=event_emitter,
                coordinator=self._coordinator,
            )

            await flow_engine.start(run, manifest_payload, input_payload or {})
            task = self._coordinator.get_task(run.id)
            if task is None:
                logger.warning(
                    "No coordinator task registered for run %s; closing session",
                    run.id,
                )
                await session.close()
                return

            def _close_session(t: asyncio.Task) -> None:
                loop = t.get_loop()
                loop.create_task(session.close())

            task.add_done_callback(_close_session)
        except Exception:
            logger.exception("Failed to schedule FlowEngine for run %s", run.id)
            await session.close()
            raise
