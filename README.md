# Shopify Partners SDK

[![PyPI version](https://badge.fury.io/py/shopify-partners-sdk.svg)](https://badge.fury.io/py/shopify-partners-sdk)
[![Python Support](https://img.shields.io/pypi/pyversions/shopify-partners-sdk.svg)](https://pypi.org/project/shopify-partners-sdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A simple and powerful Python SDK for the Shopify Partners API with two clean approaches to GraphQL queries.

## 🚀 Features

- **Two Simple Approaches** - Raw GraphQL queries or dynamic FieldSelector building
- **Type Safety** - Full type hints throughout the codebase
- **Automatic Pagination** - Built-in cursor-based pagination support with FieldSelector
- **Rate Limiting** - Intelligent rate limiting with exponential backoff
- **Comprehensive Error Handling** - Detailed error messages for GraphQL and HTTP errors
- **Synchronous API** - Simple, synchronous Python interface
- **No Complex Abstractions** - Direct access to GraphQL with minimal overhead
- **Extensible** - Easy to extend with custom field selections

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
git clone https://github.com/your-org/shopify-partners-sdk.git
cd shopify-partners-sdk

# Install with Poetry
poetry install

# Or with pip in development mode
pip install -e .
```

## 🔧 Quick Setup

### 1. Get Your Credentials

You'll need:
- **Organization ID**: Your Shopify Partners organization ID
- **Access Token**: A Partners API access token (starts with `prtapi_`)

You can find these in your [Shopify Partners Dashboard](https://partners.shopify.com/):
1. Go to Settings → API credentials
2. Create a new API credential or use an existing one
3. Note your Organization ID and Access Token

### 2. Basic Usage

The SDK provides two ways to interact with the Shopify Partners API:

#### Option 1: Raw GraphQL Queries

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
result = client.execute_query(query, {"id": "your-app-id"})
print(f"App: {result['app']['title']}")

client.close()
```

#### Option 2: FieldSelector (Dynamic Query Building)

```python
from shopify_partners_sdk import ShopifyPartnersClient, FieldSelector

# Initialize the client
client = ShopifyPartnersClient(
    organization_id="your-org-id",
    access_token="prtapi_your-access-token",
    api_version="2025-04"
)

# Build query dynamically with FieldSelector
fields = FieldSelector().add_fields('id', 'title', 'handle')
query_builder = client.field_based.query('app', fields, id='your-app-id')
result = client.field_based.execute_query_builder(query_builder)
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
result = client.execute_query(query, {"id": "app-id"})
app = result["app"]

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
result = client.execute_query(query)
versions = result["publicApiVersions"]

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
    }
  }
}
"""
result = client.execute_query(query, {"first": 25})
apps = result["apps"]
```

### FieldSelector Approach

```python
from shopify_partners_sdk import FieldSelector, CommonFields

# Simple query
fields = FieldSelector().add_fields('id', 'title', 'handle', 'apiKey')
query = client.field_based.query('app', fields, id='app-id')
result = client.field_based.execute_query_builder(query)

# Query with nested fields
app_fields = (FieldSelector()
    .add_fields('id', 'title', 'handle')
    .add_nested_field('shop', FieldSelector().add_fields('name', 'myshopifyDomain')))
query = client.field_based.query('app', app_fields, id='app-id')
result = client.field_based.execute_query_builder(query)

# Paginated connection query
app_fields = CommonFields.basic_app()  # Predefined common fields
query = client.field_based.connection_query('apps', app_fields, first=25)
result = client.field_based.execute_query_builder(query)

# Complex nested query with money fields
transaction_fields = (FieldSelector()
    .add_fields('id', 'createdAt', 'type')
    .add_money_field('netAmount')  # Automatically adds amount and currencyCode
    .add_nested_field('app', CommonFields.basic_app())
    .add_nested_field('shop', CommonFields.basic_shop()))

query = client.field_based.connection_query('transactions', transaction_fields, first=50)
result = client.field_based.execute_query_builder(query)
```

### Mutations

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

result = client.execute_query(mutation, {"input": input_data})
```

#### FieldSelector Mutations

```python
# Create an app credit with FieldSelector
result_fields = (FieldSelector()
    .add_nested_field('appCredit', FieldSelector()
        .add_fields('id', 'description')
        .add_money_field('amount'))
    .add_nested_field('userErrors', FieldSelector()
        .add_fields('field', 'message')))

mutation = client.field_based.mutation('appCreditCreate', result_fields)
mutation = mutation.with_input_variable(input_data)
result = client.field_based.execute_mutation_builder(mutation)

if result.get("userErrors"):
    print("Errors:", result["userErrors"])
else:
    print("Credit created:", result["appCredit"])
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
    # Raw GraphQL approach
    query = """
    query GetApp($id: ID!) {
      app(id: $id) { id title }
    }
    """
    result = client.execute_query(query, {"id": "invalid-id"})
except AuthenticationError:
    print("Invalid credentials")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except ValidationError as e:
    print(f"Query validation failed: {e.message}")
except GraphQLError as e:
    print(f"GraphQL error: {e.message}")
```

### Schema Validation

```python
from shopify_partners_sdk.schema import GraphQLSchema, FieldValidator

# Validate types
print("App type exists:", GraphQLSchema.validate_type("App"))
print("Currency is enum:", GraphQLSchema.is_enum_type("Currency"))

# Validate fields
app_validator = FieldValidator("App")
print("Valid field:", app_validator.validate_field("name"))  # True
print("Invalid field:", app_validator.validate_field("title"))  # False - will raise ValidationError

# Get available fields
app_type = GraphQLSchema.get_type("App")
print("Available fields:", app_type.get_available_fields())
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
git clone https://github.com/your-org/shopify-partners-sdk.git
cd shopify-partners-sdk

# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=shopify_partners_sdk --cov-report=html

# Run specific test types
poetry run pytest -m unit
poetry run pytest -m integration
```

### Code Quality

```bash
# Format code
poetry run black src tests
poetry run isort src tests

# Lint code
poetry run ruff check src tests
poetry run mypy src

# Run all quality checks
poetry run pre-commit run --all-files
```

### Building Documentation

```bash
# Install docs dependencies
poetry install --with docs

# Serve docs locally
poetry run mkdocs serve

# Build docs
poetry run mkdocs build
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

## ❓ Support

- 📖 [Documentation](https://shopify-partners-sdk.readthedocs.io)
- 🐛 [Issue Tracker](https://github.com/your-org/shopify-partners-sdk/issues)
- 💬 [Discussions](https://github.com/your-org/shopify-partners-sdk/discussions)

## 🙏 Acknowledgments

- Built with [httpx](https://www.python-httpx.org/) for HTTP client functionality
- Uses [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation and settings
- Inspired by the official Shopify GraphQL APIs

---

Made with ❤️ for the Shopify developer community
