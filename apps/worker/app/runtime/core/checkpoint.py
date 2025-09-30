"""Checkpoint memento helpers for `RunContext`."""

from __future__ import annotations

from copy import deepcopy
from typing import Any, TypedDict

from .context import RunContext


class ContextMemento(TypedDict, total=False):
    run_id: str
    flow_id: str
    user_id: str
    current_step: int
    variables: dict[str, Any]


def snapshot_context(ctx: RunContext) -> ContextMemento:
    """Create a minimal snapshot of a `RunContext` state.

    Variables are deep-copied to avoid sharing nested mutable state with the
    live context.
    """
    return ContextMemento(
        run_id=str(ctx.run_id),
        flow_id=str(ctx.flow_id),
        user_id=str(ctx.user_id),
        current_step=int(ctx.current_step),
        variables=deepcopy(ctx.variables),
    )


def restore_context(ctx: RunContext, memento: ContextMemento) -> None:
    """Restore selected fields into an existing `RunContext`.

    Variables are merged additively: keys present in the memento override the
    current values, while keys absent from the memento remain untouched.
    """
    ctx.current_step = int(memento.get("current_step", ctx.current_step))
    for k, v in (memento.get("variables") or {}).items():
        ctx.variables[k] = v


def merge_inputs(
    base_input: dict[str, Any], latest_input: dict[str, Any] | None
) -> dict[str, Any]:
    """Return a merged input payload, latest overrides base."""
    if not latest_input:
        return dict(base_input)
    merged = dict(base_input)
    merged.update(latest_input)
    return merged
