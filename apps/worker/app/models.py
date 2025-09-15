from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

class User(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class Flow(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    user_id: str
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    FAILED = "failed"

class EventType(str, Enum):
    PROGRESS = "progress"
    ACTION_REQUIRED = "action_required"
    ACTION_ACK = "action_ack"
    COMPLETED = "completed"
    FAILED = "failed"

class Run(BaseModel):
    id: str
    flow_id: str
    user_id: str
    status: RunStatus = RunStatus.PENDING
    session_url: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    artifact_path: Optional[str] = None

class Session(BaseModel):
    id: str
    run_id: str
    browser_session_id: Optional[str] = None
    steel_session_url: Optional[str] = None
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()

class Event(BaseModel):
    id: str
    run_id: str
    type: EventType
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime = datetime.now()
