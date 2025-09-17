"""Transaction-related model objects for the Shopify Partners API."""

from typing import TYPE_CHECKING, Optional, Union

from pydantic import Field

from shopify_partners_sdk.models.base import Connection, Edge, Node
from shopify_partners_sdk.models.enums import AppPricingInterval, TaxType
from shopify_partners_sdk.models.scalars import DateTime, GlobalID, Money


class Transaction(Node):
    """Base interface for all Partner transactions.

    All transaction types implement this interface.
    """

    created_at: DateTime = Field(
        ..., description="When the transaction was created", alias="createdAt"
    )

    def __str__(self) -> str:
        """String representation showing transaction ID and creation time."""
        return (
            f"{self.__class__.__name__}(id='{self.id}', created_at={self.created_at})"
        )


class AppOneTimeSale(Transaction):
    """A transaction corresponding to a one-time app purchase."""

    charge_id: Optional[GlobalID] = Field(
        None, description="ID of app charge", alias="chargeId"
    )
    gross_amount: Optional[Money] = Field(
        None, description="Total amount paid by merchant", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net amount added to payout", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Amount retained by Shopify", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fees", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory operating fees", alias="regulatoryOperatingFee"
    )
    app: "App" = Field(..., description="The app associated with the sale")
    shop: Optional["Shop"] = Field(None, description="The shop that made the purchase")

    def __str__(self) -> str:
        """String representation showing sale details."""
        return f"AppOneTimeSale(app='{self.app.name}', net_amount={self.net_amount})"


class AppSubscriptionSale(Transaction):
    """A transaction corresponding to an app subscription charge."""

    charge_id: Optional[GlobalID] = Field(
        None, description="ID of app charge", alias="chargeId"
    )
    gross_amount: Optional[Money] = Field(
        None, description="Total amount paid by merchant", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net amount added to payout", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Amount retained by Shopify", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fees", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory operating fees", alias="regulatoryOperatingFee"
    )
    billing_interval: Optional[AppPricingInterval] = Field(
        None, description="Billing frequency", alias="billingInterval"
    )
    app: "App" = Field(..., description="The app associated with the sale")
    shop: Optional["Shop"] = Field(None, description="The shop that made the purchase")

    def __str__(self) -> str:
        """String representation showing subscription details."""
        interval_str = (
            f", {self.billing_interval.value}" if self.billing_interval else ""
        )
        return f"AppSubscriptionSale(app='{self.app.name}', net_amount={self.net_amount}{interval_str})"


class AppUsageSale(Transaction):
    """A transaction corresponding to an app usage charge."""

    charge_id: Optional[GlobalID] = Field(
        None, description="ID of app charge", alias="chargeId"
    )
    gross_amount: Optional[Money] = Field(
        None, description="Total amount paid by merchant", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net amount added to payout", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Amount retained by Shopify", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fees", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory operating fees", alias="regulatoryOperatingFee"
    )
    app: "App" = Field(..., description="The app associated with the sale")
    shop: Optional["Shop"] = Field(None, description="The shop that made the purchase")

    def __str__(self) -> str:
        """String representation showing usage sale details."""
        return f"AppUsageSale(app='{self.app.name}', net_amount={self.net_amount})"


class AppSaleAdjustment(Transaction):
    """A transaction corresponding to an app sale refund or adjustment."""

    charge_id: Optional[GlobalID] = Field(
        None, description="ID of app charge", alias="chargeId"
    )
    gross_amount: Optional[Money] = Field(
        None, description="Adjustment amount", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net adjustment amount", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Fee adjustment", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fee adjustment", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory fee adjustment", alias="regulatoryOperatingFee"
    )
    app: "App" = Field(..., description="The app associated with the adjustment")
    shop: Optional["Shop"] = Field(None, description="The shop for the adjustment")

    def __str__(self) -> str:
        """String representation showing adjustment details."""
        return f"AppSaleAdjustment(app='{self.app.name}', net_amount={self.net_amount})"


class AppSaleCredit(Transaction):
    """A transaction corresponding to an app sale credit."""

    charge_id: Optional[GlobalID] = Field(
        None, description="ID of app charge", alias="chargeId"
    )
    gross_amount: Optional[Money] = Field(
        None, description="Credit amount", alias="grossAmount"
    )
    net_amount: Money = Field(..., description="Net credit amount", alias="netAmount")
    shopify_fee: Optional[Money] = Field(
        None, description="Fee credit", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fee credit", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory fee credit", alias="regulatoryOperatingFee"
    )
    app: "App" = Field(..., description="The app associated with the credit")
    shop: Optional["Shop"] = Field(None, description="The shop for the credit")

    def __str__(self) -> str:
        """String representation showing credit details."""
        return f"AppSaleCredit(app='{self.app.name}', net_amount={self.net_amount})"


