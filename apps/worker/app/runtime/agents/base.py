"""Browser agent interface protocol."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class BrowserAgentProtocol(Protocol):
    """Protocol for browser automation agents."""

    async def start(self) -> None:
        """Initialize any resources for the agent before use."""

    async def stop(self) -> None:
        """Dispose of resources (close connections)."""

    async def open_url(self, url: str) -> None:
        """Open a URL in the current page."""

    async def click(self, selector: str) -> None:
        """Click an element located by CSS selector."""

    async def type(self, selector: str, text: str, *, clear: bool = False) -> None:
        """Type into an input located by CSS selector."""

    async def wait_for(self, selector: str, *, timeout_ms: int = 10000) -> None:
        """Wait for an element to appear/be ready."""

    async def extract(self, selector: str, *, attr: str | None = None) -> Any:
        """Extract textContent or attribute from an element."""

    async def screenshot(self, name: str) -> str:
        """Take a screenshot and return an artifact reference/path."""
