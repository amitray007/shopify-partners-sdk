"""Unit tests for BaseGraphQLClient."""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import logging

from pydantic import BaseModel, ConfigDict, Field
import pytest
import requests

from shopify_partners_sdk.client.base import BaseGraphQLClient
from shopify_partners_sdk.config import ShopifyPartnersSDKSettings
from shopify_partners_sdk.exceptions.auth import (
    AuthenticationError,
    ForbiddenError,
    UnauthorizedError,
)
from shopify_partners_sdk.exceptions.graphql import (
    GraphQLError,
    GraphQLMultipleErrors,
    GraphQLResponseError,
)
from shopify_partners_sdk.exceptions.rate_limit import RateLimitServerError
from shopify_partners_sdk.version import __version__
from tests.conftest import FakeResponse, FakeSession

pytestmark = pytest.mark.unit

TOKEN = "prtapi_x"
QUERY = "query { app { id } }"
OK_BODY = {"data": {"app": {"id": "1"}}}


def make_client(session: FakeSession, **settings_overrides) -> BaseGraphQLClient:
    options = {"max_retry_attempts": 0, **settings_overrides}
    return BaseGraphQLClient(
        organization_id="123",
        access_token=TOKEN,
        settings=ShopifyPartnersSDKSettings(
            organization_id=123, access_token=TOKEN, **options
        ),
        http_client=session,  # type: ignore[arg-type]
    )


@pytest.fixture
def base(session: FakeSession) -> BaseGraphQLClient:
    return make_client(session)


class Color(str, Enum):  # noqa: UP042 - users may pass plain str-mixin enums
    RED = "RED_VALUE"


class Money(BaseModel):
    model_config = ConfigDict(populate_by_name=True)
    currency_code: str = Field(alias="currencyCode")
    note: str | None = None


class TestRequestShape:
    def test_endpoint_url(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY)
        assert session.calls[0]["url"] == (
            "https://partners.shopify.com/123/api/2026-10/graphql.json"
        )

    def test_endpoint_uses_configured_version(self, session):
        client = make_client(session, api_version="2026-04")
        session.queue(FakeResponse(body=OK_BODY))
        client.execute_query(QUERY)
        assert session.calls[0]["url"].endswith("/123/api/2026-04/graphql.json")

    def test_headers(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY)
        headers = session.calls[0]["headers"]
        assert headers["X-Shopify-Access-Token"] == TOKEN
        assert headers["Content-Type"] == "application/json"
        assert headers["Accept"] == "application/json"

    def test_user_agent_carries_sdk_version(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY)
        assert session.calls[0]["headers"]["User-Agent"] == (
            f"shopify-partners-sdk-python/{__version__}"
        )

    def test_user_agent_names_sdk(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY)
        agent = session.calls[0]["headers"]["User-Agent"]
        assert agent.startswith("shopify-partners-sdk-python/")

    def test_timeout_passed(self, session):
        client = make_client(session, timeout_seconds=42.5)
        session.queue(FakeResponse(body=OK_BODY))
        client.execute_query(QUERY)
        assert session.calls[0]["timeout"] == 42.5

    def test_minimal_payload_has_only_query(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY)
        assert session.calls[0]["json"] == {"query": QUERY}

    def test_empty_variables_omitted(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY, variables={})
        assert "variables" not in session.calls[0]["json"]

    def test_variables_and_operation_name(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY, variables={"id": "gid://x/1"}, operation_name="Op")
        assert session.calls[0]["json"] == {
            "query": QUERY,
            "variables": {"id": "gid://x/1"},
            "operationName": "Op",
        }

    def test_returns_full_response_body(self, base, session):
        session.queue(FakeResponse(body={**OK_BODY, "extensions": {"cost": 1}}))
        assert base.execute_query(QUERY) == {**OK_BODY, "extensions": {"cost": 1}}

    def test_missing_credentials_fail_before_request(self, session):
        client = BaseGraphQLClient(
            settings=ShopifyPartnersSDKSettings(max_retry_attempts=0),
            http_client=session,  # type: ignore[arg-type]
        )
        with pytest.raises(AuthenticationError, match="organization_id, access_token"):
            client.execute_query(QUERY)
        assert session.calls == []

    def test_execute_mutation_is_alias(self, base, session):
        session.queue(FakeResponse(body=OK_BODY))
        result = base.execute_mutation("mutation { x }", {"a": 1}, "M")
        assert result == OK_BODY
        assert session.calls[0]["json"] == {
            "query": "mutation { x }",
            "variables": {"a": 1},
            "operationName": "M",
        }


