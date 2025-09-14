"""Enum types from the Shopify Partners GraphQL API."""

from enum import Enum


class AppEventType(str, Enum):
    """The type of an app event."""

    CREDIT_APPLIED = "CREDIT_APPLIED"
    CREDIT_FAILED = "CREDIT_FAILED"
    CREDIT_PENDING = "CREDIT_PENDING"
    ONE_TIME_CHARGE_ACCEPTED = "ONE_TIME_CHARGE_ACCEPTED"
    ONE_TIME_CHARGE_ACTIVATED = "ONE_TIME_CHARGE_ACTIVATED"
    ONE_TIME_CHARGE_DECLINED = "ONE_TIME_CHARGE_DECLINED"
    ONE_TIME_CHARGE_EXPIRED = "ONE_TIME_CHARGE_EXPIRED"
    RELATIONSHIP_DEACTIVATED = "RELATIONSHIP_DEACTIVATED"
    RELATIONSHIP_INSTALLED = "RELATIONSHIP_INSTALLED"
    RELATIONSHIP_REACTIVATED = "RELATIONSHIP_REACTIVATED"
    RELATIONSHIP_UNINSTALLED = "RELATIONSHIP_UNINSTALLED"
    SUBSCRIPTION_APPROACHING_CAPPED_AMOUNT = "SUBSCRIPTION_APPROACHING_CAPPED_AMOUNT"
    SUBSCRIPTION_CAPPED_AMOUNT_UPDATED = "SUBSCRIPTION_CAPPED_AMOUNT_UPDATED"
    SUBSCRIPTION_CHARGE_ACCEPTED = "SUBSCRIPTION_CHARGE_ACCEPTED"
    SUBSCRIPTION_CHARGE_ACTIVATED = "SUBSCRIPTION_CHARGE_ACTIVATED"
    SUBSCRIPTION_CHARGE_CANCELED = "SUBSCRIPTION_CHARGE_CANCELED"
    SUBSCRIPTION_CHARGE_DECLINED = "SUBSCRIPTION_CHARGE_DECLINED"
    SUBSCRIPTION_CHARGE_EXPIRED = "SUBSCRIPTION_CHARGE_EXPIRED"
    SUBSCRIPTION_CHARGE_FROZEN = "SUBSCRIPTION_CHARGE_FROZEN"
    SUBSCRIPTION_CHARGE_UNFROZEN = "SUBSCRIPTION_CHARGE_UNFROZEN"
    USAGE_CHARGE_APPLIED = "USAGE_CHARGE_APPLIED"


class AppPricingInterval(str, Enum):
    """The billing frequency for the app."""

    EVERY_30_DAYS = "EVERY_30_DAYS"
    ANNUAL = "ANNUAL"


class TransactionType(str, Enum):
    """The type of a transaction."""

    APP_ONE_TIME_SALE = "APP_ONE_TIME_SALE"
    APP_SALE_ADJUSTMENT = "APP_SALE_ADJUSTMENT"
    APP_SALE_CREDIT = "APP_SALE_CREDIT"
    APP_SUBSCRIPTION_SALE = "APP_SUBSCRIPTION_SALE"
    APP_USAGE_SALE = "APP_USAGE_SALE"
    LEGACY = "LEGACY"
    LEGACY_TRANSACTION = "LEGACY_TRANSACTION"  # Added for schema compatibility
    REFERRAL = "REFERRAL"
    REFERRAL_ADJUSTMENT = "REFERRAL_ADJUSTMENT"
    REFERRAL_TRANSACTION = "REFERRAL_TRANSACTION"  # Added for schema compatibility
    SERVICE_SALE = "SERVICE_SALE"
    SERVICE_SALE_ADJUSTMENT = "SERVICE_SALE_ADJUSTMENT"
    TAX = "TAX"
    TAX_TRANSACTION = "TAX_TRANSACTION"  # Added for schema compatibility
    THEME_SALE = "THEME_SALE"
    THEME_SALE_ADJUSTMENT = "THEME_SALE_ADJUSTMENT"


