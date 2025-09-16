from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import uuid
from datetime import datetime

from ..models import RunStatus
from ..db import get_db_connection
from ..services.steel_service import SteelService
from ..sockets import emit_progress

router = APIRouter()


# Request/Response models
class CreateRunRequest(BaseModel):
    flow_id: str
    user_id: str


class CreateRunResponse(BaseModel):
    run_id: str
    session_url: str
    status: str = RunStatus.RUNNING


@router.post("/runs", response_model=CreateRunResponse, status_code=201)
async def create_run(request: CreateRunRequest):
    """Create a new run, initialize Steel.dev session, and return run details."""
    run_id = str(uuid.uuid4())

    try:
        # Create database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Validate that flow exists
        cursor.execute("SELECT id FROM flows WHERE id = ?", (request.flow_id,))
        flow = cursor.fetchone()
        if not flow:
            raise HTTPException(status_code=400, detail="Flow not found")
        cursor.execute(
            """
            INSERT INTO runs (id, flow_id, user_id, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                run_id,
                request.flow_id,
                request.user_id,
                RunStatus.PENDING.value,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )

        # Create Steel service and session
        steel_service = SteelService()
        session_data = await steel_service.create_session()

        if not session_data:
            # Update run status to FAILED if session creation fails
            cursor.execute(
                """
                UPDATE runs SET status = ?, updated_at = ? WHERE id = ?
            """,
                (RunStatus.FAILED.value, datetime.now().isoformat(), run_id),
            )
            conn.commit()
            conn.close()
            raise HTTPException(
                status_code=500, detail="Failed to create browser session"
            )

        session_url = session_data.get("sessionViewerUrl")
        browser_session_id = session_data.get("id")

        # Create session record
        session_id = str(uuid.uuid4())
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
                datetime.now().isoformat(),
                datetime.now().isoformat(),
            ),
        )

        # Update run with session URL and RUNNING status
        cursor.execute(
            """
            UPDATE runs SET session_url = ?, status = ?, updated_at = ? WHERE id = ?
        """,
            (session_url, RunStatus.RUNNING.value, datetime.now().isoformat(), run_id),
        )

        conn.commit()
        conn.close()

        # Emit progress event via Socket.IO
        await emit_progress(
            run_id, {"status": "initialized", "session_url": session_url}
        )

        return CreateRunResponse(run_id=run_id, session_url=session_url)

    except HTTPException:
        # Re-raise HTTPExceptions as-is (they have the correct status code)
        raise

    except Exception as e:
        # If anything fails, update run status to FAILED
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """
                UPDATE runs SET status = ?, updated_at = ? WHERE id = ?
            """,
                (RunStatus.FAILED.value, datetime.now().isoformat(), run_id),
            )
            conn.commit()
            conn.close()
        except:
            pass  # Ignore cleanup errors

        raise HTTPException(status_code=500, detail=f"Failed to create run: {str(e)}")
