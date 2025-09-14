# Shopify Partners API - Complete Query and Mutation Examples

Generated from the latest GraphQL schema with complete field structures and interface implementations.

## QUERIES
==================================================

### app

**Description:** A Shopify [app](/concepts/apps).

**Complete Query Example:**
```graphql
query AppQuery($id: ID!) {
  app(id: $id) {
    apiKey
    events(
      after: $after
      before: $before
      first: 10
      last: $last
      types: [RELATIONSHIP_INSTALLED]
      shopId: "gid://partners/Shop/123"
      chargeId: "gid://partners/Charge/123"
      occurredAtMin: "2024-01-01T00:00:00Z"
      occurredAtMax: "2024-01-01T00:00:00Z"
    ) {
      edges {
        cursor
        node {
          occurredAt
        ... on CreditApplied {
          occurredAt
          app {
            apiKey
            id
            name
          }
          appCredit {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on CreditFailed {
          occurredAt
          app {
            apiKey
            id
            name
          }
          appCredit {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on CreditPending {
          occurredAt
          app {
            apiKey
            id
            name
          }
          appCredit {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on OneTimeChargeAccepted {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on OneTimeChargeActivated {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on OneTimeChargeDeclined {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on OneTimeChargeExpired {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on RelationshipDeactivated {
          occurredAt
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on RelationshipInstalled {
          occurredAt
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on RelationshipReactivated {
          occurredAt
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on RelationshipUninstalled {
          description
          occurredAt
          reason
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionApproachingCappedAmount {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionCappedAmountUpdated {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionChargeAccepted {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionChargeActivated {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionChargeCanceled {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionChargeDeclined {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionChargeExpired {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionChargeFrozen {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on SubscriptionChargeUnfrozen {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            billingOn
            id
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on UsageChargeApplied {
          occurredAt
          app {
            apiKey
            id
            name
          }
          charge {
            amount
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
      }
    }
    id
    name
  }
}
```

**Variables:**
- `$id`: `ID!`
  - The app ID. Example value: `gid://partners/App/1234`.

**Return Type:** `App`

---

### conversation

**Description:** A conversation with a merchant through the Experts Marketplace.

**⚠️ DEPRECATED:** No longer supported (2024-01).

**Complete Query Example:**
```graphql
query ConversationQuery($id: ID!) {
  conversation(id: $id) {
    createdAt
    dashboardUrl
    hasUnreadMessages
    id
    lastEventAt
    merchantUser {
      avatarUrl
      id
      name
      timezone
    }
    messages(
      after: $after
      before: $before
      first: 10
      last: $last
      sentAtMin: "2024-01-01T00:00:00Z"
      sentAtMax: "2024-01-01T00:00:00Z"
    ) {
      edges {
        cursor
        node {
          body
          fileUrls
          id
          sentAt
        }
      }
      pageInfo {
        hasNextPage
        hasPreviousPage
      }
    }
  }
}
```

**Variables:**
- `$id`: `ID!`
  - The conversation ID. Example value: `gid://partners/Conversation/1234`.

**Return Type:** `Conversation`

---

### conversations

**Description:** A list of the Partner organization's conversations.

**⚠️ DEPRECATED:** No longer supported (2024-01).

**Complete Query Example:**
```graphql
query ConversationsQuery($after: String, $before: String, $first: Int, $last: Int, $unreadOnly: Boolean, $statuses: [ConversationStatus!], $createdAtMin: DateTime, $createdAtMax: DateTime, $lastEventAtMin: DateTime, $lastEventAtMax: DateTime) {
  conversations(after: $after, before: $before, first: $first, last: $last, unreadOnly: $unreadOnly, statuses: $statuses, createdAtMin: $createdAtMin, createdAtMax: $createdAtMax, lastEventAtMin: $lastEventAtMin, lastEventAtMax: $lastEventAtMax) {
  after: $after
  before: $before
  first: 10
  last: $last
  unreadOnly: $unreadOnly
  statuses: $statuses
  createdAtMin: "2024-01-01T00:00:00Z"
  createdAtMax: "2024-01-01T00:00:00Z"
  lastEventAtMin: "2024-01-01T00:00:00Z"
  lastEventAtMax: "2024-01-01T00:00:00Z"
) {
  edges {
    cursor
    node {
      createdAt
      dashboardUrl
      hasUnreadMessages
      id
      lastEventAt
    }
  }
  pageInfo {
    hasNextPage
    hasPreviousPage
  }
}
  }
}
```

