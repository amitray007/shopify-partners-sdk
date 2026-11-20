"""Unit tests for models, scalars and inputs, using API-shaped JSON."""

import base64
from decimal import Decimal
import json
from typing import Any

from pydantic import ValidationError
import pytest

from shopify_partners_sdk.config.defaults import DEFAULT_API_VERSION
from shopify_partners_sdk.models.base import Connection, PageInfo
from shopify_partners_sdk.models.inputs import (
    AppCreditCreateInput,
    DateRangeInput,
    EventsinkCreateInput,
    MoneyInput,
    PaginationInput,
)
from shopify_partners_sdk.models.objects.app import (
    App,
    AppCredit,
    CreditApplied,
    RelationshipInstalled,
)
from shopify_partners_sdk.models.objects.shop import Shop
from shopify_partners_sdk.models.objects.transaction import (
    AppOneTimeSale,
    AppSubscriptionSale,
    Transaction,
    TransactionConnection,
)
from shopify_partners_sdk.models.objects.version import ApiVersion
from shopify_partners_sdk.models.scalars import (
    URL,
    Cursor,
    DateTime,
    GlobalID,
    Money,
    MoneyAmount,
)

pytestmark = pytest.mark.unit


def money(amount: str, code: str = "USD") -> dict[str, str]:
    return {"amount": amount, "currencyCode": code}


def shop_json(domain: str = "cool-store.myshopify.com") -> dict[str, Any]:
    return {
        "id": "gid://partners/Shop/84021",
        "name": "Cool Store",
        "avatarUrl": None,
        "myshopifyDomain": domain,
    }


def app_json() -> dict[str, Any]:
    return {
        "id": "gid://partners/App/1234",
        "apiKey": "0123456789abcdef",
        "name": "Review Widget",
        "events": {
            "pageInfo": {"hasNextPage": False, "hasPreviousPage": False},
            "edges": [],
        },
    }


def page_info_json(**overrides: Any) -> dict[str, Any]:
    base = {
        "hasNextPage": True,
        "hasPreviousPage": False,
        "startCursor": "eyJpZCI6MX0",
        "endCursor": "eyJpZCI6Mn0",
    }
    return {**base, **overrides}


class TestPageInfoAndConnection:
    def test_page_info_parses_cursors_from_aliases(self) -> None:
        info = PageInfo.model_validate(page_info_json())
        assert info.start_cursor == "eyJpZCI6MX0"
        assert info.end_cursor == "eyJpZCI6Mn0"
        assert info.has_next_page is True

    def test_page_info_cursors_are_optional(self) -> None:
        info = PageInfo.model_validate({"hasNextPage": False, "hasPreviousPage": False})
        assert info.start_cursor is None
        assert info.end_cursor is None

    def test_page_info_accepts_null_cursors(self) -> None:
        info = PageInfo.model_validate(
            page_info_json(startCursor=None, endCursor=None, hasNextPage=False)
        )
        assert info.end_cursor is None

    def test_connection_exposes_cursors_and_flags(self) -> None:
        # Old PageInfo had no cursor fields, so these raised AttributeError.
        conn = Connection.model_validate({"pageInfo": page_info_json()})
        assert conn.end_cursor == "eyJpZCI6Mn0"
        assert conn.start_cursor == "eyJpZCI6MX0"
        assert conn.has_next_page is True
        assert conn.has_previous_page is False

    def test_page_info_requires_flags(self) -> None:
        with pytest.raises(ValidationError):
            PageInfo.model_validate({"startCursor": "x"})

    def test_page_info_str(self) -> None:
        info = PageInfo.model_validate(page_info_json())
        assert str(info) == "PageInfo(has_next=True, has_prev=False)"


