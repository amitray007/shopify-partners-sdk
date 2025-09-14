"""Base exception classes for the Shopify Partners SDK."""


class ShopifyPartnersSDKError(Exception):
    """Base exception for all Shopify Partners SDK errors."""

    def __init__(self, message: str, details: dict | None = None) -> None:
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        """String representation of the error."""
        if self.details:
            return f"{self.message}. Details: {self.details}"
        return self.message

    def __repr__(self) -> str:
        """Detailed representation of the error."""
        return f"{self.__class__.__name__}(message='{self.message}', details={self.details})"
