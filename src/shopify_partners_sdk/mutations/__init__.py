"""Modern field-based mutation system for the Shopify Partners SDK."""

from .base import MutationResult
from .custom_builders import CustomMutationBuilder

__all__ = [
    # Core result container
    "MutationResult",
    # Custom mutation building system
    "CustomMutationBuilder",
]
