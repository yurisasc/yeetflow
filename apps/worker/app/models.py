from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import sqlalchemy as sa
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, model_validator
from pydantic import Field as PydField
from sqlalchemy.dialects.sqlite import JSON
from sqlmodel import Column, Field, ForeignKey, Relationship, SQLModel


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(SQLModel):
    email: str = Field(index=True, unique=True)
    name: str | None = None
    role: UserRole = Field(default=UserRole.USER)


class FlowBase(SQLModel):
    key: str = Field(index=True, unique=True)
    name: str
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)


class RunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    FAILED = "failed"


class SessionStatus(str, Enum):
    STARTING = "starting"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"


class EventType(str, Enum):
    PROGRESS = "progress"
    ACTION_REQUIRED = "action_required"
    ACTION_ACK = "action_ack"
    COMPLETED = "completed"
    FAILED = "failed"
    RUN_CONTINUED = "run_continued"


class RunBase(SQLModel):
    status: RunStatus = RunStatus.PENDING
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error: str | None = None
    result_uri: str | None = None


class SessionBase(SQLModel):
    browser_provider_session_id: str | None = None
    status: SessionStatus = Field(
        default=SessionStatus.STARTING,
        sa_column=Column(sa.VARCHAR(), server_default=SessionStatus.STARTING.value),
    )
    session_url: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None


class EventBase(SQLModel):
    type: EventType = Field(sa_column=Column(sa.VARCHAR(), nullable=False))
    message: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    at: datetime = Field(default_factory=lambda: datetime.now(UTC))


# Table models
class User(UserBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    password_hash: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    flows: list["Flow"] = Relationship(back_populates="user")
    runs: list["Run"] = Relationship(back_populates="user")


class Flow(FlowBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    created_by: UUID = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    user: User | None = Relationship(back_populates="flows")
    runs: list["Run"] = Relationship(back_populates="flow")


class Run(RunBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    flow_id: UUID = Field(
        sa_column=Column(
            ForeignKey("flow.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    user_id: UUID = Field(
        sa_column=Column(
            ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )

    flow: Flow | None = Relationship(back_populates="runs")
    user: User | None = Relationship(back_populates="runs")
    sessions: list["Session"] = Relationship(
        back_populates="run", passive_deletes="all"
    )
    events: list["Event"] = Relationship(back_populates="run", passive_deletes="all")


class Session(SessionBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    run_id: UUID = Field(
        sa_column=Column(
            ForeignKey("run.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    run: Run | None = Relationship(back_populates="sessions")


class Event(EventBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)

    run_id: UUID = Field(
        sa_column=Column(
            ForeignKey("run.id", ondelete="CASCADE"), nullable=False, index=True
        )
    )
    run: Run | None = Relationship(back_populates="events")


# API models
class UserCreate(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    email: str
    name: str | None = None
    password: str
    role: UserRole = UserRole.USER


class UserRead(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: str
    name: str | None = None
    role: UserRole
    created_at: datetime
    updated_at: datetime


class UserUpdate(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str | None = None
    password: str | None = None


class FlowCreate(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    key: str
    name: str
    description: str | None = None
    config: dict = PydField(default_factory=dict)


class FlowRead(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    key: str
    name: str
    description: str | None = None
    created_by: UUID
    created_at: datetime
    updated_at: datetime


class RunCreate(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    flow_id: UUID


class RunRead(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: UUID
    flow_id: UUID
    user_id: UUID
    status: RunStatus
    started_at: datetime | None = None
    ended_at: datetime | None = None
    error: str | None = None
    result_uri: str | None = None
    created_at: datetime
    updated_at: datetime


class RunUpdate(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    result_uri: str | None = None
    status: RunStatus | None = None
    error: str | None = None
    ended_at: datetime | None = None


class RunContinue(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    input_payload: dict | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def validate_at_least_one_field(self):
        if self.input_payload is None and self.notes is None:
            error_msg = "At least one of input_payload or notes must be provided"
            raise ValueError(error_msg)
        return self

    @model_validator(mode="after")
    def validate_input_payload(self):
        if self.input_payload is not None:
            if "action" not in self.input_payload:
                error_msg = "input_payload must contain an 'action' field"
                raise ValueError(error_msg)
            valid_actions = ["continue"]
            if self.input_payload["action"] not in valid_actions:
                error_msg = f"action must be one of: {', '.join(valid_actions)}"
                raise ValueError(error_msg)
        return self


class SessionCreate(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    run_id: UUID
    browser_provider_session_id: str | None = None
    status: SessionStatus = SessionStatus.STARTING
    session_url: str | None = None


class SessionRead(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: UUID
    run_id: UUID
    browser_provider_session_id: str | None = None
    status: SessionStatus
    session_url: str | None = None
    created_at: datetime
    ended_at: datetime | None = None


class EventCreate(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True)
    run_id: UUID
    type: EventType
    message: str | None = None
    payload: dict = PydField(default_factory=dict)


class EventRead(PydanticBaseModel):
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    id: UUID
    run_id: UUID
    type: EventType
    message: str | None = None
    payload: dict
    at: datetime
