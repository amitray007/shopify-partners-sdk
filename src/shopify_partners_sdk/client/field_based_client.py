"""Field-based query and mutation client for the Shopify Partners API."""

import logging
from typing import Any

from shopify_partners_sdk.mutations.custom_builders import CustomMutationBuilder
from shopify_partners_sdk.queries.custom_builders import (
    CustomConnectionQueryBuilder,
    CustomFilterableQueryBuilder,
    CustomQueryBuilder,
)
from shopify_partners_sdk.queries.fields import FieldSelector

from .base import BaseGraphQLClient

logger = logging.getLogger(__name__)


class FieldBasedShopifyPartnersClient:
    """Field-based client interface for the Shopify Partners API.

    This client provides a field-based approach to building GraphQL queries
    and mutations, allowing users to specify exactly what fields they want.
    """

    def __init__(self, base_client: BaseGraphQLClient) -> None:
        """Initialize the field-based client.

        Args:
            base_client: The base GraphQL client to use
        """
        self._client = base_client

    # Query building methods
    def query(
        self, query_name: str, fields: FieldSelector, **variables
    ) -> CustomQueryBuilder:
        """Create a custom query builder.

        Args:
            query_name: GraphQL query field name (e.g., 'app', 'publicApiVersions')
            fields: Field selection for the query
            **variables: Query variables

        Returns:
            Configured query builder

        Example:
            >>> # Query API versions with custom fields
            >>> fields = FieldSelector().add_fields('handle', 'displayName')
            >>> query = client.field_based.query('publicApiVersions', fields)
            >>> result = client.execute_query_builder(query)
        """
        builder = CustomQueryBuilder(query_name, fields)
        return builder.add_variables(**variables)

    def connection_query(
        self, query_name: str, node_fields: FieldSelector, **variables
    ) -> CustomConnectionQueryBuilder:
        """Create a custom connection query builder for paginated results.

        Args:
            query_name: GraphQL query field name
            node_fields: Field selection for the nodes
            **variables: Query variables

        Returns:
            Configured connection query builder

        Example:
            >>> # Query apps with custom fields
            >>> app_fields = FieldSelector().add_fields('id', 'title', 'handle')
            >>> query = client.field_based.connection_query(
            ...     'apps', app_fields, first=25
            ... )
            >>> result = client.execute_query_builder(query)
        """
        # Build connection structure with edges and pageInfo
        connection_fields = FieldSelector()

        # Add edges with cursor and node
        edge_fields = FieldSelector(["cursor"]).add_nested_field("node", node_fields)
        connection_fields.add_nested_field("edges", edge_fields)

        # Add pageInfo
        page_info_fields = FieldSelector(["hasNextPage", "hasPreviousPage"])
        connection_fields.add_nested_field("pageInfo", page_info_fields)

        builder = CustomConnectionQueryBuilder(query_name, connection_fields)
        return builder.add_variables(**variables)

    def filterable_query(
        self, query_name: str, fields: FieldSelector, **variables
    ) -> CustomFilterableQueryBuilder:
        """Create a custom filterable query builder.

        Args:
            query_name: GraphQL query field name
            fields: Field selection for the query
            **variables: Query variables

        Returns:
            Configured filterable query builder

        Example:
            >>> # Query transactions with date filtering
            >>> fields = FieldSelector().add_fields('id', 'type', 'createdAt')
            >>> query = client.field_based.filterable_query('transactions', fields)
            >>> query = query.with_date_range('2024-01-01', '2024-12-31')
            >>> result = client.execute_query_builder(query)
        """
        builder = CustomFilterableQueryBuilder(query_name, fields)
        return builder.add_variables(**variables)

    # Mutation building methods
    def mutation(
        self, mutation_name: str, result_fields: FieldSelector, **variables
    ) -> CustomMutationBuilder:
        """Create a custom mutation builder.

        Args:
            mutation_name: GraphQL mutation field name
            result_fields: Field selection for the mutation result
            **variables: Mutation variables

        Returns:
            Configured mutation builder

        Example:
            >>> # Create app credit with custom result fields
            >>> result_fields = (FieldSelector()
            ...     .add_nested_field('appCredit', FieldSelector()
            ...         .add_fields('id', 'description')
            ...         .add_money_field('amount')))
            >>> mutation = client.field_based.mutation('appCreditCreate', result_fields)
            >>> mutation = mutation.with_input_variable(credit_input)
            >>> result = client.execute_mutation_builder(mutation)
        """
        builder = CustomMutationBuilder(mutation_name, result_fields)
        return builder.add_variables(**variables)

    def execute_query_builder(self, builder: CustomQueryBuilder) -> dict[str, Any]:
        """Execute a query builder and return the result.

        Args:
            builder: The query builder to execute

        Returns:
            GraphQL response data

        Raises:
            GraphQLError: If the query fails
        """
        query = builder.build_query()
        variables = builder.variables

        logger.debug(
            "Executing dynamic query",
            query_name=builder.get_query_name(),
            variables=list(variables.keys()),
        )

        response = self._client.execute_query(query, variables)
        return response["data"]

    def execute_mutation_builder(
        self, builder: CustomMutationBuilder
    ) -> dict[str, Any]:
        """Execute a mutation builder and return the result.

        Args:
            builder: The mutation builder to execute

        Returns:
            GraphQL response data

        Raises:
            GraphQLError: If the mutation fails
        """
        mutation = builder.build_mutation()
        variables = builder.variables

        logger.debug(
            "Executing dynamic mutation",
            mutation_name=builder.get_mutation_name(),
            variables=list(variables.keys()),
        )

        response = self._client.execute_query(mutation, variables)
        return response["data"]
