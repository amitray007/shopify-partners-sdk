"""Pydantic models must describe real Partner API fields."""

from pydantic import BaseModel
import pytest

import shopify_partners_sdk.models.objects as objects
from shopify_partners_sdk.models.objects import (
    App,
    AppCredit,
    RelationshipInstalled,
    RelationshipUninstalled,
    SubscriptionChargeAccepted,
    TaxTransaction,
)
from shopify_partners_sdk.schema import load_schema

pytestmark = pytest.mark.unit

STABLE = load_schema("2026-10")
UNSTABLE = load_schema("unstable")

# Optional cursors exist on HistoricalEventsPageInfo; the Edge/Connection wrappers
# and these classes are SDK conveniences rather than schema types.
ALLOWED_EXTRA = {("PageInfo", "startCursor"), ("PageInfo", "endCursor")}


def schema_models() -> list[type[BaseModel]]:
    names = set(STABLE.type_names())
    return [
        value
        for name, value in sorted(vars(objects).items())
        if isinstance(value, type) and issubclass(value, BaseModel) and name in names
    ]


def wire_names(model: type[BaseModel]) -> dict[str, bool]:
    """Map each field's API name to whether the model requires it."""
    result = {}
    for name, info in model.model_fields.items():
        alias = info.alias or name
        if info.validation_alias is not None and hasattr(
            info.validation_alias, "choices"
        ):
            alias = info.validation_alias.choices[-1]
        result[str(alias)] = info.is_required()
    return result


@pytest.mark.parametrize("model", schema_models(), ids=lambda m: m.__name__)
def test_every_model_field_exists_in_the_api(model):
    name = model.__name__
    stable_fields = STABLE.type(name).get("fields", {})
    unstable_fields = (
        UNSTABLE.type(name).get("fields", {}) if name in UNSTABLE.type_names() else {}
    )
    unknown = [
        field
        for field in wire_names(model)
        if field not in stable_fields
        and field not in unstable_fields
        and (name, field) not in ALLOWED_EXTRA
    ]
    assert unknown == []


@pytest.mark.parametrize("model", schema_models(), ids=lambda m: m.__name__)
def test_required_model_fields_are_non_null_in_the_api(model):
    """A required model field the API may omit or null makes real payloads fail."""
    fields = STABLE.type(model.__name__).get("fields", {})
    too_strict = [
        field
        for field, required in wire_names(model).items()
        if required and field in fields and not fields[field]["type"].endswith("!")
    ]
    too_strict += [
        field
        for field, required in wire_names(model).items()
        if required and field not in fields
    ]
    assert too_strict == []


SHOP = {
    "id": "gid://partners/Shop/1",
    "name": "Demo",
    "myshopifyDomain": "demo.myshopify.com",
}
APP = {"id": "gid://partners/App/2", "name": "Widget", "apiKey": "abc"}
MONEY = {"amount": "9.99", "currencyCode": "USD"}


class TestRealPayloads:
    """Payloads shaped like Partner API responses for the fields they select."""

    def test_app_without_events(self):
        """Regression: App.events was required, so plain app queries failed to parse."""
        app = App.model_validate(APP)
        assert app.events is None

    def test_relationship_installed_event(self):
        """Regression: every AppEvent model required an id the API never returns."""
        event = RelationshipInstalled.model_validate(
            {
                "type": "RELATIONSHIP_INSTALLED",
                "occurredAt": "2026-10-01T00:00:00Z",
                "app": APP,
                "shop": SHOP,
            }
        )
        assert event.shop.myshopify_domain == "demo.myshopify.com"

    def test_uninstall_reason(self):
        event = RelationshipUninstalled.model_validate(
            {
                "type": "RELATIONSHIP_UNINSTALLED",
                "occurredAt": "2026-10-01T00:00:00Z",
                "app": APP,
                "shop": SHOP,
                "reason": "Too expensive",
                "description": None,
            }
        )
        assert event.reason == "Too expensive"

    def test_subscription_charge_event(self):
        event = SubscriptionChargeAccepted.model_validate(
            {
                "type": "SUBSCRIPTION_CHARGE_ACCEPTED",
                "occurredAt": "2026-10-01T00:00:00Z",
                "app": APP,
                "shop": SHOP,
                "charge": {
                    "id": "gid://partners/AppSubscription/3",
                    "name": "Pro",
                    "amount": MONEY,
                    "test": False,
                    "billingOn": None,
                },
            }
        )
        assert event.charge.name == "Pro"

    def test_app_credit_has_only_api_fields(self):
        """Regression: AppCredit required createdAt, app, and shop (not API fields)."""
        credit = AppCredit.model_validate(
            {
                "id": "gid://partners/AppCredit/4",
                "name": "Goodwill",
                "amount": MONEY,
                "test": True,
            }
        )
        assert credit.test is True

    @pytest.mark.parametrize("key", ["type", "taxType"])
    def test_tax_transaction_type(self, key):
        tax = TaxTransaction.model_validate(
            {
                "id": "gid://partners/TaxTransaction/5",
                "createdAt": "2026-10-01T00:00:00Z",
                "amount": MONEY,
                key: "SALE_SHOPIFY_FEE",
            }
        )
        assert tax.tax_type == "SALE_SHOPIFY_FEE"
