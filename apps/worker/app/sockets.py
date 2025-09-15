import socketio
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create Socket.IO server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

# In-memory storage for connected clients (in production, use Redis or database)
connected_clients: Dict[str, str] = {}

@sio.event
async def connect(sid: str, environ: Dict[str, Any]):
    """Handle client connection."""
    logger.info(f"Client connected: {sid}")
    connected_clients[sid] = sid

@sio.event
async def disconnect(sid: str):
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {sid}")
    connected_clients.pop(sid, None)

@sio.event
async def join_run(sid: str, data: Dict[str, Any]):
    """Join a specific run room for real-time updates."""
    run_id = data.get('run_id')
    if run_id:
        await sio.enter_room(sid, run_id)
        logger.info(f"Client {sid} joined run room: {run_id}")

@sio.event
async def leave_run(sid: str, data: Dict[str, Any]):
    """Leave a specific run room."""
    run_id = data.get('run_id')
    if run_id:
        await sio.leave_room(sid, run_id)
        logger.info(f"Client {sid} left run room: {run_id}")

# Event emission functions
async def emit_progress(run_id: str, data: Dict[str, Any]):
    """Emit progress event to all clients in the run room."""
    await sio.emit('progress', data, room=run_id)

async def emit_action_required(run_id: str, data: Dict[str, Any]):
    """Emit action required event to all clients in the run room."""
    await sio.emit('action_required', data, room=run_id)

async def emit_action_ack(run_id: str, data: Dict[str, Any]):
    """Emit action ack event to all clients in the run room."""
    await sio.emit('action_ack', data, room=run_id)

async def emit_completed(run_id: str, data: Dict[str, Any]):
    """Emit completion event to all clients in the run room."""
    await sio.emit('completed', data, room=run_id)

async def emit_failed(run_id: str, data: Dict[str, Any]):
    """Emit failure event to all clients in the run room."""
    await sio.emit('failed', data, room=run_id)
