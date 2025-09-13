# Shopify Partners API GraphQL Schema Reference

This document provides a comprehensive technical reference for the Shopify Partners API GraphQL schema, including all object types, fields, relationships, and type definitions.

**Primary Schema Version:** unstable
**Last Updated:** {'2024-10': {'objects': 67, 'interfaces': 9, 'unions': 1, 'enums': 9, 'inputs': 1, 'scalars': 7}, '2025-01': {'objects': 67, 'interfaces': 9, 'unions': 1, 'enums': 9, 'inputs': 1, 'scalars': 7}, '2025-04': {'objects': 67, 'interfaces': 9, 'unions': 1, 'enums': 9, 'inputs': 1, 'scalars': 7}, '2025-07': {'objects': 67, 'interfaces': 9, 'unions': 1, 'enums': 9, 'inputs': 1, 'scalars': 7}, 'unstable': {'objects': 71, 'interfaces': 9, 'unions': 1, 'enums': 10, 'inputs': 2, 'scalars': 7}}

## Table of Contents

1. [Schema Overview](#schema-overview)
2. [Complete Object Type Catalog](#complete-object-type-catalog)
3. [Interface & Union Analysis](#interface--union-analysis)
4. [Connection Type Patterns](#connection-type-patterns)
5. [Complete Enum Documentation](#complete-enum-documentation)
6. [Input Type Structures](#input-type-structures)
7. [Scalar Type Definitions](#scalar-type-definitions)
8. [Query & Mutation Signatures](#query--mutation-signatures)
9. [Object Relationship Mapping](#object-relationship-mapping)
10. [Version Comparison Matrix](#version-comparison-matrix)

---

## Schema Overview

- **Query Type:** `QueryRoot`
- **Mutation Type:** `MutationRoot`
- **Total Object Types:** 71
- **Total Interfaces:** 9
- **Total Enums:** 10
- **Total Input Types:** 2
- **Total Scalar Types:** 7
- **Connection Types:** 5

---

## Complete Object Type Catalog

This section documents every object type in the schema with all fields, types, and relationships.

### ApiVersion

**Description:** A version of the API.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `displayName` | `String!` | The human-readable name of the version. |  |
| `handle` | `String!` | The unique identifier of an ApiVersion. All supported API versions have a date-based (YYYY-MM) or `u... |  |
| `supported` | `Boolean!` | Whether the version is supported by Shopify. |  |

---

### App

**Description:** A Shopify [app](/concepts/apps).

**Implements Interfaces:** `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `apiKey` | `String!` | A unique application API identifier. |  |
| `events` | `AppEventConnection!` | A list of app events. | `after: String` - Returns the elements in the list that come after t...; `before: String` - Returns the elements in the list that come before ...; `first: Int` - Returns the first _n_ elements from the list....; `last: Int` - Returns the last _n_ elements from the list....; `types: [AppEventTypes!]` - Returns app events of the specified types....; `shopId: ID` - Returns app events associated with the specified s...; `chargeId: ID` - Returns app events associated with the specified [...; `occurredAtMin: DateTime` - Returns app events that occurred on or after the s...; `occurredAtMax: DateTime` - Returns app events that occurred on or before the ... |
| `id` | `ID!` | The ID of the app. Example value: `gid://partners/App/1234`. |  |
| `name` | `String!` | The name of the app. |  |

---

### AppCredit

**Description:** A [credit](/docs/admin-api/rest/reference/billing/applicationcredit) issued
to a merchant for an app. Merchants are entitled to app credits under certain circumstances,
such as when a paid app subscription is downgraded partway through its billing cycle.

**Implements Interfaces:** `AppCharge`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The amount that can be used towards future app purchases in Shopify. |  |
| `id` | `ID!` | A globally unique identifier. |  |
| `name` | `String!` | The description of the app credit. |  |
| `test` | `Boolean!` | Whether the app credit was a test transaction. |  |

---

### AppCreditCreatePayload

**Description:** The result of an appCreditCreate mutation.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `appCredit` | `AppCredit` | The app credit that was created. |  |
| `userErrors` | `[UserError!]` | Errors when creating the application credit. |  |

---

### AppEventConnection

**Description:** The connection type for AppEvent.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `edges` | `[AppEventEdge!]!` | A list of edges. |  |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |  |

---

### AppEventEdge

**Description:** An edge in a connection.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `cursor` | `String!` | A cursor for use in pagination. |  |
| `node` | `AppEvent!` | The item at the end of the edge. |  |

---

### AppOneTimeSale

**Description:** A transaction corresponding to a one-time app charge.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | The app associated with the sale. |  |
| `chargeId` | `ID` | The ID of the [app charge](/tutorials/bill-for-your-app-using-graphql-admin-api) associated with the... |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the sale. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the sale. |  |

---

### AppPurchaseOneTime

**Description:** A one-time app charge for services and features purchased once by a store.
For example, a one-time migration of a merchant's data from one platform to another.

**Implements Interfaces:** `AppCharge`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The amount of the app charge. |  |
| `id` | `ID!` | A globally unique identifier. |  |
| `name` | `String!` | The name of the app charge. |  |
| `test` | `Boolean!` | Whether the app purchase was a test transaction. |  |

---

### AppSaleAdjustment

**Description:** A transaction corresponding to a refund, downgrade, or adjustment of an app charge.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | The app associated with the refund. |  |
| `chargeId` | `ID` | The ID of the [app charge](/tutorials/bill-for-your-app-using-graphql-admin-api) associated with the... |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the adjustment. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the adjustment. |  |

---

### AppSaleCredit

**Description:** A transaction corresponding to an [app credit](/docs/admin-api/rest/reference/billing/applicationcredit).

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | The app associated with the sale. |  |
| `chargeId` | `ID` | The ID of the [app charge](/tutorials/bill-for-your-app-using-graphql-admin-api) associated with the... |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the sale. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the sale. |  |

---

### AppSubscription

**Description:** A recurring charge for use of an app, such as a monthly subscription charge.

**Implements Interfaces:** `AppCharge`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The amount of the app charge. |  |
| `billingOn` | `DateTime` | The date when the merchant will next be billed. |  |
| `id` | `ID!` | A globally unique identifier. |  |
| `name` | `String!` | The name of the app charge. |  |
| `test` | `Boolean!` | Whether the app purchase was a test transaction. |  |

---

### AppSubscriptionSale

**Description:** A transaction corresponding to an app subscription charge.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | The app associated with the sale. |  |
| `billingInterval` | `AppPricingInterval` | The billing frequency for the app. |  |
| `chargeId` | `ID` | The ID of the [app charge](/tutorials/bill-for-your-app-using-graphql-admin-api) associated with the... |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the sale. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the sale. |  |

---

### AppUsageRecord

**Description:** An app charge. This charge varies based on how much the merchant uses the app
or a service that the app integrates with.

**Implements Interfaces:** `AppCharge`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The amount of the app charge. |  |
| `id` | `ID!` | A globally unique identifier. |  |
| `name` | `String!` | The name of the app charge. |  |
| `test` | `Boolean!` | Whether the app purchase was a test transaction. |  |

---

### AppUsageSale

**Description:** A transaction corresponding to an app usage charge.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | The app associated with the sale. |  |
| `chargeId` | `ID` | The ID of the [app charge](/tutorials/bill-for-your-app-using-graphql-admin-api) associated with the... |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the sale. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the sale. |  |

---

### Conversation

**Description:** A conversation with a merchant through the Experts Marketplace.

**Implements Interfaces:** `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `createdAt` | `DateTime!` | The date and time the conversation was started. |  |
| `dashboardUrl` | `Url!` | The URL to access this conversation in the Partner Dashboard. |  |
| `hasUnreadMessages` | `Boolean!` | Whether the conversation has unread messages. |  |
| `id` | `ID!` | A globally unique identifier. |  |
| `lastEventAt` | `DateTime!` | The date and time of the most recent conversation event. Example events: a message being sent, or a ... |  |
| `merchantUser` | `MerchantUser!` | The merchant account involved in the conversation. |  |
| `messages` | `MessageConnection!` | The messages exchanged within the conversation. | `after: String` - Returns the elements in the list that come after t...; `before: String` - Returns the elements in the list that come before ...; `first: Int` - Returns the first _n_ elements from the list....; `last: Int` - Returns the last _n_ elements from the list....; `sentAtMin: DateTime` - Returns messages that were sent on or after the sp...; `sentAtMax: DateTime` - Returns messages that were sent on or before the s... |
| `status` | `ConversationStatus!` | The status of the Experts Marketplace conversation. |  |

---

### ConversationConnection

**Description:** The connection type for Conversation.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `edges` | `[ConversationEdge!]!` | A list of edges. |  |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |  |

---

### ConversationEdge

**Description:** An edge in a connection.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `cursor` | `String!` | A cursor for use in pagination. |  |
| `node` | `Conversation!` | The item at the end of the edge. |  |

---

### CreditApplied

**Description:** An event that marks that an app credit was applied.

**Implements Interfaces:** `AppCreditEvent`, `AppEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `appCredit` | `AppCredit!` | A [credit](/docs/admin-api/rest/reference/billing/applicationcredit) issued to a merchant for an app... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### CreditFailed

**Description:** An event that marks that an app credit failed to apply.

**Implements Interfaces:** `AppCreditEvent`, `AppEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `appCredit` | `AppCredit!` | A [credit](/docs/admin-api/rest/reference/billing/applicationcredit) issued to a merchant for an app... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### CreditPending

**Description:** An event that marks that an app credit is pending.

**Implements Interfaces:** `AppCreditEvent`, `AppEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `appCredit` | `AppCredit!` | A [credit](/docs/admin-api/rest/reference/billing/applicationcredit) issued to a merchant for an app... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### Eventsink

**Description:** A sink for submitting customer events.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `appId` | `ID!` | The App associated with the Eventsink. |  |
| `awsUserArn` | `String` | AWS ARN given access to any SQS queues. |  |
| `id` | `ID!` | The ID of the Eventsink. |  |
| `queues` | `[EventsinkQueue!]!` | List of queues associated with the eventsink. |  |
| `topic` | `EventsinkTopic!` | The topic of the eventsink. |  |

---

### EventsinkCreatePayload

**Description:** The result of an Eventsink creation.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `eventsink` | `Eventsink` | Details of created Eventsink. |  |
| `success` | `Boolean` | True if the mutation succeeded. |  |
| `userErrors` | `[UserError!]` | Errors on mutating the Eventsink. |  |

---

### EventsinkDeletePayload

**Description:** The result of an Eventsink delete.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `id` | `ID` | Identifier of deleted Eventsink. |  |
| `success` | `Boolean` | True if the mutation succeeded. |  |
| `userErrors` | `[UserError!]` | Errors on mutating the Eventsink. |  |

---

### EventsinkQueue

**Description:** An eventsink queue.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `address` | `String` | The address of the queue. |  |
| `region` | `String` | AWS region of the queue. |  |

---

### Job

**Description:** An [Experts Marketplace job](https://help.shopify.com/partners/selling-services).

**Implements Interfaces:** `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `confirmedCompleted` | `Boolean!` | Whether the merchant has marked the job as complete. |  |
| `conversation` | `Conversation` | The conversation containing messages exchanged with the merchant. |  |
| `createdAt` | `DateTime!` | The date and time the job was submitted to your organization. |  |
| `dashboardUrl` | `Url!` | A URL to access this job in the Partner Dashboard. |  |
| `id` | `ID!` | A globally unique identifier. |  |
| `lastEventAt` | `DateTime!` | The date and time of the most recent job event. |  |
| `requirements` | `[JobRequirement!]!` | The job requirements that the merchant provided. |  |
| `services` | `[Service!]!` | The services requested for this job. |  |
| `shop` | `Shop!` | The shop that submitted the job. |  |
| `status` | `JobStatus!` | The status of the job. |  |

---

### JobConnection

**Description:** The connection type for Job.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `edges` | `[JobEdge!]!` | A list of edges. |  |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |  |

---

### JobEdge

**Description:** An edge in a connection.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `cursor` | `String!` | A cursor for use in pagination. |  |
| `node` | `Job!` | The item at the end of the edge. |  |

---

### JobRequirement

**Description:** Details that the merchant provided about their job requirements. Details are returned as sets of questions and responses.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `question` | `String!` | The question that the merchant was asked about their job or store. |  |
| `responses` | `[String!]!` | The merchant's responses to the question. |  |

---

### LegacyTransaction

**Description:** A transaction of a type that is no longer supported.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `id` | `ID!` | The transaction ID. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |

---

### MerchantUser

**Description:** A merchant account. This might be a shop owner, a staff member, or a user that isn't associated with a shop.
A single merchant account can be associated with many shops.

**Implements Interfaces:** `Actor`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `avatarUrl` | `Url` | A URL referencing the avatar associated with the actor. |  |
| `id` | `ID!` | A globally unique identifier for the actor. Example value: `gid://partners/Shop/1234`. |  |
| `name` | `String!` | The user's full name. |  |
| `timezone` | `String!` | The user's time zone. |  |

---

### Message

**Description:** A message exchanged within a conversation.

**Implements Interfaces:** `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `body` | `String` | The message body. |  |
| `fileUrls` | `[Url!]!` | A collection of URLs pointing to files attached to the message. |  |
| `id` | `ID!` | A globally unique identifier. |  |
| `sentAt` | `DateTime!` | The date and time the message was sent. |  |
| `sentBy` | `MessageSender!` | The organization or user that sent the message. |  |
| `sentVia` | `MessageSentVia!` | The platform that was used to send the message. |  |

---

### MessageConnection

**Description:** The connection type for Message.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `edges` | `[MessageEdge!]!` | A list of edges. |  |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |  |

---

### MessageEdge

**Description:** An edge in a connection.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `cursor` | `String!` | A cursor for use in pagination. |  |
| `node` | `Message!` | The item at the end of the edge. |  |

---

### Money

**Description:** A monetary value with currency.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Decimal!` | The decimal money amount. |  |
| `currencyCode` | `Currency!` | The currency. |  |

---

### MutationRoot

**Description:** The schema's entry-point for mutations. This acts as the public, top-level API from which all mutations must start.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `appCreditCreate` | `AppCreditCreatePayload` | Allows an app to create a credit for a shop that can be used towards future app purchases. This muta... | `appId: ID!` - The id of the app to associate the credit with. Ex...; `shopId: ID!` - The id of the shop to be credited. Example value: ...; `amount: MoneyInput!` - The amount that can be used towards future app pur...; `description: String!` - The description of the app credit....; `test: Boolean` - Specifies whether the app credit is a test transac... |
| `eventsinkCreate` | `EventsinkCreatePayload` | Creates a new Eventsink. | `input: EventsinkCreateInput!` - Details of eventsink to create.... |
| `eventsinkDelete` | `EventsinkDeletePayload` | Deletes an Eventsink. | `id: ID!` - Eventsink to delete....; `appId: ID!` - The App that associated with the Eventsink....; `topic: EventsinkTopic!` - The topic of the Eventsink.... |

---

### OneTimeChargeAccepted

**Description:** An event that marks that a one-time app charge was accepted by the merchant.

**Implements Interfaces:** `AppEvent`, `AppPurchaseOneTimeEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppPurchaseOneTime!` | A one-time app charge for services and features purchased once by a store. For example, a one-time m... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### OneTimeChargeActivated

**Description:** An event that marks that a one-time app charge was activated.

**Implements Interfaces:** `AppEvent`, `AppPurchaseOneTimeEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppPurchaseOneTime!` | A one-time app charge for services and features purchased once by a store. For example, a one-time m... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### OneTimeChargeDeclined

**Description:** An event that marks that a one-time app charge was declined by the merchant.

**Implements Interfaces:** `AppEvent`, `AppPurchaseOneTimeEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppPurchaseOneTime!` | A one-time app charge for services and features purchased once by a store. For example, a one-time m... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### OneTimeChargeExpired

**Description:** An event that marks that a one-time app charge expired before the merchant could accept it.

**Implements Interfaces:** `AppEvent`, `AppPurchaseOneTimeEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppPurchaseOneTime!` | A one-time app charge for services and features purchased once by a store. For example, a one-time m... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### Organization

**Description:** A Partner organization.

**Implements Interfaces:** `Actor`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `avatarUrl` | `Url` | A URL referencing the avatar associated with the actor. |  |
| `id` | `ID!` | A globally unique identifier for the actor. Example value: `gid://partners/Shop/1234`. |  |
| `name` | `String!` | The name of the actor. This might be a Partner organization or shop name. |  |

---

### PageInfo

**Description:** Information about pagination in a connection.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `hasNextPage` | `Boolean!` | Whether there are more pages to fetch. |  |
| `hasPreviousPage` | `Boolean!` | Whether there are any pages prior to the current page. |  |

---

### QueryRoot

**Description:** The schema's entry-point for queries. This acts as the public, top-level API from which all queries must start.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App` | A Shopify [app](/concepts/apps). | `id: ID!` - The app ID. Example value: `gid://partners/App/123... |
| `conversation` | `Conversation` | A conversation with a merchant through the Experts Marketplace. | `id: ID!` - The conversation ID. Example value: `gid://partner... |
| `conversations` | `ConversationConnection!` | A list of the Partner organization's conversations. | `after: String` - Returns the elements in the list that come after t...; `before: String` - Returns the elements in the list that come before ...; `first: Int` - Returns the first _n_ elements from the list....; `last: Int` - Returns the last _n_ elements from the list....; `unreadOnly: Boolean` - Only include conversations that have unread messag...; `statuses: [ConversationStatus!]` - Returns conversations with the specified statuses....; `createdAtMin: DateTime` - Returns conversations that were created on or afte...; `createdAtMax: DateTime` - Returns conversations that were created on or befo...; `lastEventAtMin: DateTime` - Returns conversations where the last event occurre...; `lastEventAtMax: DateTime` - Returns conversations where the last event occurre... |
| `eventsinks` | `[Eventsink!]!` | A list of Eventsinks configured for the specified App ID. | `appId: ID!` - The app ID. Example value: `gid://partners/App/123...; `topic: EventsinkTopic!` - The topic of the Eventsink to query.... |
| `job` | `Job` | An [Experts Marketplace job](https://help.shopify.com/partners/selling-services). | `id: ID!` - The job ID. Example value: `gid://partners/Job/123... |
| `jobs` | `JobConnection!` | A list of the Partner organization's [Experts Marketplace jobs](https://help.shopify.com/partners/se... | `after: String` - Returns the elements in the list that come after t...; `before: String` - Returns the elements in the list that come before ...; `first: Int` - Returns the first _n_ elements from the list....; `last: Int` - Returns the last _n_ elements from the list....; `statuses: [JobStatus!]` - Returns jobs with the specified statuses....; `shopId: ID` - Returns jobs associated with the specified shop ID...; `createdAtMin: DateTime` - Returns jobs that were created on or after the spe...; `createdAtMax: DateTime` - Returns jobs that were created on or before the sp...; `lastEventAtMin: DateTime` - Returns jobs where the last event occurred on or a...; `lastEventAtMax: DateTime` - Returns jobs where the last event occurred on or b... |
| `publicApiVersions` | `[ApiVersion!]!` | The list of public Partner API versions, including supported, release candidate and unstable version... |  |
| `transaction` | `Transaction` | A Shopify Partner transaction. | `id: ID!` - The transaction ID. Example value: `gid://partners... |
| `transactions` | `TransactionConnection!` | A list of the Partner organization's [transactions](https://help.shopify.com/partners/getting-starte... | `after: String` - Returns the elements in the list that come after t...; `before: String` - Returns the elements in the list that come before ...; `first: Int` - Returns the first _n_ elements from the list....; `last: Int` - Returns the last _n_ elements from the list....; `shopId: ID` - Returns transactions associated with the specified...; `myshopifyDomain: String` - Returns transactions associated with the specified...; `appId: ID` - Returns transactions associated with the specified...; `createdAtMin: DateTime` - Returns transactions that were created on or after...; `createdAtMax: DateTime` - Returns transactions that were created on or befor...; `types: [TransactionType!]` - Returns transactions of the specified types.... |

---

### ReferralAdjustment

**Description:** A transaction corresponding to a shop referral adjustment.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `category` | `ReferralCategory!` | The referral type. |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `id` | `ID!` | The transaction ID. |  |
| `shop` | `Shop` | The referred shop. |  |

---

### ReferralTransaction

**Description:** A transaction corresponding to a shop referral.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The net amount that is added to your payout. |  |
| `category` | `ReferralCategory!` | The referral type. |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `id` | `ID!` | The transaction ID. |  |
| `shop` | `Shop!` | The referred shop. |  |

---

### RelationshipDeactivated

**Description:** An event that marks that an app was deactivated.

**Implements Interfaces:** `AppEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### RelationshipInstalled

**Description:** An event that marks that an app was installed.

**Implements Interfaces:** `AppEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### RelationshipReactivated

**Description:** An event that marks that an app was reactivated.

**Implements Interfaces:** `AppEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### RelationshipUninstalled

**Description:** An event that marks that an app was uninstalled.

**Implements Interfaces:** `AppEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `description` | `String` | More details from the merchant about why they uninstalled the app. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `reason` | `String` | A comma separated list of reasons why the merchant uninstalled the app. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### Service

**Description:** A service in the Experts Marketplace.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `handle` | `String!` | A unique, human-readable ID for the service. |  |
| `name` | `String!` | The merchant-facing name of the service. |  |

---

### ServiceSale

**Description:** A transaction corresponding to a paid invoice for a service.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the sale. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the sale. |  |

---

### ServiceSaleAdjustment

**Description:** A transaction corresponding to a refund, downgrade, or adjustment of a service sale.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the adjustment. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the adjustment. |  |

---

### Shop

**Description:** A Shopify shop.

**Implements Interfaces:** `Actor`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `avatarUrl` | `Url` | A URL referencing the avatar associated with the actor. |  |
| `id` | `ID!` | A globally unique identifier for the actor. Example value: `gid://partners/Shop/1234`. |  |
| `myshopifyDomain` | `Url!` | The shop's `.myshopify.com` domain name. |  |
| `name` | `String!` | The name of the actor. This might be a Partner organization or shop name. |  |

---

### ShopifyEmployee

**Description:** A Shopify employee.

**Implements Interfaces:** `Actor`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `avatarUrl` | `Url` | A URL referencing the avatar associated with the actor. |  |
| `id` | `ID!` | A globally unique identifier for the actor. Example value: `gid://partners/Shop/1234`. |  |
| `name` | `String!` | The Shopify employee's full name. |  |

---

### SubscriptionApproachingCappedAmount

**Description:** An event that marks that a subscription is approaching its capped amount.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionCappedAmountUpdated

**Description:** An event that marks that a subscription had its capped amount updated.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionChargeAccepted

**Description:** An event that marks that a recurring app charge was accepted.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionChargeActivated

**Description:** An event that marks that a recurring app charge was activated.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionChargeCanceled

**Description:** An event that marks that a recurring app charge was cancelled.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionChargeDeclined

**Description:** An event that marks that a recurring app charge was declined.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionChargeExpired

**Description:** An event that marks that a recurring app charge has expired.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionChargeFrozen

**Description:** An event that marks that a recurring app charge has been suspended. For example, if a merchant stops paying their bills, or closes their store, then Shopify suspends the recurring app charge.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### SubscriptionChargeUnfrozen

**Description:** An event that marks that a recurring app charge was unfrozen.

**Implements Interfaces:** `AppEvent`, `AppSubscriptionEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### TaxTransaction

**Description:** Tax transactions are not computed for pending transactions. Instead, they're rolled
up as one transaction per payout. The type of tax and the way it's
computed is dependent on the type of transaction.

For sale transactions, such as app subscriptions or theme purchases, Shopify charges
the Partner tax on the fee collected for brokering the transaction. The amount is
a negative number in this scenario.

For referral transactions, such as a development store transfer, Shopify pays the Partner
a commission. The tax represents any taxes on the referral commission that are payable to
the Partner. The amount is a positive number in this scenario.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `amount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `id` | `ID!` | The transaction ID. |  |
| `taxType` | `TaxTransactionType!` | The tax model applied to the transaction, based on the transaction type. |  |
| `type` | `TaxTransactionType!` | The tax model applied to the transaction, based on the transaction type. |  |

---

### TeamMember

**Description:** An owner or staff member of the Partner Organization.

**Implements Interfaces:** `Actor`, `Node`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `avatarUrl` | `Url` | A URL referencing the avatar associated with the actor. |  |
| `id` | `ID!` | A globally unique identifier for the actor. Example value: `gid://partners/Shop/1234`. |  |
| `name` | `String!` | The team member's full name. |  |

---

### Theme

**Description:** A Shopify [theme](/concepts/themes).

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `name` | `String!` | The name of the theme. |  |

---

### ThemeSale

**Description:** A transaction corresponding to a theme purchase.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the sale. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the sale. |  |
| `theme` | `Theme!` | The theme associated with the purchase. |  |

---

### ThemeSaleAdjustment

**Description:** A transaction corresponding to a refund, downgrade, or adjustment of a theme sale.

**Implements Interfaces:** `Node`, `Transaction`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |  |
| `grossAmount` | `Money` | The total amount that the merchant paid, excluding taxes. |  |
| `id` | `ID!` | The transaction ID. |  |
| `netAmount` | `Money!` | The net amount that is added to or deducted from your payout. |  |
| `processingFee` | `Money` | The amount that is deducted for processing the adjustment. |  |
| `regulatoryOperatingFee` | `Money` | The amount that is deducted for Digital Services Tax based on the merchant's business address. |  |
| `shop` | `Shop` | The shop associated with the transaction. |  |
| `shopifyFee` | `Money` | The amount that Shopify retained from the adjustment. |  |
| `theme` | `Theme!` | The theme associated with the refund. |  |

---

### TransactionConnection

**Description:** The connection type for Transaction.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `edges` | `[TransactionEdge!]!` | A list of edges. |  |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |  |

---

### TransactionEdge

**Description:** An edge in a connection.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `cursor` | `String!` | A cursor for use in pagination. |  |
| `node` | `Transaction!` | The item at the end of the edge. |  |

---

### UsageChargeApplied

**Description:** An event that marks that an app usage charge was applied.

**Implements Interfaces:** `AppEvent`, `AppUsageRecordEvent`

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |  |
| `charge` | `AppUsageRecord!` | An app charge. This charge varies based on how much the merchant uses the app or a service that the ... |  |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |  |
| `shop` | `Shop!` | A Shopify shop. |  |
| `type` | `AppEventTypes!` | The type of app event. |  |

---

### UserError

**Description:** Represents an error in a mutation.

**Fields:**

| Field | Type | Description | Arguments |
|-------|------|-------------|-----------|
| `field` | `[String!]` | The path to the input field that caused the error. |  |
| `message` | `String!` | The error message. |  |

---

## Interface & Union Analysis

### Interfaces

#### Actor

**Description:** A Partner organization or shop.

**Implemented by:** `MerchantUser`, `Organization`, `Shop`, `ShopifyEmployee`, `TeamMember`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `avatarUrl` | `Url` | A URL referencing the avatar associated with the actor. |
| `id` | `ID!` | A globally unique identifier for the actor. Example value: `gid://partners/Shop/1234`. |
| `name` | `String!` | The name of the actor. This might be a Partner organization or shop name. |


#### AppCharge

**Description:** A [charge](/docs/admin-api/rest/reference/billing/applicationcharge) created through an app.

**Implemented by:** `AppCredit`, `AppPurchaseOneTime`, `AppSubscription`, `AppUsageRecord`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `amount` | `Money!` | The amount of the app charge. |
| `id` | `ID!` | A globally unique identifier. |
| `name` | `String!` | The name of the app charge. |
| `test` | `Boolean!` | Whether the app purchase was a test transaction. |


#### AppCreditEvent

**Description:** An event involving an app credit.

**Implemented by:** `CreditApplied`, `CreditFailed`, `CreditPending`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `appCredit` | `AppCredit!` | A [credit](/docs/admin-api/rest/reference/billing/applicationcredit) issued to a merchant for an app... |


#### AppEvent

**Description:** An event related to a Shopify app.

**Implemented by:** `CreditApplied`, `CreditFailed`, `CreditPending`, `OneTimeChargeAccepted`, `OneTimeChargeActivated`, `OneTimeChargeDeclined`, `OneTimeChargeExpired`, `RelationshipDeactivated`, `RelationshipInstalled`, `RelationshipReactivated`, `RelationshipUninstalled`, `SubscriptionApproachingCappedAmount`, `SubscriptionCappedAmountUpdated`, `SubscriptionChargeAccepted`, `SubscriptionChargeActivated`, `SubscriptionChargeCanceled`, `SubscriptionChargeDeclined`, `SubscriptionChargeExpired`, `SubscriptionChargeFrozen`, `SubscriptionChargeUnfrozen`, `UsageChargeApplied`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `app` | `App!` | A Shopify [app](/concepts/apps). |
| `occurredAt` | `DateTime!` | The date and time when the event took place. |
| `shop` | `Shop!` | A Shopify shop. |
| `type` | `AppEventTypes!` | The type of app event. |


#### AppPurchaseOneTimeEvent

**Description:** An app event for a one-time app charge.

**Implemented by:** `OneTimeChargeAccepted`, `OneTimeChargeActivated`, `OneTimeChargeDeclined`, `OneTimeChargeExpired`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `charge` | `AppPurchaseOneTime!` | A one-time app charge for services and features purchased once by a store. For example, a one-time m... |


#### AppSubscriptionEvent

**Description:** An event related to an [app subscription charge](/docs/admin-api/rest/reference/billing/recurringapplicationcharge).

**Implemented by:** `SubscriptionApproachingCappedAmount`, `SubscriptionCappedAmountUpdated`, `SubscriptionChargeAccepted`, `SubscriptionChargeActivated`, `SubscriptionChargeCanceled`, `SubscriptionChargeDeclined`, `SubscriptionChargeExpired`, `SubscriptionChargeFrozen`, `SubscriptionChargeUnfrozen`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `charge` | `AppSubscription!` | A recurring charge for use of an app, such as a monthly subscription charge. |


#### AppUsageRecordEvent

**Description:** An app event for an app usage charge.

**Implemented by:** `UsageChargeApplied`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `charge` | `AppUsageRecord!` | An app charge. This charge varies based on how much the merchant uses the app or a service that the ... |


#### Node

**Description:** An object with an ID to support global identification.

**Implemented by:** `App`, `AppCredit`, `AppOneTimeSale`, `AppPurchaseOneTime`, `AppSaleAdjustment`, `AppSaleCredit`, `AppSubscription`, `AppSubscriptionSale`, `AppUsageRecord`, `AppUsageSale`, `Conversation`, `Job`, `LegacyTransaction`, `MerchantUser`, `Message`, `Organization`, `ReferralAdjustment`, `ReferralTransaction`, `ServiceSale`, `ServiceSaleAdjustment`, `Shop`, `ShopifyEmployee`, `TaxTransaction`, `TeamMember`, `ThemeSale`, `ThemeSaleAdjustment`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `id` | `ID!` | A globally unique identifier. |


#### Transaction

**Description:** A Shopify Partner transaction.

**Implemented by:** `AppOneTimeSale`, `AppSaleAdjustment`, `AppSaleCredit`, `AppSubscriptionSale`, `AppUsageSale`, `LegacyTransaction`, `ReferralAdjustment`, `ReferralTransaction`, `ServiceSale`, `ServiceSaleAdjustment`, `TaxTransaction`, `ThemeSale`, `ThemeSaleAdjustment`

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `createdAt` | `DateTime!` | The date and time when the transaction was recorded. |
| `id` | `ID!` | The transaction ID. |


### Unions

#### MessageSender

**Description:** A union of all of the types that can send messages within a conversation.

**Possible Types:** `MerchantUser`, `Organization`, `Shop`, `ShopifyEmployee`, `TeamMember`


---

## Connection Type Patterns

GraphQL connections follow the Relay specification for pagination. All connection types implement a standard pattern.

### AppEventConnection

**Description:** The connection type for AppEvent.

**Edge Type:** `AppEventEdge`

**Standard Connection Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `edges` | `[AppEventEdge!]!` | A list of edges. |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |


### ConversationConnection

**Description:** The connection type for Conversation.

**Edge Type:** `ConversationEdge`

**Standard Connection Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `edges` | `[ConversationEdge!]!` | A list of edges. |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |


### JobConnection

**Description:** The connection type for Job.

**Edge Type:** `JobEdge`

**Standard Connection Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `edges` | `[JobEdge!]!` | A list of edges. |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |


### MessageConnection

**Description:** The connection type for Message.

**Edge Type:** `MessageEdge`

**Standard Connection Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `edges` | `[MessageEdge!]!` | A list of edges. |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |


### TransactionConnection

**Description:** The connection type for Transaction.

**Edge Type:** `TransactionEdge`

**Standard Connection Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `edges` | `[TransactionEdge!]!` | A list of edges. |
| `pageInfo` | `PageInfo!` | Information about pagination in a connection. |


---

## Complete Enum Documentation

### AppEventTypes

**Description:** The type of app event.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `CREDIT_APPLIED` | Credit applied |  |
| `CREDIT_FAILED` | Credit failed |  |
| `CREDIT_PENDING` | Credit pending |  |
| `ONE_TIME_CHARGE_ACCEPTED` | One time charge accepted |  |
| `ONE_TIME_CHARGE_ACTIVATED` | One time charge activated |  |
| `ONE_TIME_CHARGE_DECLINED` | One time charge declined |  |
| `ONE_TIME_CHARGE_EXPIRED` | One time charge expired |  |
| `RELATIONSHIP_DEACTIVATED` | Relationship deactivated |  |
| `RELATIONSHIP_INSTALLED` | Relationship installed |  |
| `RELATIONSHIP_REACTIVATED` | Relationship reactivated |  |
| `RELATIONSHIP_UNINSTALLED` | Relationship uninstalled |  |
| `SUBSCRIPTION_APPROACHING_CAPPED_AMOUNT` | Subscription is approaching capped amount. |  |
| `SUBSCRIPTION_CAPPED_AMOUNT_UPDATED` | Subscription capped amount was updated. |  |
| `SUBSCRIPTION_CHARGE_ACCEPTED` | Subscription charge accepted |  |
| `SUBSCRIPTION_CHARGE_ACTIVATED` | Subscription charge activated |  |
| `SUBSCRIPTION_CHARGE_CANCELED` | Subscription charge canceled |  |
| `SUBSCRIPTION_CHARGE_DECLINED` | Subscription charge declined |  |
| `SUBSCRIPTION_CHARGE_EXPIRED` | Subscription charge expired |  |
| `SUBSCRIPTION_CHARGE_FROZEN` | Subscription charge frozen |  |
| `SUBSCRIPTION_CHARGE_UNFROZEN` | Subscription charge unfrozen |  |
| `USAGE_CHARGE_APPLIED` | Usage charge applied |  |


### AppPricingInterval

**Description:** The billing frequency for the app.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `ANNUAL` | The merchant is billed for this app annually. |  |
| `EVERY_30_DAYS` | The merchant is billed for this app every 30 days. |  |


### ConversationStatus

**Description:** The status of the Experts Marketplace conversation.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `ACTIVE` | The conversation is active. Messages can be sent and received. |  |
| `BLOCKED` | A participant in the conversation has blocked the other. Messages can't be sent or received. |  |


### Currency

**Description:** Supported monetary currencies from ISO 4217.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `AED` | United arab emirates dirham. |  |
| `AFN` | Afghan afghani. |  |
| `ALL` | Albanian lek. |  |
| `AMD` | Armenian dram. |  |
| `ANG` | Netherlands antillean gulden. |  |
| `AOA` | Angolan kwanza. |  |
| `ARS` | Argentine peso. |  |
| `AUD` | Australian dollar. |  |
| `AWG` | Aruban florin. |  |
| `AZN` | Azerbaijani manat. |  |
| `BAM` | Bosnia and herzegovina convertible mark. |  |
| `BBD` | Barbadian dollar. |  |
| `BDT` | Bangladeshi taka. |  |
| `BGN` | Bulgarian lev. |  |
| `BHD` | Bahraini dinar. |  |
| `BIF` | Burundian franc. |  |
| `BMD` | Bermudian dollar. |  |
| `BND` | Brunei dollar. |  |
| `BOB` | Bolivian boliviano. |  |
| `BRL` | Brazilian real. |  |
| `BSD` | Bahamian dollar. |  |
| `BTN` | Bhutanese ngultrum. |  |
| `BWP` | Botswana pula. |  |
| `BYN` | Belarusian ruble. |  |
| `BYR` | Belarusian ruble. |  |
| `BZD` | Belize dollar. |  |
| `CAD` | Canadian dollar. |  |
| `CDF` | Congolese franc. |  |
| `CHF` | Swiss franc. |  |
| `CLF` | Unidad de fomento. |  |
| `CLP` | Chilean peso. |  |
| `CNY` | Chinese renminbi yuan. |  |
| `COP` | Colombian peso. |  |
| `CRC` | Costa rican colón. |  |
| `CUC` | Cuban convertible peso. |  |
| `CUP` | Cuban peso. |  |
| `CVE` | Cape verdean escudo. |  |
| `CYP` | Cypriot pound. |  |
| `CZK` | Czech koruna. |  |
| `DJF` | Djiboutian franc. |  |
| `DKK` | Danish krone. |  |
| `DOP` | Dominican peso. |  |
| `DZD` | Algerian dinar. |  |
| `EEK` | Estonian kroon. |  |
| `EGP` | Egyptian pound. |  |
| `ERN` | Eritrean nakfa. |  |
| `ETB` | Ethiopian birr. |  |
| `EUR` | Euro. |  |
| `FJD` | Fijian dollar. |  |
| `FKP` | Falkland pound. |  |
| `GBP` | British pound. |  |
| `GBX` | British penny. |  |
| `GEL` | Georgian lari. |  |
| `GGP` | Guernsey pound. |  |
| `GHC` | Ghanaian cedi. |  |
| `GHS` | Ghanaian cedi. |  |
| `GIP` | Gibraltar pound. |  |
| `GMD` | Gambian dalasi. |  |
| `GNF` | Guinean franc. |  |
| `GTQ` | Guatemalan quetzal. |  |
| `GYD` | Guyanese dollar. |  |
| `HKD` | Hong kong dollar. |  |
| `HNL` | Honduran lempira. |  |
| `HRK` | Croatian kuna. |  |
| `HTG` | Haitian gourde. |  |
| `HUF` | Hungarian forint. |  |
| `IDR` | Indonesian rupiah. |  |
| `ILS` | Israeli new sheqel. |  |
| `IMP` | Isle of man pound. |  |
| `INR` | Indian rupee. |  |
| `IQD` | Iraqi dinar. |  |
| `IRR` | Iranian rial. |  |
| `ISK` | Icelandic króna. |  |
| `JEP` | Jersey pound. |  |
| `JMD` | Jamaican dollar. |  |
| `JOD` | Jordanian dinar. |  |
| `JPY` | Japanese yen. |  |
| `KES` | Kenyan shilling. |  |
| `KGS` | Kyrgyzstani som. |  |
| `KHR` | Cambodian riel. |  |
| `KID` | Kiribati dollar. |  |
| `KMF` | Comorian franc. |  |
| `KPW` | North korean won. |  |
| `KRW` | South korean won. |  |
| `KWD` | Kuwaiti dinar. |  |
| `KYD` | Cayman islands dollar. |  |
| `KZT` | Kazakhstani tenge. |  |
| `LAK` | Lao kip. |  |
| `LBP` | Lebanese pound. |  |
| `LKR` | Sri lankan rupee. |  |
| `LRD` | Liberian dollar. |  |
| `LSL` | Lesotho loti. |  |
| `LTL` | Lithuanian litas. |  |
| `LVL` | Latvian lats. |  |
| `LYD` | Libyan dinar. |  |
| `MAD` | Moroccan dirham. |  |
| `MDL` | Moldovan leu. |  |
| `MGA` | Malagasy ariary. |  |
| `MKD` | Macedonian denar. |  |
| `MMK` | Myanmar kyat. |  |
| `MNT` | Mongolian tögrög. |  |
| `MOP` | Macanese pataca. |  |
| `MRO` | Mauritanian ouguiya. |  |
| `MRU` | Mauritanian new ouguiya. |  |
| `MTL` | Maltese lira. |  |
| `MUR` | Mauritian rupee. |  |
| `MVR` | Maldivian rufiyaa. |  |
| `MWK` | Malawian kwacha. |  |
| `MXN` | Mexican peso. |  |
| `MYR` | Malaysian ringgit. |  |
| `MZN` | Mozambican metical. |  |
| `NAD` | Namibian dollar. |  |
| `NGN` | Nigerian naira. |  |
| `NIO` | Nicaraguan córdoba. |  |
| `NOK` | Norwegian krone. |  |
| `NPR` | Nepalese rupee. |  |
| `NZD` | New zealand dollar. |  |
| `OMR` | Omani rial. |  |
| `PAB` | Panamanian balboa. |  |
| `PEN` | Peruvian sol. |  |
| `PGK` | Papua new guinean kina. |  |
| `PHP` | Philippine peso. |  |
| `PKR` | Pakistani rupee. |  |
| `PLN` | Polish złoty. |  |
| `PYG` | Paraguayan guaraní. |  |
| `QAR` | Qatari riyal. |  |
| `RON` | Romanian leu. |  |
| `RSD` | Serbian dinar. |  |
| `RUB` | Russian ruble. |  |
| `RWF` | Rwandan franc. |  |
| `SAR` | Saudi riyal. |  |
| `SBD` | Solomon islands dollar. |  |
| `SCR` | Seychellois rupee. |  |
| `SDG` | Sudanese pound. |  |
| `SEK` | Swedish krona. |  |
| `SGD` | Singapore dollar. |  |
| `SHP` | Saint helenian pound. |  |
| `SKK` | Slovak koruna. |  |
| `SLL` | Sierra leonean leone. |  |
| `SOS` | Somali shilling. |  |
| `SRD` | Surinamese dollar. |  |
| `SSP` | South sudanese pound. |  |
| `STD` | São tomé and príncipe dobra. |  |
| `STN` | São tomé and príncipe dobra. |  |
| `SVC` | Salvadoran colón. |  |
| `SYP` | Syrian pound. |  |
| `SZL` | Swazi lilangeni. |  |
| `THB` | Thai baht. |  |
| `TJS` | Tajikistani somoni. |  |
| `TMM` | Turkmenistani manat. |  |
| `TMT` | Turkmenistani manat. |  |
| `TND` | Tunisian dinar. |  |
| `TOP` | Tongan paʻanga. |  |
| `TRY` | Turkish lira. |  |
| `TTD` | Trinidad and tobago dollar. |  |
| `TWD` | New taiwan dollar. |  |
| `TZS` | Tanzanian shilling. |  |
| `UAH` | Ukrainian hryvnia. |  |
| `UGX` | Ugandan shilling. |  |
| `USD` | United states dollar. |  |
| `UYU` | Uruguayan peso. |  |
| `UZS` | Uzbekistan som. |  |
| `VEB` | Venezuelan bolívar. |  |
| `VED` | Venezuelan bolívar soberano. |  |
| `VEF` | Venezuelan bolívar fuerte. |  |
| `VES` | Venezuelan bolívar soberano. |  |
| `VND` | Vietnamese đồng. |  |
| `VUV` | Vanuatu vatu. |  |
| `WST` | Samoan tala. |  |
| `XAF` | Central african cfa franc. |  |
| `XAG` | Silver (troy ounce). |  |
| `XAU` | Gold (troy ounce). |  |
| `XBA` | European composite unit. |  |
| `XBB` | European monetary unit. |  |
| `XBC` | European unit of account 9. |  |
| `XBD` | European unit of account 17. |  |
| `XCD` | East caribbean dollar. |  |
| `XDR` | Special drawing rights. |  |
| `XFU` | Uic franc. |  |
| `XOF` | West african cfa franc. |  |
| `XPD` | Palladium. |  |
| `XPF` | Cfp franc. |  |
| `XPT` | Platinum. |  |
| `YER` | Yemeni rial. |  |
| `ZAR` | South african rand. |  |
| `ZMK` | Zambian kwacha. |  |
| `ZMW` | Zambian kwacha. |  |
| `ZWD` | Zimbabwean dollar. |  |
| `ZWL` | Zimbabwean dollar. |  |
| `ZWN` | Zimbabwean dollar. |  |
| `ZWR` | Zimbabwean dollar. |  |
| `xts` | Codes specifically reserved for testing purposes. |  |


### EventsinkTopic

**Description:** The topic name of an Eventsink.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `CUSTOMERS_REDACT` | Topic name for customer data deletion requests. |  |
| `CUSTOMER_EVENTS_CREATE` | Topic name for create customer events. |  |
| `DELIVERY_PROMISES_CREATE` | Topic name for create delivery promises. |  |


### JobStatus

**Description:** The status of the [Experts Marketplace job](https://help.shopify.com/partners/selling-services).

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `AWAITING_RESPONSE` | The merchant has taken an action that requires attention from your organization. |  |
| `CLOSED` | The job has been closed by the merchant. |  |
| `COMPLETED` | The job has been marked as complete by your organization. |  |
| `DECLINED` | The job has been declined by the merchant or your organization. |  |
| `EXPIRED` | The job has expired. A job expires when your organization does not send an initial response to a job... |  |
| `INACTIVE` | The job has been marked inactive by your organization. |  |
| `NEW` | The job has been submitted to your organization, but hasn't been opened. |  |
| `OPENED` | The job has been viewed by your organization. |  |
| `RESPONDED` | The job has been responded to by your organization. |  |


### MessageSentVia

**Description:** The platform that was used to send the message.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `DASHBOARD` | The message was sent through the Partner Dashboard. |  |
| `EMAIL` | The message was sent through an email. |  |


### ReferralCategory

**Description:** The referral type.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `AFFILIATE_STORES` | The merchant was referred using an affiliate link. |  |
| `INTUIT_POINT_OF_SALE` | The merchant was referred from an Intuit Channel Partner. |  |
| `MARKETS_PRO` | The merchant was referred to Markets Pro by a partner. |  |
| `POINT_OF_SALE` | The merchant was referred using the Partner POS lead form. |  |
| `POS_SHOPIFY_PAYMENTS_PROFIT` | The merchant was referred to POS by a partner. |  |
| `SHOPIFY_PLUS` | The merchant was referred using the Shopify Plus lead form. |  |
| `SHOPIFY_PLUS_ONE_TIME_REFERRAL` | The merchant was referred to Shopify Plus by a partner. |  |
| `TRANSFERRED_STORES` | The merchant was referred using a development store transfer. |  |


### TaxTransactionType

**Description:** The tax model applied to the transaction, based on the transaction type.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `REFERRAL_COMMISSION` | The taxes paid out on your commission fee for a referral. |  |
| `SALE_FEES` | The taxes charged on all fees applicable for an app, theme, or service transaction. |  |
| `SALE_SHOPIFY_FEE` | The taxes charged on Shopify's commission fee for an app, theme, or service transaction. | ✓ |


### TransactionType

**Description:** The type of transaction.

**Values:**

| Value | Description | Deprecated |
|-------|-------------|------------|
| `APP_ONE_TIME_SALE` | A transaction corresponding to a one-time app charge. |  |
| `APP_SALE_ADJUSTMENT` | A transaction corresponding to a refund, downgrade, or adjustment of an app charge. |  |
| `APP_SALE_CREDIT` | A transaction corresponding to an [app credit](/docs/admin-api/rest/reference/billing/applicationcre... |  |
| `APP_SUBSCRIPTION_SALE` | A transaction corresponding to an app subscription charge. |  |
| `APP_USAGE_SALE` | A transaction corresponding to an app usage charge. |  |
| `LEGACY` | A transaction of a type that is no longer supported. |  |
| `REFERRAL` | A transaction corresponding to a shop referral. |  |
| `REFERRAL_ADJUSTMENT` | A transaction corresponding to a shop referral adjustment. |  |
| `SERVICE_SALE` | A transaction corresponding to a paid invoice for a service. |  |
| `SERVICE_SALE_ADJUSTMENT` | A transaction corresponding to a refund, downgrade, or adjustment of a service sale. |  |
| `TAX` | Tax transactions are not computed for pending transactions. Instead, they're rolled up as one transa... |  |
| `THEME_SALE` | A transaction corresponding to a theme purchase. |  |
| `THEME_SALE_ADJUSTMENT` | A transaction corresponding to a refund, downgrade, or adjustment of a theme sale. |  |


---

## Input Type Structures

### EventsinkCreateInput

**Description:** Input for creating a new eventsink.

**Fields:**

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `appId` | `ID!` | The App that associated with the Eventsink. | `` |
| `awsUserArn` | `String!` | The AWS ID to be granted access. | `` |
| `topic` | `EventsinkTopic!` | The topic of the Eventsink. | `` |


### MoneyInput

**Description:** A monetary value with currency.

**Fields:**

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `amount` | `Decimal` | The amount of money. | `` |
| `currencyCode` | `Currency` | Currency of the money. | `` |


---

## Scalar Type Definitions

Custom scalar types used in the schema:

| Scalar | Description |
|--------|-------------|
| `Boolean` | Represents `true` or `false` values. |
| `DateTime` | An [ISO-8601](https://en.wikipedia.org/wiki/ISO_8601) encoded UTC date time string. Example value: `"2019-07-03T20:47:55.123456Z"`. |
| `Decimal` | A signed decimal number, which supports arbitrary precision and is serialized as a string. |
| `ID` | Represents a unique identifier that is Base64 obfuscated. It is often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"VXNlci0xMA=="`) or integer (such as `4`) input value will be accepted as an ID. |
| `Int` | Represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1. |
| `String` | Represents textual data as UTF-8 character sequences. This type is most often used by GraphQL to represent free-form human-readable text. |
| `Url` | A valid URL, transported as a string. |

---

## Query & Mutation Signatures

### Query Operations

| Query | Return Type | Description | Arguments |
|-------|-------------|-------------|-----------|
| `app` | `App` | A Shopify [app](/concepts/apps). | `id: ID!` |
| `conversation` | `Conversation` | A conversation with a merchant through the Experts Marketplace. | `id: ID!` |
| `conversations` | `ConversationConnection!` | A list of the Partner organization's conversations. | `after: String`, `before: String`, `first: Int`, `last: Int`, `unreadOnly: Boolean`, `statuses: [ConversationStatus!]`, `createdAtMin: DateTime`, `createdAtMax: DateTime`, `lastEventAtMin: DateTime`, `lastEventAtMax: DateTime` |
| `eventsinks` | `[Eventsink!]!` | A list of Eventsinks configured for the specified App ID. | `appId: ID!`, `topic: EventsinkTopic!` |
| `job` | `Job` | An [Experts Marketplace job](https://help.shopify.com/partners/selling-services). | `id: ID!` |
| `jobs` | `JobConnection!` | A list of the Partner organization's [Experts Marketplace jobs](https://help.shopify.com/partners/se | `after: String`, `before: String`, `first: Int`, `last: Int`, `statuses: [JobStatus!]`, `shopId: ID`, `createdAtMin: DateTime`, `createdAtMax: DateTime`, `lastEventAtMin: DateTime`, `lastEventAtMax: DateTime` |
| `publicApiVersions` | `[ApiVersion!]!` | The list of public Partner API versions, including supported, release candidate and unstable version |  |
| `transaction` | `Transaction` | A Shopify Partner transaction. | `id: ID!` |
| `transactions` | `TransactionConnection!` | A list of the Partner organization's [transactions](https://help.shopify.com/partners/getting-starte | `after: String`, `before: String`, `first: Int`, `last: Int`, `shopId: ID`, `myshopifyDomain: String`, `appId: ID`, `createdAtMin: DateTime`, `createdAtMax: DateTime`, `types: [TransactionType!]` |

### Mutation Operations

| Mutation | Return Type | Description | Arguments |
|----------|-------------|-------------|-----------|
| `appCreditCreate` | `AppCreditCreatePayload` | Allows an app to create a credit for a shop that can be used towards future app purchases. This muta | `appId: ID!`, `shopId: ID!`, `amount: MoneyInput!`, `description: String!`, `test: Boolean` |
| `eventsinkCreate` | `EventsinkCreatePayload` | Creates a new Eventsink. | `input: EventsinkCreateInput!` |
| `eventsinkDelete` | `EventsinkDeletePayload` | Deletes an Eventsink. | `id: ID!`, `appId: ID!`, `topic: EventsinkTopic!` |

---

## Object Relationship Mapping

This section shows how objects relate to each other through their fields.

**App:**

- `events` → `AppEventConnection`

**AppCredit:**

- `amount` → `Money`

**AppCreditCreatePayload:**

- `appCredit` → `AppCredit`
- `userErrors` → `UserError`

**AppEventConnection:**

- `edges` → `AppEventEdge`
- `pageInfo` → `PageInfo`

**AppOneTimeSale:**

- `app` → `App`
- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`

**AppPurchaseOneTime:**

- `amount` → `Money`

**AppSaleAdjustment:**

- `app` → `App`
- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`

**AppSaleCredit:**

- `app` → `App`
- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`

**AppSubscription:**

- `amount` → `Money`

**AppSubscriptionSale:**

- `app` → `App`
- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`

**AppUsageRecord:**

- `amount` → `Money`

**AppUsageSale:**

- `app` → `App`
- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`

**Conversation:**

- `merchantUser` → `MerchantUser`
- `messages` → `MessageConnection`

**ConversationConnection:**

- `edges` → `ConversationEdge`
- `pageInfo` → `PageInfo`

**ConversationEdge:**

- `node` → `Conversation`

**CreditApplied:**

- `app` → `App`
- `appCredit` → `AppCredit`
- `shop` → `Shop`

**CreditFailed:**

- `app` → `App`
- `appCredit` → `AppCredit`
- `shop` → `Shop`

**CreditPending:**

- `app` → `App`
- `appCredit` → `AppCredit`
- `shop` → `Shop`

**Eventsink:**

- `queues` → `EventsinkQueue`

**EventsinkCreatePayload:**

- `eventsink` → `Eventsink`
- `userErrors` → `UserError`

**EventsinkDeletePayload:**

- `userErrors` → `UserError`

**Job:**

- `conversation` → `Conversation`
- `requirements` → `JobRequirement`
- `services` → `Service`
- `shop` → `Shop`

**JobConnection:**

- `edges` → `JobEdge`
- `pageInfo` → `PageInfo`

**JobEdge:**

- `node` → `Job`

**LegacyTransaction:**

- `amount` → `Money`
- `shop` → `Shop`

**MessageConnection:**

- `edges` → `MessageEdge`
- `pageInfo` → `PageInfo`

**MessageEdge:**

- `node` → `Message`

**MutationRoot:**

- `appCreditCreate` → `AppCreditCreatePayload`
- `eventsinkCreate` → `EventsinkCreatePayload`
- `eventsinkDelete` → `EventsinkDeletePayload`

**OneTimeChargeAccepted:**

- `app` → `App`
- `charge` → `AppPurchaseOneTime`
- `shop` → `Shop`

**OneTimeChargeActivated:**

- `app` → `App`
- `charge` → `AppPurchaseOneTime`
- `shop` → `Shop`

**OneTimeChargeDeclined:**

- `app` → `App`
- `charge` → `AppPurchaseOneTime`
- `shop` → `Shop`

**OneTimeChargeExpired:**

- `app` → `App`
- `charge` → `AppPurchaseOneTime`
- `shop` → `Shop`

**QueryRoot:**

- `app` → `App`
- `conversation` → `Conversation`
- `conversations` → `ConversationConnection`
- `eventsinks` → `Eventsink`
- `job` → `Job`
- `jobs` → `JobConnection`
- `publicApiVersions` → `ApiVersion`
- `transactions` → `TransactionConnection`

**ReferralAdjustment:**

- `amount` → `Money`
- `shop` → `Shop`

**ReferralTransaction:**

- `amount` → `Money`
- `shop` → `Shop`

**RelationshipDeactivated:**

- `app` → `App`
- `shop` → `Shop`

**RelationshipInstalled:**

- `app` → `App`
- `shop` → `Shop`

**RelationshipReactivated:**

- `app` → `App`
- `shop` → `Shop`

**RelationshipUninstalled:**

- `app` → `App`
- `shop` → `Shop`

**ServiceSale:**

- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`

**ServiceSaleAdjustment:**

- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`

**SubscriptionApproachingCappedAmount:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionCappedAmountUpdated:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionChargeAccepted:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionChargeActivated:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionChargeCanceled:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionChargeDeclined:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionChargeExpired:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionChargeFrozen:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**SubscriptionChargeUnfrozen:**

- `app` → `App`
- `charge` → `AppSubscription`
- `shop` → `Shop`

**TaxTransaction:**

- `amount` → `Money`

**ThemeSale:**

- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`
- `theme` → `Theme`

**ThemeSaleAdjustment:**

- `grossAmount` → `Money`
- `netAmount` → `Money`
- `processingFee` → `Money`
- `regulatoryOperatingFee` → `Money`
- `shop` → `Shop`
- `shopifyFee` → `Money`
- `theme` → `Theme`

**TransactionConnection:**

- `edges` → `TransactionEdge`
- `pageInfo` → `PageInfo`

**UsageChargeApplied:**

- `app` → `App`
- `charge` → `AppUsageRecord`
- `shop` → `Shop`

---

## Version Comparison Matrix

### Type Counts by Version

| Version | Objects | Interfaces | Enums | Input Types | Scalars |
|---------|---------|------------|-------|-------------|---------|
| 2024-10 | 67 | 9 | 9 | 1 | 7 |
| 2025-01 | 67 | 9 | 9 | 1 | 7 |
| 2025-04 | 67 | 9 | 9 | 1 | 7 |
| 2025-07 | 67 | 9 | 9 | 1 | 7 |
| unstable | 71 | 9 | 10 | 2 | 7 |

### Unstable Version Differences

**Additional Objects in Unstable:**

- `Eventsink`
- `EventsinkQueue`
- `EventsinkCreatePayload`
- `EventsinkDeletePayload`

**Additional Enums in Unstable:**

- `EventsinkTopic`

**Additional Inputs in Unstable:**

- `EventsinkCreateInput`

---

*Documentation generated from schema version unstable*

*Total documented types: 99*