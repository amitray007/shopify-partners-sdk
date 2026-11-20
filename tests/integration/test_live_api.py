"""Live checks against the real Partner API.

Skipped unless SHOPIFY_PARTNERS_LIVE_ORGANIZATION_ID and
SHOPIFY_PARTNERS_LIVE_ACCESS_TOKEN are set. The token needs read access to
apps and financials. Run with: pytest -m integration --no-cov
"""

import os

import pytest

from shopify_partners_sdk import CommonFields, FieldSelector, ShopifyPartnersClient

pytestmark = pytest.mark.integration

# Read at import, before the autouse conftest fixture clears SHOPIFY_PARTNERS_*.
ORG = os.environ.get("SHOPIFY_PARTNERS_LIVE_ORGANIZATION_ID")
TOKEN = os.environ.get("SHOPIFY_PARTNERS_LIVE_ACCESS_TOKEN")

requires_credentials = pytest.mark.skipif(
    not (ORG and TOKEN), reason="live Partner API credentials not set"
)


@pytest.fixture
def client() -> ShopifyPartnersClient:
    return ShopifyPartnersClient(organization_id=ORG, access_token=TOKEN)  # type: ignore[arg-type]


@requires_credentials
def test_2026_10_is_a_supported_version(client):
    data = client.query("publicApiVersions", FieldSelector(["handle", "supported"]))
    versions = {v["handle"]: v["supported"] for v in data["publicApiVersions"]}
    assert versions.get("2026-10") is True


@requires_credentials
def test_transactions_query_is_accepted(client):
    data = client.connection_query(
        "transactions", CommonFields.basic_transaction(), first=1
    )
    assert "edges" in data["transactions"]


@requires_credentials
def test_events_query_is_accepted(client):
    node = FieldSelector(["id", "eventType", "occurredAt"]).add_interface_field(
        "Charge", FieldSelector(["chargeType"]).add_money_field("amount")
    )
    events = list(client.paginate("events", node, page_size=5, max_pages=1))
    assert all("eventType" in e for e in events)
