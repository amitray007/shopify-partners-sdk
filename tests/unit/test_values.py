"""Variable serialization and inline GraphQL literals."""

from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field
import pytest

from shopify_partners_sdk.exceptions import SchemaValidationError
from shopify_partners_sdk.models.enums import EventType, TransactionType
from shopify_partners_sdk.schema import load_schema
from shopify_partners_sdk.values import graphql_literal, to_json_value

pytestmark = pytest.mark.unit

SCHEMA = load_schema("2026-10")


class Color(Enum):
    RED = "RED"


class Amount(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    amount: Decimal
    currency_code: str = Field(alias="currencyCode")
    note: str | None = None


class TestToJsonValue:
    def test_plain_values_pass_through(self):
        assert to_json_value({"a": 1, "b": [True, None, "x"]}) == {
            "a": 1,
            "b": [True, None, "x"],
        }

    def test_enum_sends_its_value(self):
        assert (
            to_json_value(TransactionType.APP_SUBSCRIPTION_SALE)
            == "APP_SUBSCRIPTION_SALE"
        )
        assert to_json_value(Color.RED) == "RED"

    def test_decimal_keeps_precision_as_string(self):
        assert to_json_value(Decimal("10.10")) == "10.10"

    def test_dates_use_iso_format(self):
        moment = datetime(2026, 10, 1, 12, 30, tzinfo=UTC)
        assert to_json_value(moment) == "2026-10-01T12:30:00+00:00"
        assert to_json_value(date(2026, 10, 1)) == "2026-10-01"

    def test_pydantic_model_uses_aliases_and_drops_none(self):
        value = Amount(amount=Decimal("5.00"), currency_code="USD")
        assert to_json_value(value) == {"amount": "5.00", "currencyCode": "USD"}

    def test_nested_containers_are_converted(self):
        value = {"types": (EventType.CHARGE_USAGE,), "when": {"min": date(2026, 1, 2)}}
        assert to_json_value(value) == {
            "types": ["CHARGE_USAGE"],
            "when": {"min": "2026-01-02"},
        }


class TestLiteralWithoutSchema:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, "null"),
            (True, "true"),
            (False, "false"),
            (10, "10"),
            (1.5, "1.5"),
            ("plain", '"plain"'),
            ('say "hi"\n', '"say \\"hi\\"\\n"'),
            (Color.RED, "RED"),
            (TransactionType.THEME_SALE, "THEME_SALE"),
            ([1, 2], "[1, 2]"),
            ({"a": 1, "b": "c"}, '{a: 1, b: "c"}'),
            (Decimal("2.50"), '"2.50"'),
            (date(2026, 10, 1), '"2026-10-01"'),
        ],
    )
    def test_renders_graphql_syntax(self, value, expected):
        assert graphql_literal(value) == expected

    def test_bool_is_not_rendered_as_python(self):
        """Regression: inline arguments used to render True instead of true."""
        assert graphql_literal(True) != "True"

    def test_list_is_not_rendered_as_python_repr(self):
        """Regression: lists used to render as ['A'] which GraphQL rejects."""
        assert graphql_literal(["A"]) == '["A"]'

    def test_unsupported_type(self):
        with pytest.raises(TypeError):
            graphql_literal(object())


class TestLiteralWithSchema:
    def test_enum_string_renders_bare(self):
        assert (
            graphql_literal("APP_SALE_CREDIT", "TransactionType!", SCHEMA)
            == "APP_SALE_CREDIT"
        )

    def test_enum_list(self):
        rendered = graphql_literal(
            ["RELATIONSHIP_INSTALLED", EventType.CHARGE_USAGE], "[EventType!]", SCHEMA
        )
        assert rendered == "[RELATIONSHIP_INSTALLED, CHARGE_USAGE]"

    def test_invalid_enum_value_is_caught(self):
        with pytest.raises(SchemaValidationError, match="RELATIONSHIP_INSTALLED"):
            graphql_literal("RELATIONSHIP_INSTALL", "EventType", SCHEMA)

    def test_string_scalar_stays_quoted(self):
        assert graphql_literal("2026-01-01T00:00:00Z", "DateTime", SCHEMA) == (
            '"2026-01-01T00:00:00Z"'
        )

    def test_input_object_fields_are_typed(self):
        rendered = graphql_literal(
            {
                "eventTypes": ["CHARGE_ONE_TIME"],
                "subjectType": "APP",
                "shopId": "gid://1",
            },
            "EventFilterInput",
            SCHEMA,
        )
        assert (
            rendered
            == '{eventTypes: [CHARGE_ONE_TIME], subjectType: APP, shopId: "gid://1"}'
        )

    def test_unknown_input_field_is_caught(self):
        with pytest.raises(SchemaValidationError, match="eventTypes"):
            graphql_literal({"eventType": []}, "EventFilterInput", SCHEMA)

    def test_pydantic_model_as_input_object(self):
        rendered = graphql_literal(
            Amount(amount=Decimal("1.00"), currency_code="USD"), "MoneyInput!", SCHEMA
        )
        assert rendered == '{amount: "1.00", currencyCode: USD}'
