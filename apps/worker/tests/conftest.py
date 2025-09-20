import asyncio
import contextlib
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID

from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, select

# Add the parent directory to Python path so we can import the app module
sys.path.insert(0, str(Path(__file__).parent.parent))

from app import db
from app.constants import API_V1_PREFIX
from app.db import get_db_session
from app.main import app
from app.models import Flow, Run, RunStatus, User

# Set up any test-wide fixtures here if needed


class BaseTestClass:
    """Base test class with common utilities for API testing."""

    API_PREFIX = API_V1_PREFIX

    def set_run_status(self, run_id: str, status: RunStatus):
        """Helper method to set run status directly in the database."""
        asyncio.run(self._set_run_status_async(run_id, status))

    async def _set_run_status_async(self, run_id: str, status: RunStatus):
        """Async helper method to set run status directly in the database."""
        async with get_db_session() as session:
            result = await session.execute(select(Run).where(Run.id == run_id))
            run = result.scalar_one_or_none()
            if run:
                run.status = status
                await session.commit()

    def setup_method(self):
        """Set up test client before each test."""
        # Use a temporary database file for each test to avoid locking issues
        with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as temp_file:
            self.temp_db = temp_file
            self.test_db_url = f"sqlite+aiosqlite:///{temp_file.name}"
            os.environ["DATABASE_URL"] = self.test_db_url

        # Override the database session dependency for testing (this creates tables)
        self._override_db_dependency()

        # Create test data using the test session
        asyncio.run(self._create_test_data())

        # Mock the Steel service using the common utility
        self.steel_patcher = mock_steel_service()
        self.client = TestClient(app)

    def _override_db_dependency(self):
        """Override the database session dependency to use test session."""
        # Create a test session factory that uses our test database
        self.test_engine = create_async_engine(self.test_db_url, echo=False)

        # Register event listener for SQLite foreign keys (same as production)
        @event.listens_for(self.test_engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, _):
            """Enable foreign key constraints for every SQLite connection."""
            if "sqlite" in self.test_db_url:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys = ON")
                cursor.close()

        # Create tables in the test database
        async def create_tables():
            async with self.test_engine.begin() as conn:
                await conn.run_sync(SQLModel.metadata.create_all)

        asyncio.run(create_tables())

        self.TestAsyncSessionLocal = sessionmaker(
            self.test_engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        # Update the global database configuration to use test database
        db.engine = self.test_engine
        db.AsyncSessionLocal = self.TestAsyncSessionLocal

        async def override_get_db_session():
            async with self.TestAsyncSessionLocal() as session:
                try:
                    yield session
                except Exception:
                    await session.rollback()
                    raise
                finally:
                    await session.close()

        # Override the dependency in the FastAPI app
        app.dependency_overrides[get_db_session] = override_get_db_session

    async def _create_test_data(self):
        """Create test data for SQLModel."""
        async with self.TestAsyncSessionLocal() as session:
            # Create test user
            user = User(
                id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                email="test@example.com",
                password_hash="test_hash",  # noqa: S106
                name="Test User",
            )
            session.add(user)
            await session.commit()

            # Create test flows
            flows = [
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                    key="test-flow",
                    name="Test Flow",
                    description="A test flow for development and testing",
                    created_by=user.id,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                    key="hitl-flow",
                    name="HITL Flow",
                    description="A flow that requires human-in-the-loop interaction",
                    created_by=user.id,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    key="auto-complete-flow",
                    name="Auto Complete Flow",
                    description="A flow that completes automatically",
                    created_by=user.id,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440003"),
                    key="pdf-generation-flow",
                    name="PDF Generation Flow",
                    description="A flow that generates PDF artifacts",
                    created_by=user.id,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                    key="large-output-flow",
                    name="Large Output Flow",
                    description="A flow that generates large output files",
                    created_by=user.id,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                    key="multi-hitl-flow",
                    name="Multi HITL Flow",
                    description="A flow with multiple human interaction points",
                    created_by=user.id,
                ),
            ]

            for flow in flows:
                session.add(flow)

            await session.commit()

    def teardown_method(self):
        """Clean up after each test."""
        self.steel_patcher.stop()
        # Clear dependency overrides
        app.dependency_overrides = {}
        # Clean up temporary database file
        with contextlib.suppress(OSError, FileNotFoundError):
            Path(self.temp_db.name).unlink()


def mock_steel_service():
    """Mock the Steel service to avoid hitting API limits during tests."""
    mock_session_data = {
        "id": "test-session-123",
        "createdAt": "2025-09-16T02:11:28.027Z",
        "status": "live",
        "sessionViewerUrl": "https://app.steel.dev/sessions/test-session-123",
        "websocketUrl": "wss://api.steel.dev/sessions/test-session-123/ws",
        "debugUrl": "https://debug.steel.dev/sessions/test-session-123",
    }

    patcher = patch("app.services.run.service.SteelService")
    mock_service_class = patcher.start()

    mock_service_instance = MagicMock()
    mock_service_instance.create_session = AsyncMock(return_value=mock_session_data)
    mock_service_class.return_value = mock_service_instance

    return patcher