class TestVariableSerialization:
    def send(self, base, session, variables):
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY, variables=variables)
        return session.calls[-1]["json"]["variables"]

    def test_enum_becomes_value(self, base, session):
        assert self.send(base, session, {"c": Color.RED}) == {"c": "RED_VALUE"}

    def test_decimal_becomes_string(self, base, session):
        assert self.send(base, session, {"amount": Decimal("10.50")}) == {
            "amount": "10.50"
        }

    def test_datetime_becomes_iso(self, base, session):
        sent = self.send(base, session, {"at": datetime(2026, 1, 2, 3, 4, 5)})
        assert sent == {"at": "2026-01-02T03:04:05"}

    def test_date_becomes_iso(self, base, session):
        assert self.send(base, session, {"d": date(2026, 1, 2)}) == {"d": "2026-01-02"}

    def test_model_uses_alias_and_drops_none(self, base, session):
        sent = self.send(base, session, {"m": Money(currency_code="USD")})
        assert sent == {"m": {"currencyCode": "USD"}}

    def test_nested_containers(self, base, session):
        sent = self.send(
            base,
            session,
            {"list": [Color.RED, {"amount": Decimal("1.5")}], "t": (Color.RED,)},
        )
        assert sent == {
            "list": ["RED_VALUE", {"amount": "1.5"}],
            "t": ["RED_VALUE"],
        }


class TestHttpErrors:
    def test_401(self, base, session):
        session.queue(FakeResponse(status_code=401, body={}))
        with pytest.raises(UnauthorizedError):
            base.execute_query(QUERY)

    def test_403(self, base, session):
        session.queue(FakeResponse(status_code=403, body={}))
        with pytest.raises(ForbiddenError):
            base.execute_query(QUERY)

    def test_429_with_retry_after(self, base, session):
        session.queue(
            FakeResponse(status_code=429, body={}, headers={"retry-after": "2.5"})
        )
        with pytest.raises(RateLimitServerError) as info:
            base.execute_query(QUERY)
        assert info.value.retry_after == 2.5
        assert isinstance(info.value.retry_after, float)

    def test_429_without_retry_after(self, base, session):
        session.queue(FakeResponse(status_code=429, body={}))
        with pytest.raises(RateLimitServerError) as info:
            base.execute_query(QUERY)
        assert info.value.retry_after is None

    def test_429_with_unparseable_retry_after(self, base, session):
        session.queue(
            FakeResponse(
                status_code=429,
                body={},
                headers={"retry-after": "Wed, 21 Oct 2026 07:28:00 GMT"},
            )
        )
        with pytest.raises(RateLimitServerError) as info:
            base.execute_query(QUERY)
        assert info.value.retry_after is None

    def test_500_raises_http_error(self, base, session):
        session.queue(FakeResponse(status_code=500, body={}))
        with pytest.raises(requests.HTTPError):
            base.execute_query(QUERY)

    def test_non_json_body(self, base, session):
        session.queue(FakeResponse(status_code=200, text="<html>oops</html>"))
        with pytest.raises(GraphQLResponseError) as info:
            base.execute_query(QUERY)
        assert info.value.message == "Failed to parse JSON response"
        assert info.value.response_data == "<html>oops</html>"


