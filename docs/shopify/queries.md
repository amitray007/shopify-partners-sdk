# Shopify Partners API - Complete GraphQL Documentation

This document provides comprehensive examples for all queries and mutations in the Shopify Partners API, including complete field structures, interface implementations, and variable documentation.

## QUERIES

### 1. App Query

Query for retrieving detailed information about a specific Shopify app.

```graphql
query AppQuery(
  $id: ID!,
  $first: Int,
  $before: String,
  $last: Int,
  $after: String,
  $eventTypes: [AppEventType!],
  $shopId: ID,
  $chargeId: ID,
  $occurredAtMin: DateTime,
  $occurredAtMax: DateTime
) {
  app(id: $id) {
    id
    apiKey
    name
    events(
      first: $first,
      before: $before,
      last: $last,
      after: $after,
      types: $eventTypes,
      shopId: $shopId,
      chargeId: $chargeId,
      occurredAtMin: $occurredAtMin,
      occurredAtMax: $occurredAtMax
    ) {
      edges {
        cursor
        node {
          occurredAt
          ... on CreditApplied {
            app {
              id
              apiKey
              name
            }
            appCredit {
              id
              amount {
                amount
                currencyCode
              }
              name
              description
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on CreditFailed {
            app {
              id
              apiKey
              name
            }
            appCredit {
              id
              amount {
                amount
                currencyCode
              }
              name
              description
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on CreditPending {
            app {
              id
              apiKey
              name
            }
            appCredit {
              id
              amount {
                amount
                currencyCode
              }
              name
              description
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on OneTimeChargeAccepted {
            app {
              id
              apiKey
              name
            }
            charge {
              id
              amount {
                amount
                currencyCode
              }
              name
              status
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on OneTimeChargeActivated {
            app {
              id
              apiKey
              name
            }
            charge {
              id
              amount {
                amount
                currencyCode
              }
              name
              status
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on RelationshipInstalled {
            app {
              id
              apiKey
              name
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on RelationshipUninstalled {
            app {
              id
              apiKey
              name
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on SubscriptionChargeAccepted {
            app {
              id
              apiKey
              name
            }
            charge {
              id
              amount {
                amount
                currencyCode
              }
              name
              status
              billingOn
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
          ... on UsageChargeApplied {
            app {
              id
              apiKey
              name
            }
            charge {
              id
              amount {
                amount
                currencyCode
              }
              name
              description
            }
            shop {
              id
              avatarUrl
              myshopifyDomain
              name
            }
          }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
}
```

**Variables:**
- `$id`: `ID!` - The app ID. Example: `"gid://partners/App/1234"`
- `$first`: `Int` - Returns the first n elements from the list
- `$before`: `String` - Returns elements before this cursor
- `$last`: `Int` - Returns the last n elements from the list
- `$after`: `String` - Returns elements after this cursor
- `$eventTypes`: `[AppEventType!]` - Filter by event types (see Event Types section)
- `$shopId`: `ID` - Filter by shop ID. Example: `"gid://partners/Shop/5678"`
- `$chargeId`: `ID` - Filter by charge ID. Example: `"gid://shopify/AppUsageRecord/9012"`
- `$occurredAtMin`: `DateTime` - Filter events from this date
- `$occurredAtMax`: `DateTime` - Filter events to this date

---

### 2. Transaction Query

Query for retrieving a specific transaction with all possible interface implementations.

