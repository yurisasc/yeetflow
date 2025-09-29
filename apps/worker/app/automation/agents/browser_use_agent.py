"""Browser-use based agent implementation.

This agent connects to a Steel.dev managed browser via WebSocket (CDP URL)
when available and exposes first-principles primitives.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from browser_use import Browser

from .base import BrowserAgent

logger = logging.getLogger(__name__)


class BrowserUseAgent(BrowserAgent):
    """browser-use implementation of BrowserAgent."""

    def __init__(self, cdp_ws_url: str):
        self.cdp_ws_url = cdp_ws_url
        self._browser = None
        self._page = None

    async def start(self) -> None:
        try:
            # Connect to remote browser via CDP URL
            self._browser = Browser(cdp_url=self.cdp_ws_url)
            await self._browser.start()

            # Get the current page or create one
            pages = await self._browser.get_pages()
            if pages:
                self._page = pages[0]  # Use existing page
            else:
                self._page = await self._browser.new_page()

            logger.info("Initialized BrowserUseAgent connected to %s", self.cdp_ws_url)
        except Exception:
            logger.exception("Failed to initialize BrowserUseAgent")
            raise

    async def stop(self) -> None:
        try:
            if self._browser:
                await self._browser.stop()
        except Exception:
            logger.exception("Error closing BrowserUseAgent")

    async def open_url(self, url: str) -> None:
        if not self._page:
            logger.warning("BrowserUseAgent not started; open_url noop")
            return
        try:
            await self._page.goto(url)
        except Exception:
            logger.exception("browser-use open_url failed")
            raise

    async def click(self, selector: str) -> None:
        if not self._page:
            logger.warning("BrowserUseAgent not started; click noop")
            return
        try:
            elements = await self._page.get_elements_by_css_selector(selector)
            if elements:
                await elements[0].click()
            else:
                self._raise_element_not_found(selector)
        except Exception:
            logger.exception("browser-use click failed")
            raise

    async def type(self, selector: str, text: str, *, clear: bool = False) -> None:
        if not self._page:
            logger.warning("BrowserUseAgent not started; type noop")
            return
        try:
            elements = await self._page.get_elements_by_css_selector(selector)
            if elements:
                await elements[0].fill(text, clear_existing=clear)
            else:
                self._raise_element_not_found(selector)
        except Exception:
            logger.exception("browser-use type failed")
            raise

    async def wait_for(self, selector: str, timeout_ms: int = 10000) -> None:
        if not self._page:
            logger.warning("BrowserUseAgent not started; wait_for noop")
            return
        try:
            # Wait for element to appear by repeatedly checking
            start_time = asyncio.get_event_loop().time()
            while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout_ms:
                elements = await self._page.get_elements_by_css_selector(selector)
                if elements:
                    return
                await asyncio.sleep(0.1)
            self._raise_timeout_error(selector, timeout_ms)
        except Exception:
            logger.exception("browser-use wait_for failed")
            raise

    async def extract(self, selector: str, attr: str | None = None) -> Any:
        if not self._page:
            logger.warning("BrowserUseAgent not started; extract noop")
            return None
        try:
            elements = await self._page.get_elements_by_css_selector(selector)
            if not elements:
                return None

            element = elements[0]
            if attr:
                return await element.get_attribute(attr)
            # Get text content - this might need adjustment based on browser-use API
            info = await element.get_basic_info()
            return info.get("text_content", "")
        except Exception:
            logger.exception("browser-use extract failed")
            raise

    def _raise_element_not_found(self, selector: str) -> None:
        """Raise ValueError for element not found."""
        msg = f"Element not found: {selector}"
        raise ValueError(msg)

    def _raise_timeout_error(self, selector: str, timeout_ms: int) -> None:
        """Raise TimeoutError for element wait timeout."""
        msg = f"Element not found within {timeout_ms}ms: {selector}"
        raise TimeoutError(msg)

    async def screenshot(self, name: str) -> str:
        if not self._page:
            logger.warning("BrowserUseAgent not started; screenshot noop")
            return f"browser_use_screenshot_{name}"
        try:
            path = await self._page.screenshot()
            # In future, store artifact and return a reference/URI
            return str(path)
        except Exception:
            logger.exception("browser-use screenshot failed")
            raise


def create_browser_use_agent(websocket_url: str | None) -> BrowserAgent | None:
    """Factory to create a BrowserUseAgent if possible.

    Returns None if browser_use is not installed or websocket_url is missing.
    """
    if not websocket_url:
        return None
    return BrowserUseAgent(cdp_ws_url=websocket_url)
