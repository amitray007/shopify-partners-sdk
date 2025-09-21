"""Custom scalar types for the Shopify Partners GraphQL API."""

import base64
from contextlib import suppress
from datetime import datetime
from decimal import Decimal
import json
from typing import Any
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field
from pydantic_core import core_schema

from .enums import Currency


class DateTime(datetime):
    """Custom DateTime scalar that handles ISO-8601 formatted dates.

    GraphQL DateTime scalar from Shopify Partners API returns ISO-8601 strings
    like "2024-01-01T00:00:00Z".
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Generate Pydantic core schema for DateTime."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.datetime_schema(),
        )

    @classmethod
    def _validate(cls, value: Any) -> "DateTime":
        """Validate and convert datetime value."""
        if isinstance(value, str):
            try:
                dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return cls(
                    dt.year,
                    dt.month,
                    dt.day,
                    dt.hour,
                    dt.minute,
                    dt.second,
                    dt.microsecond,
                    dt.tzinfo,
                )
            except ValueError as e:
                raise ValueError(f"Invalid DateTime format: {value}") from e
        elif isinstance(value, datetime):
            return cls(
                value.year,
                value.month,
                value.day,
                value.hour,
                value.minute,
                value.second,
                value.microsecond,
                value.tzinfo,
            )
        else:
            raise ValueError(f"DateTime must be string or datetime, got {type(value)}")

    def __str__(self) -> str:
        """Convert DateTime to ISO-8601 string."""
        return self.isoformat().replace("+00:00", "Z")


class GlobalID(str):
    """Global ID scalar for Shopify Partners API.

    Global IDs are base64-encoded strings that uniquely identify objects
    across the entire Partners API. Format: "gid://partners/Type/id"
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Generate Pydantic core schema for GlobalID."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: Any) -> "GlobalID":
        """Validate GlobalID format."""
        if not isinstance(value, str):
            raise ValueError(f"GlobalID must be string, got {type(value)}")

        if not value.startswith("gid://partners/"):
            raise ValueError(f"Invalid GlobalID format: {value}")

        # Parse the GID structure
        parts = value.split("/")
        if len(parts) < 4:
            raise ValueError(f"Invalid GlobalID structure: {value}")

        return cls(value)

    @property
    def object_type(self) -> str:
        """Extract the object type from the Global ID."""
        parts = str(self).split("/")
        return parts[3] if len(parts) > 3 else ""

    @property
    def object_id(self) -> str:
        """Extract the object ID from the Global ID."""
        parts = str(self).split("/")
        return parts[4] if len(parts) > 4 else ""

    def __repr__(self) -> str:
        """String representation of GlobalID."""
        return f"GlobalID('{self}')"


class MoneyAmount(Decimal):
    """Decimal type specifically for monetary amounts.

    Ensures proper decimal precision for financial calculations.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Generate Pydantic core schema for MoneyAmount."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.decimal_schema(),
        )

    @classmethod
    def _validate(cls, value: Any) -> "MoneyAmount":
        """Validate and convert monetary amount."""
        if isinstance(value, (str, int, float, Decimal)):
            decimal_value = Decimal(str(value))
            return cls(decimal_value)
        raise ValueError(f"MoneyAmount must be numeric, got {type(value)}")

    def __str__(self) -> str:
        """Convert to string with proper formatting."""
        return f"{self:.2f}"


class Cursor(str):
    """Cursor scalar for GraphQL pagination.

    Cursors are typically base64-encoded strings used for pagination.
    """

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Generate Pydantic core schema for Cursor."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: Any) -> "Cursor":
        """Validate cursor format."""
        if not isinstance(value, str):
            raise ValueError(f"Cursor must be string, got {type(value)}")

        if not value:
            raise ValueError("Cursor cannot be empty")

        # Try to decode as base64 to validate format
        with suppress(Exception):
            base64.b64decode(value, validate=True)

        return cls(value)

    def decode(self) -> dict[str, Any]:
        """Attempt to decode cursor if it's base64 encoded JSON."""
        with suppress(Exception):
            decoded_bytes = base64.b64decode(self, validate=True)
            return json.loads(decoded_bytes.decode("utf-8"))
        # Return original value if decoding fails
        return {"cursor": str(self)}

    def __repr__(self) -> str:
        """String representation of Cursor."""
        return f"Cursor('{self}')"


class URL(str):
    """URL scalar with basic validation."""

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        """Generate Pydantic core schema for URL."""
        return core_schema.no_info_after_validator_function(
            cls._validate,
            core_schema.str_schema(),
        )

    @classmethod
    def _validate(cls, value: Any) -> "URL":
        """Validate URL format."""
        if not isinstance(value, str):
            raise ValueError(f"URL must be string, got {type(value)}")

        if not value:
            raise ValueError("URL cannot be empty")

        # Basic URL validation
        try:
            result = urlparse(value)
            if not all([result.scheme, result.netloc]):
                raise ValueError(f"Invalid URL format: {value}")
        except Exception as e:
            raise ValueError(f"Invalid URL: {value}") from e

        return cls(value)

    @property
    def domain(self) -> str:
        """Extract domain from URL."""
        return urlparse(self).netloc

    @property
    def scheme(self) -> str:
        """Extract scheme from URL."""
        return urlparse(self).scheme

    def __repr__(self) -> str:
        """String representation of URL."""
        return f"URL('{self}')"


class Money(BaseModel):
    """Money type with amount and currency code.

    Represents monetary values in the Shopify Partners API.
    """

    amount: MoneyAmount = Field(..., description="The monetary amount")
    currency_code: Currency = Field(
        ..., description="ISO 4217 currency code", alias="currencyCode"
    )

    def __str__(self) -> str:
        """String representation of Money."""
        return f"{self.amount} {self.currency_code}"

    def __repr__(self) -> str:
        """Detailed representation of Money."""
        return f"Money(amount={self.amount}, currency_code='{self.currency_code}')"

    model_config = ConfigDict(populate_by_name=True)