**Variables:**
- `$after`: `String`
  - Returns the elements in the list that come after the specified cursor.

- `$before`: `String`
  - Returns the elements in the list that come before the specified cursor.

- `$first`: `Int`
  - Returns the first _n_ elements from the list.

- `$last`: `Int`
  - Returns the last _n_ elements from the list.

- `$unreadOnly`: `Boolean`
  - Only include conversations that have unread messages.
  - Default: `false`

- `$statuses`: `[ConversationStatus!]`
  - Returns conversations with the specified statuses.

- `$createdAtMin`: `DateTime`
  - Returns conversations that were created on or after the specified date and time.

- `$createdAtMax`: `DateTime`
  - Returns conversations that were created on or before the specified date and time.

- `$lastEventAtMin`: `DateTime`
  - Returns conversations where the last event occurred on or after the specified date and time.

- `$lastEventAtMax`: `DateTime`
  - Returns conversations where the last event occurred on or before the specified date and time.

**Return Type:** `ConversationConnection!`

---

### eventsinks

**Description:** A list of Eventsinks configured for the specified App ID.

**Complete Query Example:**
```graphql
query EventsinksQuery($appId: ID!, $topic: EventsinkTopic!) {
  eventsinks(appId: $appId, topic: $topic) {
    appId
    awsUserArn
    id
    queues {
      address
      region
    }
  }
}
```

**Variables:**
- `$appId`: `ID!`
  - The app ID. Example value: `gid://partners/App/1234`.

- `$topic`: `EventsinkTopic!`
  - The topic of the Eventsink to query.

**Return Type:** `[Eventsink!]!`

---

### job