class ServiceSale(Transaction):
    """A transaction for Expert Marketplace service sales."""

    gross_amount: Optional[Money] = Field(
        None, description="Total service amount", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net amount from service", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Shopify's service fee", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fees", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory operating fees", alias="regulatoryOperatingFee"
    )

    def __str__(self) -> str:
        """String representation showing service sale details."""
        return f"ServiceSale(net_amount={self.net_amount})"


class ServiceSaleAdjustment(Transaction):
    """A transaction for Expert Marketplace service sale adjustments."""

    gross_amount: Optional[Money] = Field(
        None, description="Adjustment amount", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net adjustment amount", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Fee adjustment", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fee adjustment", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory fee adjustment", alias="regulatoryOperatingFee"
    )

    def __str__(self) -> str:
        """String representation showing service adjustment details."""
        return f"ServiceSaleAdjustment(net_amount={self.net_amount})"


class ThemeSale(Transaction):
    """A transaction for theme marketplace sales."""

    gross_amount: Optional[Money] = Field(
        None, description="Total theme amount", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net amount from theme sale", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Shopify's theme fee", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fees", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory operating fees", alias="regulatoryOperatingFee"
    )

    def __str__(self) -> str:
        """String representation showing theme sale details."""
        return f"ThemeSale(net_amount={self.net_amount})"


class ThemeSaleAdjustment(Transaction):
    """A transaction for theme marketplace sale adjustments."""

    gross_amount: Optional[Money] = Field(
        None, description="Adjustment amount", alias="grossAmount"
    )
    net_amount: Money = Field(
        ..., description="Net adjustment amount", alias="netAmount"
    )
    shopify_fee: Optional[Money] = Field(
        None, description="Fee adjustment", alias="shopifyFee"
    )
    processing_fee: Optional[Money] = Field(
        None, description="Processing fee adjustment", alias="processingFee"
    )
    regulatory_operating_fee: Optional[Money] = Field(
        None, description="Regulatory fee adjustment", alias="regulatoryOperatingFee"
    )

    def __str__(self) -> str:
        """String representation showing theme adjustment details."""
        return f"ThemeSaleAdjustment(net_amount={self.net_amount})"


class TaxTransaction(Transaction):
    """A transaction for tax-related charges."""

    amount: Money = Field(..., description="Tax amount")
    tax_type: Optional[TaxType] = Field(
        None, description="Type of tax", alias="taxType"
    )

    def __str__(self) -> str:
        """String representation showing tax details."""
        tax_str = f", type={self.tax_type.value}" if self.tax_type else ""
        return f"TaxTransaction(amount={self.amount}{tax_str})"


class ReferralTransaction(Transaction):
    """A transaction for partner referral payments."""

    amount: Money = Field(..., description="Referral payment amount")

    def __str__(self) -> str:
        """String representation showing referral details."""
        return f"ReferralTransaction(amount={self.amount})"


class ReferralAdjustment(Transaction):
    """A transaction for partner referral adjustments."""

    amount: Money = Field(..., description="Referral adjustment amount")

    def __str__(self) -> str:
        """String representation showing referral adjustment details."""
        return f"ReferralAdjustment(amount={self.amount})"


class LegacyTransaction(Transaction):
    """A legacy transaction format for historical data."""

    amount: Money = Field(..., description="Transaction amount")

    def __str__(self) -> str:
        """String representation showing legacy transaction details."""
        return f"LegacyTransaction(amount={self.amount})"


# Union type for all transaction types
TransactionUnion = Union[
    AppOneTimeSale,
    AppSubscriptionSale,
    AppUsageSale,
    AppSaleAdjustment,
    AppSaleCredit,
    ServiceSale,
    ServiceSaleAdjustment,
    ThemeSale,
    ThemeSaleAdjustment,
    TaxTransaction,
    ReferralTransaction,
    ReferralAdjustment,
    LegacyTransaction,
]


class TransactionEdge(Edge):
    """Edge for transaction connections."""

    node: TransactionUnion = Field(..., description="The transaction")


class TransactionConnection(Connection):
    """Connection for paginated transactions."""

    edges: list[TransactionEdge] = Field(..., description="List of transaction edges")
    nodes: Optional[list[TransactionUnion]] = Field(
        None, description="List of transactions"
    )

    @property
    def transactions(self) -> list[TransactionUnion]:
        """Get list of transactions from edges."""
        return [edge.node for edge in self.edges]


# Forward reference imports
if TYPE_CHECKING:
    from .app import App
    from .shop import Shop
