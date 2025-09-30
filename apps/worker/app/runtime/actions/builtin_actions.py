"""Built-in action commands and registration."""

import logging
from typing import Any

from app.runtime.actions import registry
from app.runtime.actions.base import ActionExecution, RequiresParam


class OpenUrlAction(RequiresParam):
    def __init__(self, params: dict[str, Any]):
        self.params = params

    async def execute(self, execution: ActionExecution) -> None:
        url = self.require(self.params, "url")
        await execution.agent.open_url(url)


class ClickAction(RequiresParam):
    def __init__(self, params: dict[str, Any]):
        self.params = params

    async def execute(self, execution: ActionExecution) -> None:
        selector = self.require(self.params, "selector")
        await execution.agent.click(selector)


class TypeAction(RequiresParam):
    def __init__(self, params: dict[str, Any]):
        self.params = params

    async def execute(self, execution: ActionExecution) -> None:
        selector = self.require(self.params, "selector")
        text = self.require(self.params, "text")
        clear = bool(self.params.get("clear", False))
        await execution.agent.type(selector, text, clear=clear)


class WaitForAction(RequiresParam):
    def __init__(self, params: dict[str, Any]):
        self.params = params

    async def execute(self, execution: ActionExecution) -> None:
        selector = self.require(self.params, "selector")
        timeout_ms = int(self.params.get("timeout_ms", 10000))
        await execution.agent.wait_for(selector, timeout_ms=timeout_ms)


class ExtractAction(RequiresParam):
    def __init__(self, params: dict[str, Any]):
        self.params = params

    async def execute(self, execution: ActionExecution) -> None:
        selector = self.require(self.params, "selector")
        attr = self.params.get("attr")
        var = self.params.get("var")
        value = await execution.agent.extract(selector, attr=attr)
        if var:
            execution.context.set_variable(var, value)


class ScreenshotAction:
    def __init__(self, params: dict[str, Any]):
        self.params = params

    async def execute(self, execution: ActionExecution) -> None:
        name = self.params.get("name") or "screenshot"
        ref = await execution.agent.screenshot(name)
        await execution.events.emit_screenshot_taken(execution.context, name, ref)


class LogAction:
    def __init__(self, params: dict[str, Any]):
        self.params = params

    async def execute(self, execution: ActionExecution) -> None:
        message = self.params.get("message", "")
        logging.getLogger(__name__).info(
            "Flow log: %s | Run: %s", message, execution.context.run_id
        )


# Register built-ins (including aliases)
registry.register("open_url", lambda p: OpenUrlAction(p))
registry.register("navigate", lambda p: OpenUrlAction(p))
registry.register("click", lambda p: ClickAction(p))
registry.register("type", lambda p: TypeAction(p))
registry.register("wait_for", lambda p: WaitForAction(p))
registry.register("extract", lambda p: ExtractAction(p))
registry.register("screenshot", lambda p: ScreenshotAction(p))
registry.register("log", lambda p: LogAction(p))