```graphql
query TransactionQuery($id: ID!) {
  transaction(id: $id) {
    id
    createdAt
    ... on AppOneTimeSale {
      id
      createdAt
      chargeId
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
      app {
        id
        apiKey
        name
      }
      shop {
        id
        avatarUrl
        myshopifyDomain
        name
      }
    }
    ... on AppSaleAdjustment {
      id
      createdAt
      chargeId
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
      app {
        id
        apiKey
        name
      }
      shop {
        id
        avatarUrl
        myshopifyDomain
        name
      }
    }
    ... on AppSaleCredit {
      id
      createdAt
      chargeId
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
      app {
        id
        apiKey
        name
      }
      shop {
        id
        avatarUrl
        myshopifyDomain
        name
      }
    }
    ... on AppSubscriptionSale {
      id
      createdAt
      chargeId
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
      app {
        id
        apiKey
        name
      }
      shop {
        id
        avatarUrl
        myshopifyDomain
        name
      }
    }
    ... on AppUsageSale {
      id
      createdAt
      chargeId
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
      app {
        id
        apiKey
        name
      }
      shop {
        id
        avatarUrl
        myshopifyDomain
        name
      }
    }
    ... on ServiceSale {
      id
      createdAt
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
    }
    ... on ServiceSaleAdjustment {
      id
      createdAt
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
    }
    ... on ThemeSale {
      id
      createdAt
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
    }
    ... on ThemeSaleAdjustment {
      id
      createdAt
      grossAmount {
        amount
        currencyCode
      }
      netAmount {
        amount
        currencyCode
      }
      shopifyFee {
        amount
        currencyCode
      }
      processingFee {
        amount
        currencyCode
      }
      regulatoryOperatingFee {
        amount
        currencyCode
      }
    }
    ... on TaxTransaction {
      id
      createdAt
      amount {
        amount
        currencyCode
      }
      taxType
    }
    ... on ReferralTransaction {
      id
      createdAt
      amount {
        amount
        currencyCode
      }
    }
    ... on ReferralAdjustment {
      id
      createdAt
      amount {
        amount
        currencyCode
      }
    }
    ... on LegacyTransaction {
      id
      createdAt
      amount {
        amount
        currencyCode
      }
    }
  }
}
```

**Variables:**
- `$id`: `ID!` - Transaction ID. Example: `"gid://partners/AppOneTimeSale/1234"`

---

### 3. Transactions Query

Query for retrieving a paginated list of transactions with comprehensive filtering.

```graphql
query TransactionsQuery(
  $first: Int,
  $after: String,
  $last: Int,
  $before: String,
  $shopId: ID,
  $myshopifyDomain: String,
  $appId: ID,
  $createdAtMin: DateTime,
  $createdAtMax: DateTime,
  $types: [TransactionType!]
) {
  transactions(
    first: $first,
    after: $after,
    last: $last,
    before: $before,
    shopId: $shopId,
    myshopifyDomain: $myshopifyDomain,
    appId: $appId,
    createdAtMin: $createdAtMin,
    createdAtMax: $createdAtMax,
    types: $types
  ) {
    edges {
      cursor
      node {
        id
        createdAt
        ... on AppOneTimeSale {
          chargeId
          grossAmount {
            amount
            currencyCode
          }
          netAmount {
            amount
            currencyCode
          }
          app {
            id
            name
          }
          shop {
            id
            myshopifyDomain
          }
        }
        ... on ServiceSale {
          grossAmount {
            amount
            currencyCode
          }
          netAmount {
            amount
            currencyCode
          }
        }
        ... on ThemeSale {
          grossAmount {
            amount
            currencyCode
          }
          netAmount {
            amount
            currencyCode
          }
        }
        # Include other transaction types as needed
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```

**Variables:**
- `$first`: `Int` - Returns the first n elements
- `$after`: `String` - Returns elements after this cursor
- `$last`: `Int` - Returns the last n elements
- `$before`: `String` - Returns elements before this cursor
- `$shopId`: `ID` - Filter by shop ID
- `$myshopifyDomain`: `String` - Filter by shop domain. Example: `"example.myshopify.com"`
- `$appId`: `ID` - Filter by app ID
- `$createdAtMin`: `DateTime` - Filter from this date
- `$createdAtMax`: `DateTime` - Filter to this date
- `$types`: `[TransactionType!]` - Filter by transaction types

---

### 4. Eventsinks Query (NEW in unstable)

Query for retrieving eventsinks configured for a specific app.

```graphql
query EventsinksQuery($appId: ID!, $topic: EventsinkTopic!) {
  eventsinks(appId: $appId, topic: $topic) {
    id
    queue
    topic
    url
    appId
    createdAt
    updatedAt
  }
}
```

**Variables:**
- `$appId`: `ID!` - The app ID. Example: `"gid://partners/App/1234"`
- `$topic`: `EventsinkTopic!` - The eventsink topic. Values: `CUSTOMER_EVENTS_CREATE`, `CUSTOMERS_REDACT`, `DELIVERY_PROMISES_CREATE`

---

### 5. Public API Versions Query

Query for retrieving all available Partner API versions.

```graphql
query PublicApiVersionsQuery {
  publicApiVersions {
    name
    displayName
    handle
    supported
  }
}
```

**Variables:** None

---

### 6. Conversation Query (DEPRECATED)

⚠️ **DEPRECATED:** No longer supported as of 2024-01.

