"""Default configuration values for the Shopify Partners SDK."""

from typing import Final

# API Configuration
DEFAULT_API_VERSION: Final[str] = "2025-04"
DEFAULT_BASE_URL: Final[str] = "https://partners.shopify.com"
DEFAULT_GRAPHQL_PATH: Final[str] = "api/{version}/graphql.json"

# Rate Limiting
DEFAULT_RATE_LIMIT_PER_SECOND: Final[float] = 4.0
DEFAULT_MAX_RETRY_ATTEMPTS: Final[int] = 3
DEFAULT_RETRY_BASE_DELAY: Final[float] = 1.0
DEFAULT_RETRY_MAX_DELAY: Final[float] = 60.0
DEFAULT_RETRY_BACKOFF_FACTOR: Final[float] = 2.0

# HTTP Client
DEFAULT_TIMEOUT_SECONDS: Final[float] = 30.0
DEFAULT_MAX_CONNECTIONS: Final[int] = 10
DEFAULT_MAX_KEEPALIVE_CONNECTIONS: Final[int] = 5

# Pagination
DEFAULT_PAGE_SIZE: Final[int] = 50
DEFAULT_MAX_PAGE_SIZE: Final[int] = 250

# Logging
DEFAULT_LOG_LEVEL: Final[str] = "INFO"

# Headers
USER_AGENT: Final[str] = "shopify-partners-sdk-python"
ACCESS_TOKEN_HEADER: Final[str] = "X-Shopify-Access-Token"
CONTENT_TYPE_HEADER: Final[str] = "application/json"