class TestGlobalID:
    @pytest.mark.parametrize(
        ("value", "object_type", "object_id"),
        [
            ("gid://partners/App/1234", "App", "1234"),
            ("gid://partners/Shop/84021", "Shop", "84021"),
            ("gid://partners/AppSubscriptionSale/9", "AppSubscriptionSale", "9"),
        ],
    )
    def test_valid(self, value: str, object_type: str, object_id: str) -> None:
        gid = GlobalID._validate(value)
        assert gid == value
        assert gid.object_type == object_type
        assert gid.object_id == object_id
        assert repr(gid) == f"GlobalID('{value}')"

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "App/1234",
            "gid://shopify/Product/1",
            "gid://partners/",
            "gid://partners/App",
            "gid://partners/App/",
            "gid://partners//1234",
            "gid://partners//",
        ],
    )
    def test_invalid(self, value: str) -> None:
        # The last four were accepted by the old length-only check.
        with pytest.raises(ValueError, match="Invalid GlobalID"):
            GlobalID._validate(value)

    def test_non_string_rejected(self) -> None:
        with pytest.raises(ValueError, match="must be string"):
            GlobalID._validate(123)

    def test_model_field_rejects_bare_prefix(self) -> None:
        payload = {"id": "gid://partners/", "name": "x", "myshopifyDomain": "a.b"}
        with pytest.raises(ValidationError):
            Shop.model_validate(payload)


class TestScalars:
    def test_money_parses_aliases_and_decimal(self) -> None:
        parsed = Money.model_validate(money("49.99", "EUR"))
        assert parsed.amount == Decimal("49.99")
        assert parsed.currency_code == "EUR"
        assert str(parsed) == "49.99 EUR"

    def test_money_populates_by_field_name(self) -> None:
        parsed = Money(amount="5", currency_code="USD")  # type: ignore[arg-type]
        assert parsed.amount == Decimal("5")

    def test_money_rejects_unknown_currency(self) -> None:
        with pytest.raises(ValidationError):
            Money.model_validate(money("1.00", "ZZZ"))

    def test_money_amount_formats_two_places(self) -> None:
        assert str(MoneyAmount._validate("3.5")) == "3.50"
        assert MoneyAmount._validate(2) == Decimal("2")
        assert MoneyAmount._validate(0.1) == Decimal("0.1")

    def test_money_amount_rejects_non_numeric_type(self) -> None:
        with pytest.raises(ValueError, match="numeric"):
            MoneyAmount._validate(["1"])

    def test_datetime_parses_z_suffix(self) -> None:
        value = DateTime._validate("2024-03-05T10:20:30Z")
        assert (value.year, value.month, value.day) == (2024, 3, 5)
        assert value.utcoffset().total_seconds() == 0  # type: ignore[union-attr]
        assert str(value) == "2024-03-05T10:20:30Z"

    def test_datetime_parses_offset_and_fraction(self) -> None:
        value = DateTime._validate("2024-03-05T10:20:30.250+02:00")
        assert value.microsecond == 250000
        assert value.utcoffset().total_seconds() == 7200  # type: ignore[union-attr]

    def test_datetime_rejects_garbage(self) -> None:
        with pytest.raises(ValueError, match="Invalid DateTime"):
            DateTime._validate("yesterday")
        with pytest.raises(ValueError, match="string or datetime"):
            DateTime._validate(5)

    def test_cursor_accepts_any_non_empty_string(self) -> None:
        assert Cursor._validate("not base64 at all!") == "not base64 at all!"

    def test_cursor_rejects_empty_and_non_string(self) -> None:
        with pytest.raises(ValueError, match="empty"):
            Cursor._validate("")
        with pytest.raises(ValueError, match="string"):
            Cursor._validate(1)

    def test_cursor_decode_json_payload(self) -> None:
        token = base64.b64encode(json.dumps({"last_id": 7}).encode()).decode()
        assert Cursor._validate(token).decode() == {"last_id": 7}

    def test_cursor_decode_falls_back_for_opaque_cursor(self) -> None:
        assert Cursor._validate("opaque-cursor").decode() == {"cursor": "opaque-cursor"}

    def test_url_properties(self) -> None:
        url = URL._validate("https://partners.shopify.com/1/api")
        assert url.domain == "partners.shopify.com"
        assert url.scheme == "https"

    @pytest.mark.parametrize("value", ["", "no-scheme.com", "https://", 5])
    def test_url_rejects_invalid(self, value: Any) -> None:
        with pytest.raises(ValueError):
            URL._validate(value)


