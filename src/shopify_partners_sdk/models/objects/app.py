"""App-related model objects for the Shopify Partners API."""

from typing import TYPE_CHECKING, Any

from pydantic import Field

from shopify_partners_sdk.models.base import (
    Connection,
    Edge,
    Node,
    ShopifyPartnersBaseModel,
    typename_union,
)
from shopify_partners_sdk.models.enums import AppEventType
from shopify_partners_sdk.models.objects.shop import Shop  # noqa: TC001
from shopify_partners_sdk.models.scalars import DateTime, Money


class App(Node):
    """A Shopify app.

    Represents an app in the Partner organization's portfolio.
    """

    api_key: str = Field(
        ..., description="Unique application API identifier", alias="apiKey"
    )
    name: str = Field(..., description="The name of the app")
    events: "AppEventConnection | None" = Field(
        None, description="App events; present only when selected"
    )

    def __str__(self) -> str:
        """String representation showing app name."""
        return f"App(name='{self.name}', api_key='{self.api_key}')"


class AppEvent(ShopifyPartnersBaseModel):
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
        return f"{self.__class__.__name__}(type={self.type}, occurred_at={self.occurred_at})"


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

    reason: str | None = Field(None, description="Why the merchant uninstalled")
    description: str | None = Field(
        None, description="The merchant's own words about the uninstall"
    )


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


def _event_type_name(data: dict[str, Any]) -> str | None:
    """RELATIONSHIP_INSTALLED -> RelationshipInstalled (event class names)."""
    event_type = data.get("type")
    if not isinstance(event_type, str):
        return None
    return "".join(part.capitalize() for part in event_type.split("_"))


if TYPE_CHECKING:
    AppEventUnion = AppEvent
else:
    AppEventUnion = typename_union(
        AppEvent.__subclasses__(), AppEvent, infer=_event_type_name
    )


class AppEventEdge(Edge):
    """Edge for app event connections."""

    node: AppEventUnion = Field(..., description="The app event, as its own type")


class AppEventConnection(Connection):
    """Connection for paginated app events."""

    edges: list[AppEventEdge] = Field(..., description="List of app event edges")

    @property
    def events(self) -> list[AppEventUnion]:
        """Get list of app events from edges."""
        return [edge.node for edge in self.edges]


class AppCredit(Node):
    """An app credit that can be applied to future purchases."""

    amount: "Money" = Field(..., description="The credit amount")
    name: str = Field(..., description="The name of the credit")
    test: bool = Field(..., description="Whether this is a test credit")

    def __str__(self) -> str:
        """String representation showing credit details."""
        return f"AppCredit(amount={self.amount}, name='{self.name}')"


class AppCharge(Node):
    """Fields shared by every app charge (the AppCharge interface)."""

    amount: "Money" = Field(..., description="The charge amount")
    name: str = Field(..., description="The name of the charge")
    test: bool = Field(..., description="Whether this is a test charge")

    def __str__(self) -> str:
        """String representation showing charge details."""
        return f"{self.__class__.__name__}(amount={self.amount}, name='{self.name}')"


class AppSubscriptionCharge(AppCharge):
    """A recurring subscription app charge."""

    billing_on: DateTime | None = Field(
        None, description="Next billing date", alias="billingOn"
    )


class AppUsageCharge(AppCharge):
    """A usage-based app charge (AppUsageRecord in the schema)."""


class AppSubscription(Node):
    """A recurring charge for use of an app, such as a monthly subscription charge."""

    amount: "Money" = Field(..., description="The amount of the app charge")
    name: str = Field(..., description="The name of the app charge")
    test: bool = Field(
        ..., description="Whether the app purchase was a test transaction"
    )
    billing_on: DateTime | None = Field(
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
