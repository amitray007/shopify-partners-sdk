"""Query and mutation builders: documents, variable types, and validation."""

import pytest

from shopify_partners_sdk import CommonFields, FieldSelector
from shopify_partners_sdk.exceptions import SchemaValidationError
from shopify_partners_sdk.models.enums import TransactionType
from shopify_partners_sdk.mutations.custom_builders import CustomMutationBuilder
from shopify_partners_sdk.queries.custom_builders import (
    CustomConnectionQueryBuilder,
    CustomFilterableQueryBuilder,
    CustomQueryBuilder,
)
from shopify_partners_sdk.queries.fields import connection_fields
from shopify_partners_sdk.schema import load_schema

pytestmark = pytest.mark.unit


class TestQueryBuilder:
    def test_document_with_variables(self):
        builder = CustomQueryBuilder("app", FieldSelector(["id", "name"])).add_variable(
            "id", "gid://partners/App/1"
        )
        assert builder.build_query() == (
            "query($id: ID!) {\n"
            "  app(id: $id) {\n"
            "    id\n"
            "    name\n"
            "  }\n"
            "}"
        )
        assert builder.variables == {"id": "gid://partners/App/1"}
        assert builder.get_query_name() == "app"

    def test_operation_name(self):
        builder = CustomQueryBuilder(
            "publicApiVersions", FieldSelector(["handle"]), operation_name="Versions"
        )
        assert builder.build().startswith("query Versions {")
        assert builder.with_operation_name("Other").build().startswith("query Other {")

    def test_no_variables_means_no_parentheses(self):
        document = CustomQueryBuilder(
            "publicApiVersions", FieldSelector(["handle"])
        ).build()
        assert document == "query {\n  publicApiVersions {\n    handle\n  }\n}"

    @pytest.mark.parametrize(
        ("name", "value", "declared"),
        [
            ("types", [TransactionType.APP_USAGE_SALE], "$types: [TransactionType!]"),
            ("types", ["APP_USAGE_SALE"], "$types: [TransactionType!]"),
            ("createdAtMin", "2026-01-01T00:00:00Z", "$createdAtMin: DateTime"),
            ("shopId", "gid://partners/Shop/1", "$shopId: ID"),
            ("myshopifyDomain", "a.myshopify.com", "$myshopifyDomain: String"),
            ("first", 10, "$first: Int"),
            ("after", "cursor", "$after: String"),
        ],
    )
    def test_variable_types_come_from_the_schema(self, name, value, declared):
        """Regression: enums used to be declared as String and lists as [String]."""
        builder = CustomQueryBuilder(
            "transactions", connection_fields(FieldSelector(["id"]))
        )
        assert declared in builder.add_variable(name, value).build()

    def test_none_variables_are_skipped(self):
        builder = CustomQueryBuilder(
            "transactions", connection_fields(FieldSelector(["id"]))
        )
        builder.add_variables(first=5, appId=None)
        assert builder.variables == {"first": 5}
        assert "appId" not in builder.build()

    def test_variables_property_is_a_copy(self):
        builder = CustomQueryBuilder("app", FieldSelector(["id"])).add_variable(
            "id", "1"
        )
        builder.variables["id"] = "changed"
        assert builder.variables == {"id": "1"}

    def test_unknown_root_query(self):
        with pytest.raises(SchemaValidationError, match="Did you mean 'transactions'"):
            CustomQueryBuilder("transaction_s")

    def test_removed_root_query_is_rejected(self):
        with pytest.raises(SchemaValidationError):
            CustomQueryBuilder("conversations")

    def test_unknown_argument_fails_when_added(self):
        builder = CustomQueryBuilder("app", FieldSelector(["id"]))
        with pytest.raises(SchemaValidationError, match="Did you mean 'id'"):
            builder.add_variable("ids", "1")

    def test_missing_required_argument(self):
        with pytest.raises(SchemaValidationError, match="requires argument"):
            CustomQueryBuilder("app", FieldSelector(["id"])).build()

    def test_missing_selection(self):
        with pytest.raises(SchemaValidationError, match="Select at least one field"):
            CustomQueryBuilder("app").add_variable("id", "1").build()

    def test_selection_validated_against_return_type(self):
        builder = CustomQueryBuilder("app", FieldSelector(["title"])).add_variable(
            "id", "1"
        )
        with pytest.raises(SchemaValidationError, match="type 'App'"):
            builder.build()

    def test_list_return_type(self):
        document = CustomQueryBuilder(
            "publicApiVersions", FieldSelector(["handle", "supported"])
        ).build()
        assert "handle" in document

    def test_with_fields_replaces_selection(self):
        builder = CustomQueryBuilder("publicApiVersions", FieldSelector(["handle"]))
        assert (
            "displayName" in builder.with_fields(FieldSelector(["displayName"])).build()
        )

    def test_builder_uses_given_schema_version(self):
        with pytest.raises(SchemaValidationError):
            CustomQueryBuilder("events", schema=load_schema("2026-04"))
        assert CustomQueryBuilder("events", schema=load_schema("2026-07"))

    def test_result_type(self):
        assert CustomQueryBuilder("publicApiVersions").get_result_type() is dict


