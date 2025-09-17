"""Authentication-related exceptions for the Shopify Partners SDK."""

from .base import ShopifyPartnersSDKError


class AuthenticationError(ShopifyPartnersSDKError):
    """Exception raised for authentication-related errors.

    This includes missing credentials, invalid tokens, organization ID issues, etc.
    """


class AccessTokenError(AuthenticationError):
    """Exception raised for access token-related errors."""

    def __init__(self, message: str = "Invalid or missing access token") -> None:
        super().__init__(message)


class OrganizationIdError(AuthenticationError):
    """Exception raised for organization ID-related errors."""

    def __init__(self, message: str = "Invalid or missing organization ID") -> None:
        super().__init__(message)


class UnauthorizedError(AuthenticationError):
    """Exception raised when API returns 401 Unauthorized."""

    def __init__(self, message: str = "API request was not authorized") -> None:
        super().__init__(message)


class ForbiddenError(AuthenticationError):
    """Exception raised when API returns 403 Forbidden."""

    def __init__(
        self, message: str = "API request was forbidden - insufficient permissions"
    ) -> None:
        super().__init__(message)
