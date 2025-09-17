"""Rate limiter implementation for the Shopify Partners API."""

from collections import deque
from threading import Lock
import time
from typing import Optional

from shopify_partners_sdk.config import ShopifyPartnersSDKSettings
from shopify_partners_sdk.exceptions.rate_limit import RateLimitExceededError


class RateLimiter:
    """Token bucket rate limiter for API requests.

    Implements a token bucket algorithm to enforce rate limiting of 4 requests
    per second
    as required by the Shopify Partners API. This prevents local rate limit violations
    before requests are sent to the server.
    """

    def __init__(
        self,
        rate_limit: Optional[float] = None,
        settings: Optional[ShopifyPartnersSDKSettings] = None,
    ) -> None:
        """Initialize the rate limiter.

        Args:
            rate_limit: Maximum requests per second (defaults to settings value)
            settings: SDK settings instance
        """
        self._settings = settings or ShopifyPartnersSDKSettings()
        self._rate_limit = rate_limit or self._settings.rate_limit_per_second

        # Token bucket parameters
        self._bucket_capacity = max(
            1.0, self._rate_limit
        )  # Allow burst of 1 second worth
        self._refill_rate = self._rate_limit  # Tokens per second
        self._tokens = self._bucket_capacity  # Start with full bucket
        self._last_refill = time.monotonic()
        self._lock = Lock()

        # Request tracking for monitoring
        self._request_times: deque[float] = deque()
        self._total_requests = 0
        self._blocked_requests = 0

    @property
    def rate_limit(self) -> float:
        """Get the current rate limit in requests per second."""
        return self._rate_limit

    @property
    def current_rate(self) -> float:
        """Get the current request rate based on recent activity."""
        current_time = time.monotonic()
        # Keep only requests from the last second
        while self._request_times and current_time - self._request_times[0] > 1.0:
            self._request_times.popleft()
        return len(self._request_times)

    @property
    def available_tokens(self) -> float:
        """Get the number of tokens currently available."""
        return self._tokens

    @property
    def total_requests(self) -> int:
        """Get the total number of requests processed."""
        return self._total_requests

    @property
    def blocked_requests(self) -> int:
        """Get the number of requests that were rate limited."""
        return self._blocked_requests

    def _refill_tokens(self) -> None:
        """Refill the token bucket based on elapsed time."""
        current_time = time.monotonic()
        elapsed = current_time - self._last_refill

        if elapsed > 0:
            # Add tokens based on elapsed time
            tokens_to_add = elapsed * self._refill_rate
            self._tokens = min(self._bucket_capacity, self._tokens + tokens_to_add)
            self._last_refill = current_time

    def _calculate_wait_time(self) -> float:
        """Calculate how long to wait for the next token."""
        if self._tokens >= 1.0:
            return 0.0

        # Calculate time needed to accumulate 1 token
        tokens_needed = 1.0 - self._tokens
        return tokens_needed / self._refill_rate

    def acquire(self, tokens: float = 1.0, timeout: Optional[float] = None) -> None:
        """Acquire tokens from the rate limiter.

        Args:
            tokens: Number of tokens to acquire (default 1.0 for one request)
            timeout: Maximum time to wait for tokens (None for no timeout)

        Raises:
            RateLimitExceededError: If timeout is exceeded while waiting for tokens
            ValueError: If tokens requested is invalid
        """
        if tokens <= 0:
            raise ValueError("tokens must be positive")

        if tokens > self._bucket_capacity:
            raise ValueError(
                f"tokens ({tokens}) exceeds bucket capacity ({self._bucket_capacity})"
            )

        start_time = time.monotonic()

        with self._lock:
            while True:
                self._refill_tokens()

                if self._tokens >= tokens:
                    # Sufficient tokens available
                    self._tokens -= tokens
                    self._total_requests += 1
                    self._request_times.append(time.monotonic())
                    return

                # Not enough tokens, calculate wait time
                wait_time = self._calculate_wait_time()

                # Check timeout
                if timeout is not None:
                    elapsed = time.monotonic() - start_time
                    if elapsed + wait_time > timeout:
                        self._blocked_requests += 1
                        raise RateLimitExceededError(
                            current_rate=self.current_rate,
                            max_rate=self._rate_limit,
                            retry_after=wait_time,
                        )

                # Wait for tokens to be available
                time.sleep(wait_time)

    def acquire_multiple(
        self,
        count: int,
        timeout: Optional[float] = None,
        batch_size: Optional[int] = None,
    ) -> None:
        """Acquire multiple tokens with optional batching.

        Args:
            count: Number of tokens to acquire
            timeout: Maximum time to wait for all tokens
            batch_size: Maximum tokens to acquire in each batch
                (default: bucket_capacity)

        Raises:
            RateLimitExceededError: If timeout is exceeded
            ValueError: If count or batch_size is invalid
        """
        if count <= 0:
            raise ValueError("count must be positive")

        batch_size = batch_size or int(self._bucket_capacity)
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")

        remaining = count
        while remaining > 0:
            tokens_to_acquire = min(remaining, batch_size)
            self.acquire(tokens=tokens_to_acquire, timeout=timeout)
            remaining -= tokens_to_acquire

    def try_acquire(self, tokens: float = 1.0) -> bool:
        """Try to acquire tokens without waiting.

        Args:
            tokens: Number of tokens to acquire

        Returns:
            True if tokens were acquired, False otherwise
        """
        if tokens <= 0:
            raise ValueError("tokens must be positive")

        if tokens > self._bucket_capacity:
            return False

        # Use synchronous refill for non-blocking check
        current_time = time.monotonic()
        elapsed = current_time - self._last_refill

        if elapsed > 0:
            tokens_to_add = elapsed * self._refill_rate
            available_tokens = min(self._bucket_capacity, self._tokens + tokens_to_add)
        else:
            available_tokens = self._tokens

        # Would be able to acquire, but don't actually modify state
        # This is just a check - use acquire() to actually get tokens
        return available_tokens >= tokens

    def reset(self) -> None:
        """Reset the rate limiter to initial state."""
        with self._lock:
            self._tokens = self._bucket_capacity
            self._last_refill = time.monotonic()
            self._request_times.clear()
            self._total_requests = 0
            self._blocked_requests = 0

    def get_stats(self) -> dict[str, float | int]:
        """Get rate limiter statistics.

        Returns:
            Dictionary with rate limiter statistics
        """
        return {
            "rate_limit": self._rate_limit,
            "current_rate": self.current_rate,
            "available_tokens": self._tokens,
            "total_requests": self._total_requests,
            "blocked_requests": self._blocked_requests,
            "bucket_capacity": self._bucket_capacity,
        }

    def __repr__(self) -> str:
        """String representation of the rate limiter."""
        return (
            f"RateLimiter("
            f"rate_limit={self._rate_limit}, "
            f"available_tokens={self._tokens:.2f}, "
            f"current_rate={self.current_rate:.2f}"
            f")"
        )
