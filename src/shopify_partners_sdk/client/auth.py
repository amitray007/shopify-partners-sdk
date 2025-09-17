"""Authentication handler for the Shopify Partners API."""

from typing import Optional

from shopify_partners_sdk.config import ShopifyPartnersSDKSettings
from shopify_partners_sdk.exceptions.auth import AuthenticationError


class AuthenticationHandler:
    """Handles authentication for Shopify Partners API requests.

    This class manages organization IDs, access tokens, and builds the necessary
    headers for API authentication.
    """

    def __init__(
        self,
        organization_id: Optional[str] = None,
        access_token: Optional[str] = None,
        settings: Optional[ShopifyPartnersSDKSettings] = None,
    ) -> None:
        """Initialize the authentication handler.

        Args:
            organization_id: Shopify Partners organization ID
            access_token: Shopify Partners API access token
            settings: SDK settings instance
        """
        self._settings = settings or ShopifyPartnersSDKSettings()
        self._organization_id = organization_id or self._settings.organization_id
        self._access_token = access_token or self._settings.access_token

    @property
    def organization_id(self) -> str:
        """Get the organization ID.

        Returns:
            The organization ID.

        Raises:
            AuthenticationError: If organization ID is not set.
        """
        if not self._organization_id:
            raise AuthenticationError(
                "Organization ID is required. Set it during initialization or via "
                "SHOPIFY_PARTNERS_ORGANIZATION_ID environment variable."
            )
        return self._organization_id

    @organization_id.setter
    def organization_id(self, value: str) -> None:
        """Set the organization ID.

        Args:
            value: The organization ID to set.

        Raises:
            AuthenticationError: If the organization ID format is invalid.
        """
        if not value or not value.isdigit():
            raise AuthenticationError(
                "Organization ID must be a non-empty numeric string"
            )
        self._organization_id = value

    @property
    def access_token(self) -> str:
        """Get the access token.

        Returns:
            The access token.

        Raises:
            AuthenticationError: If access token is not set.
        """
        if not self._access_token:
            raise AuthenticationError(
                "Access token is required. Set it during initialization or via "
                "SHOPIFY_PARTNERS_ACCESS_TOKEN environment variable."
            )
        return self._access_token

    @access_token.setter
    def access_token(self, value: str) -> None:
        """Set the access token.

        Args:
            value: The access token to set.

        Raises:
            AuthenticationError: If the access token format is invalid.
        """
        if not value or not value.startswith("prtapi_"):
            raise AuthenticationError(
                "Access token must be a non-empty string starting with 'prtapi_'"
            )
        self._access_token = value

    def get_api_endpoint(self) -> str:
        """Build the full GraphQL API endpoint URL.

        Returns:
            The complete API endpoint URL.

        Raises:
            AuthenticationError: If organization ID is not available.
        """
        org_id = self.organization_id  # This will raise if not set
        base_url = self._settings.base_url
        api_version = self._settings.api_version
        return f"{base_url}/{org_id}/api/{api_version}/graphql.json"

    def get_auth_headers(self) -> dict[str, str]:
        """Build authentication headers for API requests.

        Returns:
            Dictionary of HTTP headers for authentication.

        Raises:
            AuthenticationError: If access token is not available.
        """
        token = self.access_token  # This will raise if not set
        return {
            "X-Shopify-Access-Token": token,
        }

    def get_request_headers(self) -> dict[str, str]:
        """Build complete headers for API requests including auth and content type.

        Returns:
            Dictionary of HTTP headers for API requests.

        Raises:
            AuthenticationError: If authentication credentials are not available.
        """
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"shopify-partners-sdk-python/{self._settings.api_version}",
        }
        headers.update(self.get_auth_headers())
        return headers

    def is_authenticated(self) -> bool:
        """Check if authentication credentials are available.

        Returns:
            True if both organization ID and access token are available and valid.
        """
        try:
            _ = self.organization_id
            _ = self.access_token
            return True
        except AuthenticationError:
            return False

    def validate_credentials(self) -> None:
        """Validate that authentication credentials are properly configured.

        Raises:
            AuthenticationError: If credentials are missing or invalid.
        """
        if not self.is_authenticated():
            missing = []
            if not self._organization_id:
                missing.append("organization_id")
            if not self._access_token:
                missing.append("access_token")

            raise AuthenticationError(
                f"Missing required authentication credentials: {', '.join(missing)}. "
                "Provide them during client initialization or set the corresponding "
                "environment variables: SHOPIFY_PARTNERS_ORGANIZATION_ID and "
                "SHOPIFY_PARTNERS_ACCESS_TOKEN."
            )

    def __repr__(self) -> str:
        """String representation of the authentication handler."""
        org_masked = "***" if self._organization_id else "None"
        token_masked = "prtapi_***" if self._access_token else "None"
        return f"AuthenticationHandler(organization_id={org_masked}, access_token={token_masked})"
