"""API Version-related model objects for the Shopify Partners API."""

from pydantic import Field

from shopify_partners_sdk.models.base import ShopifyPartnersBaseModel


class ApiVersion(ShopifyPartnersBaseModel):
    """Represents a version of the Shopify Partners API."""

    display_name: str = Field(
        ..., description="Human-readable version name", alias="displayName"
    )
    handle: str = Field(..., description="Version identifier (YYYY-MM or 'unstable')")
    supported: bool = Field(
        ..., description="Whether the version is supported by Shopify"
    )

    @property
    def is_stable(self) -> bool:
        """Check if this is a stable API version."""
        return self.handle != "unstable"

    @property
    def is_current(self) -> bool:
        """Check if this is the current stable version (2025-04)."""
        return self.handle == "2025-04"

    def __str__(self) -> str:
        """String representation showing version details."""
        status = "supported" if self.supported else "unsupported"
        return f"ApiVersion(handle='{self.handle}', {status})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"ApiVersion("
            f"handle='{self.handle}', "
            f"display_name='{self.display_name}', "
            f"supported={self.supported}"
            f")"
        )