class TestShop:
    def test_parses_real_shaped_payload(self) -> None:
        shop = Shop.model_validate(shop_json())
        assert shop.id == "gid://partners/Shop/84021"
        assert shop.name == "Cool Store"
        assert shop.avatar_url is None
        assert shop.myshopify_domain == "cool-store.myshopify.com"
        assert shop.shop_name == "cool-store"

    def test_bare_domain_is_accepted(self) -> None:
        # Old URL-typed field rejected the scheme-less domain Shopify returns.
        assert Shop.model_validate(shop_json("a.myshopify.com")).shop_name == "a"

    @pytest.mark.parametrize(
        "domain", ["example.com", "a.myshopify.org", ".myshopify.com"]
    )
    def test_non_myshopify_domain_rejected(self, domain: str) -> None:
        with pytest.raises(ValidationError, match=r"myshopify\.com"):
            Shop.model_validate(shop_json(domain))

    def test_populate_by_field_name(self) -> None:
        shop = Shop.model_validate(
            {
                "id": "gid://partners/Shop/1",
                "name": "S",
                "myshopify_domain": "s.myshopify.com",
            }
        )
        assert shop.myshopify_domain == "s.myshopify.com"

    def test_str(self) -> None:
        assert str(Shop.model_validate(shop_json())) == (
            "Shop(domain='cool-store.myshopify.com', name='Cool Store')"
        )

    def test_validator_runs_on_assignment(self) -> None:
        shop = Shop.model_validate(shop_json())
        with pytest.raises(ValidationError):
            shop.myshopify_domain = "evil.example.com"


class TestApp:
    def test_parses_app_with_empty_events(self) -> None:
        app = App.model_validate(app_json())
        assert app.api_key == "0123456789abcdef"
        assert app.name == "Review Widget"
        assert app.events.events == []
        assert str(app) == "App(name='Review Widget', api_key='0123456789abcdef')"

    def test_extra_fields_are_ignored(self) -> None:
        app = App.model_validate({**app_json(), "futureField": 1})
        assert not hasattr(app, "futureField")

    def test_missing_required_field_fails(self) -> None:
        payload = app_json()
        del payload["apiKey"]
        with pytest.raises(ValidationError, match="apiKey"):
            App.model_validate(payload)

    def test_event_resolves_forward_references(self) -> None:
        # Old code left Shop/AppCredit unresolved (PydanticUserError).
        event = RelationshipInstalled.model_validate(
            {
                "id": "gid://partners/AppEvent/55",
                "app": app_json(),
                "shop": shop_json(),
                "occurredAt": "2025-06-01T12:00:00Z",
                "type": "RELATIONSHIP_INSTALLED",
            }
        )
        assert event.shop.shop_name == "cool-store"
        assert event.type == "RELATIONSHIP_INSTALLED"
        assert str(event) == (
            "RelationshipInstalled(type=RELATIONSHIP_INSTALLED, "
            "occurred_at=2025-06-01T12:00:00Z)"
        )

    def test_credit_applied_with_nested_credit(self) -> None:
        credit = {
            "id": "gid://partners/AppCredit/3",
            "amount": money("25.00"),
            "name": "Goodwill",
            "description": None,
            "createdAt": "2025-06-01T12:00:00Z",
            "test": False,
            "app": app_json(),
            "shop": shop_json(),
        }
        event = CreditApplied.model_validate(
            {
                "id": "gid://partners/AppEvent/56",
                "app": app_json(),
                "shop": shop_json(),
                "occurredAt": "2025-06-01T12:00:00Z",
                "type": "CREDIT_APPLIED",
                "appCredit": credit,
            }
        )
        assert isinstance(event.app_credit, AppCredit)
        assert event.app_credit.amount.amount == Decimal("25.00")
        assert str(event.app_credit) == "AppCredit(amount=25.00 USD, name='Goodwill')"

    def test_unknown_event_type_fails(self) -> None:
        with pytest.raises(ValidationError):
            RelationshipInstalled.model_validate(
                {
                    "id": "gid://partners/AppEvent/55",
                    "app": app_json(),
                    "shop": shop_json(),
                    "occurredAt": "2025-06-01T12:00:00Z",
                    "type": "NOT_A_TYPE",
                }
            )


