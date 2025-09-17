"""Shop-related model objects for the Shopify Partners API."""

from pydantic import Field, validator

from shopify_partners_sdk.models.base import Actor
from shopify_partners_sdk.models.scalars import URL


class Shop(Actor):
    """A Shopify shop.

    Represents a merchant's shop that can install apps from the Partner organization.
    """

    myshopify_domain: URL = Field(
        ...,
        description="The shop's .myshopify.com domain name",
        alias="myshopifyDomain",
    )

    @validator("myshopify_domain")
    def validate_myshopify_domain(cls, v: str) -> str:
        """Validate that the domain ends with .myshopify.com."""
        if not v.endswith(".myshopify.com"):
            raise ValueError("myshopify_domain must end with .myshopify.com")
        return v

    @property
    def shop_name(self) -> str:
        """Get the shop name from the myshopify domain."""
        return self.myshopify_domain.replace(".myshopify.com", "")

    def __str__(self) -> str:
        """String representation showing shop domain."""
        return f"Shop(domain='{self.myshopify_domain}', name='{self.name}')"
