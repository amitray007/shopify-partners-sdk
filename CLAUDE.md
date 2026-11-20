# CLAUDE.md

Guidance for agents working in this repository: a synchronous Python client for the Shopify
Partners GraphQL API (`requests`, Pydantic v2, Python 3.11+).

## Commands

```bash
poetry install --with dev
poetry run pytest                      # unit tests, offline (the default run)
poetry run pytest -m integration --no-cov   # live API; needs SHOPIFY_PARTNERS_LIVE_ORGANIZATION_ID and _ACCESS_TOKEN
poetry run ruff check src tests && poetry run black --check src tests && poetry run mypy src
```

CI (`.github/workflows/ci.yml`) runs the same checks on Python 3.11-3.14. mypy runs in strict
mode and is clean; keep it clean.

## How a request flows

1. `ShopifyPartnersClient` (`src/shopify_partners_sdk/__init__.py`) loads the bundled schema for
   its API version and owns a `FieldBasedShopifyPartnersClient`.
2. The field-based client creates an `OperationBuilder` subclass (`queries/custom_builders.py`,
   `mutations/custom_builders.py`). The builder takes every variable type from the schema and
   validates the `FieldSelector` tree while rendering (`queries/fields.py`).
3. `BaseGraphQLClient` (`client/base.py`) serializes variables (`values.py`), applies the rate
   limiter and retry handler, and maps HTTP and GraphQL errors to SDK exceptions.

Schema errors raise `SchemaValidationError` (a `ValueError`) before any network call. Keep
validation schema-driven: look types up in `PartnerSchema`; never infer a GraphQL type from a
Python value.

## Bundled schema: the single source of truth

- Raw introspection: `schema/versions/<version>/introspection.json`.
- Compact package data: `src/shopify_partners_sdk/schema/data/partner_<version>.json`, generated
  by `python schema/utils/build_sdk_schema.py`. Never edit the generated files by hand.
- `SUPPORTED_API_VERSIONS` is read from the data files present. Settings accept only those.

To add or update an API version: save the raw introspection, update `SUPPORTED_VERSIONS` in the
generator, run it, update `DEFAULT_API_VERSION` in `config/defaults.py`, then run the tests.
`tests/unit/test_schema.py` fails when generated data drifts from the raw files,
`test_enums.py` when `models/enums.py` drifts from the schema, and `test_models_schema.py` when a
model field does not exist in the API. Shopify's `@shopify/dev-mcp` npm package ships official
Partner API introspection in `dist/data/partner_<version>.json.gz`; that is the source when no
API token is at hand.

## Release gotcha

Every push to `main` runs `.github/workflows/release.yml`, which bumps the version, tags, and
publishes to PyPI. Merging a PR is a release.

## Conventions

- Built-in generics and `X | None` annotations.
- Tests: `pytestmark = pytest.mark.unit` per module, the scripted `FakeSession` from
  `tests/conftest.py` for HTTP, and expected values written as literals.
- `docs/` and `schema/analysis/` hold older research notes; the bundled schema wins when they
  disagree.
