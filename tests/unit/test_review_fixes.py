"""Regressions for defects found in the 2026-10 code review."""

from decimal import Decimal

import pytest
import requests

from shopify_partners_sdk import FieldSelector
from shopify_partners_sdk.client.base import is_mutation
from shopify_partners_sdk.client.retry import ExponentialBackoff, RetryHandler
from shopify_partners_sdk.exceptions import (
    InvalidPageSizeError,
    RateLimitServerError,
    SchemaValidationError,
)
from shopify_partners_sdk.models.base import UserError
from shopify_partners_sdk.models.inputs import MoneyInput
from shopify_partners_sdk.models.objects import (
    AppEventConnection,
    AppSaleCredit,
    CreditApplied,
    RelationshipUninstalled,
    Transaction,
    TransactionConnection,
)
from shopify_partners_sdk.models.scalars import MoneyAmount
from shopify_partners_sdk.mutations.custom_builders import CustomMutationBuilder
from shopify_partners_sdk.queries.custom_builders import CustomQueryBuilder
from shopify_partners_sdk.values import graphql_literal, to_json_value
from tests.conftest import FakeResponse

pytestmark = pytest.mark.unit

APP = {"id": "gid://partners/App/1", "name": "Widget", "apiKey": "key"}
SHOP = {
    "id": "gid://partners/Shop/1",
    "name": "Demo",
    "myshopifyDomain": "d.myshopify.com",
}
MONEY = {"amount": "4.20", "currencyCode": "USD"}
PAGE = {"hasNextPage": False, "hasPreviousPage": False}


def http_error(status: int) -> requests.HTTPError:
    return requests.HTTPError(response=FakeResponse(status_code=status))  # type: ignore[arg-type]


class TestMutationsAreNotRetriedUnsafely:
    """A retried appCreditCreate could credit a merchant twice."""

    @pytest.mark.parametrize(
        "error",
        [
            requests.Timeout(),
            requests.ConnectionError(),
            http_error(500),
            http_error(503),
        ],
    )
    def test_ambiguous_failures_do_not_retry_mutations(self, error):
        handler = RetryHandler(max_attempts=3)
        assert handler.should_retry(error, 0, idempotent=True) is True
        assert handler.should_retry(error, 0, idempotent=False) is False

    @pytest.mark.parametrize("error", [RateLimitServerError(), http_error(429)])
    def test_rate_limit_rejections_still_retry_mutations(self, error):
        assert RetryHandler(max_attempts=3).should_retry(error, 0, idempotent=False)

    def test_mutation_request_sent_once_on_server_error(self, client, session):
        session.queue(FakeResponse(status_code=502, body={}))
        with pytest.raises(requests.HTTPError):
            client.execute_raw(
                "mutation { appCreditCreate { userErrors { message } } }"
            )
        assert len(session.calls) == 1

    def test_query_retried_on_server_error(self, client, session):
        session.queue(FakeResponse(status_code=502, body={}))
        session.queue_data({"publicApiVersions": []})
        client.query("publicApiVersions", FieldSelector(["handle"]))
        assert len(session.calls) == 2

    @pytest.mark.parametrize(
        ("document", "expected"),
        [
            ("mutation { a }", True),
            ("  # comment\n mutation Named($x: ID!) { a }", True),
            ("query A { a } mutation B { b }", True),
            ("query { a }", False),
            ("{ a }", False),
            ('query { a(note: "mutation") }', False),
            ("mutations { a }", False),
        ],
    )
    def test_is_mutation(self, document, expected):
        assert is_mutation(document) is expected


class TestRetryAfter:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (5.0, 5.0),
            (10_000.0, 30.0),
            (float("inf"), None),
            (float("nan"), None),
            (-3.0, None),
        ],
    )
    def test_server_value_is_bounded(self, value, expected):
        handler = RetryHandler(
            max_attempts=1,
            backoff=ExponentialBackoff(base_delay=1.0, max_delay=30.0, jitter=False),
        )
        delay = handler.get_retry_delay(RateLimitServerError(retry_after=value), 0)
        assert delay == (expected if expected is not None else 1.0)


class TestPaginateGuards:
    @pytest.mark.parametrize("size", [0, -1, 251])
    def test_page_size_outside_limits(self, client, size):
        with pytest.raises(InvalidPageSizeError):
            next(client.paginate("transactions", FieldSelector(["id"]), page_size=size))

    @pytest.mark.parametrize("name", ["first", "last", "before"])
    def test_reserved_arguments(self, client, name):
        with pytest.raises(ValueError, match=name):
            next(client.paginate("transactions", FieldSelector(["id"]), **{name: 1}))

    def test_repeated_cursor_stops(self, client, session):
        stuck = {
            "transactions": {
                "edges": [{"cursor": "same", "node": {"id": "1"}}],
                "pageInfo": {"hasNextPage": True, "hasPreviousPage": False},
            }
        }
        session.queue_data(stuck, stuck)
        nodes = list(
            client.paginate("transactions", FieldSelector(["id"]), page_size=1)
        )
        assert [n["id"] for n in nodes] == ["1", "1"]
        assert len(session.calls) == 2


