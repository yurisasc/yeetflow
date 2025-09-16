"""
Retry utilities with exponential backoff for handling transient failures.
"""
import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Optional, Type
import random

logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Exception raised when all retry attempts are exhausted."""
    
    def __init__(self, message: str, last_exception: Exception = None):
        super().__init__(message)
        self.last_exception = last_exception


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    jitter: bool = True,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    logger: Optional[logging.Logger] = None
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
    if logger is None:
        logger = logging.getLogger(__name__)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, don't retry
                        break
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if jitter:
                        # Add jitter to prevent thundering herd
                        delay *= (0.5 + random.random())
                    
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_attempts} for {func.__name__} "
                        f"after {type(e).__name__}: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    await asyncio.sleep(delay)
            
            # All attempts exhausted
            raise RetryError(
                f"Function {func.__name__} failed after {max_attempts} attempts",
                last_exception
            )
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            last_exception = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts - 1:
                        # Last attempt, don't retry
                        break
                    
                    # Calculate delay with exponential backoff and jitter
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay
                    )
                    
                    if jitter:
                        delay *= (0.5 + random.random())
                    
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_attempts} for {func.__name__} "
                        f"after {type(e).__name__}: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    
                    # For sync functions, use asyncio.sleep if in async context
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            # We're in an async context, use async sleep
                            import threading
                            import time
                            time.sleep(delay)
                        else:
                            # Not in async context, use regular sleep
                            time.sleep(delay)
                    except RuntimeError:
                        # No event loop, use regular sleep
                        import time
                        time.sleep(delay)
            
            # All attempts exhausted
            raise RetryError(
                f"Function {func.__name__} failed after {max_attempts} attempts",
                last_exception
            )
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def retry_db_operation(
    max_attempts: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 5.0
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
    import sqlite3
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=(sqlite3.Error, sqlite3.OperationalError, sqlite3.DatabaseError),
        logger=logging.getLogger(__name__)
    )


def retry_network_operation(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 30.0
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
    import aiohttp
    import requests
    return retry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        exceptions=(
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            requests.RequestException,
            ConnectionError,
            TimeoutError
        ),
        logger=logging.getLogger(__name__)
    )
