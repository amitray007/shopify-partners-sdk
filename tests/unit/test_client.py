"""ShopifyPartnersClient end to end over a scripted HTTP session."""

import logging

import pytest

from shopify_partners_sdk import (
    SUPPORTED_API_VERSIONS,
    CommonFields,
    FieldSelector,
    SchemaValidationError,
    ShopifyPartnersClient,
    __version__,
)
from shopify_partners_sdk.exceptions import AuthenticationError, GraphQLError
from shopify_partners_sdk.models.enums import EventType, TransactionType
from tests.conftest import ORG_ID, TOKEN, FakeResponse, FakeSession

pytestmark = pytest.mark.unit

ENDPOINT = f"https://partners.shopify.com/{ORG_ID}/api/2026-10/graphql.json"


def page(nodes: list[dict], has_next: bool, root: str = "transactions") -> dict:
    return {
        root: {
            "edges": [{"cursor": f"c-{n['id']}", "node": n} for n in nodes],
            "pageInfo": {"hasNextPage": has_next, "hasPreviousPage": False},
        }
    }


class TestConstruction:
    def test_defaults_to_2026_10(self, client):
        assert client.api_version == "2026-10"
        assert client.schema.version == "2026-10"

    def test_explicit_version(self, session, no_wait):
        client = ShopifyPartnersClient(
            ORG_ID, TOKEN, api_version="2026-07", http_client=session
        )
        assert client.schema.version == "2026-07"

    def test_version_from_environment(self, monkeypatch, session):
        monkeypatch.setenv("SHOPIFY_PARTNERS_API_VERSION", "unstable")
        client = ShopifyPartnersClient(ORG_ID, TOKEN, http_client=session)
        assert client.api_version == "unstable"

    @pytest.mark.parametrize("version", ["2025-04", "2025-07", "2099-01"])
    def test_unsupported_version(self, version, session):
        with pytest.raises(ValueError, match="2026-10"):
            ShopifyPartnersClient(
                ORG_ID, TOKEN, api_version=version, http_client=session
            )

    def test_all_supported_versions_construct(self, session):
        for version in SUPPORTED_API_VERSIONS:
            assert ShopifyPartnersClient(
                ORG_ID, TOKEN, api_version=version, http_client=session
            )

    def test_string_organization_id(self, session):
        client = ShopifyPartnersClient("42", TOKEN, http_client=session)
        assert "/42/api/" in client._client.auth.get_api_endpoint()

    def test_bad_token(self, session):
        with pytest.raises(ValueError, match="prtapi_"):
            ShopifyPartnersClient(ORG_ID, "shpat_nope", http_client=session)

    def test_credentials_from_environment(self, monkeypatch, session):
        monkeypatch.setenv("SHOPIFY_PARTNERS_ORGANIZATION_ID", "777")
        monkeypatch.setenv("SHOPIFY_PARTNERS_ACCESS_TOKEN", "prtapi_from_env")
        client = ShopifyPartnersClient(http_client=session)
        assert client._client.auth.get_api_endpoint() == (
            "https://partners.shopify.com/777/api/2026-10/graphql.json"
        )
        assert client._client.auth.access_token == "prtapi_from_env"

    def test_arguments_beat_environment(self, monkeypatch, session):
        monkeypatch.setenv("SHOPIFY_PARTNERS_ORGANIZATION_ID", "777")
        client = ShopifyPartnersClient(ORG_ID, TOKEN, http_client=session)
        assert f"/{ORG_ID}/" in client._client.auth.get_api_endpoint()

    def test_no_credentials_anywhere(self, session):
        with pytest.raises(AuthenticationError, match="organization_id"):
            ShopifyPartnersClient(http_client=session)

    @pytest.mark.parametrize("bad", ["abc", "-1", "12a"])
    def test_non_numeric_organization_id(self, bad, session):
        with pytest.raises(ValueError, match="organization_id"):
            ShopifyPartnersClient(bad, TOKEN, http_client=session)

    def test_missing_token(self, session):
        with pytest.raises((AuthenticationError, ValueError)):
            ShopifyPartnersClient(ORG_ID, "", http_client=session)

    def test_info_logging_does_not_crash(self, session, caplog):
        """Regression: logger.info(msg, key=value) raised TypeError once INFO was on."""
        caplog.set_level(logging.DEBUG)
        client = ShopifyPartnersClient(ORG_ID, TOKEN, http_client=session)
        session.queue_data({"publicApiVersions": []})
        client.query("publicApiVersions", FieldSelector(["handle"]))
        client.close()
        assert TOKEN not in caplog.text


