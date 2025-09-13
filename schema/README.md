# Shopify Partners API - GraphQL Schema Documentation

This directory contains comprehensive GraphQL schema analysis for the Shopify Partners API, including introspection data, analysis utilities, and generated documentation.

## Directory Structure

```
schema/
├── README.md                    # This file
├── utils/                       # Python analysis utilities
│   ├── README.md               # Utils documentation
│   ├── analyze_schema.py       # Original schema analysis script
│   ├── analyze_complete_schema.py
│   ├── build_detailed_queries.py
│   └── compare_schema_versions.py
├── analysis/                    # Generated analysis results
│   ├── README.md               # Analysis files documentation
│   ├── complete_field_structures.txt
│   ├── detailed_query_examples.md
│   ├── version_comparison.md
│   ├── schema_summary.txt
│   └── evolution_summary.txt
└── versions/                    # Schema version data
    ├── 2024-10/
    │   └── introspection.json
    ├── 2025-01/
    │   └── introspection.json
    ├── 2025-04/
    │   └── introspection.json
    ├── 2025-07/
    │   └── introspection.json
    └── unstable/
        └── introspection.json
```

## Quick Start

To generate fresh analysis from the schema files:

```bash
# Run all analysis utilities
cd schema/utils
python analyze_schema.py              # Original analysis script
python analyze_complete_schema.py     # Comprehensive analysis
python build_detailed_queries.py      # Detailed query examples
python compare_schema_versions.py     # Version comparison
```

This will regenerate all files in the `analysis/` directory.

## API Overview

### Current API (Unstable Version)
- **9 Queries:** app, conversation†, conversations†, eventsinks*, job†, jobs†, publicApiVersions, transaction, transactions
- **3 Mutations:** appCreditCreate, eventsinkCreate*, eventsinkDelete*
- **109 Types** including interfaces, objects, enums, and input types

*New in unstable version
†Deprecated as of 2024-01

### Key Features
- **Transaction Interface:** Polymorphic transaction types (AppOneTimeSale, ServiceSale, ThemeSale, etc.)
- **Connection Patterns:** Standardized GraphQL pagination
- **Event System:** App events with comprehensive filtering
- **Eventsink Integration:** Webhook management (unstable)

## Documentation

The complete API documentation is available in:
- **`../docs/shopify/queries.md`** - Primary documentation with complete examples
- **`analysis/detailed_query_examples.md`** - Raw generated examples
- **`analysis/complete_field_structures.txt`** - Technical field analysis

## Schema Versions

| Version | Queries | Mutations | Notes |
|---------|---------|-----------|-------|
| 2024-10 | 8 | 1 | Stable release |
| 2025-01 | 8 | 1 | No changes |
| 2025-04 | 8 | 1 | No changes |
| 2025-07 | 8 | 1 | No changes |
| unstable | 9 | 3 | Added eventsink functionality, enhanced transaction types |

### Major Changes in Unstable
- **New Eventsink Features:**
  - `eventsinks` query for webhook management
  - `eventsinkCreate` and `eventsinkDelete` mutations
  - Support for CUSTOMER_EVENTS_CREATE, CUSTOMERS_REDACT, DELIVERY_PROMISES_CREATE topics

- **Enhanced Transaction Types:**
  - Added `processingFee` and `regulatoryOperatingFee` fields to all sale types
  - Added `taxType` field to TaxTransaction
  - Affects: AppOneTimeSale, AppSaleAdjustment, AppSaleCredit, AppSubscriptionSale, AppUsageSale, ServiceSale, ServiceSaleAdjustment, ThemeSale, ThemeSaleAdjustment

## Interface Implementations

### Transaction Interface
The Transaction interface has 13 implementations:
- **App Transactions:** AppOneTimeSale, AppSaleAdjustment, AppSaleCredit, AppSubscriptionSale, AppUsageSale
- **Service Transactions:** ServiceSale, ServiceSaleAdjustment
- **Theme Transactions:** ThemeSale, ThemeSaleAdjustment
- **Other:** TaxTransaction, ReferralTransaction, ReferralAdjustment, LegacyTransaction

### Usage Example
```graphql
query TransactionQuery($id: ID!) {
  transaction(id: $id) {
    id
    createdAt
    ... on AppOneTimeSale {
      chargeId
      grossAmount { amount currencyCode }
      netAmount { amount currencyCode }
      processingFee { amount currencyCode }
      app { id name }
    }
    # ... other implementations
  }
}
```

## How to Get Schema for Specific Versions

1. Create a Partners API Client Token in the Partners Dashboard
2. Visit the Partners GraphiQL Explorer
3. Capture the network request to `https://partners.shopify.com/{organization_id}/api/{version}/graphql`
4. Use the introspection query below:

```json
{
  "query": "query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }",
  "operationName": "IntrospectionQuery"
}
```

## Integration

This schema analysis powers:
- **SDK Development:** Complete type definitions and operation signatures
- **Documentation Generation:** Automated API documentation
- **Testing:** Comprehensive coverage of all fields and operations
- **Version Migration:** Understanding of breaking changes and new features
