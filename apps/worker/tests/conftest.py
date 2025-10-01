import asyncio
import contextlib
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch
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
from app.models import Flow, FlowVisibility, Run, RunStatus, User, UserRole
from app.utils.auth import create_access_token, get_password_hash


class MockStorageBackend:
    """Mock storage backend for testing with tmp_path files."""

    def __init__(self, test_files):
        self.test_files = test_files

    async def get_file_info(self, storage_uri: str) -> tuple[str, int]:
        """Return file info for test files."""
        file_path = self.test_files.get(storage_uri)
        if file_path and file_path.exists():
            return file_path.name, file_path.stat().st_size
        error_msg = f"File not found: {storage_uri}"
        raise FileNotFoundError(error_msg)

    async def retrieve(self, storage_uri: str):
        """Yield file content in chunks for streaming tests."""
        file_path = self.test_files.get(storage_uri)
        if file_path and file_path.exists():
            with file_path.open("rb") as f:
                while True:
                    chunk = f.read(8192)
                    if not chunk:
                        break
                    yield chunk
        else:
            error_msg = f"File not found: {storage_uri}"
            raise FileNotFoundError(error_msg)


def mock_steel_service():
    """Mock the Steel service to avoid hitting API limits during tests."""
    # Patch the settings.steel_api_key to None to force SteelService into dev mode
    settings_patcher = patch("app.config.settings.steel_api_key", None)
    settings_patcher.start()
    return settings_patcher


class BaseTestClass:
    """Base test class with common utilities for API testing."""

    API_PREFIX = API_V1_PREFIX

    def set_run_status(self, run_id: str, status: RunStatus):
        """Helper method to set run status directly in the database.

        Note: This method uses asyncio.run() internally and should only be
        called from synchronous test methods. For async test methods, use
        async_set_run_status().
        """
        asyncio.run(self._set_run_status_async(run_id, status))

    def set_flow_visibility(self, flow_id: str, visibility: FlowVisibility):
        """Helper method to update flow visibility in the database."""

        asyncio.run(self._set_flow_visibility_async(flow_id, visibility))

    async def async_set_run_status(self, run_id: str, status: RunStatus):
        """Async helper method to set run status directly in the database.

        Safe to call from async test methods.
        """
        await self._set_run_status_async(run_id, status)

    async def _set_run_status_async(self, run_id: str, status: RunStatus):
        """Async helper method to set run status directly in the database."""
        async with self.TestAsyncSessionLocal() as session:
            result = await session.execute(select(Run).where(Run.id == UUID(run_id)))
            run = result.scalar_one_or_none()
            if run:
                run.status = status
                await session.commit()

    async def _set_flow_visibility_async(
        self, flow_id: str, visibility: FlowVisibility
    ) -> None:
        """Async helper method to update flow visibility."""

        async with self.TestAsyncSessionLocal() as session:
            result = await session.execute(select(Flow).where(Flow.id == UUID(flow_id)))
            flow = result.scalar_one_or_none()
            if flow:
                flow.visibility = visibility
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
        self.settings_patcher = mock_steel_service()
        self.client = TestClient(app)

    def _override_db_dependency(self):
        """Override the database session dependency to use test session."""
        # Create a test session factory that uses our test database
        self.test_engine = create_async_engine(self.test_db_url, echo=False)

        # Enforce SQLite FKs for all conns
        @event.listens_for(self.test_engine.sync_engine, "connect")
        def _fk_on(dbapi_connection, connection_record):  # noqa: ARG001
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
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
        """Create test data for SQLModel including authenticated users."""
        async with self.TestAsyncSessionLocal() as session:
            # Create test users with authentication
            self.test_user = User(
                id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                email="user@example.com",
                password_hash=get_password_hash("userpass"),
                name="Test User",
                role=UserRole.USER,
            )

            self.test_admin = User(
                id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                email="admin@example.com",
                password_hash=get_password_hash("adminpass"),
                name="Test Admin",
                role=UserRole.ADMIN,
            )

            session.add(self.test_user)
            session.add(self.test_admin)
            await session.commit()  # Commit to persist users

            # Refresh to get any auto-generated fields
            await session.refresh(self.test_user)
            await session.refresh(self.test_admin)

            # Create test flows for the user
            flows = [
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440000"),
                    key="test-flow",
                    name="Test Flow",
                    description="A test flow for development and testing",
                    created_by=self.test_user.id,
                    visibility=FlowVisibility.PUBLIC,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440001"),
                    key="hitl-flow",
                    name="HITL Flow",
                    description="A flow that requires human-in-the-loop interaction",
                    created_by=self.test_user.id,
                    visibility=FlowVisibility.PUBLIC,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440002"),
                    key="auto-complete-flow",
                    name="Auto Complete Flow",
                    description="A flow that completes automatically",
                    created_by=self.test_user.id,
                    visibility=FlowVisibility.PUBLIC,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440003"),
                    key="pdf-generation-flow",
                    name="PDF Generation Flow",
                    description="A flow that generates PDF artifacts",
                    created_by=self.test_user.id,
                    visibility=FlowVisibility.PUBLIC,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440004"),
                    key="large-output-flow",
                    name="Large Output Flow",
                    description="A flow that generates large output files",
                    created_by=self.test_user.id,
                    visibility=FlowVisibility.PUBLIC,
                ),
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440005"),
                    key="multi-hitl-flow",
                    name="Multi HITL Flow",
                    description="A flow with multiple human interaction points",
                    created_by=self.test_user.id,
                    visibility=FlowVisibility.PUBLIC,
                ),
                # Add a flow owned by admin to test visibility differences
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440006"),
                    key="admin-only-flow",
                    name="Admin Only Flow",
                    description="A flow only visible to admins",
                    created_by=self.test_admin.id,
                ),
                # Add another admin-owned flow for access control testing
                Flow(
                    id=UUID("550e8400-e29b-41d4-a716-446655440007"),
                    key="admin-secret-flow",
                    name="Admin Secret Flow",
                    description="Another flow only admins can access",
                    created_by=self.test_admin.id,
                ),
            ]

            for flow in flows:
                session.add(flow)

            await session.commit()

    def get_auth_headers(self, user: User = None):
        """Get authentication headers for a user using direct JWT token creation."""

        if user is None:
            user = self.test_user

        # Create token data directly
        token_data = {"sub": str(user.id), "email": user.email, "role": user.role.value}

        # Create token directly using JWT utility
        token = create_access_token(token_data)
        return {"Authorization": f"Bearer {token}"}

    def get_user_auth_headers(self):
        """Get authentication headers for test user."""
        return self.get_auth_headers(self.test_user)

    def get_admin_auth_headers(self):
        """Get authentication headers for test admin."""
        return self.get_auth_headers(self.test_admin)

    def teardown_method(self):
        """Clean up after each test."""
        self.settings_patcher.stop()
        # Clear dependency overrides
        app.dependency_overrides = {}
        # Clean up temporary database file
        # Ensure engine is closed before unlink
        with contextlib.suppress(Exception):
            asyncio.run(self.test_engine.dispose())
        with contextlib.suppress(OSError, FileNotFoundError):
            Path(self.temp_db.name).unlink()
