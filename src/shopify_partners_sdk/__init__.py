"""
Shopify Partners API Client - A Python client for the Shopify Partners API.

This client provides two simple ways to interact with the Shopify Partners GraphQL API:
1. Raw Query - Execute GraphQL queries directly
2. FieldSelector - Build queries dynamically with field selection
"""

from collections.abc import Iterator
import logging
from typing import Any, Optional, Self, Union

import requests

from .client.base import BaseGraphQLClient
from .client.field_based_client import FieldBasedShopifyPartnersClient
from .config import ShopifyPartnersSDKSettings
from .exceptions.validation import SchemaValidationError
from .queries.fields import CommonFields, FieldSelector
from .schema import SUPPORTED_API_VERSIONS, PartnerSchema, load_schema
from .version import __version__

logger = logging.getLogger(__name__)


def _explicit_settings(
    organization_id: int | str | None,
    access_token: str | None,
    api_version: str | None,
) -> dict[str, Any]:
    """Settings the caller passed; anything omitted comes from the environment."""
    explicit: dict[str, Any] = {}
    if organization_id is not None:
        if not str(organization_id).isdigit():
            raise ValueError("organization_id must be a positive integer")
        explicit["organization_id"] = int(organization_id)
    if access_token is not None:
        explicit["access_token"] = access_token
    if api_version:
        explicit["api_version"] = api_version
    return explicit