**Description:** An [Experts Marketplace job](https://help.shopify.com/partners/selling-services).

**⚠️ DEPRECATED:** No longer supported (2024-01).

**Complete Query Example:**
```graphql
query JobQuery($id: ID!) {
  job(id: $id) {
    confirmedCompleted
    conversation {
      createdAt
      dashboardUrl
      hasUnreadMessages
      id
      lastEventAt
    }
    createdAt
    dashboardUrl
    id
    lastEventAt
    requirements {
      question
      responses
    }
    services {
      handle
      name
    }
    shop {
      avatarUrl
      id
      myshopifyDomain
      name
    }
  }
}
```

**Variables:**
- `$id`: `ID!`
  - The job ID. Example value: `gid://partners/Job/1234`.

**Return Type:** `Job`

---

### jobs

**Description:** A list of the Partner organization's [Experts Marketplace jobs](https://help.shopify.com/partners/selling-services).

**⚠️ DEPRECATED:** No longer supported (2024-01).

**Complete Query Example:**
```graphql
query JobsQuery($after: String, $before: String, $first: Int, $last: Int, $statuses: [JobStatus!], $shopId: ID, $createdAtMin: DateTime, $createdAtMax: DateTime, $lastEventAtMin: DateTime, $lastEventAtMax: DateTime) {
  jobs(after: $after, before: $before, first: $first, last: $last, statuses: $statuses, shopId: $shopId, createdAtMin: $createdAtMin, createdAtMax: $createdAtMax, lastEventAtMin: $lastEventAtMin, lastEventAtMax: $lastEventAtMax) {
  after: $after
  before: $before
  first: 10
  last: $last
  statuses: $statuses
  shopId: "gid://partners/Shop/123"
  createdAtMin: "2024-01-01T00:00:00Z"
  createdAtMax: "2024-01-01T00:00:00Z"
  lastEventAtMin: "2024-01-01T00:00:00Z"
  lastEventAtMax: "2024-01-01T00:00:00Z"
) {
  edges {
    cursor
    node {
      confirmedCompleted
      createdAt
      dashboardUrl
      id
      lastEventAt
    }
  }
  pageInfo {
    hasNextPage
    hasPreviousPage
  }
}
  }
}
```

**Variables:**
- `$after`: `String`
  - Returns the elements in the list that come after the specified cursor.

- `$before`: `String`
  - Returns the elements in the list that come before the specified cursor.

- `$first`: `Int`
  - Returns the first _n_ elements from the list.

- `$last`: `Int`
  - Returns the last _n_ elements from the list.

- `$statuses`: `[JobStatus!]`
  - Returns jobs with the specified statuses.

- `$shopId`: `ID`
  - Returns jobs associated with the specified shop ID.

- `$createdAtMin`: `DateTime`
  - Returns jobs that were created on or after the specified date and time.

- `$createdAtMax`: `DateTime`
  - Returns jobs that were created on or before the specified date and time.

- `$lastEventAtMin`: `DateTime`
  - Returns jobs where the last event occurred on or after the specified date and time.

- `$lastEventAtMax`: `DateTime`
  - Returns jobs where the last event occurred on or before the specified date and time.

**Return Type:** `JobConnection!`

---

### publicApiVersions

**Description:** The list of public Partner API versions, including supported, release candidate and unstable versions.

**Complete Query Example:**
```graphql
query PublicapiversionsQuery {
  publicApiVersions {
    displayName
    handle
    supported
  }
}
```

**Return Type:** `[ApiVersion!]!`

---

### transaction

**Description:** A Shopify Partner transaction.

**Complete Query Example:**
```graphql
query TransactionQuery($id: ID!) {
  transaction(id: $id) {
    createdAt
    id
    ... on AppOneTimeSale {
      chargeId
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      app {
        apiKey
        id
        name
      }
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on AppSaleAdjustment {
      chargeId
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      app {
        apiKey
        id
        name
      }
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on AppSaleCredit {
      chargeId
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      app {
        apiKey
        id
        name
      }
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on AppSubscriptionSale {
      chargeId
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      app {
        apiKey
        id
        name
      }
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on AppUsageSale {
      chargeId
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      app {
        apiKey
        id
        name
      }
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on LegacyTransaction {
      amount
      createdAt
      id
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on ReferralAdjustment {
      amount
      createdAt
      id
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on ReferralTransaction {
      amount
      createdAt
      id
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on ServiceSale {
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on ServiceSaleAdjustment {
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
    }
    ... on TaxTransaction {
      amount
      createdAt
      id
    }
    ... on ThemeSale {
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
      theme {
        name
      }
    }
    ... on ThemeSaleAdjustment {
      createdAt
      grossAmount
      id
      netAmount
      processingFee
      regulatoryOperatingFee
      shopifyFee
      shop {
        avatarUrl
        id
        myshopifyDomain
      }
      theme {
        name
      }
    }
  }
}
```

**Variables:**
- `$id`: `ID!`
  - The transaction ID. Example value: `gid://partners/ThemeSale/1234`.

**Return Type:** `Transaction`

---

### transactions

**Description:** A list of the Partner organization's [transactions](https://help.shopify.com/partners/getting-started/getting-paid).

**Complete Query Example:**
```graphql
query TransactionsQuery($after: String, $before: String, $first: Int, $last: Int, $shopId: ID, $myshopifyDomain: String, $appId: ID, $createdAtMin: DateTime, $createdAtMax: DateTime, $types: [TransactionType!]) {
  transactions(after: $after, before: $before, first: $first, last: $last, shopId: $shopId, myshopifyDomain: $myshopifyDomain, appId: $appId, createdAtMin: $createdAtMin, createdAtMax: $createdAtMax, types: $types) {
  after: $after
  before: $before
  first: 10
  last: $last
  shopId: "gid://partners/Shop/123"
  myshopifyDomain: $myshopifyDomain
  appId: "gid://partners/App/123"
  createdAtMin: "2024-01-01T00:00:00Z"
  createdAtMax: "2024-01-01T00:00:00Z"
  types: [SERVICE_SALE]
) {
  edges {
    cursor
    node {
      createdAt
      id
        ... on AppOneTimeSale {
          chargeId
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on AppSaleAdjustment {
          chargeId
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on AppSaleCredit {
          chargeId
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on AppSubscriptionSale {
          chargeId
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on AppUsageSale {
          chargeId
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          app {
            apiKey
            id
            name
          }
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on LegacyTransaction {
          amount
          createdAt
          id
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on ReferralAdjustment {
          amount
          createdAt
          id
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on ReferralTransaction {
          amount
          createdAt
          id
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on ServiceSale {
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on ServiceSaleAdjustment {
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
        }
        ... on TaxTransaction {
          amount
          createdAt
          id
        }
        ... on ThemeSale {
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
          theme {
            name
          }
        }
        ... on ThemeSaleAdjustment {
          createdAt
          grossAmount
          id
          netAmount
          processingFee
          regulatoryOperatingFee
          shopifyFee
          shop {
            avatarUrl
            id
            myshopifyDomain
          }
          theme {
            name
          }
        }
    }
  }
  pageInfo {
    hasNextPage
    hasPreviousPage
  }
}
  }
}
```

**Variables:**
- `$after`: `String`
  - Returns the elements in the list that come after the specified cursor.

- `$before`: `String`
  - Returns the elements in the list that come before the specified cursor.

- `$first`: `Int`
  - Returns the first _n_ elements from the list.

- `$last`: `Int`
  - Returns the last _n_ elements from the list.

- `$shopId`: `ID`
  - Returns transactions associated with the specified shop ID.

- `$myshopifyDomain`: `String`
  - Returns transactions associated with the specified `.myshopify.com` shop domain. Example value: `example.myshopify.com`.

- `$appId`: `ID`
  - Returns transactions associated with the specified app ID.

- `$createdAtMin`: `DateTime`
  - Returns transactions that were created on or after the specified date and time.

- `$createdAtMax`: `DateTime`
  - Returns transactions that were created on or before the specified date and time.

- `$types`: `[TransactionType!]`
  - Returns transactions of the specified types.

**Return Type:** `TransactionConnection!`

---

## MUTATIONS
==================================================

### appCreditCreate

**Description:** Allows an app to create a credit for a shop that can be used towards future app purchases. This mutation is only available to Partner API clients that have been granted the `View financials` permission.

**Complete Mutation Example:**
```graphql
mutation AppcreditcreateMutation($appId: ID!, $shopId: ID!, $amount: MoneyInput!, $description: String!, $test: Boolean) {
  appCreditCreate(appId: $appId, shopId: $shopId, amount: $amount, description: $description, test: $test) {
    appCredit {
      amount
      id
      name
      test
    }
    userErrors {
      field
      message
    }
  }
}
```

**Variables:**
- `$appId`: `ID!`
  - The id of the app to associate the credit with. Example value: `gid://partners/App/123`.

- `$shopId`: `ID!`
  - The id of the shop to be credited. Example value: `gid://partners/Shop/456`.

- `$amount`: `MoneyInput!`
  - The amount that can be used towards future app purchases in Shopify.

- `$description`: `String!`
  - The description of the app credit.

- `$test`: `Boolean`
  - Specifies whether the app credit is a test transaction.
  - Default: `false`

**Return Type:** `AppCreditCreatePayload`

---

### eventsinkCreate

**Description:** Creates a new Eventsink.

**Complete Mutation Example:**
```graphql
mutation EventsinkcreateMutation($input: EventsinkCreateInput!) {
  eventsinkCreate(input: $input) {
    eventsink {
      appId
      awsUserArn
      id
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
- `$input`: `EventsinkCreateInput!`
  - Details of eventsink to create.

**Return Type:** `EventsinkCreatePayload`

---

### eventsinkDelete

**Description:** Deletes an Eventsink.

**Complete Mutation Example:**
```graphql
mutation EventsinkdeleteMutation($id: ID!, $appId: ID!, $topic: EventsinkTopic!) {
  eventsinkDelete(id: $id, appId: $appId, topic: $topic) {
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
- `$id`: `ID!`
  - Eventsink to delete.

- `$appId`: `ID!`
  - The App that associated with the Eventsink.

- `$topic`: `EventsinkTopic!`
  - The topic of the Eventsink.

**Return Type:** `EventsinkDeletePayload`

---
