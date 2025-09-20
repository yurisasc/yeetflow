import logging
from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Run, RunCreate, RunStatus
from app.models import Session as SessionModel
from app.services.run.errors import (
    MissingSessionURLError,
    RunNotFoundError,
    SessionCreationFailedError,
)
from app.services.run.repository import RunRepository
from app.services.steel_service import SteelService
from app.sockets import emit_progress

logger = logging.getLogger(__name__)


class RunService:
    """Service for managing run lifecycle and business logic."""

    def __init__(
        self,
        steel_service: SteelService | None = None,
        repository: RunRepository | None = None,
    ):
        self.steel_service = steel_service or SteelService()
        self.repository = repository or RunRepository()

    async def create_run(self, request: RunCreate, session: AsyncSession) -> Run:
        """Create a new run with Steel.dev session integration."""
        run_id = uuid4()

        try:
            # Create initial run record
            run = await self._create_run_record(request, run_id, session)

            # Create Steel session
            session_data = await self.steel_service.create_session()

            if not session_data:
                await self._handle_session_creation_failure(
                    run_id, session, "Failed to create browser session"
                )
                self._fail_session_creation()

            session_url = session_data.get("sessionViewerUrl")
            browser_session_id = session_data.get("id")

            if not session_url:
                await self._handle_session_creation_failure(
                    run_id, session, "Session created without viewer URL"
                )
                self._fail_missing_url()

            # Create session record and finalize run
            run = await self._create_session_and_finalize_run(
                run_id, session_url, browser_session_id, session
            )

            # Emit final progress event
            await self._emit_progress_safe(
                run_id,
                {
                    "status": RunStatus.RUNNING.value,
                    "session_url": session_url,
                    "message": "Session initialized",
                },
            )

        except Exception:
            # Handle any other errors
            logger.exception("Error creating run")
            await session.rollback()
            raise
        else:
            return run

    async def get_run(self, run_id: UUID, session: AsyncSession) -> Run:
        """Get a run by its ID."""
        run = await self.repository.get_by_id(session, run_id)
        if not run:
            raise RunNotFoundError(str(run_id))
        return run

    async def list_runs(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Run]:
        """List runs with pagination."""
        return await self.repository.list_runs(session, skip, limit)

    async def get_run_sessions(
        self, run_id: UUID, session: AsyncSession
    ) -> list[SessionModel]:
        """Get all sessions for a specific run."""
        # Verify run exists first
        await self.get_run(run_id, session)
        return await self.repository.get_sessions(session, run_id)

    async def get_run_events(
        self, run_id: UUID, session: AsyncSession
    ) -> list[SessionModel]:
        """Get all events for a specific run."""
        # Verify run exists first
        await self.get_run(run_id, session)
        # TODO: Implement event repository when events are added
        # For now, return empty list
        return []

    # Private helper methods
    async def _create_run_record(
        self, request: RunCreate, run_id: UUID, session: AsyncSession
    ) -> Run:
        """Create the initial run record."""
        run = Run(
            id=run_id,
            flow_id=request.flow_id,
            user_id=request.user_id,
            status=RunStatus.PENDING,
        )
        run = await self.repository.create(session, run)

        # Emit pending status event
        await self._emit_progress_safe(
            run_id,
            {
                "status": RunStatus.PENDING.value,
                "message": "Run created, initializing session",
            },
        )
        return run

    async def _handle_session_creation_failure(
        self, run_id: UUID, session: AsyncSession, error_message: str
    ) -> None:
        """Handle session creation failure."""
        run = await self.repository.get_by_id(session, run_id)
        if run:
            run.status = RunStatus.FAILED
            run.error = error_message
            run.ended_at = datetime.now(UTC)
            run.updated_at = datetime.now(UTC)
            await self.repository.update(session, run)

            await self._emit_progress_safe(
                run_id,
                {
                    "status": RunStatus.FAILED.value,
                    "message": error_message,
                },
            )

    async def _create_session_and_finalize_run(
        self,
        run_id: UUID,
        session_url: str,
        browser_session_id: str,
        session: AsyncSession,
    ) -> Run:
        """Create session record and finalize the run."""
        # Create session record
        db_session = SessionModel(
            id=uuid4(),
            run_id=run_id,
            browser_provider_session_id=browser_session_id,
            session_url=session_url,
            status="running",
        )
        await self.repository.create_session(session, db_session)

        # Update run
        run = await self.repository.get_by_id(session, run_id)
        if run:
            run.status = RunStatus.RUNNING
            run.started_at = datetime.now(UTC)
            run.updated_at = datetime.now(UTC)
            await self.repository.update(session, run)

        return run

    def _fail_session_creation(self) -> None:
        """Raise session creation failure."""
        raise SessionCreationFailedError

    def _fail_missing_url(self) -> None:
        """Raise missing URL failure."""
        raise MissingSessionURLError

    async def _emit_progress_safe(self, run_id: UUID, data: dict) -> None:
        """Safely emit progress events."""
        try:
            await emit_progress(str(run_id), data)
        except (ConnectionError, TimeoutError, OSError, ValueError) as e:
            logger.warning("Failed to emit progress for run %s: %s", run_id, str(e))

    async def update_run(
        self, run_id: UUID, request: dict, session: AsyncSession
    ) -> Run:
        """Update an existing run."""
        run = await self.repository.get_by_id(session, run_id)
        if not run:
            error_msg = f"Run {run_id} not found"
            raise RunNotFoundError(error_msg)

        # Update fields from request
        if "result_uri" in request:
            run.result_uri = request["result_uri"]
        if "status" in request:
            new_status = request["status"]
            if not self._is_valid_status_transition(run.status, new_status):
                error_msg = (
                    f"Invalid status transition from {run.status} to {new_status}"
                )
                raise ValueError(error_msg)
            run.status = new_status
        if "error" in request:
            run.error = request["error"]
        if "ended_at" in request:
            run.ended_at = request["ended_at"]

        run.updated_at = datetime.now(UTC)
        return await self.repository.update(session, run)
