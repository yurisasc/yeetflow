import sqlite3
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import uuid

from fastapi import HTTPException
from ..db import get_db_connection
from ..models import RunStatus
from ..utils.retry import retry_db_operation, RetryError

logger = logging.getLogger(__name__)


class RunService:
    """Service for managing run-related database operations."""

    def __init__(self):
        pass

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def create_run_with_transaction(
        self, run_id: str, flow_id: str, user_id: str
    ) -> Dict[str, Any]:
        """
        Create a run record and commit immediately.
        Returns the created run data.
        """
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()

                # Validate flow exists
                cursor.execute("SELECT id FROM flows WHERE id = ?", (flow_id,))
                if not cursor.fetchone():
                    raise HTTPException(status_code=400, detail="Flow not found")

                # Create run record and commit immediately
                created_at = datetime.now(timezone.utc).isoformat()
                cursor.execute(
                    """
                    INSERT INTO runs (id, flow_id, user_id, status, created_at, updated_at)
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

        except sqlite3.Error as e:
            logger.error(f"Database error creating run: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def update_run_with_session(
        self, run_id: str, session_url: str, status: RunStatus
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
                        datetime.now(timezone.utc).isoformat(),
                        run_id,
                    ),
                )
                conn.commit()
            finally:
                conn.close()

        except sqlite3.Error as e:
            logger.error(f"Database error updating run with session: {e}")
            raise HTTPException(status_code=500, detail="Database error")

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
                        datetime.now(timezone.utc).isoformat(),
                        run_id,
                    ),
                )
                conn.commit()
            finally:
                conn.close()

        except sqlite3.Error as e:
            logger.error(f"Database error updating run status: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def create_session_record(
        self, run_id: str, browser_session_id: str, session_url: str
    ) -> str:
        """Create a session record and return session_id."""
        session_id = str(uuid.uuid4())
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    INSERT INTO sessions (id, run_id, browser_session_id, steel_session_url, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        session_id,
                        run_id,
                        browser_session_id,
                        session_url,
                        datetime.now(timezone.utc).isoformat(),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                conn.commit()
                return session_id
            finally:
                conn.close()

        except sqlite3.Error as e:
            logger.error(f"Database error creating session: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    @retry_db_operation(max_attempts=3, base_delay=0.5, max_delay=5.0)
    async def get_run_by_id(self, run_id: str) -> Optional[Dict[str, Any]]:
        """Get run details by ID."""
        try:
            conn = get_db_connection()
            try:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT id, flow_id, user_id, status, session_url, created_at, updated_at
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

        except sqlite3.Error as e:
            logger.error(f"Database error getting run: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    async def commit_transaction(self, conn) -> None:
        """Commit the current transaction."""
        try:
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"Database error committing transaction: {e}")
            raise HTTPException(status_code=500, detail="Database error")

    async def rollback_transaction(self, conn) -> None:
        """Rollback the current transaction."""
        try:
            conn.rollback()
        except sqlite3.Error as e:
            logger.error(f"Database error rolling back transaction: {e}")
            # Don't raise here since we're already in error handling
