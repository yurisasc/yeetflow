import asyncio
import contextlib
import importlib
import sys
from logging.config import fileConfig
from pathlib import Path

# Add parent directory to sys.path to make app package discoverable when Alembic runs
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel
from sqlmodel.sql.sqltypes import AutoString

from alembic import context
from app.config import get_database_url

# Make sure models are imported so SQLModel.metadata is populated for autogenerate
for _mod in ("app.models", "app.db.models"):
    with contextlib.suppress(ModuleNotFoundError):
        importlib.import_module(_mod)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


database_url = get_database_url()
config.set_main_option("sqlalchemy.url", database_url)

target_metadata = SQLModel.metadata


def render_item(type_, obj, autogen_context):
    """Ensure enums are rendered with their value strings."""

    if type_ == "type":
        if isinstance(obj, SQLEnum) and getattr(obj, "enum_class", None):
            values = ", ".join(repr(member.value) for member in obj.enum_class)
            enum_name = (
                obj.name if obj.name is not None else obj.enum_class.__name__.lower()
            )
            return f"sa.Enum({values}, name={enum_name!r})"

        if isinstance(obj, AutoString):
            autogen_context.imports.add("import sqlmodel")
            return "sqlmodel.sql.sqltypes.AutoString()"
    return False


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    is_sqlite = url.startswith("sqlite")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
        render_as_batch=is_sqlite,
        render_item=render_item,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Run migrations with the given connection."""
    is_sqlite = config.get_main_option("sqlalchemy.url").startswith("sqlite")
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
        render_as_batch=is_sqlite,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an async Engine
    and associate a connection with the context.

    """
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,
        pool_pre_ping=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online_sync() -> None:
    """Synchronous wrapper for running migrations online."""
    asyncio.run(run_migrations_online())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online_sync()
