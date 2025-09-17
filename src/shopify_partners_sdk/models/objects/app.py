"""App-related model objects for the Shopify Partners API."""

from typing import TYPE_CHECKING, Optional

from pydantic import Field

from shopify_partners_sdk.models.base import Connection, Edge, Node
from shopify_partners_sdk.models.enums import AppEventType
from shopify_partners_sdk.models.scalars import DateTime


class App(Node):
    """A Shopify app.

    Represents an app in the Partner organization's portfolio.
    """

    api_key: str = Field(
        ..., description="Unique application API identifier", alias="apiKey"
    )
    name: str = Field(..., description="The name of the app")
    events: "AppEventConnection" = Field(..., description="A list of app events")

    def __str__(self) -> str:
        """String representation showing app name."""
        return f"App(name='{self.name}', api_key='{self.api_key}')"


class AppEvent(Node):
    """Base interface for app events.

    All app events implement this interface and include app, shop, and timing
    information.
    """

    app: App = Field(..., description="The app associated with this event")
    occurred_at: DateTime = Field(
        ..., description="When the event occurred", alias="occurredAt"
    )
    shop: "Shop" = Field(..., description="The shop where the event occurred")
    type: AppEventType = Field(..., description="The type of the event")

    def __str__(self) -> str:
        """String representation showing event type and timing."""
        return f"{self.__class__.__name__}(type={self.type.value}, occurred_at={self.occurred_at})"


class CreditApplied(AppEvent):
    """Event for when an app credit is successfully applied."""

    app_credit: "AppCredit" = Field(
        ..., description="The credit that was applied", alias="appCredit"
    )


class CreditFailed(AppEvent):
    """Event for when an app credit fails to be applied."""

    app_credit: "AppCredit" = Field(
        ..., description="The credit that failed", alias="appCredit"
    )


class CreditPending(AppEvent):
    """Event for when an app credit is pending."""

    app_credit: "AppCredit" = Field(
        ..., description="The pending credit", alias="appCredit"
    )


class RelationshipInstalled(AppEvent):
    """Event for when an app is installed on a shop."""


class RelationshipUninstalled(AppEvent):
    """Event for when an app is uninstalled from a shop."""


class RelationshipReactivated(AppEvent):
    """Event for when an app relationship is reactivated."""


class RelationshipDeactivated(AppEvent):
    """Event for when an app relationship is deactivated."""


class OneTimeChargeAccepted(AppEvent):
    """Event for when a one-time charge is accepted."""

    charge: "AppCharge" = Field(..., description="The charge that was accepted")


class OneTimeChargeActivated(AppEvent):
    """Event for when a one-time charge is activated."""

    charge: "AppCharge" = Field(..., description="The charge that was activated")


class OneTimeChargeDeclined(AppEvent):
    """Event for when a one-time charge is declined."""

    charge: "AppCharge" = Field(..., description="The charge that was declined")


class OneTimeChargeExpired(AppEvent):
    """Event for when a one-time charge expires."""

    charge: "AppCharge" = Field(..., description="The charge that expired")


class SubscriptionChargeAccepted(AppEvent):
    """Event for when a subscription charge is accepted."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge that was accepted"
    )


class SubscriptionChargeActivated(AppEvent):
    """Event for when a subscription charge is activated."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge that was activated"
    )


class SubscriptionChargeCanceled(AppEvent):
    """Event for when a subscription charge is canceled."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge that was canceled"
    )


class SubscriptionChargeDeclined(AppEvent):
    """Event for when a subscription charge is declined."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge that was declined"
    )


class SubscriptionChargeExpired(AppEvent):
    """Event for when a subscription charge expires."""

    charge: "AppSubscriptionCharge" = Field(..., description="The charge that expired")


class SubscriptionChargeFrozen(AppEvent):
    """Event for when a subscription charge is frozen."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge that was frozen"
    )


class SubscriptionChargeUnfrozen(AppEvent):
    """Event for when a subscription charge is unfrozen."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge that was unfrozen"
    )


