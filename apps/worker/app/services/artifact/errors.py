"""Errors for artifact service operations."""


class ArtifactNotFoundError(Exception):
    """Raised when an artifact is not found."""


class RunNotFoundError(Exception):
    """Raised when a run is not found."""


class ArtifactAccessError(Exception):
    """Raised when there's an error accessing artifact files."""
