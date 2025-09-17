"""
Shopify Partners API Client - A Python client for the Shopify Partners API.

This client provides two simple ways to interact with the Shopify Partners GraphQL API:
1. Raw Query - Execute GraphQL queries directly
2. FieldSelector - Build queries dynamically with field selection
"""

import logging
from typing import Any, Optional

import requests

from .client.base import BaseGraphQLClient
from .client.field_based_client import FieldBasedShopifyPartnersClient
from .config import ShopifyPartnersSDKSettings
from .queries.fields import CommonFields, FieldSelector
from .version import __version__

logger = logging.getLogger(__name__)


class ShopifyPartnersClient:
    """
    Simple, clean interface for the Shopify Partners API.

    This client provides two ways to interact with the API:
    1. Raw Query - Execute GraphQL queries directly using execute_query()
    2. FieldSelector - Build queries dynamically using the field_based property
    """

    def __init__(
        self,
        organization_id: int,
        access_token: str,
        api_version: str = "2025-04",
        http_client: Optional[requests.Session] = None,
    ):
        """Initialize the client.

        Args:
            organization_id: Shopify Partners organization ID
            access_token: API access token (must start with 'prtapi_')
            api_version: API version to use (default: 2025-04)
            http_client: Optional custom HTTP client

        Raises:
            ValueError: If credentials are invalid
        """
        # Create settings
        settings = ShopifyPartnersSDKSettings(
            organization_id=organization_id,
            access_token=access_token,
            api_version=api_version,
        )

        # Initialize base client
        self._client = BaseGraphQLClient(
            organization_id=organization_id,
            access_token=access_token,
            settings=settings,
            http_client=http_client,
        )

        # Initialize field-based client
        self._field_based = FieldBasedShopifyPartnersClient(self._client)

        # Validate credentials
        self._client.auth.validate_credentials()

        logger.info(
            "Shopify Partners Client initialized",
            api_version=api_version,
            organization_id=str(organization_id)[:4] + "***",
        )

    def query(
        self, query_name: str, fields: FieldSelector, **variables
    ) -> dict[str, Any]:
        """Build and execute a query using FieldSelector.

        Args:
            query_name: GraphQL query field name (e.g., 'app', 'publicApiVersions')
            fields: Field selection for the query
            **variables: Query variables

        Returns:
            GraphQL response data

        Example:
            >>> # Simple query
            >>> fields = FieldSelector().add_fields('id', 'title', 'handle')
            >>> result = client.query('app', fields, id='123')
            >>>
            >>> # Connection query with pagination
            >>> event_fields = FieldSelector().add_field('type')
            >>> app_fields = (FieldSelector()
            ...     .add_field('name')
            ...     .add_connection_field('events', event_fields, first=10))
            >>> result = client.query('app', app_fields, id='123')
        """
        query_builder = self._field_based.query(query_name, fields, **variables)
        return self._field_based.execute_query_builder(query_builder)

    def connection_query(
        self, query_name: str, node_fields: FieldSelector, **variables
    ) -> dict[str, Any]:
        """Build and execute a connection query using FieldSelector.

        Args:
            query_name: GraphQL query field name
            node_fields: Field selection for the nodes
            **variables: Query variables

        Returns:
            GraphQL response data

        Example:
            >>> # Query apps with pagination
            >>> app_fields = FieldSelector().add_fields('id', 'title', 'handle')
            >>> result = client.connection_query('apps', app_fields, first=25)
        """
        query_builder = self._field_based.connection_query(
            query_name, node_fields, **variables
        )
        return self._field_based.execute_query_builder(query_builder)

    def mutation(
        self, mutation_name: str, result_fields: FieldSelector, **variables
    ) -> dict[str, Any]:
        """Build and execute a mutation using FieldSelector.

        Args:
            mutation_name: GraphQL mutation field name
            result_fields: Field selection for the mutation result
            **variables: Mutation variables

        Returns:
            GraphQL response data

        Example:
            >>> # Create app credit
            >>> result_fields = (FieldSelector()
            ...     .add_nested_field('appCredit', FieldSelector()
            ...         .add_fields('id', 'description')
            ...         .add_money_field('amount'))
            ...     .add_nested_field('userErrors', FieldSelector()
            ...         .add_fields('field', 'message')))
            >>> input_data = {
            ...     "appId": "123",
            ...     "amount": {"amount": "10.00", "currencyCode": "USD"}
            ... }
            >>> result = client.mutation(
            ...     'appCreditCreate', result_fields, input=input_data
            ... )
        """
        mutation_builder = self._field_based.mutation(
            mutation_name, result_fields, **variables
        )
        return self._field_based.execute_mutation_builder(mutation_builder)

    def execute_raw(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a raw GraphQL query and return the full response.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name (for multi-operation queries)

        Returns:
            Full GraphQL response including data, errors, and extensions

        Example:
            >>> query = '''
            ... query GetApp($id: ID!) {
            ...   app(id: $id) {
            ...     id
            ...     title
            ...     handle
            ...   }
            ... }
            ... '''
            >>> response = client.execute_raw(query, {"id": "123"})
            >>> if response.get("errors"):
            >>>     print("Errors:", response["errors"])
            >>> else:
            >>>     print("Data:", response["data"]["app"])
        """
        return self._client.execute_query(query, variables, operation_name)

    def health_check(self) -> dict[str, Any]:
        """Perform a health check on the API connection.

        Returns:
            Health check results

        Example:
            >>> health = client.health_check()
            >>> print(health["status"])  # "healthy" or "unhealthy"
        """
        try:
            # Simple query to test connectivity
            query = """
            query HealthCheck {
              publicApiVersions {
                handle
                supported
              }
            }
            """
            response = self.execute_raw(query)
            result = response.get("data", {})

            return {
                "status": "healthy",
                "api_accessible": True,
                "authentication": "valid",
                "available_versions": len(result.get("publicApiVersions", [])),
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "api_accessible": False,
                "error": str(e),
            }

    def close(self):
        """Close the client and clean up resources.

        Example:
            >>> client.close()
        """
        self._client.close()
        logger.info("Shopify Partners Client closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    @property
    def stats(self) -> dict[str, Any]:
        """Get client statistics.

        Returns:
            Dictionary with request stats

        Example:
            >>> stats = client.stats
            >>> print(f"Total requests: {stats['request_count']}")
        """
        return self._client.get_stats()


__all__ = [
    "__version__",
    # Main API
    "ShopifyPartnersClient",
    # Field selection system
    "FieldSelector",
    "CommonFields",
    # Configuration
    "ShopifyPartnersSDKSettings",
]
