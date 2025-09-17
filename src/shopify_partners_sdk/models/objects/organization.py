"""Organization-related model objects for the Shopify Partners API."""

from shopify_partners_sdk.models.base import Actor


class Organization(Actor):
    """A Partner organization.

    Represents the Partner organization that owns apps and receives transaction data.
    """

    def __str__(self) -> str:
        """String representation showing organization name."""
        return f"Organization(name='{self.name}', id='{self.id}')"