class TestQuery:
    def test_request_shape(self, client, session):
        session.queue_data({"app": {"id": "gid://partners/App/1", "name": "Demo"}})
        data = client.query("app", CommonFields.basic_app(), id="gid://partners/App/1")

        assert data == {"app": {"id": "gid://partners/App/1", "name": "Demo"}}
        call = session.calls[0]
        assert call["url"] == ENDPOINT
        assert call["headers"]["X-Shopify-Access-Token"] == TOKEN
        assert call["headers"]["User-Agent"].endswith(__version__)
        assert call["json"]["variables"] == {"id": "gid://partners/App/1"}
        assert call["json"]["query"].startswith("query($id: ID!) {\n  app(id: $id) {")

    def test_invalid_field_never_reaches_the_network(self, client, session):
        with pytest.raises(SchemaValidationError, match="Did you mean 'name'"):
            client.query("app", FieldSelector(["nam"]), id="1")
        assert session.calls == []

    def test_enum_variables_are_sent_as_strings(self, client, session):
        session.queue_data(page([], has_next=False))
        client.connection_query(
            "transactions",
            CommonFields.basic_transaction(),
            types=[TransactionType.APP_SUBSCRIPTION_SALE],
            first=10,
        )
        payload = session.last_payload
        assert payload["variables"] == {"types": ["APP_SUBSCRIPTION_SALE"], "first": 10}
        assert "$types: [TransactionType!]" in payload["query"]

    def test_graphql_error_is_raised(self, client, session):
        session.queue(
            FakeResponse(body={"errors": [{"message": "Throttled"}], "data": None})
        )
        with pytest.raises(GraphQLError, match="Throttled"):
            client.query("publicApiVersions", FieldSelector(["handle"]))

    def test_version_specific_validation(self, session, no_wait):
        old = ShopifyPartnersClient(
            ORG_ID, TOKEN, api_version="2026-04", http_client=session
        )
        with pytest.raises(SchemaValidationError):
            old.connection_query("events", FieldSelector(["id"]))


class TestConnectionQuery:
    def test_wraps_node_fields(self, client, session):
        session.queue_data(
            page([{"id": "1", "createdAt": "x", "__typename": "ThemeSale"}], False)
        )
        data = client.connection_query(
            "transactions", CommonFields.basic_transaction(), first=1
        )
        assert data["transactions"]["edges"][0]["node"]["__typename"] == "ThemeSale"
        query = session.last_payload["query"]
        assert "edges {\n      cursor\n      node {\n        id" in query
        assert "pageInfo {" in query


class TestMutation:
    def test_app_subscription_cancel(self, client, session):
        session.queue_data({"appSubscriptionCancel": {"userErrors": []}})
        result = client.mutation(
            "appSubscriptionCancel",
            FieldSelector().add_nested_field("userErrors", CommonFields.user_error()),
            appId="gid://partners/App/1",
            shopId="gid://partners/Shop/2",
            prorate=True,
            deferCancellation=False,
            skipFinalUsageCharge=False,
        )
        assert result == {"appSubscriptionCancel": {"userErrors": []}}
        payload = session.last_payload
        assert payload["query"].startswith("mutation(")
        assert payload["variables"]["deferCancellation"] is False

    def test_app_credit_create_docstring_example(self, client, session):
        session.queue_data({"appCreditCreate": {"appCredit": None, "userErrors": []}})
        result_fields = (
            FieldSelector()
            .add_nested_field(
                "appCredit",
                FieldSelector().add_fields("id", "name").add_money_field("amount"),
            )
            .add_nested_field("userErrors", CommonFields.user_error())
        )
        client.mutation(
            "appCreditCreate",
            result_fields,
            appId="gid://partners/App/123",
            shopId="gid://partners/Shop/456",
            description="Refund for downtime",
            amount={"amount": "10.00", "currencyCode": "USD"},
        )
        assert session.last_payload["variables"]["amount"] == {
            "amount": "10.00",
            "currencyCode": "USD",
        }


