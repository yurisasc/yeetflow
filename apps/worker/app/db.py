import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text

from .config import get_database_url

logger = logging.getLogger(__name__)

# Database configuration
ASYNC_DATABASE_URL = get_database_url()

# Create async engine
engine = create_async_engine(
    ASYNC_DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False} if "sqlite" in ASYNC_DATABASE_URL else {},
)

# Create session maker
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@asynccontextmanager
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get an async SQLModel session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize the database with SQLModel tables."""
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
        # Enable foreign keys for SQLite
        if "sqlite" in str(conn.engine.url):
            await conn.execute(text("PRAGMA foreign_keys = ON"))


async def get_db_session() -> AsyncSession:
    """Get a database session (for use with FastAPI Depends)."""
    async with get_session() as session:
        yield session
