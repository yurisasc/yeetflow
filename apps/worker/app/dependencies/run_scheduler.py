"""Application-wide dependency injection for FastAPI."""

from collections.abc import Callable

from sqlalchemy.ext.asyncio import AsyncSession

from app.db import AsyncSessionLocal
from app.runtime.core import RunnerCoordinator
from app.runtime.scheduler import RunScheduler

# Global singleton coordinator for pause/resume orchestration
_coordinator = RunnerCoordinator()


def get_run_scheduler() -> RunScheduler:
    """Create a RunScheduler with the global coordinator and session factory."""
    session_factory: Callable[[], AsyncSession] = AsyncSessionLocal
    return RunScheduler(
        coordinator=_coordinator,
        session_factory=session_factory,
    )
