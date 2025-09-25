class RunError(Exception):
    """Base exception for run-related errors."""


class SessionCreationFailedError(RunError):
    """Raised when Steel session creation fails."""

    def __init__(self, message: str = "Failed to create browser session") -> None:
        super().__init__(message)


class MissingSessionURLError(RunError):
    """Raised when session is created without viewer URL."""

    def __init__(self, message: str = "Session created without viewer URL") -> None:
        super().__init__(message)


class RunNotFoundError(RunError):
    """Raised when a requested run does not exist."""

    def __init__(self, run_id: str) -> None:
        super().__init__(f"Run {run_id} not found")


class RunFinalizationError(RunError):
    """Raised when a run cannot be finalized after session creation."""

    def __init__(self, run_id: str, session_id: str | None = None) -> None:
        message = f"Run {run_id} could not be finalized"
        if session_id:
            message = f"{message} for session {session_id}"
        super().__init__(message)
