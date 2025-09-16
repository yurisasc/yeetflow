import logging
import sqlite3
import uuid
from datetime import UTC, datetime
from typing import Any

from fastapi import HTTPException

from app.db import get_db_connection
from app.models import RunStatus
from app.utils.retry import retry_db_operation

logger = logging.getLogger(__name__)


class RunService:
    """Service for managing run-related database operations."""

    def __init__(self):
        pass

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def create_run_with_transaction(
        self,
        run_id: str,
        flow_id: str,
        user_id: str,
    ) -> dict[str, Any]:
        """Create a run record (autocommit) and return the created run data."""
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()

                # Validate flow exists
                cursor.execute("SELECT id FROM flows WHERE id = ?", (flow_id,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Flow not found")

                # Create run record and commit immediately
                created_at = datetime.now(UTC).isoformat()
                cursor.execute(
                    """
                    INSERT INTO runs (
                        id, flow_id, user_id, status, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        flow_id,
                        user_id,
                        RunStatus.PENDING.value,
                        created_at,
                        created_at,
                    ),
                )
                conn.commit()

                return {
                    "id": run_id,
                    "flow_id": flow_id,
                    "user_id": user_id,
                    "status": RunStatus.PENDING.value,
                    "session_url": None,
                    "created_at": created_at,
                    "updated_at": created_at,
                }
            finally:
                conn.close()

        except sqlite3.Error:
            logger.exception("Database error creating run")
            raise

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def update_run_with_session(
        self,
        run_id: str,
        session_url: str,
        status: RunStatus,
    ) -> None:
        """Update run with session URL and status."""
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE runs
                    SET session_url = ?, status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        session_url,
                        status.value,
                        datetime.now(UTC).isoformat(),
                        run_id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Run not found")
                conn.commit()
            finally:
                conn.close()

        except sqlite3.Error:
            logger.exception("Database error updating run with session")
            raise

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def update_run_status(self, run_id: str, status: RunStatus) -> None:
        """Update run status."""
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    UPDATE runs
                    SET status = ?, updated_at = ?
                    WHERE id = ?
                    """,
                    (
                        status.value,
                        datetime.now(UTC).isoformat(),
                        run_id,
                    ),
                )
                if cursor.rowcount == 0:
                    raise HTTPException(status_code=404, detail="Run not found")
                conn.commit()
            finally:
                conn.close()

        except sqlite3.Error:
            logger.exception("Database error updating run status")
            raise

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def create_session_record(
        self,
        run_id: str,
        browser_session_id: str,
        session_url: str,
    ) -> str:
        """Create a session record and return session_id."""
        session_id = str(uuid.uuid4())
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO sessions (
                        id, run_id, browser_session_id,
                        steel_session_url, created_at, updated_at
                    )
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        run_id,
                        browser_session_id,
                        session_url,
                        datetime.now(UTC).isoformat(),
                        datetime.now(UTC).isoformat(),
                    ),
                )
                conn.commit()
                return session_id
            finally:
                conn.close()

        except sqlite3.Error:
            logger.exception("Database error creating session")
            raise

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def get_run_by_id(self, run_id: str) -> dict[str, Any] | None:
        """Get run details by ID."""
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, flow_id, user_id, status,
                           session_url, created_at, updated_at
                    FROM runs WHERE id = ?
                    """,
                    (run_id,),
                )
                row = cursor.fetchone()
                if not row:
                    return None

                return {
                    "id": row["id"],
                    "flow_id": row["flow_id"],
                    "user_id": row["user_id"],
                    "status": row["status"],
                    "session_url": row["session_url"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                }
            finally:
                conn.close()

        except sqlite3.Error:
            logger.exception("Database error getting run")
            raise

    async def commit_transaction(self, conn: sqlite3.Connection) -> None:
        """Commit the current transaction."""
        try:
            conn.commit()
        except sqlite3.Error:
            logger.exception("Database error committing transaction")
            raise

    async def rollback_transaction(self, conn: sqlite3.Connection) -> None:
        """Rollback the current transaction."""
        try:
            conn.rollback()
        except sqlite3.Error:
            logger.exception("Database error rolling back transaction")
            # Don't raise here since we're already in error handling
