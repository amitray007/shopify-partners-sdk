# Contributing to Shopify Partners SDK

Thank you for helping. This guide covers setup, checks, and the steps for new API versions. Report unacceptable behavior to the [maintainer](mailto:mail@amitray.dev). Be respectful and constructive.

## Setup

You need Python 3.11 or later and [Poetry](https://python-poetry.org/). CI tests Python 3.11 to 3.14.

```bash
git clone https://github.com/your-username/shopify-partners-sdk.git
cd shopify-partners-sdk
poetry install --with dev
poetry run pytest --version
```

## Make a change

1. Open an issue first for a large change.
2. Create a branch: `git checkout -b feat/your-change`.
3. Write the change and its tests.
4. Run the checks below.
5. Commit with a [conventional commit](https://www.conventionalcommits.org/) message: `feat:`, `fix:`, `docs:`, `refactor:`, `test:`, or `chore:`.
6. Open a pull request. Describe the problem, the fix, and how you tested it. Note any breaking change.

## Checks

CI runs these on every pull request. Run them before you push.

```bash
poetry run ruff check src tests schema/utils/build_sdk_schema.py
poetry run black --check src tests schema/utils/build_sdk_schema.py
poetry run mypy src
poetry run pytest
```

Useful `pytest` commands:

```bash
poetry run pytest tests/unit/test_schema.py   # one file
poetry run pytest -m unit                     # unit tests only
poetry run pytest --cov=shopify_partners_sdk  # coverage (on by default)
```

Unit tests run offline. Live tests in `tests/integration` run only when you set both variables. The token needs read access to apps and financials.

```bash
export SHOPIFY_PARTNERS_LIVE_ORGANIZATION_ID=123456
export SHOPIFY_PARTNERS_LIVE_ACCESS_TOKEN=prtapi_...
poetry run pytest -m integration --no-cov
```

## Code style

- Black formatting, 88 columns. Ruff for linting and import order.
- Type hints on all public APIs. `mypy` must pass on `src`.
- Use built-in generics (`dict[str, Any]`, `list[str]`) and `X | None`.
- Write tests for new behavior. Mock HTTP calls. Do not call the live API from unit tests.

## Add a new API version

Shopify ships a Partners API version each quarter. The SDK bundles one schema file per version.

1. Get the introspection result for the new version. Use the introspection query in [schema/README.md](schema/README.md) against `https://partners.shopify.com/{organization_id}/api/{version}/graphql`, or copy it from a published source. Save it as `schema/versions/<version>/introspection.json`.
2. Add the version to `SUPPORTED_VERSIONS` in `schema/utils/build_sdk_schema.py`. Remove versions Shopify retired.
3. Generate the bundled schema from the repository root:

   ```bash
   python schema/utils/build_sdk_schema.py            # all supported versions
   python schema/utils/build_sdk_schema.py 2027-04    # one version
   ```

   The generator writes `src/shopify_partners_sdk/schema/data/partner_<version>.json`.
4. To change the default, set `DEFAULT_API_VERSION` in `src/shopify_partners_sdk/config/defaults.py`. Update the expected values in `tests/unit/test_schema.py` to match.
5. Run `poetry run pytest`. `tests/unit/test_schema.py` and `tests/unit/test_enums.py` fail when the bundled schema, the supported list, the default, or the Python enums drift apart. Fix each failure.
6. Update examples in `README.md` for removed or renamed fields. Run each one against the new schema.

## Report an issue

Search existing issues first. Include the SDK version, the Python version, the API version, a minimal reproduction, and the full error message. For a security issue, email the maintainer instead of opening a public issue.

## License

By contributing, you agree to license your work under the MIT License.