class TestConnectionBuilder:
    def test_default_selection(self):
        document = (
            CustomConnectionQueryBuilder("transactions").with_page_size(25).build()
        )
        assert document == (
            "query($first: Int) {\n"
            "  transactions(first: $first) {\n"
            "    edges {\n"
            "      cursor\n"
            "      node {\n"
            "        id\n"
            "      }\n"
            "    }\n"
            "    pageInfo {\n"
            "      hasNextPage\n"
            "      hasPreviousPage\n"
            "    }\n"
            "  }\n"
            "}"
        )

    def test_paginate_sets_only_given_values(self):
        builder = CustomConnectionQueryBuilder("events").paginate(first=10, after="abc")
        assert builder.variables == {"first": 10, "after": "abc"}

    @pytest.mark.parametrize(
        "kwargs", [{"first": 1, "last": 1}, {"after": "a", "before": "b"}]
    )
    def test_conflicting_pagination(self, kwargs):
        with pytest.raises(ValueError, match="Cannot specify both"):
            CustomConnectionQueryBuilder("events").paginate(**kwargs)

    def test_first_zero_is_not_dropped(self):
        assert CustomConnectionQueryBuilder("events").paginate(first=0).variables == {
            "first": 0
        }

    @pytest.mark.parametrize(("forward", "key"), [(True, "after"), (False, "before")])
    def test_with_cursor(self, forward, key):
        builder = CustomConnectionQueryBuilder("events").with_cursor(
            "c1", forward=forward
        )
        assert builder.variables == {key: "c1"}

    def test_events_filter_input(self):
        builder = CustomConnectionQueryBuilder(
            "events", connection_fields(FieldSelector(["id", "eventType"]))
        ).add_variables(
            filter={"eventTypes": ["SUBSCRIPTION_CREATED"]}, orderBy="OCCURRED_AT_DESC"
        )
        document = builder.build()
        assert "$filter: EventFilterInput" in document
        assert "$orderBy: EventOrder" in document

    def test_partner_event_fragments(self):
        node = (
            FieldSelector(["id", "eventType", "occurredAt"])
            .add_interface_field(
                "Charge", FieldSelector(["chargeType"]).add_money_field("amount")
            )
            .add_interface_field("Relationship", FieldSelector(["state", "reason"]))
        )
        document = CustomConnectionQueryBuilder(
            "events", connection_fields(node)
        ).build()
        assert "... on Charge {" in document
        assert "... on Relationship {" in document


