"""Input types for GraphQL mutations and queries."""

from typing import Optional

from pydantic import ConfigDict, Field, field_validator

from .base import ShopifyPartnersBaseModel
from .scalars import GlobalID, MoneyAmount


class MoneyInput(ShopifyPartnersBaseModel):
    """Input type for monetary amounts."""

    amount: MoneyAmount = Field(..., description="The monetary amount")
    currency_code: str = Field(
        ..., description="ISO 4217 currency code", alias="currencyCode"
    )

    @field_validator("currency_code")
    @classmethod
    def validate_currency_code(cls, v: str) -> str:
        """Validate currency code format."""
        if not isinstance(v, str) or len(v) != 3:
            raise ValueError("Currency code must be a 3-character string")
        return v.upper()

    model_config = ConfigDict(populate_by_name=True)


class AppCreditCreateInput(ShopifyPartnersBaseModel):
    """Input for creating an app credit."""

    app_id: GlobalID = Field(..., description="The app ID", alias="appId")
    shop_id: GlobalID = Field(..., description="The shop ID", alias="shopId")
    amount: MoneyInput = Field(..., description="Credit amount")
    description: str = Field(..., description="Credit description")
    test: Optional[bool] = Field(None, description="Whether this is a test transaction")

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        """Validate description length."""
        if not v or len(v) > 255:
            raise ValueError("Description must be between 1 and 255 characters")
        return v

    model_config = ConfigDict(populate_by_name=True)


class EventsinkCreateInput(ShopifyPartnersBaseModel):
    """Input for creating an eventsink (unstable API)."""

    app_id: GlobalID = Field(..., description="The app ID", alias="appId")
    topic: str = Field(..., description="Event topic")
    url: str = Field(..., description="Webhook URL")
    queue: Optional[str] = Field(None, description="Queue type")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate webhook URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL must be a valid HTTP or HTTPS URL")
        return v

    model_config = ConfigDict(populate_by_name=True)


class EventsinkDeleteInput(ShopifyPartnersBaseModel):
    """Input for deleting an eventsink (unstable API)."""

    id: GlobalID = Field(..., description="Eventsink ID")
    app_id: GlobalID = Field(..., description="The app ID", alias="appId")
    topic: str = Field(..., description="Event topic")

    model_config = ConfigDict(populate_by_name=True)


class PaginationInput(ShopifyPartnersBaseModel):
    """Input for pagination parameters."""

    first: Optional[int] = Field(
        None, ge=1, le=250, description="Returns the first n elements"
    )
    after: Optional[str] = Field(None, description="Returns elements after this cursor")
    last: Optional[int] = Field(
        None, ge=1, le=250, description="Returns the last n elements"
    )
    before: Optional[str] = Field(
        None, description="Returns elements before this cursor"
    )

    @field_validator("first", "last")
    @classmethod
    def validate_pagination_limit(cls, v: Optional[int]) -> Optional[int]:
        """Validate pagination limits."""
        if v is not None and (v < 1 or v > 250):
            raise ValueError("Pagination limit must be between 1 and 250")
        return v

    def validate_pagination_combination(self) -> None:
        """Validate pagination parameter combinations."""
        if self.first is not None and self.last is not None:
            raise ValueError("Cannot specify both 'first' and 'last'")
        if self.after is not None and self.before is not None:
            raise ValueError("Cannot specify both 'after' and 'before'")
        if self.first is not None and self.before is not None:
            raise ValueError("Cannot use 'before' with 'first'")
        if self.last is not None and self.after is not None:
            raise ValueError("Cannot use 'after' with 'last'")


class DateRangeInput(ShopifyPartnersBaseModel):
    """Input for date range filters."""

    min_date: Optional[str] = Field(None, description="Minimum date (ISO-8601)")
    max_date: Optional[str] = Field(None, description="Maximum date (ISO-8601)")

    @field_validator("min_date", "max_date")
    @classmethod
    def validate_date_format(cls, v: Optional[str]) -> Optional[str]:
        """Validate ISO-8601 date format."""
        if v is not None:
            from datetime import datetime

            try:
                datetime.fromisoformat(v.replace("Z", "+00:00"))
            except ValueError:
                raise ValueError(f"Invalid date format: {v}. Use ISO-8601 format.")
        return v

    def validate_date_range(self) -> None:
        """Validate that min_date is before max_date."""
        if self.min_date and self.max_date:
            from datetime import datetime

            min_dt = datetime.fromisoformat(self.min_date.replace("Z", "+00:00"))
            max_dt = datetime.fromisoformat(self.max_date.replace("Z", "+00:00"))
            if min_dt >= max_dt:
                raise ValueError("min_date must be before max_date")


class FilterInput(ShopifyPartnersBaseModel):
    """Base class for filter inputs."""

    def model_dump_for_query(self) -> dict:
        """Dump model for use in GraphQL query variables."""
        return self.model_dump(exclude_none=True, by_alias=True)
