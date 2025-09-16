"""
Retry utilities with exponential backoff for handling transient failures.
"""

import asyncio
import logging
import random
import sqlite3
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

import aiohttp
import httpx
import requests

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""

    def __init__(self, message: str, last_exception: Exception | None = None):
        super().__init__(message)
        self.last_exception = last_exception


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""

    max_attempts: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    exceptions: tuple[type[Exception], ...] = (Exception,)


@dataclass
class RetryRuntime:
    """Runtime parameters bound for a specific retry decorator instance."""

    config: RetryConfig
    logger: logging.Logger


def _compute_delay(
    base: float,
    exp_base: float,
    attempt: int,
    max_d: float,
    *,
    add_jitter: bool,
) -> float:
    delay = min(base * (exp_base**attempt), max_d)
    if add_jitter:
        delay *= 0.5 + random.random()
    return delay


def _log_retry(
    runtime: RetryRuntime,
    fn_name: str,
    attempt: int,
    err: Exception,
    delay: float,
) -> None:
    log = runtime.logger
    log.warning(
        "Retry attempt %d/%d for %s after %s: %s. Retrying in %.2f s...",
        attempt + 1,
        runtime.config.max_attempts,
        fn_name,
        type(err).__name__,
        err,
        delay,
    )


async def _run_with_retries_async(
    func: Callable,
    args: tuple,
    kwargs: dict,
    runtime: RetryRuntime,
) -> Any:
    last_exception: Exception | None = None
    for attempt in range(runtime.config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except runtime.config.exceptions as e:  # type: ignore[misc]
            last_exception = e
            if attempt == runtime.config.max_attempts - 1:
                break
            delay = _compute_delay(
                runtime.config.base_delay,
                runtime.config.exponential_base,
                attempt,
                runtime.config.max_delay,
                add_jitter=runtime.config.jitter,
            )
            _log_retry(runtime, func.__name__, attempt, e, delay)
            await asyncio.sleep(delay)
    msg = (
        f"Function {func.__name__} failed after {runtime.config.max_attempts} attempts"
    )
    raise RetryError(msg, last_exception) from last_exception


def _run_with_retries_sync(
    func: Callable,
    args: tuple,
    kwargs: dict,
    runtime: RetryRuntime,
) -> Any:
    last_exception: Exception | None = None
    for attempt in range(runtime.config.max_attempts):
        try:
            return func(*args, **kwargs)
        except runtime.config.exceptions as e:  # type: ignore[misc]
            last_exception = e
            if attempt == runtime.config.max_attempts - 1:
                break
            delay = _compute_delay(
                runtime.config.base_delay,
                runtime.config.exponential_base,
                attempt,
                runtime.config.max_delay,
                add_jitter=runtime.config.jitter,
            )
            _log_retry(runtime, func.__name__, attempt, e, delay)
            time.sleep(delay)
    msg = (
        f"Function {func.__name__} failed after {runtime.config.max_attempts} attempts"
    )
    raise RetryError(msg, last_exception)


def retry(
    config: RetryConfig | None = None,
    logger: logging.Logger | None = None,
) -> Callable:
    """
    Decorator that implements retry logic with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts (including the first attempt)
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries in seconds
        exponential_base: Base for exponential backoff calculation
        jitter: Whether to add random jitter to delays
        exceptions: Tuple of exception types to catch and retry on
        logger: Logger instance for retry messages

    Returns:
        Decorated function with retry logic
    """
    if config is None:
        config = RetryConfig()
    if logger is None:
        logger = logging.getLogger(__name__)
    runtime = RetryRuntime(config=config, logger=logger)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            return await _run_with_retries_async(func, args, kwargs, runtime)

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            return _run_with_retries_sync(func, args, kwargs, runtime)

        # Return appropriate wrapper based on function type
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


def retry_db_operation(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0,
) -> Callable:
    """
    Specialized retry decorator for database operations.

    Args:
        max_attempts: Maximum retry attempts for DB operations
        base_delay: Base delay for DB retries (shorter for local DB)
        max_delay: Maximum delay for DB retries

    Returns:
        Decorator for database operations
    """

    return retry(
        RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            exceptions=(
                sqlite3.Error,
                sqlite3.OperationalError,
                sqlite3.DatabaseError,
            ),
            logger=logging.getLogger(__name__),
        ),
    )


def retry_network_operation(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
) -> Callable:
    """
    Specialized retry decorator for network operations (API calls, etc.).

    Args:
        max_attempts: Maximum retry attempts for network operations
        base_delay: Base delay for network retries
        max_delay: Maximum delay for network retries

    Returns:
        Decorator for network operations
    """

    return retry(
        RetryConfig(
            max_attempts=max_attempts,
            base_delay=base_delay,
            max_delay=max_delay,
            exceptions=(
                aiohttp.ClientError,
                aiohttp.ClientConnectionError,
                requests.RequestException,
                httpx.RequestError,
                httpx.ConnectError,
                httpx.HTTPStatusError,
                ConnectionError,
                TimeoutError,
            ),
            logger=logging.getLogger(__name__),
        ),
    )
