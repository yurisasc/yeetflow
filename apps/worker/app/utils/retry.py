"""
Retry utilities with exponential backoff for handling transient failures.
"""

import asyncio
import logging
import random
import time
from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from http import HTTPStatus
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

HTTP_RETRY_STATUSES = {
    HTTPStatus.TOO_MANY_REQUESTS,  # 429
    HTTPStatus.REQUEST_TIMEOUT,  # 408
    HTTPStatus.INTERNAL_SERVER_ERROR,  # 500
    HTTPStatus.NOT_IMPLEMENTED,  # 501
    HTTPStatus.BAD_GATEWAY,  # 502
    HTTPStatus.SERVICE_UNAVAILABLE,  # 503
    HTTPStatus.GATEWAY_TIMEOUT,  # 504
    HTTPStatus.HTTP_VERSION_NOT_SUPPORTED,  # 505
}


def should_retry_http_response(response: httpx.Response) -> bool:
    """Check if an HTTP response should trigger a retry."""
    return response.status_code in HTTP_RETRY_STATUSES


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
    delay = base * (exp_base**attempt)
    if add_jitter:
        delay *= 0.5 + random.random()
    return min(delay, max_d)


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
        config: RetryConfig with attempts/delays/exceptions. If None, uses defaults.
        logger: Optional Logger for retry messages.

    Returns:
        A decorator that wraps sync/async functions with retry behavior.
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


def retry_network_operation() -> Callable:
    """
    Specialized retry decorator for network operations (API calls, etc.).
    Uses centralized configuration from settings.

    Returns:
        Decorator for network operations
    """
    return retry(
        RetryConfig(
            max_attempts=settings.retry_max_attempts,
            base_delay=settings.retry_base_delay,
            max_delay=settings.retry_max_delay,
            exceptions=(
                httpx.RequestError,
                httpx.ConnectError,
                httpx.HTTPStatusError,
                ConnectionError,
                TimeoutError,
            ),
        ),
        logger=logging.getLogger(__name__),
    )
