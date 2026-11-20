"""Object model types for the Shopify Partners SDK."""

from pydantic import BaseModel

from .app import (
    App,
    AppCharge,
    AppCredit,
    AppEvent,
    AppEventConnection,
    AppEventEdge,
    AppPurchaseOneTime,
    AppSubscription,
    AppSubscriptionCharge,
    AppUsageCharge,
    CreditApplied,
    CreditFailed,
    CreditPending,
    OneTimeChargeAccepted,
    OneTimeChargeActivated,
    OneTimeChargeDeclined,
    OneTimeChargeExpired,
    RelationshipDeactivated,
    RelationshipInstalled,
    RelationshipReactivated,
    RelationshipUninstalled,
    SubscriptionApproachingCappedAmount,
    SubscriptionCappedAmountUpdated,
    SubscriptionChargeAccepted,
    SubscriptionChargeActivated,
    SubscriptionChargeCanceled,
    SubscriptionChargeDeclined,
    SubscriptionChargeExpired,
    SubscriptionChargeFrozen,
    SubscriptionChargeUnfrozen,
    UsageChargeApplied,
)
from .organization import Organization
from .shop import Shop
from .transaction import (
    AppOneTimeSale,
    AppSaleAdjustment,
    AppSaleCredit,
    AppSubscriptionSale,
    AppUsageSale,
    LegacyTransaction,
    ReferralAdjustment,
    ReferralTransaction,
    ServiceSale,
    ServiceSaleAdjustment,
    TaxTransaction,
    ThemeSale,
    ThemeSaleAdjustment,
    Transaction,
    TransactionConnection,
    TransactionEdge,
    TransactionUnion,
)
from .version import ApiVersion

__all__ = [
    # API Version
    "ApiVersion",
    # App models
    "App",
    "AppCharge",
    "AppCredit",
    "AppEvent",
    "AppEventConnection",
    "AppEventEdge",
    "AppOneTimeSale",
    "AppPurchaseOneTime",
    "AppSaleAdjustment",
    "AppSaleCredit",
    "AppSubscription",
    "AppSubscriptionCharge",
    "AppSubscriptionSale",
    "AppUsageCharge",
    "AppUsageSale",
    # App events
    "CreditApplied",
    "CreditFailed",
    "CreditPending",
    "LegacyTransaction",
    "OneTimeChargeAccepted",
    "OneTimeChargeActivated",
    "OneTimeChargeDeclined",
    "OneTimeChargeExpired",
    # Core objects
    "Organization",
    "ReferralAdjustment",
    "ReferralTransaction",
    "RelationshipDeactivated",
    "RelationshipInstalled",
    "RelationshipReactivated",
    "RelationshipUninstalled",
    "ServiceSale",
    "ServiceSaleAdjustment",
    "Shop",
    "SubscriptionApproachingCappedAmount",
    "SubscriptionCappedAmountUpdated",
    "SubscriptionChargeAccepted",
    "SubscriptionChargeActivated",
    "SubscriptionChargeCanceled",
    "SubscriptionChargeDeclined",
    "SubscriptionChargeExpired",
    "SubscriptionChargeFrozen",
    "SubscriptionChargeUnfrozen",
    "TaxTransaction",
    "ThemeSale",
    "ThemeSaleAdjustment",
    # Transactions
    "Transaction",
    "TransactionConnection",
    "TransactionEdge",
    "TransactionUnion",
    "UsageChargeApplied",
]

# Models reference classes defined later in their module; resolve once all exist.
for _name in __all__:
    _obj = globals()[_name]
    if isinstance(_obj, type) and issubclass(_obj, BaseModel):
        _obj.model_rebuild()
