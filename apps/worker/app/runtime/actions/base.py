"""Action command base interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from app.runtime.core import Agent, RunContext
from app.runtime.engine import EventEmitter


@dataclass(slots=True)
class ActionExecution:
    """Aggregated execution context passed to actions."""

    context: RunContext
    agent: Agent
    events: EventEmitter
    action_type: str
    step_name: str
    params: dict[str, Any]


class Action(Protocol):
    """Action command interface."""

    async def execute(
        self, execution: ActionExecution
    ) -> None:  # pragma: no cover - interface only
        ...


class RequiresParam:
    """Mixin with helpers for required parameters."""

    @staticmethod
    def require(d: dict[str, Any], key: str, *, allow_empty: bool = False) -> Any:
        if key not in d:
            msg = f"Missing required action param: {key}"
            raise ValueError(msg)

        value = d[key]
        if value is None:
            msg = f"Missing required action param: {key}"
            raise ValueError(msg)

        if not allow_empty and value == "":
            msg = f"Missing required action param: {key}"
            raise ValueError(msg)

        return value
