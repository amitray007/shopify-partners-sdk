"""Modern field-based query system for the Shopify Partners SDK."""

from .base import QueryResult
from .custom_builders import (
    CustomConnectionQueryBuilder,
    CustomFilterableQueryBuilder,
    CustomQueryBuilder,
)
from .fields import CommonFields, FieldSelector

__all__ = [
    # Core result container
    "QueryResult",
    # Custom query building system
    "CustomQueryBuilder",
    "CustomConnectionQueryBuilder",
    "CustomFilterableQueryBuilder",
    # Field selection system
    "FieldSelector",
    "CommonFields",
]
