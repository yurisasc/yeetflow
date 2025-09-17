from datetime import UTC, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class User(BaseModel):
    id: str
    email: str
    name: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Flow(BaseModel):
    id: str
    name: str
    description: str | None = None
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


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
    session_url: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    artifact_path: str | None = None


class Session(BaseModel):
    id: str
    run_id: str
    browser_session_id: str | None = None
    steel_session_url: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class Event(BaseModel):
    id: str
    run_id: str
    type: EventType
    data: dict[str, Any] | None = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