class TestPaginate:
    def test_walks_every_page_with_cursors(self, client, session):
        session.queue_data(
            page([{"id": "1"}, {"id": "2"}], has_next=True),
            page([{"id": "3"}], has_next=False),
        )
        ids = [
            n["id"]
            for n in client.paginate("transactions", FieldSelector(["id"]), page_size=2)
        ]

        assert ids == ["1", "2", "3"]
        first, second = (c["json"]["variables"] for c in session.calls)
        assert first == {"first": 2}
        assert second == {"first": 2, "after": "c-2"}

    def test_is_lazy(self, client, session):
        session.queue_data(page([{"id": "1"}], has_next=True))
        iterator = client.paginate("transactions", FieldSelector(["id"]), page_size=1)
        assert session.calls == []
        assert next(iterator) == {"id": "1"}
        assert len(session.calls) == 1

    def test_max_pages(self, client, session):
        session.queue_data(
            page([{"id": "1"}], has_next=True),
            page([{"id": "2"}], has_next=True),
        )
        nodes = list(
            client.paginate(
                "transactions", FieldSelector(["id"]), page_size=1, max_pages=2
            )
        )
        assert [n["id"] for n in nodes] == ["1", "2"]
        assert len(session.calls) == 2

    def test_stops_on_empty_page_even_if_has_next(self, client, session):
        session.queue_data(page([], has_next=True))
        assert list(client.paginate("transactions", FieldSelector(["id"]))) == []
        assert len(session.calls) == 1

    def test_default_page_size_from_settings(self, client, session):
        session.queue_data(page([], has_next=False))
        list(client.paginate("transactions", FieldSelector(["id"])))
        assert session.last_payload["variables"]["first"] == 50

    def test_starts_after_given_cursor_and_passes_filters(self, client, session):
        session.queue_data(page([], has_next=False, root="events"))
        list(
            client.paginate(
                "events",
                FieldSelector(["id", "eventType"]),
                after="start",
                filter={"eventTypes": [EventType.RELATIONSHIP_INSTALLED]},
                orderBy="OCCURRED_AT_ASC",
            )
        )
        assert session.last_payload["variables"] == {
            "first": 50,
            "after": "start",
            "filter": {"eventTypes": ["RELATIONSHIP_INSTALLED"]},
            "orderBy": "OCCURRED_AT_ASC",
        }

    def test_non_connection_root_is_rejected(self, client):
        with pytest.raises(SchemaValidationError):
            list(client.paginate("publicApiVersions", FieldSelector(["handle"])))


class TestExecuteRaw:
    def test_returns_full_response(self, client, session):
        body = {"data": {"publicApiVersions": []}, "extensions": {"cost": 1}}
        session.queue(FakeResponse(body=body))
        assert client.execute_raw("{ publicApiVersions { handle } }") == body

    def test_sends_operation_name_and_variables(self, client, session):
        session.queue_data({"app": None})
        client.execute_raw(
            "query A($id: ID!) { app(id: $id) { id } }", {"id": "1"}, "A"
        )
        assert session.last_payload == {
            "query": "query A($id: ID!) { app(id: $id) { id } }",
            "variables": {"id": "1"},
            "operationName": "A",
        }


class TestHealthAndLifecycle:
    def test_healthy(self, client, session):
        session.queue_data(
            {"publicApiVersions": [{"handle": "2026-10", "supported": True}]}
        )
        health = client.health_check()
        assert health["status"] == "healthy"
        assert health["available_versions"] == 1

    def test_unhealthy(self, client, session):
        session.queue(FakeResponse(status_code=401, body={}))
        health = client.health_check()
        assert health["status"] == "unhealthy"
        assert health["api_accessible"] is False

    def test_stats_count_requests(self, client, session):
        session.queue_data({"publicApiVersions": []})
        client.query("publicApiVersions", FieldSelector(["handle"]))
        assert client.stats["request_count"] == 1
        assert client.stats["error_count"] == 0

    def test_context_manager_leaves_injected_session_open(self, session, no_wait):
        with ShopifyPartnersClient(ORG_ID, TOKEN, http_client=session):
            pass
        assert session.closed is False

    def test_close_owned_session(self, monkeypatch):
        created: list[FakeSession] = []

        def make_session() -> FakeSession:
            fake = FakeSession()
            fake.mount = lambda *_args: None  # type: ignore[attr-defined]
            created.append(fake)
            return fake

        monkeypatch.setattr(
            "shopify_partners_sdk.client.base.requests.Session", make_session
        )
        ShopifyPartnersClient(ORG_ID, TOKEN).close()
        assert created[0].closed is True
