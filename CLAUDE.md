# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the **Shopify Partners SDK** - a Python client library for the Shopify Partners API. It provides a simple, intuitive interface to interact with Shopify's Partners GraphQL API with full schema validation and helpful error messages.

**Key Design Philosophy**: The SDK prioritizes simplicity and developer experience over complex abstractions, providing both a simple method-chaining API and comprehensive schema validation.

## Development Commands

### Environment Setup
```bash
# Install dependencies
poetry install

# Install with all development dependencies
poetry install --with dev,docs
```

### Code Quality & Linting
```bash
# Format code (primary formatter)
black src/

# Lint and fix automatically
ruff --fix src/

# Type checking
mypy src/

# Run all quality checks
poetry run ruff src/ && poetry run black --check src/ && poetry run mypy src/
```

### Testing
```bash
# Run all tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov=shopify_partners_sdk

# Run specific test file
poetry run pytest tests/test_specific.py

# Run tests by marker
poetry run pytest -m unit
poetry run pytest -m integration
```

## Architecture Overview

### Core Design Pattern: Schema-Driven Validation

The SDK implements a **two-tier architecture**:

1. **Simple Client Layer** (`__init__.py`): Primary user interface with method chaining
2. **Schema Validation Layer** (`schema/`): Comprehensive GraphQL schema validation

### Primary Entry Point

The main client class `ShopifyPartnersClient` is defined directly in `__init__.py` for easy importing:

```python
from shopify_partners_sdk import ShopifyPartnersClient

client = ShopifyPartnersClient(organization_id="...", access_token="...")
query = client.query("app", id="123").select("id", "title", "shop.name")
```

### Schema System Architecture (`schema/`)

The schema system provides build-time validation and field discovery:

- **`definitions.py`**: Complete GraphQL schema type definitions with all available types and their fields
- **`registry.py`**: Registry of available queries and mutations with metadata (arguments, pagination support, etc.)
- **`validators.py`**: Validation logic with intelligent error messages and field suggestions

### Query Building System (`queries/`)

Two query building approaches coexist:

1. **Primary: Schema-Driven Builders** (`builders.py`): Used by the main client, provides full validation
2. **Legacy: Custom Builders** (`custom_builders.py`): Flexible builders for advanced use cases

### Client Infrastructure (`client/`)

Core GraphQL client components:
- **`base.py`**: BaseGraphQLClient handles HTTP requests, authentication, and response parsing
- **`auth.py`**: Authentication validation and credential management
- **`rate_limiter.py`**: Token bucket rate limiting (4 req/sec) with burst capacity
- **`retry.py`**: Exponential backoff with jitter for resilience

### Key Design Decisions

#### Modern Python Typing
The codebase uses Python 3.9+ built-in generics (`dict[str, Any]`, `list[str]`) instead of deprecated `typing.Dict`, `typing.List`. This was systematically applied across the entire codebase.

#### Validation Strategy
- **Build-time validation**: Field names and query structure validated when building queries
- **Helpful errors**: Typos get intelligent suggestions (e.g., "Did you mean 'title' instead of 'titel'?")
- **Schema-aware**: All validation based on actual Shopify Partners API GraphQL schema

#### Client Design Philosophy
- **Method chaining**: Natural, discoverable API (`client.query().select().filter().paginate()`)
- **Field discovery**: Users can explore available fields (`client.query_fields("app")`)
- **No complex abstractions**: Avoid overengineering, keep the API intuitive

## Important Development Guidelines

### Typing Standards
- Always use built-in generics: `dict[str, Any]` not `Dict[str, Any]`
- Always use built-in generics: `list[str]` not `List[str]`
- Import only necessary typing constructs: `from typing import Optional, Union`

### Schema Validation Pattern
When modifying validation logic:
1. Update schema definitions in `schema/definitions.py` first
2. Update query/mutation registry in `schema/registry.py` if needed
3. Validation logic in `schema/validators.py` automatically uses updated definitions

### Query Builder Extensions
To add new query capabilities:
1. Add query definition to `QueryRegistry.QUERIES` in `schema/registry.py`
2. Add field definitions to `GraphQLSchema.TYPES` in `schema/definitions.py`
3. Validation and error handling automatically work

## File Structure Notes

### Main Package (`src/shopify_partners_sdk/`)
- **`__init__.py`**: Contains the main `ShopifyPartnersClient` class (not just exports)
- **`version.py`**: Simple version string
- **`py.typed`**: Indicates this is a typed package

### Legacy Components (For Backward Compatibility)
- **`client/field_based_client.py`**: Legacy field-based client (kept for compatibility)
- **`queries/custom_builders.py`**: Legacy custom query builders
- **`mutations/custom_builders.py`**: Legacy mutation builders

These can be removed in future major versions as they're superseded by the schema-driven approach.

### Examples and Documentation
- **`examples/`**: Real-world usage examples (revenue analytics, app lifecycle tracking, etc.)
- **`docs/`**: API research, schema analysis, and introspection documentation
- **`schema/`**: GraphQL schema analysis and version comparison tools

## Testing Strategy

The project uses pytest with specific markers:
- `@pytest.mark.unit`: Fast unit tests
- `@pytest.mark.integration`: Tests requiring API access
- `@pytest.mark.slow`: Long-running tests

Coverage target is maintained through pytest-cov with HTML reports.

## GraphQL Schema Maintenance

The project includes a specialized Claude Code agent (`graphql-schema-documenter`) for maintaining GraphQL schema documentation from introspection data. Use the Task tool with `subagent_type: "graphql-schema-documenter"` when schema updates are needed.

## Development Environment

- **Python 3.9+** (uses modern typing features)
- **Poetry** for dependency management
- **Async/await** throughout (requires asyncio-compatible testing)
- **Pydantic v2** for data validation
- **httpx** for HTTP client (async-first)