```graphql
query ConversationQuery($id: ID!) {
  conversation(id: $id) {
    id
    createdAt
    lastEventAt
    hasUnreadMessages
    dashboardUrl
    status
    merchantUser {
      id
      name
      avatarUrl
      timezone
    }
    messages(first: 20) {
      edges {
        cursor
        node {
          id
          body
          sentAt
          sentVia
          fromPartner
          fromMerchant
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
        startCursor
        endCursor
      }
    }
  }
}
```

---

### 7. Conversations Query (DEPRECATED)

⚠️ **DEPRECATED:** No longer supported as of 2024-01.

```graphql
query ConversationsQuery(
  $first: Int,
  $after: String,
  $last: Int,
  $before: String,
  $unreadOnly: Boolean,
  $statuses: [ConversationStatus!],
  $createdAtMin: DateTime,
  $createdAtMax: DateTime,
  $lastEventAtMin: DateTime,
  $lastEventAtMax: DateTime
) {
  conversations(
    first: $first,
    after: $after,
    last: $last,
    before: $before,
    unreadOnly: $unreadOnly,
    statuses: $statuses,
    createdAtMin: $createdAtMin,
    createdAtMax: $createdAtMax,
    lastEventAtMin: $lastEventAtMin,
    lastEventAtMax: $lastEventAtMax
  ) {
    edges {
      cursor
      node {
        id
        createdAt
        lastEventAt
        hasUnreadMessages
        status
        merchantUser {
          id
          name
        }
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
      startCursor
      endCursor
    }
  }
}
```

---

### 8. Job Query (DEPRECATED)

⚠️ **DEPRECATED:** No longer supported as of 2024-01.

```graphql
query JobQuery($id: ID!) {
  job(id: $id) {
    id
    createdAt
    confirmedCompleted
    dashboardUrl
    conversation {
      id
      hasUnreadMessages
    }
  }
}
```

---

### 9. Jobs Query (DEPRECATED)

⚠️ **DEPRECATED:** No longer supported as of 2024-01.

```graphql
query JobsQuery(
  $first: Int,
  $after: String,
  $statuses: [JobStatus!],
  $shopId: ID
) {
  jobs(
    first: $first,
    after: $after,
    statuses: $statuses,
    shopId: $shopId
  ) {
    edges {
      cursor
      node {
        id
        createdAt
        confirmedCompleted
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
    }
  }
}
```

---

## MUTATIONS

### 1. App Credit Create

Create a credit for a shop that can be used towards future app purchases.

```graphql
mutation AppCreditCreateMutation(
  $appId: ID!,
  $shopId: ID!,
  $amount: MoneyInput!,
  $description: String!,
  $test: Boolean
) {
  appCreditCreate(
    appId: $appId,
    shopId: $shopId,
    amount: $amount,
    description: $description,
    test: $test
  ) {
    appCredit {
      id
      amount {
        amount
        currencyCode
      }
      name
      description
      createdAt
      test
      app {
        id
        name
      }
      shop {
        id
        myshopifyDomain
      }
    }
    userErrors {
      field
      message
    }
  }
}
```

**Variables:**
- `$appId`: `ID!` - App ID. Example: `"gid://partners/App/123"`
- `$shopId`: `ID!` - Shop ID. Example: `"gid://partners/Shop/456"`
- `$amount`: `MoneyInput!` - Credit amount. Example: `{ amount: "10.00", currencyCode: "USD" }`
- `$description`: `String!` - Credit description
- `$test`: `Boolean` - Whether this is a test transaction (default: false)

---

### 2. Eventsink Create (NEW in unstable)

Create a new eventsink for receiving webhook events.

```graphql
mutation EventsinkCreateMutation($input: EventsinkCreateInput!) {
  eventsinkCreate(input: $input) {
    eventsink {
      id
      queue
      topic
      url
      appId
      createdAt
      updatedAt
    }
    success
    userErrors {
      field
      message
    }
  }
}
```

**Variables:**
- `$input`: `EventsinkCreateInput!` - Eventsink creation input
  - `appId`: `ID!` - App ID
  - `topic`: `EventsinkTopic!` - Event topic
  - `url`: `String!` - Webhook URL
  - `queue`: `EventsinkQueue` - Queue type (optional)

---

### 3. Eventsink Delete (NEW in unstable)

Delete an existing eventsink.

```graphql
mutation EventsinkDeleteMutation(
  $id: ID!,
  $appId: ID!,
  $topic: EventsinkTopic!
) {
  eventsinkDelete(
    id: $id,
    appId: $appId,
    topic: $topic
  ) {
    id
    success
    userErrors {
      field
      message
    }
  }
}
```