def sale_json(**extra: Any) -> dict[str, Any]:
    return {
        "id": "gid://partners/AppSale/901",
        "createdAt": "2025-02-14T08:30:00Z",
        "chargeId": "gid://partners/AppCharge/77",
        "grossAmount": money("100.00"),
        "netAmount": money("80.50"),
        "shopifyFee": money("19.50"),
        "processingFee": None,
        "app": app_json(),
        "shop": shop_json(),
        **extra,
    }


class TestTransactions:
    def test_one_time_sale_fields(self) -> None:
        sale = AppOneTimeSale.model_validate(sale_json())
        assert sale.net_amount.amount == Decimal("80.50")
        assert sale.gross_amount is not None
        assert sale.gross_amount.amount == Decimal("100.00")
        assert sale.processing_fee is None
        assert sale.charge_id == "gid://partners/AppCharge/77"
        assert sale.created_at.year == 2025
        assert str(sale) == "AppOneTimeSale(app='Review Widget', net_amount=80.50 USD)"

    def test_subscription_sale_billing_interval(self) -> None:
        sale = AppSubscriptionSale.model_validate(
            sale_json(billingInterval="EVERY_30_DAYS")
        )
        assert sale.billing_interval == "EVERY_30_DAYS"
        assert "EVERY_30_DAYS" in str(sale)

    def test_connection_parses_edges_cursors_and_nodes(self) -> None:
        payload = {
            "pageInfo": page_info_json(),
            "edges": [
                {
                    "cursor": "c1",
                    "node": {**sale_json(), "__typename": "AppOneTimeSale"},
                },
                {
                    "cursor": "c2",
                    "node": {
                        "id": "gid://partners/Referral/4",
                        "createdAt": "2025-02-15T00:00:00Z",
                        "amount": money("5.00"),
                    },
                },
            ],
        }
        conn = TransactionConnection.model_validate(payload)
        assert [e.cursor for e in conn.edges] == ["c1", "c2"]
        assert conn.end_cursor == "eyJpZCI6Mn0"
        assert conn.has_next_page is True
        first, second = conn.transactions
        assert isinstance(first, AppOneTimeSale)
        assert isinstance(second, Transaction)
        assert second.id == "gid://partners/Referral/4"

    def test_transaction_requires_created_at(self) -> None:
        payload = sale_json()
        del payload["createdAt"]
        with pytest.raises(ValidationError):
            AppOneTimeSale.model_validate(payload)

    def test_net_amount_is_required(self) -> None:
        payload = sale_json()
        del payload["netAmount"]
        with pytest.raises(ValidationError):
            AppOneTimeSale.model_validate(payload)

    def test_graphql_round_trip_uses_aliases(self) -> None:
        sale = AppOneTimeSale.model_validate(sale_json())
        dumped = sale.model_dump_graphql()
        assert dumped["netAmount"] == {"amount": "80.50", "currencyCode": "USD"}
        assert "processingFee" not in dumped  # None values are dropped


