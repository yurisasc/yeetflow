"""No-op browser agent for development and testing."""

from __future__ import annotations

import logging
from typing import Any

from app.runtime.agents.base import BrowserAgentProtocol

logger = logging.getLogger(__name__)


class NoopAgent(BrowserAgentProtocol):
    """No-op implementation of BrowserAgent."""

    async def start(self) -> None:
        logger.info("NoopAgent started")

    async def stop(self) -> None:
        logger.info("NoopAgent stopped")

    async def open_url(self, url: str) -> None:
        logger.info("noop open_url: %s", url)

    async def click(self, selector: str) -> None:
        logger.info("noop click: %s", selector)

    async def type(self, selector: str, text: str, *, clear: bool = False) -> None:
        logger.info(
            "noop type: selector=%s text_len=%d clear=%s",
            selector,
            len(text),
            clear,
        )

    async def wait_for(self, selector: str, *, timeout_ms: int = 10000) -> None:
        logger.info("noop wait_for: %s (timeout=%sms)", selector, timeout_ms)

    async def extract(self, selector: str, *, attr: str | None = None) -> Any:
        logger.info("noop extract: selector=%s attr=%s", selector, attr)
        # Return placeholder value
        return None

    async def screenshot(self, name: str) -> str:
        ref = f"noop_screenshot_{name}"
        logger.info("noop screenshot: %s -> %s", name, ref)
        return ref
