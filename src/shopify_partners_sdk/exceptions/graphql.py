"""GraphQL-related exceptions for the Shopify Partners SDK."""

from typing import Any

from .base import ShopifyPartnersSDKError


class GraphQLError(ShopifyPartnersSDKError):
    """Exception raised for GraphQL-related errors."""

    def __init__(
        self,
        message: str,
        locations: list[dict[str, int]] | None = None,
        path: list[str | int] | None = None,
        extensions: dict[str, Any] | None = None,
    ) -> None:
        """Initialize the GraphQL error.

        Args:
            message: Error message
            locations: List of locations in the GraphQL document
            path: Path to the field that caused the error
            extensions: Additional error information
        """
        details = {}
        if locations:
            details["locations"] = locations
        if path:
            details["path"] = path
        if extensions:
            details["extensions"] = extensions

        super().__init__(message, details)
        self.locations = locations
        self.path = path
        self.extensions = extensions


class GraphQLValidationError(GraphQLError):
    """Exception raised for GraphQL query validation errors."""


class GraphQLSyntaxError(GraphQLError):
    """Exception raised for GraphQL query syntax errors."""


class GraphQLExecutionError(GraphQLError):
    """Exception raised for GraphQL query execution errors."""


class GraphQLResponseError(ShopifyPartnersSDKError):
    """Exception raised when GraphQL response format is invalid."""

    def __init__(
        self,
        message: str = "Invalid GraphQL response format",
        response_data: Any = None,
    ) -> None:
        """Initialize the response error.

        Args:
            message: Error message
            response_data: The invalid response data
        """
        details = {"response_data": response_data} if response_data is not None else {}
        super().__init__(message, details)
        self.response_data = response_data


class GraphQLMultipleErrors(ShopifyPartnersSDKError):
    """Exception raised when multiple GraphQL errors occur."""

    def __init__(self, errors: list[GraphQLError]) -> None:
        """Initialize the multiple errors exception.

        Args:
            errors: List of GraphQL errors
        """
        if not errors:
            raise ValueError("errors list cannot be empty")

        message = f"Multiple GraphQL errors occurred ({len(errors)} errors)"
        details = {
            "error_count": len(errors),
            "errors": [
                {
                    "message": error.message,
                    "locations": error.locations,
                    "path": error.path,
                    "extensions": error.extensions,
                }
                for error in errors
            ],
        }
        super().__init__(message, details)
        self.errors = errors

    def __iter__(self):
        """Iterate over the errors."""
        return iter(self.errors)
