"""Abstract browser automation agent interface."""

from __future__ import annotations

import abc
from typing import Any


class BrowserAgent(abc.ABC):
    """Abstract agent for browser automation primitives."""

    @abc.abstractmethod
    async def start(self) -> None:
        """Initialize any resources for the agent before use."""

    @abc.abstractmethod
    async def stop(self) -> None:
        """Dispose of resources (close connections)."""

    # Primitives
    @abc.abstractmethod
    async def open_url(self, url: str) -> None:
        """Open a URL in the current page."""

    @abc.abstractmethod
    async def click(self, selector: str) -> None:
        """Click an element located by CSS selector."""

    @abc.abstractmethod
    async def type(self, selector: str, text: str, *, clear: bool = False) -> None:
        """Type into an input located by CSS selector."""

    @abc.abstractmethod
    async def wait_for(self, selector: str, timeout_ms: int = 10000) -> None:
        """Wait for an element to appear/be ready."""

    @abc.abstractmethod
    async def extract(self, selector: str, attr: str | None = None) -> Any:
        """Extract textContent or attribute from an element."""

    @abc.abstractmethod
    async def screenshot(self, name: str) -> str:
        """Take a screenshot and return an artifact reference/path."""
