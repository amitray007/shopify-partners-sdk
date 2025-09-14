"""Exception classes for the Shopify Partners SDK."""

from .auth import (
    AccessTokenError,
    AuthenticationError,
    ForbiddenError,
    OrganizationIdError,
    UnauthorizedError,
)
from .base import ShopifyPartnersSDKError
from .graphql import (
    GraphQLError,
    GraphQLExecutionError,
    GraphQLMultipleErrors,
    GraphQLResponseError,
    GraphQLSyntaxError,
    GraphQLValidationError,
)
from .rate_limit import (
    RateLimitError,
    RateLimitExceededError,
    RateLimitServerError,
)
from .validation import (
    InvalidCursorError,
    InvalidDateRangeError,
    InvalidGlobalIdError,
    InvalidPageSizeError,
    ValidationError,
)

__all__ = [
    # Base
    "ShopifyPartnersSDKError",
    # Authentication
    "AuthenticationError",
    "AccessTokenError",
    "OrganizationIdError",
    "UnauthorizedError",
    "ForbiddenError",
    # GraphQL
    "GraphQLError",
    "GraphQLValidationError",
    "GraphQLSyntaxError",
    "GraphQLExecutionError",
    "GraphQLResponseError",
    "GraphQLMultipleErrors",
    # Rate Limiting
    "RateLimitError",
    "RateLimitExceededError",
    "RateLimitServerError",
    # Validation
    "ValidationError",
    "InvalidGlobalIdError",
    "InvalidPageSizeError",
    "InvalidCursorError",
    "InvalidDateRangeError",
]
