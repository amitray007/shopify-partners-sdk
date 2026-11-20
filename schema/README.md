# Shopify Partners API - GraphQL Schema Data

This directory holds the raw introspection data for each Partners API version, the script that compiles it into the schema the SDK bundles, and older analysis tools.

## Directory structure

```
schema/
├── README.md
├── utils/
│   ├── build_sdk_schema.py          # Compiles raw files into the SDK's bundled schema
│   ├── analyze_schema.py            # Analysis scripts (see utils/README.md)
│   ├── analyze_complete_schema.py
│   ├── build_detailed_queries.py
│   └── compare_schema_versions.py
├── analysis/                        # Generated analysis output (2024-10 to unstable)
└── versions/
    ├── 2024-10/ 2025-01/ 2025-04/ 2025-07/   # Retired. Kept for history. Not bundled.
    ├── 2026-01/ 2026-04/ 2026-07/            # Supported
    ├── 2026-10/                              # Default
    ├── 2027-01/                              # Release candidate
    └── unstable/
        └── introspection.json               # One raw file per version directory
```

## Supported versions

The SDK bundles 2026-01, 2026-04, 2026-07, 2026-10, 2027-01, and unstable. The default is 2026-10. The SDK rejects every other version.

| Version | Queries | Mutations |
|---------|---------|-----------|
| 2026-01, 2026-04 | `app`, `publicApiVersions`, `transaction`, `transactions` | `appCreditCreate` |
| 2026-07, 2026-10, 2027-01 | the above, plus `activeSubscription` and `events` | plus `appSubscriptionCancel` |
| unstable | the above, plus `appSubscriptionMigrationOperation`, `eventsinks`, `migratableAppSubscriptions`, `migratableAppSubscriptionsCount` | plus `appSubscriptionMigrationOperationCancel`, `appSubscriptionMigrationOperationCreate`, `eventsinkCreate`, `eventsinkDelete` |

Since 2026-01, `conversation`, `conversations`, `job`, and `jobs` do not exist. `App` has `id`, `name`, `apiKey`, and `events`. `Transaction` is an interface with `id` and `createdAt`.

## Provenance

The raw files for 2026-01 to unstable come from the data that ships in Shopify's `@shopify/dev-mcp` 1.19.0 npm package. That package carries the official Partners API introspection result for each version. The origin of the 2024-10 to 2025-07 files is not recorded.

## Build the bundled schema

The SDK does not read the raw files at runtime. It loads compact files from `src/shopify_partners_sdk/schema/data/partner_<version>.json`. Generate them from the repository root:

```bash
python schema/utils/build_sdk_schema.py            # all supported versions
python schema/utils/build_sdk_schema.py 2026-10    # selected versions
```

The script reads `schema/versions/<version>/introspection.json` and keeps what the SDK needs to type variables and validate selections. It lists the versions to build in `SUPPORTED_VERSIONS`. `tests/unit/test_schema.py` fails when a bundled file differs from its raw file. To add a version, follow "Add a new API version" in [CONTRIBUTING.md](../CONTRIBUTING.md).

## Capture a new introspection file

1. Create a Partners API client token in the Partner Dashboard.
2. Send the query below to `https://partners.shopify.com/{organization_id}/api/{version}/graphql` with the `X-Shopify-Access-Token` header.
3. Save the response as `schema/versions/<version>/introspection.json`.

```json
{
  "query": "query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }",
  "operationName": "IntrospectionQuery"
}
```

## Analysis scripts

The scripts in `utils/` write reports to `analysis/`. They cover the 2024-10 to unstable files and predate the 2026 versions. See [utils/README.md](utils/README.md).

```bash
cd schema/utils
python analyze_schema.py
python analyze_complete_schema.py
python build_detailed_queries.py
python compare_schema_versions.py
```
