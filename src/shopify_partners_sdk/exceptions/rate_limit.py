"""Rate limiting exceptions for the Shopify Partners SDK."""

from .base import ShopifyPartnersSDKError


class RateLimitError(ShopifyPartnersSDKError):
    """Exception raised when API rate limits are exceeded."""

    def __init__(
        self,
        message: str = "API rate limit exceeded",
        retry_after: float | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the rate limit error.

        Args:
            message: Error message
            retry_after: Seconds to wait before retrying (if known)
            details: Additional error details
        """
        super().__init__(message, details)
        self.retry_after = retry_after

    def __str__(self) -> str:
        """String representation of the error."""
        base_msg = super().__str__()
        if self.retry_after:
            return f"{base_msg}. Retry after {self.retry_after} seconds."
        return base_msg


class RateLimitExceededError(RateLimitError):
    """Exception raised when the configured rate limit is exceeded locally."""

    def __init__(
        self,
        current_rate: float,
        max_rate: float,
        retry_after: float | None = None,
    ) -> None:
        """Initialize the rate limit exceeded error.

        Args:
            current_rate: Current request rate
            max_rate: Maximum allowed request rate
            retry_after: Seconds to wait before retrying
        """
        message = (
            f"Rate limit exceeded: {current_rate:.2f} req/s > {max_rate:.2f} req/s"
        )
        details = {
            "current_rate": current_rate,
            "max_rate": max_rate,
        }
        super().__init__(message, retry_after, details)
        self.current_rate = current_rate
        self.max_rate = max_rate


class RateLimitServerError(RateLimitError):
    """Exception raised when server returns HTTP 429 Too Many Requests."""

    def __init__(
        self,
        retry_after: float | None = None,
        details: dict | None = None,
    ) -> None:
        """Initialize the server rate limit error.

        Args:
            retry_after: Seconds to wait before retrying (from server)
            details: Additional error details from server response
        """
        message = "Server rate limit exceeded (HTTP 429)"
        super().__init__(message, retry_after, details)
