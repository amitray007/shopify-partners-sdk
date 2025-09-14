# Shopify Partners SDK

[![PyPI version](https://badge.fury.io/py/shopify-partners-sdk.svg)](https://badge.fury.io/py/shopify-partners-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/shopify-partners-sdk.svg)](https://pypi.org/project/shopify-partners-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

**Modern Python SDK for Shopify Partners API** - Comprehensive GraphQL client with type safety, automatic pagination, and dual query approaches (raw GraphQL + dynamic FieldSelector). Built for developers who want powerful functionality without complex abstractions.

## 🚀 Key Features

### 🎯 **Dual Query Approaches**
- **Raw GraphQL** - Execute queries directly with full control
- **Dynamic FieldSelector** - Build queries programmatically with type safety

### 🛡️ **Production-Ready**
- **Type Safety** - Full type hints throughout the codebase
- **Automatic Pagination** - Built-in cursor-based pagination support
- **Intelligent Rate Limiting** - Exponential backoff with retry logic
- **Comprehensive Error Handling** - Detailed GraphQL and HTTP error messages

### 🚀 **Developer Experience**
- **Zero Complex Abstractions** - Direct GraphQL access with minimal overhead
- **Synchronous API** - Simple, intuitive Python interface
- **Extensible Architecture** - Easy to extend with custom field selections
- **Rich Documentation** - Comprehensive examples and API reference

## 📦 Installation

### Using pip

```bash
pip install shopify-partners-sdk
```

### Using Poetry

```bash
poetry add shopify-partners-sdk
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/amitray007/shopify-partners-sdk.git
cd shopify-partners-sdk

# Install with Poetry
poetry install

# Or with pip in development mode
pip install -e .
```

## ⚡ Quick Start

### 1. Get Your Credentials

Get your credentials from the [Shopify Partners Dashboard](https://partners.shopify.com/):
1. **Settings** → **API credentials**
2. Create or select an API credential
3. Copy your **Organization ID** and **Access Token** (starts with `prtapi_`)

### 2. Choose Your Approach

The SDK provides two ways to interact with the Shopify Partners API:

#### 🎯 Option 1: FieldSelector (Recommended)

```python
from shopify_partners_sdk import ShopifyPartnersClient, FieldSelector

# Initialize the client
client = ShopifyPartnersClient(
    organization_id="your-org-id",
    access_token="prtapi_your-access-token",
    api_version="2025-04"
)

# Build and execute query with FieldSelector
fields = FieldSelector().add_fields('id', 'title', 'handle')
result = client.query('app', fields, id='your-app-id')
print(f"App: {result['app']['title']}")

client.close()
```

#### 🔧 Option 2: Raw GraphQL

```python
from shopify_partners_sdk import ShopifyPartnersClient

# Initialize the client
client = ShopifyPartnersClient(
    organization_id="your-org-id",
    access_token="prtapi_your-access-token",
    api_version="2025-04"
)

# Execute raw GraphQL
query = """
query GetApp($id: ID!) {
  app(id: $id) {
    id
    title
    handle
  }
}
"""
response = client.execute_raw(query, {"id": "your-app-id"})
result = response["data"]
print(f"App: {result['app']['title']}")

client.close()
```

### 3. Environment Variables

You can also configure the client using environment variables:

```bash
export SHOPIFY_PARTNERS_ORGANIZATION_ID="your-org-id"
export SHOPIFY_PARTNERS_ACCESS_TOKEN="prtapi_your-access-token"
export SHOPIFY_PARTNERS_API_VERSION="2025-04"
```

```python
from shopify_partners_sdk import ShopifyPartnersClient

# Client will automatically use environment variables
client = ShopifyPartnersClient()
```

## 📚 Usage Examples

### FieldSelector Approach (Recommended)

```python
from shopify_partners_sdk import FieldSelector, CommonFields

# Simple query
fields = FieldSelector().add_fields('id', 'title', 'handle', 'apiKey')
result = client.query('app', fields, id='app-id')

# Query with nested fields
app_fields = (FieldSelector()
    .add_fields('id', 'title', 'handle')
    .add_nested_field('shop', FieldSelector().add_fields('name', 'myshopifyDomain')))
result = client.query('app', app_fields, id='app-id')

# Paginated connection query
app_fields = CommonFields.basic_app()  # Predefined common fields
result = client.connection_query('apps', app_fields, first=25)

# Complex nested query with money fields
transaction_fields = (FieldSelector()
    .add_fields('id', 'createdAt', 'type')
    .add_money_field('netAmount')  # Automatically adds amount and currencyCode
    .add_nested_field('app', CommonFields.basic_app())
    .add_nested_field('shop', CommonFields.basic_shop()))

result = client.connection_query('transactions', transaction_fields, first=50)

# Complex query with nested connections
event_fields = FieldSelector().add_field('type')
app_fields = (FieldSelector()
    .add_field('name')
    .add_connection_field('events', event_fields, first=10))  # Connection with args
result = client.query('app', app_fields, id='app-id')
```

### Raw GraphQL Approach

```python
# Get a single app
query = """
query GetApp($id: ID!) {
  app(id: $id) {
    id
    title
    handle
    apiKey
  }
}
"""
response = client.execute_raw(query, {"id": "app-id"})
app = response["data"]["app"]

# Get API versions
query = """
query GetApiVersions {
  publicApiVersions {
    handle
    displayName
    supported
  }
}
"""
response = client.execute_raw(query)
versions = response["data"]["publicApiVersions"]

# Get paginated apps
query = """
query GetApps($first: Int!, $after: String) {
  apps(first: $first, after: $after) {
    edges {
      cursor
      node {
        id
        title
        handle
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
    }
  }
}
"""
response = client.execute_raw(query, {"first": 25})
apps = response["data"]["apps"]
```

### Mutations

#### FieldSelector Mutations (Recommended)

```python
# Create an app credit with FieldSelector
result_fields = (FieldSelector()
    .add_nested_field('appCredit', FieldSelector()
        .add_fields('id', 'description')
        .add_money_field('amount'))
    .add_nested_field('userErrors', FieldSelector()
        .add_fields('field', 'message')))

input_data = {
    "appId": "your-app-id",
    "amount": {"amount": "10.00", "currencyCode": "USD"},
    "description": "Refund for billing issue"
}

result = client.mutation('appCreditCreate', result_fields, input=input_data)

if result.get("userErrors"):
    print("Errors:", result["userErrors"])
else:
    print("Credit created:", result["appCredit"])
```

#### Raw GraphQL Mutations

```python
# Create an app credit
mutation = """
mutation CreateAppCredit($input: AppCreditCreateInput!) {
  appCreditCreate(input: $input) {
    appCredit {
      id
      description
      amount {
        amount
        currencyCode
      }
    }
    userErrors {
      field
      message
    }
  }
}
"""

input_data = {
    "appId": "your-app-id",
    "amount": {"amount": "10.00", "currencyCode": "USD"},
    "description": "Refund for billing issue"
}

response = client.execute_raw(mutation, {"input": input_data})
result = response["data"]
```

## 🏗️ Advanced Usage

### Custom HTTP Client

```python
import requests
from shopify_partners_sdk import ShopifyPartnersClient

# Custom HTTP client with specific settings
session = requests.Session()
session.timeout = 60.0

client = ShopifyPartnersClient(
    organization_id="your-org-id",
    access_token="your-token",
    http_client=session
)
```

### Error Handling

```python
from shopify_partners_sdk.exceptions import (
    AuthenticationError,
    RateLimitError,
    GraphQLError
)

try:
    # FieldSelector approach
    fields = FieldSelector().add_fields('id', 'title')
    result = client.query('app', fields, id='invalid-id')
except AuthenticationError:
    print("Invalid credentials")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except GraphQLError as e:
    print(f"GraphQL error: {e.message}")

try:
    # Raw GraphQL approach
    query = """
    query GetApp($id: ID!) {
      app(id: $id) { id title }
    }
    """
    response = client.execute_raw(query, {"id": "invalid-id"})
    if response.get("errors"):
        print("GraphQL errors:", response["errors"])
    else:
        result = response["data"]
except AuthenticationError:
    print("Invalid credentials")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
```


### Configuration

```python
from shopify_partners_sdk.config import ShopifyPartnersSDKSettings

# Custom configuration
settings = ShopifyPartnersSDKSettings(
    organization_id="your-org-id",
    access_token="your-token",
    api_version="2025-04",
    base_url="https://partners.shopify.com",
    timeout_seconds=30.0,
    max_retries=3,
    log_level="INFO"
)

client = ShopifyPartnersClient.from_settings(settings)
```

## 🔍 Available Types and Fields

### Core Types

- **App**: `id`, `name`, `apiKey`, `events`
- **Shop**: `id`, `name`, `myshopifyDomain`, `avatarUrl`
- **Organization**: `id`, `name`, `avatarUrl`
- **Transaction**: `id`, `createdAt` (interface)
- **Money**: `amount`, `currencyCode`
- **AppEvent**: `type`, `occurredAt`, `app`, `shop` (interface)

### Billing Types

- **AppCharge**: `id`, `amount`, `name`, `test` (interface)
- **AppCredit**: `id`, `amount`, `name`, `test`
- **AppSubscription**: `id`, `amount`, `name`, `test`, `billingOn`
- **AppPurchaseOneTime**: `id`, `amount`, `name`, `test`

### Enums

- **Currency**: `USD`, `EUR`, `GBP`, `CAD`, `AUD`, etc.
- **AppEventTypes**: `RELATIONSHIP_INSTALLED`, `CREDIT_APPLIED`, `SUBSCRIPTION_CHARGE_ACCEPTED`, etc.
- **TransactionType**: `APP_ONE_TIME_SALE`, `APP_SUBSCRIPTION_SALE`, `SERVICE_SALE`, etc.
- **AppPricingInterval**: `EVERY_30_DAYS`, `ANNUAL`

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/amitray007/shopify-partners-sdk.git
cd shopify-partners-sdk

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

## 🤝 Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`poetry run pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- [Shopify Partners API Documentation](https://shopify.dev/docs/api/partners)
- [GraphQL Schema Reference](https://shopify.dev/docs/api/partners/reference)
- [Shopify Partners Dashboard](https://partners.shopify.com/)

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

## 💬 Community & Support

- 📖 **[Documentation](https://shopify-partners-sdk.readthedocs.io)** - Comprehensive guides and API reference
- 🐛 **[Issue Tracker](https://github.com/amitray007/shopify-partners-sdk/issues)** - Bug reports and feature requests
- 💬 **[Discussions](https://github.com/amitray007/shopify-partners-sdk/discussions)** - Community Q&A and support
- 🚀 **[Examples](https://github.com/amitray007/shopify-partners-sdk/tree/main/examples)** - Real-world usage examples

## 🙏 Acknowledgments

- Built with [Requests](https://requests.readthedocs.io/) for reliable HTTP client functionality
- Uses [Pydantic](https://docs.pydantic.dev/) for data validation and settings management
- Inspired by the official Shopify GraphQL APIs and developer feedback

---

<div align="center">

**Made with ❤️ for the Shopify developer community**

[⭐ Star this repo](https://github.com/amitray007/shopify-partners-sdk) • [🐛 Report Bug](https://github.com/amitray007/shopify-partners-sdk/issues) • [💡 Request Feature](https://github.com/amitray007/shopify-partners-sdk/issues)

</div>