class Currency(str, Enum):
    """ISO 4217 currency codes supported by Shopify Partners API."""

    # Major currencies
    USD = "USD"  # United States dollar
    EUR = "EUR"  # Euro
    GBP = "GBP"  # British pound
    CAD = "CAD"  # Canadian dollar
    AUD = "AUD"  # Australian dollar
    JPY = "JPY"  # Japanese yen
    CHF = "CHF"  # Swiss franc
    NZD = "NZD"  # New Zealand dollar
    SEK = "SEK"  # Swedish krona
    NOK = "NOK"  # Norwegian krone
    DKK = "DKK"  # Danish krone
    PLN = "PLN"  # Polish złoty
    CZK = "CZK"  # Czech koruna
    HUF = "HUF"  # Hungarian forint

    # Asian currencies
    CNY = "CNY"  # Chinese yuan
    KRW = "KRW"  # South Korean won
    HKD = "HKD"  # Hong Kong dollar
    SGD = "SGD"  # Singapore dollar
    THB = "THB"  # Thai baht
    INR = "INR"  # Indian rupee
    MYR = "MYR"  # Malaysian ringgit
    PHP = "PHP"  # Philippine peso
    IDR = "IDR"  # Indonesian rupiah
    VND = "VND"  # Vietnamese đồng

    # Latin American currencies
    BRL = "BRL"  # Brazilian real
    MXN = "MXN"  # Mexican peso
    ARS = "ARS"  # Argentine peso
    CLP = "CLP"  # Chilean peso
    COP = "COP"  # Colombian peso
    PEN = "PEN"  # Peruvian sol

    # African currencies
    ZAR = "ZAR"  # South African rand
    NGN = "NGN"  # Nigerian naira
    EGP = "EGP"  # Egyptian pound

    # Middle Eastern currencies
    AED = "AED"  # UAE dirham
    SAR = "SAR"  # Saudi riyal
    ILS = "ILS"  # Israeli shekel
    TRY = "TRY"  # Turkish lira

    # Precious metals (testing)
    XAG = "XAG"  # Silver
    XAU = "XAU"  # Gold
    XTS = "XTS"  # Testing currency code


class ConversationStatus(str, Enum):
    """The status of a conversation (DEPRECATED)."""

    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class JobStatus(str, Enum):
    """The status of a job (DEPRECATED)."""

    NEW = "NEW"
    OPENED = "OPENED"
    RESPONDED = "RESPONDED"
    AWAITING_RESPONSE = "AWAITING_RESPONSE"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
    CLOSED = "CLOSED"
    EXPIRED = "EXPIRED"
    INACTIVE = "INACTIVE"


class MessageSentVia(str, Enum):
    """Platform used to send a message."""

    EMAIL = "EMAIL"
    PARTNERS_DASHBOARD = "PARTNERS_DASHBOARD"
    PHONE = "PHONE"


class EventsinkTopic(str, Enum):
    """Event sink topics (unstable API)."""

    CUSTOMER_EVENTS_CREATE = "CUSTOMER_EVENTS_CREATE"
    CUSTOMERS_REDACT = "CUSTOMERS_REDACT"
    DELIVERY_PROMISES_CREATE = "DELIVERY_PROMISES_CREATE"


class EventsinkQueue(str, Enum):
    """Event sink queue types (unstable API)."""

    STANDARD = "STANDARD"
    PRIORITY = "PRIORITY"


class TaxType(str, Enum):
    """Types of tax transactions."""

    GST = "GST"
    HST = "HST"
    PST = "PST"
    QST = "QST"
    VAT = "VAT"
    SALES_TAX = "SALES_TAX"
    OTHER = "OTHER"


class ChargeStatus(str, Enum):
    """Status of app charges."""

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    ACTIVE = "ACTIVE"
    DECLINED = "DECLINED"
    EXPIRED = "EXPIRED"
    FROZEN = "FROZEN"
    CANCELLED = "CANCELLED"


class ServiceType(str, Enum):
    """Types of services in the Experts Marketplace."""

    SETUP = "SETUP"
    DEVELOPMENT = "DEVELOPMENT"
    DESIGN = "DESIGN"
    MARKETING = "MARKETING"
    TRAINING = "TRAINING"
    CONSULTATION = "CONSULTATION"
    MAINTENANCE = "MAINTENANCE"
    OTHER = "OTHER"


class ApiVersionStatus(str, Enum):
    """Status of API versions."""

    SUPPORTED = "SUPPORTED"
    DEPRECATED = "DEPRECATED"
    UNSUPPORTED = "UNSUPPORTED"


# Type aliases for backwards compatibility
AppEventTypes = AppEventType  # Match GraphQL schema naming
