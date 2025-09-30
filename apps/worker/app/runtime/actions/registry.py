"""Action registry and factory."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from app.runtime.actions.base import Action

_REGISTRY: dict[str, Callable[[dict[str, Any]], Action]] = {}


def register(name: str, factory: Callable[[dict[str, Any]], Action]) -> None:
    """Register an action factory under a name."""
    key = (name or "").lower()
    _REGISTRY[key] = factory


def create(action_type: str, params: dict[str, Any]) -> Action:
    """Create an action instance for the given type and parameters."""
    key = (action_type or "").lower()
    factory = _REGISTRY.get(key)
    if not factory:
        msg = f"Unknown action type: {key or '<empty>'}"
        raise ValueError(msg)
    return factory(params)


def known_actions() -> list[str]:
    return sorted(_REGISTRY.keys())