class SubscriptionCappedAmountUpdated(AppEvent):
    """Event for when a subscription capped amount is updated."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge with updated capped amount"
    )


class SubscriptionApproachingCappedAmount(AppEvent):
    """Event for when a subscription is approaching its capped amount."""

    charge: "AppSubscriptionCharge" = Field(
        ..., description="The charge approaching its cap"
    )


class UsageChargeApplied(AppEvent):
    """Event for when a usage charge is applied."""

    charge: "AppUsageCharge" = Field(
        ..., description="The usage charge that was applied"
    )


class AppEventEdge(Edge):
    """Edge for app event connections."""

    node: AppEvent = Field(..., description="The app event")


class AppEventConnection(Connection):
    """Connection for paginated app events."""

    edges: list[AppEventEdge] = Field(..., description="List of app event edges")
    nodes: Optional[list[AppEvent]] = Field(None, description="List of app events")

    @property
    def events(self) -> list[AppEvent]:
        """Get list of app events from edges."""
        return [edge.node for edge in self.edges]


class AppCredit(Node):
    """An app credit that can be applied to future purchases."""

    amount: "Money" = Field(..., description="The credit amount")
    name: str = Field(..., description="The name of the credit")
    description: Optional[str] = Field(None, description="Description of the credit")
    created_at: DateTime = Field(
        ..., description="When the credit was created", alias="createdAt"
    )
    test: bool = Field(..., description="Whether this is a test credit")
    app: App = Field(..., description="The app this credit belongs to")
    shop: "Shop" = Field(..., description="The shop this credit applies to")

    def __str__(self) -> str:
        """String representation showing credit details."""
        return f"AppCredit(amount={self.amount}, name='{self.name}')"


class AppCharge(Node):
    """A one-time app charge."""

    amount: "Money" = Field(..., description="The charge amount")
    name: str = Field(..., description="The name of the charge")
    status: str = Field(..., description="The status of the charge")
    created_at: DateTime = Field(
        ..., description="When the charge was created", alias="createdAt"
    )
    test: bool = Field(..., description="Whether this is a test charge")

    def __str__(self) -> str:
        """String representation showing charge details."""
        return f"AppCharge(amount={self.amount}, name='{self.name}', status='{self.status}')"


class AppSubscriptionCharge(AppCharge):
    """A recurring subscription app charge."""

    billing_on: Optional[DateTime] = Field(
        None, description="Next billing date", alias="billingOn"
    )
    capped_amount: Optional["Money"] = Field(
        None, description="Usage cap amount", alias="cappedAmount"
    )
    terms: Optional[str] = Field(None, description="Terms of the subscription")

    def __str__(self) -> str:
        """String representation showing subscription details."""
        return f"AppSubscriptionCharge(amount={self.amount}, name='{self.name}', status='{self.status}')"


class AppUsageCharge(Node):
    """A usage-based app charge."""

    amount: "Money" = Field(..., description="The usage charge amount")
    name: str = Field(..., description="The name of the usage charge")
    description: Optional[str] = Field(None, description="Description of the usage")
    created_at: DateTime = Field(
        ..., description="When the charge was created", alias="createdAt"
    )

    def __str__(self) -> str:
        """String representation showing usage charge details."""
        return f"AppUsageCharge(amount={self.amount}, name='{self.name}')"


class AppSubscription(Node):
    """A recurring charge for use of an app, such as a monthly subscription charge."""

    amount: "Money" = Field(..., description="The amount of the app charge")
    name: str = Field(..., description="The name of the app charge")
    test: bool = Field(
        ..., description="Whether the app purchase was a test transaction"
    )
    billing_on: Optional[DateTime] = Field(
        None,
        description="The date when the merchant will next be billed",
        alias="billingOn",
    )

    def __str__(self) -> str:
        """String representation showing subscription details."""
        return f"AppSubscription(amount={self.amount}, name='{self.name}')"


class AppPurchaseOneTime(Node):
    """A one-time app charge for services and features purchased once by a store."""

    amount: "Money" = Field(..., description="The amount of the app charge")
    name: str = Field(..., description="The name of the app charge")
    test: bool = Field(
        ..., description="Whether the app purchase was a test transaction"
    )

    def __str__(self) -> str:
        """String representation showing one-time purchase details."""
        return f"AppPurchaseOneTime(amount={self.amount}, name='{self.name}')"


if TYPE_CHECKING:
    from shopify_partners_sdk.models.scalars import Money

    from .shop import Shop
