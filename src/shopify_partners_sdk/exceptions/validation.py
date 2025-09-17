"""Validation exceptions for the Shopify Partners SDK."""

from .base import ShopifyPartnersSDKError


class ValidationError(ShopifyPartnersSDKError):
    """Exception raised for validation errors."""


class InvalidGlobalIdError(ValidationError):
    """Exception raised for invalid Global ID format."""

    def __init__(self, global_id: str) -> None:
        """Initialize the invalid global ID error.

        Args:
            global_id: The invalid global ID
        """
        message = f"Invalid Global ID format: {global_id}"
        details = {"global_id": global_id}
        super().__init__(message, details)
        self.global_id = global_id


class InvalidPageSizeError(ValidationError):
    """Exception raised for invalid page size values."""

    def __init__(self, page_size: int, max_size: int) -> None:
        """Initialize the invalid page size error.

        Args:
            page_size: The invalid page size
            max_size: Maximum allowed page size
        """
        message = f"Invalid page size: {page_size} (max: {max_size})"
        details = {"page_size": page_size, "max_size": max_size}
        super().__init__(message, details)
        self.page_size = page_size
        self.max_size = max_size


class InvalidCursorError(ValidationError):
    """Exception raised for invalid cursor values."""

    def __init__(self, cursor: str) -> None:
        """Initialize the invalid cursor error.

        Args:
            cursor: The invalid cursor
        """
        message = f"Invalid cursor format: {cursor}"
        details = {"cursor": cursor}
        super().__init__(message, details)
        self.cursor = cursor


class InvalidDateRangeError(ValidationError):
    """Exception raised for invalid date ranges."""

    def __init__(self, start_date: str, end_date: str) -> None:
        """Initialize the invalid date range error.

        Args:
            start_date: Start date
            end_date: End date
        """
        message = f"Invalid date range: {start_date} to {end_date}"
        details = {"start_date": start_date, "end_date": end_date}
        super().__init__(message, details)
        self.start_date = start_date
        self.end_date = end_date
