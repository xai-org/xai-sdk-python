"""Retry utilities for resilient SDK operations.

Provides retry strategies and decorators for handling transient failures
in xAI SDK operations.
"""

import time
from typing import Callable, TypeVar, Any, Optional
from functools import wraps

T = TypeVar("T")


class RetryPolicy:
    """Configuration for retry behavior.
    
    Attributes:
        max_retries: Maximum number of retry attempts (default: 3).
        initial_delay: Initial delay in seconds before first retry (default: 0.1).
        max_delay: Maximum delay in seconds between retries (default: 10.0).
        exponential_base: Base for exponential backoff (default: 2.0).
    """

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 0.1,
        max_delay: float = 10.0,
        exponential_base: float = 2.0,
    ) -> None:
        """Initialize a retry policy.
        
        Args:
            max_retries: Maximum number of attempts.
            initial_delay: Initial delay before first retry.
            max_delay: Maximum delay between retries.
            exponential_base: Base for exponential backoff calculation.
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base

    def get_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number.
        
        Args:
            attempt: The attempt number (0-indexed).
            
        Returns:
            The delay in seconds.
        """
        delay = self.initial_delay * (self.exponential_base ** attempt)
        return min(delay, self.max_delay)


def retry(
    policy: Optional[RetryPolicy] = None,
    retryable_exceptions: tuple = (Exception,),
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Decorator to retry a function with exponential backoff.
    
    Args:
        policy: The retry policy to use (default: standard policy).
        retryable_exceptions: Exceptions that should trigger a retry.
        
    Returns:
        A decorator that adds retry logic to a function.
        
    Example:
        ```
        from xai_sdk.retry import retry
        
        @retry()
        def unstable_operation():
            # This will be retried up to 3 times if it raises an exception
            pass
        ```
    """
    if policy is None:
        policy = RetryPolicy()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            for attempt in range(policy.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    if attempt == policy.max_retries:
                        raise
                    delay = policy.get_delay(attempt)
                    time.sleep(delay)
            # Should never reach here
            raise RuntimeError("Unexpected retry logic error")

        return wrapper

    return decorator
