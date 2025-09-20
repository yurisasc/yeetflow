import asyncio

import pytest
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel


@pytest.fixture
def engine():
    """Create async SQLite engine for unit tests."""
    # Use in-memory SQLite to avoid file conflicts between tests
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Ensure FK enforcement on every connection
    @event.listens_for(engine.sync_engine, "connect")
    def _fk_on(dbapi_connection, connection_record):  # noqa: ARG001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    # Create tables
    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    # Setup and teardown
    asyncio.run(create_tables())

    yield engine

    # Cleanup
    asyncio.run(engine.dispose())


@pytest.fixture
def async_session_maker(engine):
    """Create async session maker."""
    return async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest.fixture
async def session(async_session_maker):
    """Provide clean async session for each test."""
    session = async_session_maker()
    try:
        yield session
    finally:
        await session.close()
