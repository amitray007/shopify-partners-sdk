"""FieldSelector rendering and schema validation of selections."""

import pytest

from shopify_partners_sdk import CommonFields, FieldSelector
from shopify_partners_sdk.exceptions import SchemaValidationError
from shopify_partners_sdk.models.enums import AppEventType
from shopify_partners_sdk.schema import SUPPORTED_API_VERSIONS, load_schema

pytestmark = pytest.mark.unit

SCHEMA = load_schema("2026-10")


def lines(text: str) -> list[str]:
    return text.splitlines()


class TestRendering:
    def test_flat_fields_keep_insertion_order(self):
        assert (
            FieldSelector(["id", "name"]).add_field("apiKey").build()
            == "id\nname\napiKey"
        )

    def test_duplicate_field_is_rendered_once(self):
        assert FieldSelector(["id"]).add_fields("id", "id").build() == "id"

    def test_nested_field_and_indent(self):
        selector = FieldSelector(["id"]).add_nested_field(
            "shop", FieldSelector(["name"])
        )
        assert lines(selector.build(1)) == ["  id", "  shop {", "    name", "  }"]

    def test_empty_selector_renders_nothing(self):
        assert FieldSelector().build() == ""

    def test_money_field(self):
        assert lines(FieldSelector().add_money_field("netAmount").build()) == [
            "netAmount {",
            "  amount",
            "  currencyCode",
            "}",
        ]

    def test_interface_fragment(self):
        selector = FieldSelector(["id"]).add_interface_field(
            "AppSubscriptionSale", FieldSelector().add_money_field("netAmount")
        )
        assert lines(selector.build()) == [
            "id",
            "... on AppSubscriptionSale {",
            "  netAmount {",
            "    amount",
            "    currencyCode",
            "  }",
            "}",
        ]

    def test_connection_field_with_arguments(self):
        selector = FieldSelector().add_connection_field(
            "events",
            FieldSelector(["type"]),
            first=5,
            types=[AppEventType.CREDIT_APPLIED],
        )
        assert lines(selector.build()) == [
            "events(first: 5, types: [CREDIT_APPLIED]) {",
            "  edges {",
            "    cursor",
            "    node {",
            "      type",
            "    }",
            "  }",
            "  pageInfo {",
            "    hasNextPage",
            "    hasPreviousPage",
            "  }",
            "}",
        ]

    def test_connection_field_without_page_info(self):
        selector = FieldSelector().add_connection_field(
            "events", FieldSelector(["type"]), include_page_info=False
        )
        assert "pageInfo" not in selector.build()

    def test_inline_string_argument_is_escaped(self):
        """Regression: quotes in string arguments used to break the query."""
        selector = FieldSelector().add_connection_field(
            "events", FieldSelector(["type"]), after='a"b'
        )
        assert 'after: "a\\"b"' in selector.build()

    def test_remove_field(self):
        assert FieldSelector(["id", "name"]).remove_field("id").build() == "name"
        assert FieldSelector(["id"]).remove_field("missing").build() == "id"

    def test_copy_is_deep_and_keeps_arguments(self):
        """Regression: copy() used to drop connection arguments."""
        original = FieldSelector().add_connection_field(
            "events", FieldSelector(["type"]), first=3
        )
        clone = original.copy()
        assert clone.build() == original.build()
        assert "events(first: 3)" in clone.build()
        clone.add_field("id")
        assert "id" not in original.build()

    def test_str_matches_build(self):
        selector = FieldSelector(["id"])
        assert str(selector) == selector.build()

    def test_add_nested_and_interface_fields_in_bulk(self):
        selector = (
            FieldSelector()
            .add_nested_fields({"app": FieldSelector(["id"])})
            .add_interface_fields({"ThemeSale": FieldSelector(["id"])})
        )
        assert lines(selector.build()) == [
            "app {",
            "  id",
            "}",
            "... on ThemeSale {",
            "  id",
            "}",
        ]


