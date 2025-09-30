"""Typed flow steps and manifest parser.

Provides simple classes for action and checkpoint steps and a parser that
normalizes a manifest dict into a list of typed steps.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class ActionStep:
    """Represents an executable action step.

    Attributes
    - name: optional display name for the step
    - action: the action payload, e.g. {"type": "click", "selector": "#id"}
    """

    name: str | None
    action: dict[str, Any]


@dataclass
class CheckpointStep:
    """Represents a human-in-the-loop pause point.

    Attributes
    - id: optional identifier; falls back to name when not provided
    - name: human-readable label
    - reason: why we pause
    - expected_action: e.g., "continue"
    - timeout: seconds until auto-timeout
    """

    id: str | None = None
    name: str | None = None
    reason: str | None = None
    expected_action: str | None = None
    timeout: int | None = None


def parse_manifest_steps(manifest: dict[str, Any]) -> list[ActionStep | CheckpointStep]:
    """Parse a manifest dict into typed steps.

    Accepts both {"config": {"steps": [...]}} and {"steps": [...]} forms.
    Unknown step types are ignored.
    """

    cfg = manifest or {}
    steps_data = (
        (
            (cfg.get("config") or {}).get("steps")
            if isinstance(cfg.get("config"), dict)
            else None
        )
        or cfg.get("steps")
        or []
    )

    typed: list[ActionStep | CheckpointStep] = []
    for raw in steps_data:
        if not isinstance(raw, dict):
            logger.debug("Skipping non-dict step: %s", raw)
            continue
        step_type = (raw.get("type") or "").lower()
        if step_type == "action":
            action = raw.get("action") or {}
            name = raw.get("name")
            if isinstance(action, dict):
                typed.append(ActionStep(name=name, action=action))
            else:
                logger.debug(
                    "Skipping action step with non-dict action payload: %s", raw
                )
        elif step_type == "checkpoint":
            typed.append(
                CheckpointStep(
                    id=raw.get("id"),
                    name=raw.get("name"),
                    reason=raw.get("reason"),
                    expected_action=raw.get("expected_action"),
                    timeout=raw.get("timeout"),
                )
            )
        # else: skip unknown types silently

    return typed