class TestGraphQLErrors:
    def test_single_error_fields(self, base, session):
        session.queue(
            FakeResponse(
                body={
                    "data": None,
                    "errors": [
                        {
                            "message": "Field 'x' not found",
                            "path": ["app", 0, "x"],
                            "locations": [{"line": 1, "column": 9}],
                            "extensions": {"code": "undefinedField"},
                        }
                    ],
                }
            )
        )
        with pytest.raises(GraphQLError) as info:
            base.execute_query(QUERY)
        error = info.value
        assert error.message == "Field 'x' not found"
        assert error.path == ["app", 0, "x"]
        assert error.locations == [{"line": 1, "column": 9}]
        assert error.extensions == {"code": "undefinedField"}

    def test_two_errors_raise_multiple(self, base, session):
        session.queue(
            FakeResponse(body={"errors": [{"message": "one"}, {"message": "two"}]})
        )
        with pytest.raises(GraphQLMultipleErrors) as info:
            base.execute_query(QUERY)
        assert [e.message for e in info.value] == ["one", "two"]

    def test_error_without_message_gets_default(self, base, session):
        session.queue(FakeResponse(body={"errors": [{}]}))
        with pytest.raises(GraphQLError) as info:
            base.execute_query(QUERY)
        assert info.value.message == "Unknown GraphQL error"

    def test_non_dict_entries_skipped(self, base, session):
        session.queue(FakeResponse(body={"errors": ["junk", {"message": "real"}, 7]}))
        with pytest.raises(GraphQLError) as info:
            base.execute_query(QUERY)
        assert info.value.message == "real"
        assert not isinstance(info.value, GraphQLMultipleErrors)

    def test_only_non_dict_entries_fall_through_to_missing_data(self, base, session):
        session.queue(FakeResponse(body={"errors": ["junk"]}))
        with pytest.raises(GraphQLResponseError, match="missing 'data'"):
            base.execute_query(QUERY)

    def test_empty_errors_list_with_data_succeeds(self, base, session):
        session.queue(FakeResponse(body={"data": {"a": 1}, "errors": []}))
        assert base.execute_query(QUERY)["data"] == {"a": 1}

    def test_missing_data_field(self, base, session):
        session.queue(FakeResponse(body={"extensions": {}}))
        with pytest.raises(GraphQLResponseError) as info:
            base.execute_query(QUERY)
        assert info.value.message == "Response missing 'data' field"
        assert info.value.response_data == {"extensions": {}}

    @pytest.mark.parametrize("body", [[1, 2], "text", 5])
    def test_non_dict_body(self, base, session, body):
        session.queue(FakeResponse(body=body))
        with pytest.raises(GraphQLResponseError) as info:
            base.execute_query(QUERY)
        assert info.value.message == "Response is not a JSON object"
        assert info.value.response_data == body


class TestStats:
    def test_initial_counts(self, base):
        assert base.request_count == 0
        assert base.error_count == 0

    def test_successful_requests_counted(self, base, session):
        session.queue(FakeResponse(body=OK_BODY), FakeResponse(body=OK_BODY))
        base.execute_query(QUERY)
        base.execute_query(QUERY)
        assert base.request_count == 2
        assert base.error_count == 0

    def test_http_error_counted_once(self, base, session):
        session.queue(FakeResponse(status_code=500, body={}))
        with pytest.raises(requests.HTTPError):
            base.execute_query(QUERY)
        assert (base.request_count, base.error_count) == (1, 1)

    def test_auth_error_counted(self, base, session):
        session.queue(FakeResponse(status_code=401, body={}))
        with pytest.raises(UnauthorizedError):
            base.execute_query(QUERY)
        assert base.error_count == 1

    def test_graphql_error_counted(self, base, session):
        session.queue(FakeResponse(body={"errors": [{"message": "m"}]}))
        with pytest.raises(GraphQLError):
            base.execute_query(QUERY)
        assert (base.request_count, base.error_count) == (1, 1)

    def test_get_stats(self, base, session):
        session.queue(
            FakeResponse(body=OK_BODY), FakeResponse(status_code=500, body={})
        )
        base.execute_query(QUERY)
        with pytest.raises(requests.HTTPError):
            base.execute_query(QUERY)
        stats = base.get_stats()
        assert stats["request_count"] == 2
        assert stats["error_count"] == 1
        assert stats["error_rate"] == 50.0
        assert stats["auth_configured"] is True
        assert "rate_limiter" in stats
        assert "retry_handler" in stats

    def test_get_stats_without_requests(self, base):
        assert base.get_stats()["error_rate"] == 0.0

    def test_repr(self, base):
        assert repr(base) == (
            "BaseGraphQLClient(requests=0, errors=0, authenticated=True)"
        )