class TestSchemaValidation:
    def build(self, selector: FieldSelector, type_name: str) -> str:
        return selector.build(0, SCHEMA, type_name)

    def test_valid_selection_renders_like_plain_build(self):
        selector = FieldSelector(["id", "name", "apiKey"])
        assert self.build(selector, "App") == selector.build()

    def test_unknown_field(self):
        with pytest.raises(SchemaValidationError, match="Did you mean 'apiKey'"):
            self.build(FieldSelector(["apikey"]), "App")

    def test_fields_from_older_examples_are_rejected(self):
        """App has no title or handle in the Partner API; the old docs used them."""
        for field in ("title", "handle"):
            with pytest.raises(SchemaValidationError):
                self.build(FieldSelector([field]), "App")

    def test_object_field_needs_subselection(self):
        with pytest.raises(SchemaValidationError, match="add_nested_field"):
            self.build(FieldSelector(["shop"]), "AppSubscriptionSale")

    def test_empty_nested_selection_is_rejected(self):
        with pytest.raises(SchemaValidationError, match="at least one"):
            self.build(
                FieldSelector().add_nested_field("shop", FieldSelector()),
                "AppSubscriptionSale",
            )

    def test_leaf_field_takes_no_subselection(self):
        with pytest.raises(SchemaValidationError, match="no sub-selection"):
            self.build(
                FieldSelector().add_nested_field("name", FieldSelector(["x"])), "App"
            )

    def test_nested_errors_name_the_nested_type(self):
        selector = FieldSelector().add_nested_field("shop", FieldSelector(["domain"]))
        with pytest.raises(SchemaValidationError, match="type 'Shop'"):
            self.build(selector, "AppSubscriptionSale")

    def test_typename_is_allowed_on_any_composite(self):
        assert self.build(FieldSelector(["__typename"]), "Transaction") == "__typename"

    def test_typename_takes_no_subselection(self):
        selector = FieldSelector().add_nested_field("__typename", FieldSelector(["x"]))
        with pytest.raises(SchemaValidationError):
            self.build(selector, "App")

    def test_interface_field_must_use_fragment(self):
        with pytest.raises(SchemaValidationError, match="inline fragment"):
            self.build(FieldSelector().add_money_field("netAmount"), "Transaction")

    def test_fragment_fields_validate_against_fragment_type(self):
        good = FieldSelector().add_interface_field(
            "AppSubscriptionSale", FieldSelector().add_money_field("netAmount")
        )
        assert "netAmount" in self.build(good, "Transaction")
        bad = FieldSelector().add_interface_field(
            "TaxTransaction", FieldSelector().add_money_field("netAmount")
        )
        with pytest.raises(SchemaValidationError, match="TaxTransaction"):
            self.build(bad, "Transaction")

    def test_fragment_on_unrelated_type(self):
        selector = FieldSelector().add_interface_field("Charge", FieldSelector(["id"]))
        with pytest.raises(SchemaValidationError, match="can never match"):
            self.build(selector, "Transaction")

    def test_union_fragments(self):
        subject = (
            FieldSelector()
            .add_interface_field("AppReference", FieldSelector(["apiKey"]))
            .add_interface_field("ThemeReference", FieldSelector(["name"]))
        )
        selector = FieldSelector(["eventType"]).add_nested_field("subject", subject)
        assert "... on ThemeReference" in self.build(selector, "PartnerEvent")

    def test_connection_arguments_are_typed(self):
        selector = FieldSelector().add_connection_field(
            "events", FieldSelector(["type"]), first=2, types=["RELATIONSHIP_INSTALLED"]
        )
        assert "events(first: 2, types: [RELATIONSHIP_INSTALLED])" in self.build(
            selector, "App"
        )

    def test_unknown_connection_argument(self):
        selector = FieldSelector().add_connection_field(
            "events", FieldSelector(["type"]), frist=2
        )
        with pytest.raises(SchemaValidationError, match="Did you mean 'first'"):
            self.build(selector, "App")

    def test_wrong_enum_in_connection_argument(self):
        """EventType values are not AppEventTypes values even when they look alike."""
        selector = FieldSelector().add_connection_field(
            "events", FieldSelector(["type"]), types=["CHARGE_USAGE"]
        )
        with pytest.raises(SchemaValidationError, match="AppEventTypes"):
            self.build(selector, "App")

    def test_without_type_name_no_validation_happens(self):
        assert FieldSelector(["whatever"]).build(0, SCHEMA, None) == "whatever"


class TestCommonFields:
    """Every preset must be valid for its type in every bundled API version."""

    PRESETS = [
        (CommonFields.basic_node, "App"),
        (CommonFields.money_fields, "Money"),
        (CommonFields.page_info, "PageInfo"),
        (CommonFields.user_error, "UserError"),
        (CommonFields.basic_app, "App"),
        (CommonFields.basic_transaction, "Transaction"),
        (CommonFields.basic_shop, "Shop"),
    ]

    @pytest.mark.parametrize("version", SUPPORTED_API_VERSIONS)
    @pytest.mark.parametrize(("preset", "type_name"), PRESETS)
    def test_preset_is_valid(self, version, preset, type_name):
        preset().build(0, load_schema(version), type_name)

    def test_presets_return_fresh_selectors(self):
        first = CommonFields.basic_app()
        first.add_field("events")
        assert "events" not in CommonFields.basic_app().build()
