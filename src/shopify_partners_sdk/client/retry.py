"""Retry logic and backoff strategies for the Shopify Partners SDK."""

from collections.abc import Callable
from contextlib import suppress
import math
import random
import time
from typing import Any, TypeVar

import requests

from shopify_partners_sdk.config import ShopifyPartnersSDKSettings
from shopify_partners_sdk.exceptions.rate_limit import RateLimitServerError

T = TypeVar("T")


class ExponentialBackoff:
    """Exponential backoff strategy with jitter."""

    def __init__(
        self,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
    ) -> None:
        """Initialize the exponential backoff strategy.

        Args:
            base_delay: Base delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Multiplier for each retry
            jitter: Whether to add random jitter to delays
        """
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter

    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for a given attempt number.

        Args:
            attempt: Attempt number (0-based)

        Returns:
            Delay in seconds
        """
        delay = self.base_delay * (self.backoff_factor**attempt)
        delay = min(delay, self.max_delay)

        if self.jitter:
            # Add up to 25% jitter to prevent thundering herd
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)

        return max(0.0, delay)


class RetryHandler:
    """Handles retry logic for HTTP requests with various backoff strategies."""

    def __init__(
        self,
        max_attempts: int | None = None,
        backoff: ExponentialBackoff | None = None,
        settings: ShopifyPartnersSDKSettings | None = None,
    ) -> None:
        """Initialize the retry handler.

        Args:
            max_attempts: Maximum number of retries after the first call
                (0 means a single call; defaults to settings value)
            backoff: Backoff strategy (defaults to exponential backoff)
            settings: SDK settings instance
        """
        self._settings = settings or ShopifyPartnersSDKSettings()
        self.max_attempts = (
            max_attempts
            if max_attempts is not None
            else self._settings.max_retry_attempts
        )
        if self.max_attempts < 0:
            raise ValueError("max_attempts must not be negative")

        if backoff is None:
            backoff = ExponentialBackoff(
                base_delay=self._settings.retry_base_delay,
                max_delay=self._settings.retry_max_delay,
                backoff_factor=self._settings.retry_backoff_factor,
            )
        self.backoff = backoff

        self._total_attempts = 0
        self._successful_attempts = 0
        self._failed_attempts = 0

    @property
    def total_attempts(self) -> int:
        """Get total number of attempts made."""
        return self._total_attempts

    @property
    def successful_attempts(self) -> int:
        """Get number of successful attempts."""
        return self._successful_attempts

    @property
    def failed_attempts(self) -> int:
        """Get number of failed attempts."""
        return self._failed_attempts

    @property
    def success_rate(self) -> float:
        """Get success rate as a percentage."""
        if self._total_attempts == 0:
            return 0.0
        return (self._successful_attempts / self._total_attempts) * 100.0

    def should_retry(
        self, exception: Exception, attempt: int, idempotent: bool = True
    ) -> bool:
        """Determine if a request should be retried.

        Args:
            exception: The exception that occurred
            attempt: Current attempt number (0-based)
            idempotent: False for requests that must not run twice, such as
                mutations; those retry only when the server rejected them (429)

        Returns:
            True if the request should be retried
        """
        if attempt >= self.max_attempts:
            return False

        if not idempotent:
            return _is_rate_limited(exception)

        if isinstance(exception, RateLimitServerError):
            return True

        if isinstance(exception, requests.HTTPError):
            # No response: failure below HTTP, so retry as a network error.
            # Test `is None`, never truthiness: Response is falsy on 4xx/5xx.
            if exception.response is None:
                return True
            status = exception.response.status_code
            return status == 429 or 500 <= status < 600

        return isinstance(exception, (requests.ConnectionError, requests.Timeout))

    def get_retry_delay(self, exception: Exception, attempt: int) -> float:
        """Get the delay before retrying.

        Args:
            exception: The exception that occurred
            attempt: Current attempt number (0-based)

        Returns:
            Delay in seconds
        """
        server_delay = self._server_retry_after(exception)
        if server_delay is not None:
            return server_delay
        return self.backoff.calculate_delay(attempt)

    def _server_retry_after(self, exception: Exception) -> float | None:
        """Retry-After from the server, capped at the backoff maximum."""
        value: float | None = None
        if isinstance(exception, RateLimitServerError):
            value = exception.retry_after
        elif (
            isinstance(exception, requests.HTTPError)
            and exception.response is not None
            and exception.response.status_code == 429
        ):
            with suppress(TypeError, ValueError):
                value = float(exception.response.headers.get("retry-after", ""))
        if value is None or not math.isfinite(value) or value <= 0:
            return None
        return min(value, self.backoff.max_delay)

    def execute_with_retry(
        self,
        func: Callable[..., T],
        *args: Any,
        idempotent: bool = True,
        **kwargs: Any,
    ) -> T:
        """Execute a function with retry logic.

        Args:
            func: The function to execute
            *args: Positional arguments for the function
            idempotent: False when a repeated call could apply twice (mutations)
            **kwargs: Keyword arguments for the function

        Returns:
            The result of the function call

        Raises:
            The last exception if all retry attempts fail
        """
        last_exception: Exception | None = None

        for attempt in range(self.max_attempts + 1):
            self._total_attempts += 1

            try:
                result = func(*args, **kwargs)
                self._successful_attempts += 1
                return result

            except Exception as e:
                last_exception = e
                self._failed_attempts += 1

                if not self.should_retry(e, attempt, idempotent):
                    raise e

                if attempt < self.max_attempts:
                    delay = self.get_retry_delay(e, attempt)
                    if delay > 0:
                        time.sleep(delay)

        # This should never be reached, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Unexpected retry loop exit")

    def reset_stats(self) -> None:
        """Reset retry statistics."""
        self._total_attempts = 0
        self._successful_attempts = 0
        self._failed_attempts = 0

    def get_stats(self) -> dict[str, Any]:
        """Get retry handler statistics.

        Returns:
            Dictionary with retry statistics
        """
        return {
            "max_attempts": self.max_attempts,
            "total_attempts": self._total_attempts,
            "successful_attempts": self._successful_attempts,
            "failed_attempts": self._failed_attempts,
            "success_rate": self.success_rate,
            "backoff_base_delay": self.backoff.base_delay,
            "backoff_max_delay": self.backoff.max_delay,
            "backoff_factor": self.backoff.backoff_factor,
        }

    def __repr__(self) -> str:
        """String representation of the retry handler."""
        return (
            f"RetryHandler("
            f"max_attempts={self.max_attempts}, "
            f"success_rate={self.success_rate:.1f}%"
            f")"
        )


def _is_rate_limited(exception: Exception) -> bool:
    """True when the server refused the request (HTTP 429) without processing it."""
    if isinstance(exception, RateLimitServerError):
        return True
    return (
        isinstance(exception, requests.HTTPError)
        and exception.response is not None
        and exception.response.status_code == 429
    )