class ShopifyPartnersClient:
    """
    Simple, clean interface for the Shopify Partners API.

    This client provides two ways to interact with the API:
    1. Raw Query - Execute GraphQL queries directly using execute_query()
    2. FieldSelector - Build queries dynamically using the field_based property
    """

    def __init__(
        self,
        organization_id: int | str | None = None,
        access_token: str | None = None,
        api_version: str | None = None,
        http_client: requests.Session | None = None,
    ) -> None:
        """Initialize the client.

        Each argument left out falls back to its SHOPIFY_PARTNERS_* environment
        variable (or a local .env file), then to the default.

        Args:
            organization_id: Shopify Partners organization ID
                (SHOPIFY_PARTNERS_ORGANIZATION_ID)
            access_token: API access token starting with 'prtapi_'
                (SHOPIFY_PARTNERS_ACCESS_TOKEN)
            api_version: One of SUPPORTED_API_VERSIONS
                (SHOPIFY_PARTNERS_API_VERSION, default 2026-10)
            http_client: Optional custom HTTP client

        Raises:
            ValueError: If credentials or the API version are invalid
            AuthenticationError: If no organization ID or access token is available
        """
        settings = ShopifyPartnersSDKSettings(
            **_explicit_settings(organization_id, access_token, api_version)
        )
        self._client = BaseGraphQLClient(settings=settings, http_client=http_client)
        self._field_based = FieldBasedShopifyPartnersClient(
            self._client, load_schema(settings.api_version)
        )
        self._client.auth.validate_credentials()
        logger.debug(
            "Shopify Partners client initialized for API version %s",
            settings.api_version,
        )

    @property
    def api_version(self) -> str:
        """API version this client sends requests to."""
        return self._client.settings.api_version

    @property
    def schema(self) -> PartnerSchema:
        """Bundled schema for this client's API version, used to validate queries."""
        return self._field_based.schema

    def query(
        self, query_name: str, fields: FieldSelector, **variables: Any
    ) -> dict[str, Any]:
        """Build and execute a query using FieldSelector.

        Args:
            query_name: GraphQL query field name (e.g., 'app', 'publicApiVersions')
            fields: Field selection for the query
            **variables: Query variables

        Returns:
            GraphQL response data

        Raises:
            SchemaValidationError: If the query, a field, or an argument does not
                exist in this API version

        Example:
            >>> fields = FieldSelector().add_fields('id', 'name', 'apiKey')
            >>> result = client.query('app', fields, id='gid://partners/App/123')
            >>>
            >>> # Nested connection with inline arguments
            >>> event_fields = FieldSelector().add_fields('type', 'occurredAt')
            >>> app_fields = (FieldSelector()
            ...     .add_field('name')
            ...     .add_connection_field('events', event_fields, first=10))
            >>> result = client.query('app', app_fields, id='gid://partners/App/123')
        """
        query_builder = self._field_based.query(query_name, fields, **variables)
        return self._field_based.execute_query_builder(query_builder)

    def connection_query(
        self, query_name: str, node_fields: FieldSelector, **variables: Any
    ) -> dict[str, Any]:
        """Build and execute a connection query using FieldSelector.

        Args:
            query_name: GraphQL query field name
            node_fields: Field selection for the nodes
            **variables: Query variables

        Returns:
            GraphQL response data

        Example:
            >>> result = client.connection_query(
            ...     'transactions', CommonFields.basic_transaction(), first=25
            ... )
            >>> edges = result['transactions']['edges']
        """
        query_builder = self._field_based.connection_query(
            query_name, node_fields, **variables
        )
        return self._field_based.execute_query_builder(query_builder)

    def mutation(
        self, mutation_name: str, result_fields: FieldSelector, **variables: Any
    ) -> dict[str, Any]:
        """Build and execute a mutation using FieldSelector.

        Args:
            mutation_name: GraphQL mutation field name
            result_fields: Field selection for the mutation result
            **variables: Mutation variables

        Returns:
            GraphQL response data

        Example:
            >>> result_fields = (FieldSelector()
            ...     .add_nested_field('appCredit', FieldSelector()
            ...         .add_fields('id', 'name')
            ...         .add_money_field('amount'))
            ...     .add_nested_field('userErrors', CommonFields.user_error()))
            >>> result = client.mutation(
            ...     'appCreditCreate', result_fields,
            ...     appId='gid://partners/App/123',
            ...     shopId='gid://partners/Shop/456',
            ...     description='Refund for downtime',
            ...     amount={'amount': '10.00', 'currencyCode': 'USD'},
            ... )
        """
        mutation_builder = self._field_based.mutation(
            mutation_name, result_fields, **variables
        )
        return self._field_based.execute_mutation_builder(mutation_builder)

    def paginate(
        self,
        query_name: str,
        node_fields: FieldSelector,
        page_size: int | None = None,
        max_pages: int | None = None,
        **variables: Any,
    ) -> Iterator[dict[str, Any]]:
        """Iterate over every node of a connection, requesting pages as needed.

        Args:
            query_name: Connection query, e.g. 'transactions' or 'events'
            node_fields: Fields to select on each node
            page_size: Nodes per request (defaults to settings.default_page_size)
            max_pages: Stop after this many requests (None means no limit)
            **variables: Other query arguments

        Example:
            >>> for event in client.paginate(
            ...     'events',
            ...     FieldSelector().add_fields('id', 'eventType', 'occurredAt'),
            ...     filter={'eventTypes': ['RELATIONSHIP_INSTALLED']},
            ... ):
            ...     print(event['eventType'])
        """
        return self._field_based.paginate(
            query_name, node_fields, page_size, max_pages, **variables
        )

    def execute_raw(
        self,
        query: str,
        variables: dict[str, Any] | None = None,
        operation_name: str | None = None,
    ) -> dict[str, Any]:
        """Execute a raw GraphQL query and return the full response.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name (for multi-operation queries)

        Returns:
            The full GraphQL response: ``data`` and any ``extensions``

        Raises:
            GraphQLError: If the response contains GraphQL errors

        Example:
            >>> query = '''
            ... query GetApp($id: ID!) {
            ...   app(id: $id) {
            ...     id
            ...     name
            ...   }
            ... }
            ... '''
            >>> response = client.execute_raw(query, {"id": "gid://partners/App/123"})
            >>> print(response["data"]["app"])
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

    def close(self) -> None:
        """Close the client and clean up resources.

        Example:
            >>> client.close()
        """
        self._client.close()

    def __enter__(self) -> Self:
        """Context manager entry."""
        return self

    def __exit__(self, *exc_info: object) -> None:
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
    # Schema
    "SUPPORTED_API_VERSIONS",
    "PartnerSchema",
    "SchemaValidationError",
]
