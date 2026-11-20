# Shopify Partners SDK

[![PyPI version](https://badge.fury.io/py/shopify-partners-sdk.svg)](https://badge.fury.io/py/shopify-partners-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/shopify-partners-sdk.svg)](https://pypi.org/project/shopify-partners-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python client for the Shopify Partners GraphQL API. It builds queries from a field selector, checks them against the bundled API schema before it sends a request, and pages through connections for you. It targets API version 2026-10 and needs Python 3.11 or later.

## What it does

- Schema validation. The SDK bundles the Partners API schema for each supported version. A misspelled query, field, argument, or enum value raises `SchemaValidationError` with a "Did you mean ...?" suggestion. No request goes out.
- Two query styles. Build queries with `FieldSelector`, or send raw GraphQL.
- Pagination. `client.paginate()` yields every node of a connection.
- Rate limiting and retries. A token bucket and exponential backoff protect your quota.
- Typed. The package ships `py.typed`.

## Installation

```bash
pip install shopify-partners-sdk
# or
poetry add shopify-partners-sdk
```

For development setup, see [CONTRIBUTING.md](CONTRIBUTING.md).

## Quick start

Get your credentials in the [Partner Dashboard](https://partners.shopify.com/): Settings → API credentials. Create or select a credential, then copy the Organization ID (digits only) and the Access Token (starts with `prtapi_`).

```python
from shopify_partners_sdk import FieldSelector, ShopifyPartnersClient

with ShopifyPartnersClient(
    organization_id="123456",
    access_token="prtapi_your-access-token",
) as client:
    fields = FieldSelector().add_fields("id", "name", "apiKey")
    result = client.query("app", fields, id="gid://partners/App/123")
    print(result["app"]["name"])
```

Raw GraphQL works too. `execute_raw` returns the response with its `data` key and raises `GraphQLError` when the response has errors.

```python
query = """
query GetApp($id: ID!) {
  app(id: $id) {
    id
    name
    apiKey
  }
}
"""
response = client.execute_raw(query, {"id": "gid://partners/App/123"})
print(response["data"]["app"]["name"])
```

### API versions

The default version is 2026-10. Pass `api_version` or set `SHOPIFY_PARTNERS_API_VERSION` to pick another one. The constructor argument wins.

```python
from shopify_partners_sdk import SUPPORTED_API_VERSIONS

print(SUPPORTED_API_VERSIONS)
# ('2026-01', '2026-04', '2026-07', '2026-10', '2027-01', 'unstable')

client = ShopifyPartnersClient(
    organization_id="123456",
    access_token="prtapi_your-access-token",
    api_version="2026-07",
)
print(client.api_version)
```

The SDK rejects any other version, including 2024-10 to 2025-07, with a `ValueError`.

### Credentials from the environment

Any argument you leave out comes from its `SHOPIFY_PARTNERS_*` environment variable, or from a local `.env` file:

```bash
export SHOPIFY_PARTNERS_ORGANIZATION_ID="123456"
export SHOPIFY_PARTNERS_ACCESS_TOKEN="prtapi_your-access-token"
export SHOPIFY_PARTNERS_API_VERSION="2026-10"   # optional
```

```python
client = ShopifyPartnersClient()
```

Arguments you pass win over the environment. The other settings (timeouts, retries, page size) read their `SHOPIFY_PARTNERS_*` variables the same way.

## Schema validation

Every builder checks names against the schema for the client's API version.

```python
from shopify_partners_sdk import SchemaValidationError

try:
    client.query("app", FieldSelector().add_fields("id", "nmae"), id="gid://partners/App/123")
except SchemaValidationError as error:
    print(error)  # Unknown field 'nmae' on type 'App'. Did you mean 'name'?
```

`SchemaValidationError` is also a `ValueError`. The builders type GraphQL variables from the schema, so `first=25` becomes `$first: Int` and the `appId` argument becomes `$appId: ID!`.

`client.schema` exposes the same data. For example, `client.schema.field("App", "events")` returns the field definition, and `client.schema.enum_values("EventOrder")` lists the allowed values.

## FieldSelector

```python
from shopify_partners_sdk import CommonFields, FieldSelector

# Scalar fields
fields = FieldSelector().add_fields("id", "name", "apiKey")
result = client.query("app", fields, id="gid://partners/App/123")

# Nested connection with arguments
event_fields = FieldSelector().add_fields("type", "occurredAt")
app_fields = (
    FieldSelector()
    .add_field("name")
    .add_connection_field("events", event_fields, first=10)
)
result = client.query("app", app_fields, id="gid://partners/App/123")

# Paginated connection with a preset
result = client.connection_query(
    "transactions", CommonFields.basic_transaction(), first=25
)
```

`Transaction` is an interface with only `id` and `createdAt`. Select the rest through inline fragments with `add_interface_field`:

```python
sale_fields = (
    FieldSelector()
    .add_money_field("grossAmount")  # adds amount and currencyCode
    .add_money_field("netAmount")
    .add_nested_field("shop", CommonFields.basic_shop())
)
transaction_fields = (
    CommonFields.basic_transaction()
    .add_interface_field("AppSubscriptionSale", sale_fields)
)
result = client.connection_query("transactions", transaction_fields, first=50)
```

The presets in `CommonFields`:

| Preset | Fields |
| --- | --- |
| `basic_app()` | `id`, `name`, `apiKey` |
| `basic_shop()` | `id`, `name`, `myshopifyDomain` |
| `basic_transaction()` | `id`, `createdAt`, `__typename` |
| `basic_node()` | `id` |
| `money_fields()` | `amount`, `currencyCode` |
| `page_info()` | pagination fields |
| `user_error()` | `field`, `message` |

### Pagination

`paginate()` requests pages as needed and yields each node. Pass `page_size` and `max_pages` to bound the work. Other keyword arguments go to the query.

```python
event_fields = FieldSelector().add_fields("id", "eventType", "occurredAt")

for event in client.paginate(
    "events",
    event_fields,
    page_size=50,
    max_pages=10,
    filter={"eventTypes": ["RELATIONSHIP_INSTALLED"]},
):
    print(event["id"], event["occurredAt"])
```

### Events

`events` returns a `PartnerEvent` interface. Its types are `Charge`, `Credit`, `Earning`, `Relationship`, and `SubscriptionStatus`. Select type-specific fields with fragments.

```python
event_fields = (
    FieldSelector()
    .add_fields("id", "eventType", "occurredAt")
    .add_interface_field("Relationship", FieldSelector().add_fields("state", "reason"))
    .add_interface_field("Charge", FieldSelector().add_money_field("amount"))
)
result = client.connection_query(
    "events", event_fields, first=25, orderBy="OCCURRED_AT_DESC"
)
```

## Raw GraphQL

```python
query = """
query GetApiVersions {
  publicApiVersions {
    handle
    displayName
    supported
  }
}
"""
versions = client.execute_raw(query)["data"]["publicApiVersions"]

query = """
query GetTransactions($first: Int) {
  transactions(first: $first) {
    edges {
      cursor
      node {
        id
        createdAt
        ... on AppSubscriptionSale {
          netAmount { amount currencyCode }
        }
      }
    }
    pageInfo {
      hasNextPage
    }
  }
}
"""
transactions = client.execute_raw(query, {"first": 25})["data"]["transactions"]

query = """
query ActiveSubscription($appId: ID!, $shopId: ID!) {
  activeSubscription(appId: $appId, shopId: $shopId) {
    billingPeriod
    cancelAtEndOfCycle
    trialEndsAt
  }
}
"""
variables = {"appId": "gid://partners/App/123", "shopId": "gid://partners/Shop/456"}
subscription = client.execute_raw(query, variables)["data"]["activeSubscription"]
```

Raw strings skip the SDK's schema checks. The API validates them.

## Mutations

The 2026-10 mutations take flat arguments. They have no `input:` object.

```python
result_fields = (
    FieldSelector()
    .add_nested_field(
        "appCredit",
        FieldSelector().add_fields("id", "name").add_money_field("amount"),
    )
    .add_nested_field("userErrors", CommonFields.user_error())
)

result = client.mutation(
    "appCreditCreate",
    result_fields,
    appId="gid://partners/App/123",
    shopId="gid://partners/Shop/456",
    description="Refund for billing issue",
    amount={"amount": "10.00", "currencyCode": "USD"},
)

payload = result["appCreditCreate"]
if payload["userErrors"]:
    print("Errors:", payload["userErrors"])
else:
    print("Credit created:", payload["appCredit"])
```

Cancel a subscription with `appSubscriptionCancel`. All five arguments are required.

```python
result_fields = (
    FieldSelector()
    .add_nested_field(
        "appSubscription",
        FieldSelector().add_fields("cancelledAt", "cancelAtEndOfCycle"),
    )
    .add_nested_field("userErrors", CommonFields.user_error())
)
result = client.mutation(
    "appSubscriptionCancel",
    result_fields,
    appId="gid://partners/App/123",
    shopId="gid://partners/Shop/456",
    prorate=True,
    deferCancellation=False,
    skipFinalUsageCharge=False,
)
```

Raw form of the first mutation:

```python
mutation = """
mutation CreateCredit(
  $appId: ID!, $shopId: ID!, $description: String!, $amount: MoneyInput!
) {
  appCreditCreate(
    appId: $appId, shopId: $shopId, description: $description, amount: $amount
  ) {
    appCredit { id name }
    userErrors { field message }
  }
}
"""
response = client.execute_raw(
    mutation,
    {
        "appId": "gid://partners/App/123",
        "shopId": "gid://partners/Shop/456",
        "description": "Refund for billing issue",
        "amount": {"amount": "10.00", "currencyCode": "USD"},
    },
)
```

## Error handling

```python
from shopify_partners_sdk.exceptions import (
    AuthenticationError,
    GraphQLError,
    RateLimitError,
)

try:
    result = client.query("app", FieldSelector().add_fields("id"), id="invalid-id")
except AuthenticationError:
    print("Invalid credentials")
except RateLimitError as error:
    print(f"Rate limited. Retry after: {error.retry_after} seconds")
except GraphQLError as error:
    print(f"GraphQL error: {error.message}")
```

## Custom HTTP session

Pass your own `requests.Session` to control proxies, adapters, or headers.

```python
import requests

session = requests.Session()
session.proxies = {"https": "http://proxy.example.com:8080"}

client = ShopifyPartnersClient(
    organization_id="123456",
    access_token="prtapi_your-access-token",
    http_client=session,
)
```

## Migrating to API 2026-10

Shopify changed the Partners API. Update your code in these places:

- Removed: `conversation`, `conversations`, `job`, `jobs`, and messages. The `apps` connection and the `title` and `handle` fields on `App` do not exist. `App` has `id`, `name`, `apiKey`, and `events`.
- Added: the `events` query with `PartnerEvent` types, the `activeSubscription` query, and the `appSubscriptionCancel` mutation. They exist from 2026-07. Versions 2026-01 and 2026-04 do not have them.
- Changed: `appCreditCreate` takes `appId`, `shopId`, `description`, `amount`, and `test` as separate arguments. `shopId` is required.
- Changed: `Transaction` is an interface with `id` and `createdAt`. Request amounts and shops through fragments such as `AppSubscriptionSale`.
- Removed from the SDK: the `shopify_partners_sdk.pagination` package. Use `client.paginate()`.
- Python: 3.11 or later.

Run your queries against the 2026-10 schema offline. The builders raise `SchemaValidationError` for anything the version no longer has.

## Reference

Core types in 2026-10: `App`, `Shop`, `Organization`, `Money`, `Transaction` (interface), `PartnerEvent` (interface), `AppEvent` (interface), `AppCharge` (interface), `AppCredit`, `AppSubscription`, `AppPurchaseOneTime`.

Common enums: `Currency`, `EventType`, `EventOrder` (`OCCURRED_AT_ASC`, `OCCURRED_AT_DESC`), `TransactionType`, `AppPricingInterval` (`EVERY_30_DAYS`, `ANNUAL`), `ChargeType`.

Use `client.schema.type("Name")` to inspect any type. The [Partners API reference](https://shopify.dev/docs/api/partners/reference) has the full list. Schema files and how to refresh them are in [schema/README.md](schema/README.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, checks, and the process for new API versions.

## License

MIT. See [LICENSE](LICENSE).

## Links

- [Shopify Partners API documentation](https://shopify.dev/docs/api/partners)
- [Issue tracker](https://github.com/amitray007/shopify-partners-sdk/issues)
- [Changelog](CHANGELOG.md)
