"""Event service errors."""


class EventError(Exception):
    """Base exception for event-related errors."""


class EventNotFoundError(EventError):
    """Raised when a requested event does not exist."""

    def __init__(self, event_id: str) -> None:
        super().__init__(f"Event {event_id} not found")


class EventValidationError(EventError):
    """Raised when event data is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Event validation error: {message}")


class EventAccessDeniedError(EventError):
    """Raised when access to event data is denied."""

    def __init__(self, run_id: str) -> None:
        super().__init__(f"Access denied to events for run {run_id}")
