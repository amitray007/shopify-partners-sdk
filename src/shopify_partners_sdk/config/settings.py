"""Configuration settings for the Shopify Partners SDK using Pydantic."""

from typing import Self

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from shopify_partners_sdk.schema import SUPPORTED_API_VERSIONS
from shopify_partners_sdk.version import __version__

from .defaults import (
    DEFAULT_API_VERSION,
    DEFAULT_BASE_URL,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MAX_CONNECTIONS,
    DEFAULT_MAX_KEEPALIVE_CONNECTIONS,
    DEFAULT_MAX_PAGE_SIZE,
    DEFAULT_MAX_RETRY_ATTEMPTS,
    DEFAULT_PAGE_SIZE,
    DEFAULT_RATE_LIMIT_PER_SECOND,
    DEFAULT_RETRY_BACKOFF_FACTOR,
    DEFAULT_RETRY_BASE_DELAY,
    DEFAULT_RETRY_MAX_DELAY,
    DEFAULT_TIMEOUT_SECONDS,
    USER_AGENT,
)


class ShopifyPartnersSDKSettings(BaseSettings):
    """Configuration settings for the Shopify Partners SDK.

    Settings can be configured via environment variables with the prefix
    SHOPIFY_PARTNERS_.
    For example: SHOPIFY_PARTNERS_API_VERSION=2026-10. Values passed to the
    constructor take precedence over the environment and a local ``.env`` file.
    """

    model_config = SettingsConfigDict(
        env_prefix="SHOPIFY_PARTNERS_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # API Configuration
    api_version: str = Field(
        default=DEFAULT_API_VERSION,
        description="Shopify Partners API version to use",
    )
    base_url: str = Field(
        default=DEFAULT_BASE_URL,
        description="Base URL for the Shopify Partners API",
    )

    # Authentication (typically set programmatically, not via env vars)
    organization_id: int | None = Field(
        default=None,
        description="Shopify Partners organization ID",
    )
    access_token: str | None = Field(
        default=None,
        description="Shopify Partners API access token",
    )

    # Rate Limiting
    rate_limit_per_second: float = Field(
        default=DEFAULT_RATE_LIMIT_PER_SECOND,
        ge=0.1,
        le=10.0,
        description="Maximum requests per second (4.0 is Shopify's limit)",
    )
    max_retry_attempts: int = Field(
        default=DEFAULT_MAX_RETRY_ATTEMPTS,
        ge=0,
        le=10,
        description="Maximum number of retry attempts for failed requests",
    )
    retry_base_delay: float = Field(
        default=DEFAULT_RETRY_BASE_DELAY,
        ge=0.1,
        le=10.0,
        description="Base delay in seconds for exponential backoff",
    )
    retry_max_delay: float = Field(
        default=DEFAULT_RETRY_MAX_DELAY,
        ge=1.0,
        le=300.0,
        description="Maximum delay in seconds for exponential backoff",
    )
    retry_backoff_factor: float = Field(
        default=DEFAULT_RETRY_BACKOFF_FACTOR,
        ge=1.0,
        le=5.0,
        description="Backoff factor for exponential backoff",
    )

    # HTTP Client
    timeout_seconds: float = Field(
        default=DEFAULT_TIMEOUT_SECONDS,
        ge=5.0,
        le=300.0,
        description="Request timeout in seconds",
    )
    max_connections: int = Field(
        default=DEFAULT_MAX_CONNECTIONS,
        ge=1,
        le=100,
        description="Maximum number of HTTP connections",
    )
    max_keepalive_connections: int = Field(
        default=DEFAULT_MAX_KEEPALIVE_CONNECTIONS,
        ge=1,
        le=50,
        description="Maximum number of keep-alive connections",
    )

    # Pagination
    default_page_size: int = Field(
        default=DEFAULT_PAGE_SIZE,
        ge=1,
        le=DEFAULT_MAX_PAGE_SIZE,
        description="Default page size for paginated queries",
    )
    max_page_size: int = Field(
        default=DEFAULT_MAX_PAGE_SIZE,
        ge=1,
        le=1000,
        description="Maximum allowed page size",
    )

    # Logging
    log_level: str = Field(
        default=DEFAULT_LOG_LEVEL,
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)",
    )

    @field_validator("api_version")
    @classmethod
    def validate_api_version(cls, v: str) -> str:
        """Accept only versions Shopify supports and the SDK bundles a schema for."""
        if v not in SUPPORTED_API_VERSIONS:
            raise ValueError(
                f"api_version must be one of: {', '.join(SUPPORTED_API_VERSIONS)}"
            )
        return v

    @field_validator("organization_id")
    @classmethod
    def validate_organization_id(cls, v: int | None) -> int | None:
        """Validate organization ID format."""
        if v is not None and v <= 0:
            raise ValueError("organization_id must be a positive integer")
        return v

    @field_validator("access_token")
    @classmethod
    def validate_access_token(cls, v: str | None) -> str | None:
        """Validate access token format."""
        if v is not None and not v.startswith("prtapi_"):
            raise ValueError("access_token must start with 'prtapi_'")
        return v

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"log_level must be one of: {valid_levels}")
        return v_upper

    @model_validator(mode="after")
    def validate_limits(self) -> Self:
        """Check limits that depend on each other."""
        if self.max_keepalive_connections > self.max_connections:
            raise ValueError("max_keepalive_connections cannot exceed max_connections")
        if self.default_page_size > self.max_page_size:
            raise ValueError("default_page_size cannot exceed max_page_size")
        return self

    def get_api_endpoint(self) -> str:
        """Get the full GraphQL API endpoint URL."""
        if not self.organization_id:
            raise ValueError("organization_id is required to build API endpoint")

        return f"{self.base_url}/{self.organization_id}/api/{self.api_version}/graphql.json"

    def get_headers(self) -> dict[str, str]:
        """Get default HTTP headers for API requests."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"{USER_AGENT}/{__version__}",
        }

        if self.access_token:
            headers["X-Shopify-Access-Token"] = self.access_token

        return headers