**Variables:**
- `$id`: `ID!` - Eventsink ID to delete
- `$appId`: `ID!` - Associated app ID
- `$topic`: `EventsinkTopic!` - Eventsink topic

---

## ENUM VALUES

### App Event Types
```
CREDIT_APPLIED, CREDIT_FAILED, CREDIT_PENDING,
ONE_TIME_CHARGE_ACCEPTED, ONE_TIME_CHARGE_ACTIVATED, ONE_TIME_CHARGE_DECLINED, ONE_TIME_CHARGE_EXPIRED,
RELATIONSHIP_DEACTIVATED, RELATIONSHIP_INSTALLED, RELATIONSHIP_REACTIVATED, RELATIONSHIP_UNINSTALLED,
SUBSCRIPTION_APPROACHING_CAPPED_AMOUNT, SUBSCRIPTION_CAPPED_AMOUNT_UPDATED,
SUBSCRIPTION_CHARGE_ACCEPTED, SUBSCRIPTION_CHARGE_ACTIVATED, SUBSCRIPTION_CHARGE_CANCELED,
SUBSCRIPTION_CHARGE_DECLINED, SUBSCRIPTION_CHARGE_EXPIRED, SUBSCRIPTION_CHARGE_FROZEN, SUBSCRIPTION_CHARGE_UNFROZEN,
USAGE_CHARGE_APPLIED
```

### Transaction Types
```
SERVICE_SALE, SERVICE_SALE_ADJUSTMENT, THEME_SALE, THEME_SALE_ADJUSTMENT,
APP_ONE_TIME_SALE, APP_SUBSCRIPTION_SALE, APP_USAGE_SALE, APP_SALE_CREDIT, APP_SALE_ADJUSTMENT,
REFERRAL, REFERRAL_ADJUSTMENT, TAX, LEGACY
```

### Eventsink Topics (NEW in unstable)
```
CUSTOMER_EVENTS_CREATE, CUSTOMERS_REDACT, DELIVERY_PROMISES_CREATE
```

### Conversation Status (DEPRECATED)
```
ACTIVE, BLOCKED
```

### Job Status (DEPRECATED)
```
NEW, OPENED, RESPONDED, AWAITING_RESPONSE, COMPLETED, DECLINED, CLOSED, EXPIRED, INACTIVE
```

---

## VERSION CHANGES

### Changes in Unstable Version

**New Features:**
- Added `eventsinks` query
- Added `eventsinkCreate` and `eventsinkDelete` mutations
- Added eventsink-related types: `Eventsink`, `EventsinkTopic`, `EventsinkQueue`, etc.

**Enhanced Transaction Types:**
All transaction types now include additional fee fields:
- `processingFee`: Processing fees charged
- `regulatoryOperatingFee`: Regulatory operating fees

**Affected Types:**
- AppOneTimeSale, AppSaleAdjustment, AppSaleCredit, AppSubscriptionSale, AppUsageSale
- ServiceSale, ServiceSaleAdjustment
- ThemeSale, ThemeSaleAdjustment

**Enhanced Tax Transactions:**
- Added `taxType` field to `TaxTransaction` type

---

## PAGINATION PATTERNS

All connection queries support standard GraphQL pagination:

**Forward Pagination:**
```graphql
{
  field(first: 20, after: "cursor") {
    edges { cursor node { ... } }
    pageInfo { hasNextPage endCursor }
  }
}
```

**Backward Pagination:**
```graphql
{
  field(last: 20, before: "cursor") {
    edges { cursor node { ... } }
    pageInfo { hasPreviousPage startCursor }
  }
}
```

---

## EXAMPLE VARIABLE VALUES

**Global ID Format:**
- App: `"gid://partners/App/1234567890"`
- Shop: `"gid://partners/Shop/1234567890"`
- Transaction: `"gid://partners/AppOneTimeSale/1234567890"`
- Conversation: `"gid://partners/Conversation/1234567890"`

**DateTime Format:**
- ISO 8601: `"2024-01-01T00:00:00Z"`

**Money Input Format:**
```json
{
  "amount": "10.00",
  "currencyCode": "USD"
}
```

**Pagination Examples:**
- First 10: `{ "first": 10 }`
- Next page: `{ "first": 10, "after": "eyJpZCI6IjEyMzQ1Njc4OTAifQ==" }`