class TestEmptySelections:
    def test_empty_selector_is_falsy(self):
        assert not FieldSelector()
        assert len(FieldSelector(["id", "name"])) == 2

    def test_empty_query_selection_is_rejected(self):
        builder = CustomQueryBuilder("app", FieldSelector()).add_variable("id", "1")
        with pytest.raises(SchemaValidationError, match="Select at least one field"):
            builder.build()

    def test_empty_mutation_selection_uses_user_errors(self):
        builder = CustomMutationBuilder(
            "appCreditCreate", FieldSelector()
        ).add_variables(
            appId="a",
            shopId="s",
            description="d",
            amount={"amount": "1", "currencyCode": "USD"},
        )
        assert "userErrors {" in builder.build()

    def test_empty_fragment_is_rejected(self):
        selector = FieldSelector(["id"]).add_interface_field(
            "ThemeSale", FieldSelector()
        )
        with pytest.raises(SchemaValidationError, match="ThemeSale"):
            selector.build()


class TestDecimalPrecision:
    def test_money_amount_keeps_all_digits_on_the_wire(self):
        amount = MoneyAmount("10.005")
        assert str(amount) == "10.00"  # display only
        assert to_json_value(amount) == "10.005"
        assert graphql_literal(amount) == '"10.005"'

    def test_money_input_dump(self):
        value = MoneyInput(amount=MoneyAmount("0.125"), currency_code="USD")
        assert to_json_value(value) == {"amount": "0.125", "currencyCode": "USD"}

    def test_exponent_decimals_are_plain(self):
        assert to_json_value(Decimal("1E+2")) == "100"


class TestPolymorphicModels:
    def test_app_event_edges_parse_as_their_own_type(self):
        connection = AppEventConnection.model_validate(
            {
                "pageInfo": PAGE,
                "edges": [
                    {
                        "cursor": "a",
                        "node": {
                            "type": "CREDIT_APPLIED",
                            "occurredAt": "2026-10-01T00:00:00Z",
                            "app": APP,
                            "shop": SHOP,
                            "appCredit": {
                                "id": "gid://partners/AppCredit/9",
                                "name": "Goodwill",
                                "amount": MONEY,
                                "test": False,
                            },
                        },
                    },
                    {
                        "cursor": "b",
                        "node": {
                            "__typename": "RelationshipUninstalled",
                            "type": "RELATIONSHIP_UNINSTALLED",
                            "occurredAt": "2026-10-02T00:00:00Z",
                            "app": APP,
                            "shop": SHOP,
                            "reason": "Too expensive",
                        },
                    },
                ],
            }
        )
        credit, uninstall = connection.events
        assert isinstance(credit, CreditApplied)
        assert credit.app_credit.name == "Goodwill"
        assert isinstance(uninstall, RelationshipUninstalled)
        assert uninstall.reason == "Too expensive"

    def test_transaction_edges_follow_typename(self):
        """Regression: an AppSaleCredit used to parse as the first compatible type."""
        connection = TransactionConnection.model_validate(
            {
                "pageInfo": PAGE,
                "edges": [
                    {
                        "cursor": "a",
                        "node": {
                            "__typename": "AppSaleCredit",
                            "id": "gid://partners/AppSaleCredit/1",
                            "createdAt": "2026-10-01T00:00:00Z",
                            "netAmount": MONEY,
                            "app": APP,
                        },
                    },
                    {
                        "cursor": "b",
                        "node": {
                            "id": "gid://partners/Unknown/2",
                            "createdAt": "2026-10-01T00:00:00Z",
                        },
                    },
                ],
            }
        )
        credit, unknown = connection.transactions
        assert type(credit) is AppSaleCredit
        assert type(unknown) is Transaction


class TestUserErrorField:
    def test_field_is_a_path_list(self):
        error = UserError.model_validate(
            {"field": ["amount", "currencyCode"], "message": "bad"}
        )
        assert error.field == ["amount", "currencyCode"]
        assert str(error) == "UserError(field='amount.currencyCode', message='bad')"


class TestRateLimiterMemory:
    def test_request_history_stays_within_one_second(self, monkeypatch):
        from shopify_partners_sdk.client import rate_limiter

        clock = iter(i * 0.5 for i in range(10_000))
        monkeypatch.setattr(rate_limiter.time, "monotonic", lambda: next(clock))
        limiter = rate_limiter.RateLimiter(rate_limit=10.0)
        for _ in range(200):
            assert limiter.try_acquire()
        assert len(limiter._request_times) <= 3