class TestFilterableBuilder:
    def fields(self) -> FieldSelector:
        return connection_fields(CommonFields.basic_transaction())

    def test_date_range(self):
        builder = CustomFilterableQueryBuilder(
            "transactions", self.fields()
        ).with_date_range("2026-01-01T00:00:00Z", "2026-02-01T00:00:00Z")
        assert builder.variables == {
            "createdAtMin": "2026-01-01T00:00:00Z",
            "createdAtMax": "2026-02-01T00:00:00Z",
        }
        assert "$createdAtMin: DateTime, $createdAtMax: DateTime" in builder.build()

    def test_one_sided_date_range(self):
        builder = CustomFilterableQueryBuilder(
            "transactions", self.fields()
        ).with_date_range(max_date="2026-02-01T00:00:00Z")
        assert builder.variables == {"createdAtMax": "2026-02-01T00:00:00Z"}

    def test_reversed_date_range(self):
        with pytest.raises(ValueError, match="min_date"):
            CustomFilterableQueryBuilder("transactions").with_date_range(
                "2026-03-01", "2026-02-01"
            )

    def test_shop_and_app_filters(self):
        builder = (
            CustomFilterableQueryBuilder("transactions", self.fields())
            .with_shop_filter(myshopify_domain="a.myshopify.com")
            .with_app_filter("gid://partners/App/9")
        )
        assert builder.variables == {
            "myshopifyDomain": "a.myshopify.com",
            "appId": "gid://partners/App/9",
        }

    def test_filter_on_query_without_that_argument(self):
        with pytest.raises(SchemaValidationError, match="createdAtMin"):
            CustomFilterableQueryBuilder("events").with_date_range("2026-01-01")


class TestMutationBuilder:
    def test_app_credit_create_with_flat_arguments(self):
        result = (
            FieldSelector()
            .add_nested_field(
                "appCredit", FieldSelector(["id", "name"]).add_money_field("amount")
            )
            .add_nested_field("userErrors", CommonFields.user_error())
        )
        builder = CustomMutationBuilder("appCreditCreate", result).add_variables(
            appId="gid://partners/App/1",
            shopId="gid://partners/Shop/2",
            description="Goodwill credit",
            amount={"amount": "5.00", "currencyCode": "USD"},
        )
        document = builder.build_mutation()
        assert document.startswith(
            "mutation($appId: ID!, $shopId: ID!, $description: String!, "
            "$amount: MoneyInput!) {\n"
            "  appCreditCreate(appId: $appId, shopId: $shopId, "
            "description: $description, amount: $amount) {"
        )
        assert builder.get_mutation_name() == "appCreditCreate"

    def test_old_input_style_is_rejected(self):
        """Regression: the old builder invented an AppCreditCreateInput! type."""
        with pytest.raises(SchemaValidationError, match="input"):
            CustomMutationBuilder("appCreditCreate").with_input_variable({"appId": "1"})

    def test_app_subscription_cancel_new_in_2026_07(self):
        builder = CustomMutationBuilder("appSubscriptionCancel").add_variables(
            appId="gid://partners/App/1",
            shopId="gid://partners/Shop/2",
            prorate=True,
            deferCancellation=False,
            skipFinalUsageCharge=False,
        )
        document = builder.build()
        assert "$prorate: Boolean!" in document
        assert "$deferCancellation: Boolean!" in document
        assert "userErrors {\n      field\n      message\n    }" in document

    def test_false_booleans_are_kept(self):
        builder = CustomMutationBuilder("appSubscriptionCancel").add_variable(
            "deferCancellation", False
        )
        assert builder.variables == {"deferCancellation": False}

    def test_missing_required_arguments_are_listed(self):
        builder = CustomMutationBuilder("appSubscriptionCancel").add_variable(
            "appId", "1"
        )
        with pytest.raises(SchemaValidationError) as exc:
            builder.build()
        for name in ("shopId", "prorate", "deferCancellation", "skipFinalUsageCharge"):
            assert name in str(exc.value)

    def test_query_name_is_not_a_mutation(self):
        with pytest.raises(SchemaValidationError, match="MutationRoot"):
            CustomMutationBuilder("transactions")

    def test_variable_definitions(self):
        builder = CustomMutationBuilder("appCreditCreate").add_variable("test", True)
        assert builder.build_variable_definitions() == "($test: Boolean)"
