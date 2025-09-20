"""Errors for artifact service operations."""


class ArtifactNotFoundError(Exception):
    """Raised when an artifact is not found."""


class RunNotFoundError(Exception):
    """Raised when a run is not found."""

    def __init__(self, run_id: str) -> None:
        super().__init__(f"Run {run_id} not found")


class ArtifactAccessError(Exception):
    """Raised when there's an error accessing artifact files."""