class TestApiVersion:
    def payload(self, handle: str) -> dict[str, Any]:
        return {"displayName": handle, "handle": handle, "supported": True}

    def test_parses_aliases(self) -> None:
        version = ApiVersion.model_validate(
            {"displayName": "2025-07", "handle": "2025-07", "supported": False}
        )
        assert version.display_name == "2025-07"
        assert version.supported is False
        assert str(version) == "ApiVersion(handle='2025-07', unsupported)"

    def test_is_stable(self) -> None:
        assert ApiVersion.model_validate(self.payload("2025-07")).is_stable is True
        assert ApiVersion.model_validate(self.payload("unstable")).is_stable is False

    def test_is_current_tracks_sdk_default(self) -> None:
        assert DEFAULT_API_VERSION == "2026-10"
        assert ApiVersion.model_validate(self.payload("2026-10")).is_current is True
        # Old code hardcoded 2025-04.
        assert ApiVersion.model_validate(self.payload("2025-04")).is_current is False

    def test_is_current_follows_default_constant(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from shopify_partners_sdk.models.objects import version

        monkeypatch.setattr(version, "DEFAULT_API_VERSION", "2027-01")
        assert ApiVersion.model_validate(self.payload("2027-01")).is_current is True
        assert ApiVersion.model_validate(self.payload("2026-10")).is_current is False

    def test_docstring_is_not_stale(self) -> None:
        assert "2025-04" not in (ApiVersion.is_current.__doc__ or "")


class TestInputs:
    def test_money_input_uppercases_currency(self) -> None:
        parsed = MoneyInput.model_validate({"amount": "9.99", "currencyCode": "usd"})
        assert parsed.currency_code == "USD"

    @pytest.mark.parametrize("code", ["US", "USDX", ""])
    def test_money_input_rejects_bad_currency_length(self, code: str) -> None:
        with pytest.raises(ValidationError):
            MoneyInput.model_validate({"amount": "1", "currencyCode": code})

    def test_credit_create_input_dumps_graphql_aliases(self) -> None:
        payload = AppCreditCreateInput.model_validate(
            {
                "appId": "gid://partners/App/1",
                "shopId": "gid://partners/Shop/2",
                "amount": {"amount": "5.00", "currencyCode": "USD"},
                "description": "Thanks",
            }
        )
        assert payload.model_dump_graphql() == {
            "appId": "gid://partners/App/1",
            "shopId": "gid://partners/Shop/2",
            "amount": {"amount": "5.00", "currencyCode": "USD"},
            "description": "Thanks",
        }

    def test_credit_description_bounds(self) -> None:
        base = {
            "appId": "gid://partners/App/1",
            "shopId": "gid://partners/Shop/2",
            "amount": {"amount": "5", "currencyCode": "USD"},
        }
        AppCreditCreateInput.model_validate({**base, "description": "x" * 255})
        for bad in ("", "x" * 256):
            with pytest.raises(ValidationError):
                AppCreditCreateInput.model_validate({**base, "description": bad})

    def test_eventsink_url_must_be_http(self) -> None:
        base = {"appId": "gid://partners/App/1", "topic": "t"}
        EventsinkCreateInput.model_validate({**base, "url": "https://x.test/hook"})
        with pytest.raises(ValidationError):
            EventsinkCreateInput.model_validate({**base, "url": "ftp://x.test"})

    def test_pagination_limits_and_combinations(self) -> None:
        PaginationInput.model_validate({"first": 250}).validate_pagination_combination()
        with pytest.raises(ValidationError):
            PaginationInput.model_validate({"first": 251})
        with pytest.raises(ValidationError):
            PaginationInput.model_validate({"last": 0})
        for bad in (
            {"first": 1, "last": 1},
            {"after": "a", "before": "b"},
            {"first": 1, "before": "b"},
            {"last": 1, "after": "a"},
        ):
            with pytest.raises(ValueError):
                PaginationInput.model_validate(bad).validate_pagination_combination()

    def test_date_range(self) -> None:
        good = DateRangeInput.model_validate(
            {"min_date": "2025-01-01T00:00:00Z", "max_date": "2025-02-01T00:00:00Z"}
        )
        good.validate_date_range()
        with pytest.raises(ValidationError):
            DateRangeInput.model_validate({"min_date": "01/02/2025"})
        reversed_range = DateRangeInput.model_validate(
            {"min_date": "2025-02-01", "max_date": "2025-01-01"}
        )
        with pytest.raises(ValueError, match="before"):
            reversed_range.validate_date_range()
