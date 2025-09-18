import logging
from typing import Any

import socketio

from app.config import get_socketio_config

logger = logging.getLogger(__name__)

# Create Socket.IO server
socketio_config = get_socketio_config()
sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=socketio_config["cors_allowed_origins"],
)

# In-memory storage for connected clients (in production, use Redis or database)
connected_clients: dict[str, str] = {}


@sio.event
async def connect(sid: str, environ: dict[str, Any]) -> None:
    """Handle client connection."""
    _ = environ  # Unused parameter required by Socket.IO event signature
    logger.info("Client connected: %s", sid)
    connected_clients[sid] = sid


@sio.event
async def disconnect(sid: str):
    """Handle client disconnection."""
    logger.info("Client disconnected: %s", sid)
    connected_clients.pop(sid, None)


@sio.event
async def join_run(sid: str, data: dict[str, Any]):
    """Join a specific run room for real-time updates."""
    run_id = data.get("run_id")
    if isinstance(run_id, str) and run_id:
        await sio.enter_room(sid, run_id)
        logger.info("Client %s joined run room: %s", sid, run_id)


@sio.event
async def leave_run(sid: str, data: dict[str, Any]):
    """Leave a specific run room."""
    run_id = data.get("run_id")
    if isinstance(run_id, str) and run_id:
        await sio.leave_room(sid, run_id)
        logger.info("Client %s left run room: %s", sid, run_id)


# Event emission functions
async def emit_progress(run_id: str, data: dict[str, Any]):
    """Emit progress event to all clients in the run room."""
    await sio.emit("progress", data, room=run_id)


async def emit_action_required(run_id: str, data: dict[str, Any]):
    """Emit action required event to all clients in the run room."""
    await sio.emit("action_required", data, room=run_id)


async def emit_action_ack(run_id: str, data: dict[str, Any]):
    """Emit action ack event to all clients in the run room."""
    await sio.emit("action_ack", data, room=run_id)


async def emit_completed(run_id: str, data: dict[str, Any]):
    """Emit completion event to all clients in the run room."""
    await sio.emit("completed", data, room=run_id)


async def emit_failed(run_id: str, data: dict[str, Any]):
    """Emit failure event to all clients in the run room."""
    await sio.emit("failed", data, room=run_id)
