"""Execution context for flow runs."""

from typing import Any
from uuid import UUID


class RunContext:
    """Context object for flow execution."""

    def __init__(
        self,
        run_id: UUID,
        flow_id: UUID,
        user_id: UUID,
        input_payload: dict[str, Any],
        manifest: dict[str, Any],
    ):
        self.run_id = run_id
        self.flow_id = flow_id
        self.user_id = user_id
        self.input_payload = input_payload
        self.manifest = manifest

        # Execution state
        self.current_step = 0
        self.variables: dict[str, Any] = {}
        self.checkpoints: dict[str, Any] = {}

    def get_input(self, key: str, default: Any = None) -> Any:
        """Get input value by key."""
        return self.input_payload.get(key, default)

    def set_variable(self, key: str, value: Any) -> None:
        """Set a runtime variable."""
        self.variables[key] = value

    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a runtime variable."""
        return self.variables.get(key, default)

    def add_checkpoint(self, checkpoint_id: str, data: dict[str, Any]) -> None:
        """Add a checkpoint."""
        self.checkpoints[checkpoint_id] = data

    def get_checkpoint(self, checkpoint_id: str) -> dict[str, Any]:
        """Get checkpoint data."""
        return self.checkpoints.get(checkpoint_id, {})
