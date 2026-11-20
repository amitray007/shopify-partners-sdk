"""Bundled Partner API schema: contents, lookups, and error messages."""

import importlib.util
import json
from pathlib import Path

import pytest

from shopify_partners_sdk.config.defaults import DEFAULT_API_VERSION
from shopify_partners_sdk.exceptions import SchemaValidationError, ValidationError
from shopify_partners_sdk.schema import (
    SUPPORTED_API_VERSIONS,
    PartnerSchema,
    load_schema,
    named_type,
)

pytestmark = pytest.mark.unit

REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_generator():
    path = REPO_ROOT / "schema" / "utils" / "build_sdk_schema.py"
    spec = importlib.util.spec_from_file_location("build_sdk_schema", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def schema() -> PartnerSchema:
    return load_schema("2026-10")


class TestBundledVersions:
    def test_supported_versions_are_what_shopify_supports_in_2026_10(self):
        assert SUPPORTED_API_VERSIONS == (
            "2026-01",
            "2026-04",
            "2026-07",
            "2026-10",
            "2027-01",
            "unstable",
        )

    def test_default_version_is_latest_stable(self):
        assert DEFAULT_API_VERSION == "2026-10"
        assert DEFAULT_API_VERSION in SUPPORTED_API_VERSIONS

    def test_generator_and_package_agree_on_versions(self):
        assert (
            tuple(sorted(_load_generator().SUPPORTED_VERSIONS))
            == SUPPORTED_API_VERSIONS
        )

    @pytest.mark.parametrize("version", SUPPORTED_API_VERSIONS)
    def test_bundled_data_matches_raw_introspection(self, version):
        """Fails when someone edits the raw file but forgets to regenerate."""
        generator = _load_generator()
        raw = json.loads(
            (
                REPO_ROOT / "schema" / "versions" / version / "introspection.json"
            ).read_text()
        )
        bundled = json.loads(
            (
                REPO_ROOT
                / "src/shopify_partners_sdk/schema/data"
                / f"partner_{version}.json"
            ).read_text()
        )
        assert generator.compact_schema(raw) == bundled

    @pytest.mark.parametrize("version", SUPPORTED_API_VERSIONS)
    def test_every_version_loads(self, version):
        loaded = load_schema(version)
        assert loaded.version == version
        assert loaded.root_type("query") == "QueryRoot"
        assert loaded.root_type("mutation") == "MutationRoot"

    def test_load_is_cached(self):
        assert load_schema("2026-10") is load_schema("2026-10")

    @pytest.mark.parametrize("version", ["2025-04", "2025-07", "2024-10", "latest", ""])
    def test_unsupported_version_is_rejected_with_the_list(self, version):
        with pytest.raises(SchemaValidationError) as exc:
            load_schema(version)
        assert "2026-10" in str(exc.value)


class Test2026_10Contents:
    """Spot checks taken from the 2026-10 introspection, independent of the loader."""

    def test_new_root_queries(self, schema):
        assert schema.root_field("query", "events")["type"] == "PartnerEventConnection"
        assert (
            schema.root_field("query", "activeSubscription")["type"]
            == "ActiveSubscription"
        )

    def test_new_mutation(self, schema):
        field = schema.root_field("mutation", "appSubscriptionCancel")
        assert field["type"] == "AppSubscriptionCancelPayload"
        assert sorted(field["required"]) == [
            "appId",
            "deferCancellation",
            "prorate",
            "shopId",
            "skipFinalUsageCharge",
        ]

    @pytest.mark.parametrize(
        "removed", ["conversation", "conversations", "job", "jobs"]
    )
    def test_removed_queries_are_gone(self, schema, removed):
        with pytest.raises(SchemaValidationError):
            schema.root_field("query", removed)

    @pytest.mark.parametrize(
        "removed", ["Conversation", "Job", "Message", "TeamMember"]
    )
    def test_removed_types_are_gone(self, schema, removed):
        with pytest.raises(SchemaValidationError):
            schema.type(removed)

    def test_partner_event_interface(self, schema):
        assert schema.kind("PartnerEvent") == "INTERFACE"
        assert schema.possible_types("PartnerEvent") == [
            "Charge",
            "Credit",
            "Earning",
            "Relationship",
            "SubscriptionStatus",
        ]

    def test_referral_category_gained_values(self, schema):
        values = schema.enum_values("ReferralCategory")
        for added in ("B2B_PROFIT_SHARE", "CO_MARKETING", "PARTNER_DEVELOPMENT_FUNDS"):
            assert added in values

    def test_events_only_exists_from_2026_07(self):
        with pytest.raises(SchemaValidationError):
            load_schema("2026-04").root_field("query", "events")
        assert load_schema("2026-07").root_field("query", "events")

    def test_unstable_has_eventsink_mutations(self):
        unstable = load_schema("unstable")
        assert unstable.root_field("mutation", "eventsinkCreate")
        with pytest.raises(SchemaValidationError):
            load_schema("2026-10").root_field("mutation", "eventsinkCreate")


class TestLookups:
    def test_argument_types_keep_list_and_non_null_wrappers(self, schema):
        assert (
            schema.argument_type("QueryRoot", "transactions", "types")
            == "[TransactionType!]"
        )
        assert schema.argument_type("QueryRoot", "app", "id") == "ID!"
        assert (
            schema.argument_type("QueryRoot", "events", "filter") == "EventFilterInput"
        )
        assert (
            schema.argument_type("MutationRoot", "appCreditCreate", "amount")
            == "MoneyInput!"
        )

    def test_required_arguments(self, schema):
        assert schema.required_arguments("QueryRoot", "app") == ["id"]
        assert schema.required_arguments("QueryRoot", "transactions") == []

    def test_is_leaf(self, schema):
        assert schema.is_leaf("String")
        assert schema.is_leaf("TransactionType")
        assert not schema.is_leaf("App")
        assert not schema.is_leaf("Transaction")

    def test_input_field_type(self, schema):
        assert (
            schema.input_field_type("EventFilterInput", "eventTypes") == "[EventType!]"
        )
        with pytest.raises(SchemaValidationError, match="eventType"):
            schema.input_field_type("EventFilterInput", "eventType")

    def test_named_type(self):
        assert named_type("[Foo!]!") == "Foo"
        assert named_type("Foo") == "Foo"
        assert named_type("[[Foo]]") == "Foo"


class TestErrors:
    def test_unknown_root_field_suggests_closest(self, schema):
        with pytest.raises(SchemaValidationError) as exc:
            schema.root_field("query", "transaction_list")
        assert exc.value.suggestions[0] in ("transaction", "transactions")

    def test_typo_in_field_suggests_fix(self, schema):
        with pytest.raises(SchemaValidationError) as exc:
            schema.field("App", "nmae")
        assert exc.value.suggestions == ["name"]
        assert "Did you mean 'name'?" in str(exc.value)

    def test_no_suggestion_when_nothing_is_close(self, schema):
        with pytest.raises(SchemaValidationError) as exc:
            schema.field("App", "zzzzzz")
        assert exc.value.suggestions == []
        assert "Did you mean" not in str(exc.value)

    def test_interface_field_points_to_fragment_types(self, schema):
        with pytest.raises(SchemaValidationError) as exc:
            schema.field("Transaction", "netAmount")
        message = str(exc.value)
        assert "AppSubscriptionSale" in message
        assert "add_interface_field" in message
        assert "TaxTransaction" not in message  # it has no netAmount

    def test_unknown_argument(self, schema):
        with pytest.raises(SchemaValidationError, match="Did you mean 'createdAtMin'"):
            schema.argument_type("QueryRoot", "transactions", "createdAtMn")

    def test_enum_value_check(self, schema):
        schema.check_enum_value("TransactionType", "APP_SUBSCRIPTION_SALE")
        with pytest.raises(SchemaValidationError, match="APP_SUBSCRIPTION_SALE"):
            schema.check_enum_value("TransactionType", "APP_SUBSCRIPTION_SALES")

    @pytest.mark.parametrize(
        ("parent", "fragment"),
        [
            ("Transaction", "AppSubscriptionSale"),  # interface -> implementor
            ("PartnerEvent", "Charge"),
            ("Subject", "AppReference"),  # union -> member
            ("Charge", "PartnerEvent"),  # object -> its interface
            ("App", "App"),
        ],
    )
    def test_valid_fragments(self, schema, parent, fragment):
        schema.check_fragment(parent, fragment)

    def test_impossible_fragment(self, schema):
        with pytest.raises(SchemaValidationError, match="can never match"):
            schema.check_fragment("Transaction", "Charge")

    def test_error_is_a_value_error_and_sdk_validation_error(self, schema):
        with pytest.raises(ValueError):
            schema.type("Nope")
        with pytest.raises(ValidationError):
            schema.type("Nope")
