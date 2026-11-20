"""Convert Python values into GraphQL variables and inline literals."""

from collections.abc import Mapping
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import json
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel

from shopify_partners_sdk.schema import named_type

if TYPE_CHECKING:
    from shopify_partners_sdk.schema import PartnerSchema


def to_json_value(value: Any) -> Any:
    """Make a variable value JSON-serializable the way the Partner API expects.

    Pydantic models dump by alias (camelCase), enums send their value, dates send
    ISO-8601, and decimals send strings so no precision is lost.
    """
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json", by_alias=True, exclude_none=True)
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, Mapping):
        return {str(k): to_json_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_json_value(v) for v in value]
    return value


def graphql_literal(
    value: Any,
    type_ref: str | None = None,
    schema: "PartnerSchema | None" = None,
) -> str:
    """Render a value as an inline GraphQL literal.

    With a schema and the argument's type, enum values render bare and are checked
    against the enum, and input-object fields are checked by name. Without one,
    only ``Enum`` members render bare; every other string is quoted.
    """
    value = _normalize_scalar(value)
    named = named_type(type_ref) if type_ref else None

    if value is None:
        return "null"
    if isinstance(value, Enum):
        return _enum_literal(str(value.value), named, schema)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return json.dumps(value)
    if isinstance(value, str):
        if named and schema and schema.kind(named) == "ENUM":
            return _enum_literal(value, named, schema)
        return json.dumps(value)
    if isinstance(value, list):
        item_type = _list_item_type(type_ref)
        return (
            "[" + ", ".join(graphql_literal(v, item_type, schema) for v in value) + "]"
        )
    if isinstance(value, dict):
        return _object_literal(value, named, schema)
    raise TypeError(f"Cannot render {type(value).__name__} as a GraphQL literal")


def _normalize_scalar(value: Any) -> Any:
    """Convert models, dates, and decimals; leave enums for the literal renderer."""
    if isinstance(value, BaseModel):
        return value.model_dump(by_alias=True, exclude_none=True)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (tuple, set)):
        return list(value)
    return value


def _enum_literal(value: str, enum: str | None, schema: "PartnerSchema | None") -> str:
    if enum and schema:
        schema.check_enum_value(enum, value)
    return value


def _list_item_type(type_ref: str | None) -> str | None:
    if not type_ref:
        return None
    inner = type_ref.rstrip("!")
    if inner.startswith("[") and inner.endswith("]"):
        return inner[1:-1]
    return type_ref


def _object_literal(
    value: dict[str, Any], input_type: str | None, schema: "PartnerSchema | None"
) -> str:
    parts = []
    for key, item in value.items():
        field_type = (
            schema.input_field_type(input_type, key) if schema and input_type else None
        )
        parts.append(f"{key}: {graphql_literal(item, field_type, schema)}")
    return "{" + ", ".join(parts) + "}"