class TestLifecycle:
    def test_injected_session_stays_open(self, base, session):
        base.close()
        assert session.closed is False

    def test_owned_session_is_closed(self, monkeypatch):
        closed = []
        monkeypatch.setattr(requests.Session, "close", lambda self: closed.append(self))
        client = BaseGraphQLClient(
            organization_id="123",
            access_token=TOKEN,
            settings=ShopifyPartnersSDKSettings(),
        )
        client.close()
        assert closed == [client._http_client]

    def test_context_manager_returns_client_and_closes(self, monkeypatch):
        closed = []
        monkeypatch.setattr(requests.Session, "close", lambda self: closed.append(1))
        with BaseGraphQLClient(organization_id="123", access_token=TOKEN) as client:
            assert isinstance(client, BaseGraphQLClient)
        assert closed == [1]

    def test_context_manager_keeps_injected_session(self, session):
        with make_client(session):
            pass
        assert session.closed is False

    def test_exposes_components(self, base):
        assert base.settings.organization_id == 123
        assert base.auth.is_authenticated()
        assert base.rate_limiter is not None
        assert base.retry_handler is not None


class TestRetryIntegration:
    def test_retries_429_until_success(self, session, no_wait):
        client = make_client(session, max_retry_attempts=2)
        session.queue(
            FakeResponse(status_code=429, body={}),
            FakeResponse(status_code=429, body={}),
            FakeResponse(body=OK_BODY),
        )
        assert client.execute_query(QUERY) == OK_BODY
        assert len(session.calls) == 3
        assert client.request_count == 3
        assert client.error_count == 2

    def test_gives_up_after_max_attempts(self, session, no_wait):
        client = make_client(session, max_retry_attempts=2)
        session.queue(*(FakeResponse(status_code=429, body={}) for _ in range(3)))
        with pytest.raises(RateLimitServerError):
            client.execute_query(QUERY)
        assert len(session.calls) == 3

    def test_no_retry_when_disabled(self, session, no_wait):
        client = make_client(session, max_retry_attempts=0)
        session.queue(FakeResponse(status_code=429, body={}))
        with pytest.raises(RateLimitServerError):
            client.execute_query(QUERY)
        assert len(session.calls) == 1


class TestLogging:
    def test_success_with_debug_logging(self, base, session, caplog):
        caplog.set_level(logging.DEBUG)
        session.queue(FakeResponse(body=OK_BODY))
        assert base.execute_query(QUERY, {"a": 1}, "Op") == OK_BODY
        assert TOKEN not in caplog.text
        assert "GraphQL request succeeded" in caplog.text

    def test_http_failure_with_debug_logging(self, base, session, caplog):
        caplog.set_level(logging.DEBUG)
        session.queue(FakeResponse(status_code=500, body={}))
        with pytest.raises(requests.HTTPError):
            base.execute_query(QUERY)
        assert TOKEN not in caplog.text
        assert "failed" in caplog.text

    def test_no_log_record_carries_token(self, base, session, caplog):
        caplog.set_level(logging.DEBUG)
        session.queue(FakeResponse(body=OK_BODY))
        base.execute_query(QUERY)
        for record in caplog.records:
            assert TOKEN not in record.getMessage()
            assert TOKEN not in str(record.__dict__)
