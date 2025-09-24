class FlowError(Exception):
    """Base exception for flow-related errors."""


class FlowNotFoundError(FlowError):
    """Raised when a requested flow does not exist."""

    def __init__(self, flow_id: str) -> None:
        super().__init__(f"Flow {flow_id} not found")


class FlowAccessDeniedError(FlowError):
    """Raised when the user does not have access to the specified flow."""

    def __init__(self, flow_id: str) -> None:
        super().__init__(f"Access denied to flow {flow_id}")


class InvalidFlowError(FlowError):
    """Raised when the specified flow_id does not exist."""

    def __init__(self, flow_id: str) -> None:
        super().__init__(f"Flow {flow_id} does not exist")
