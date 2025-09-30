"""Run Finite State Machine (FSM) skeleton."""

from __future__ import annotations

from typing import Final

ALLOWED: Final[dict[str, set[str]]] = {
    "pending": {"running", "canceled"},
    "running": {"awaiting_input", "completed", "failed", "canceled"},
    "awaiting_input": {"running", "failed", "canceled"},
    "completed": set(),
    "failed": set(),
    "canceled": set(),
}


class RunStateMachine:
    """Simple FSM for run lifecycle transitions."""

    def __init__(self, current: str) -> None:
        self.current = (current or "pending").lower()
        if self.current not in ALLOWED:
            msg = f"Unknown run state: {self.current}"
            raise ValueError(msg)

    def can_transition(self, to_state: str) -> bool:
        target = (to_state or "").lower()
        return target in ALLOWED.get(self.current, set())

    def transition(self, to_state: str) -> str:
        target = (to_state or "").lower()
        if not self.can_transition(target):
            msg = f"Invalid transition: {self.current} → {target}"
            raise ValueError(msg)
        self.current = target
        return self.current
