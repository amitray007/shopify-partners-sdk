"""Field-based query and mutation client for the Shopify Partners API."""

from collections.abc import Iterator
import logging
from typing import Any

from shopify_partners_sdk.exceptions.validation import InvalidPageSizeError
from shopify_partners_sdk.mutations.custom_builders import CustomMutationBuilder
from shopify_partners_sdk.queries.custom_builders import (
    CustomConnectionQueryBuilder,
    CustomFilterableQueryBuilder,
    CustomQueryBuilder,
    OperationBuilder,
    connection_fields,
)
from shopify_partners_sdk.queries.fields import FieldSelector
from shopify_partners_sdk.schema import PartnerSchema, load_schema

from .base import BaseGraphQLClient

logger = logging.getLogger(__name__)


class FieldBasedShopifyPartnersClient:
    """Builds field-based queries and mutations and runs them on a base client.

    Every builder validates against the schema of the client's API version.
    """

    def __init__(
        self, base_client: BaseGraphQLClient, schema: PartnerSchema | None = None
    ) -> None:
        """Initialize the field-based client.

        Args:
            base_client: The base GraphQL client to use
            schema: Schema to validate against (defaults to the client's API version)
        """
        self._client = base_client
        self._schema = schema or load_schema(base_client.settings.api_version)

    @property
    def schema(self) -> PartnerSchema:
        """Schema the builders validate against."""
        return self._schema

    def query(
        self, query_name: str, fields: FieldSelector, **variables: Any
    ) -> CustomQueryBuilder:
        """Create a query builder for a top-level query field.

        Example:
            >>> fields = FieldSelector().add_fields('handle', 'displayName')
            >>> builder = client.query('publicApiVersions', fields)
        """
        builder = CustomQueryBuilder(query_name, fields, schema=self._schema)
        return builder.add_variables(**variables)

    def connection_query(
        self, query_name: str, node_fields: FieldSelector, **variables: Any
    ) -> CustomConnectionQueryBuilder:
        """Create a builder that selects ``edges { cursor node { ... } }`` and pageInfo.

        Example:
            >>> builder = client.connection_query(
            ...     'transactions', CommonFields.basic_transaction(), first=25
            ... )
        """
        builder = CustomConnectionQueryBuilder(
            query_name, connection_fields(node_fields), schema=self._schema
        )
        return builder.add_variables(**variables)

    def filterable_query(
        self, query_name: str, fields: FieldSelector, **variables: Any
    ) -> CustomFilterableQueryBuilder:
        """Create a query builder with date, shop, and app filter helpers.

        Example:
            >>> builder = client.filterable_query('transactions', fields)
            >>> builder = builder.with_date_range('2026-01-01', '2026-12-31')
        """
        builder = CustomFilterableQueryBuilder(query_name, fields, schema=self._schema)
        return builder.add_variables(**variables)

    def mutation(
        self, mutation_name: str, result_fields: FieldSelector, **variables: Any
    ) -> CustomMutationBuilder:
        """Create a mutation builder for a top-level mutation field.

        Example:
            >>> result_fields = FieldSelector().add_nested_field(
            ...     'userErrors', FieldSelector(['field', 'message']))
            >>> builder = client.mutation(
            ...     'appSubscriptionCancel', result_fields, appId='...', shopId='...',
            ...     prorate=True, deferCancellation=False, skipFinalUsageCharge=False)
        """
        builder = CustomMutationBuilder(
            mutation_name, result_fields, schema=self._schema
        )
        return builder.add_variables(**variables)

    def paginate(
        self,
        query_name: str,
        node_fields: FieldSelector,
        page_size: int | None = None,
        max_pages: int | None = None,
        **variables: Any,
    ) -> Iterator[dict[str, Any]]:
        """Yield every node of a connection query, fetching pages as needed.

        Args:
            query_name: Connection field, e.g. 'transactions' or 'events'
            node_fields: Fields to select on each node
            page_size: Nodes per request (defaults to settings.default_page_size)
            max_pages: Stop after this many requests (None means no limit)
            **variables: Other arguments, e.g. types=[...] or filter={...}

        Yields:
            Each node's data, in API order
        """
        first = self._page_size(page_size)
        reserved = {"first", "last", "before"} & variables.keys()
        if reserved:
            raise ValueError(
                f"paginate() sets {', '.join(sorted(reserved))} itself; "
                "use page_size and after instead"
            )
        cursor: str | None = variables.pop("after", None)
        pages = 0
        while max_pages is None or pages < max_pages:
            builder = self.connection_query(
                query_name, node_fields, first=first, after=cursor, **variables
            )
            connection = self.execute_query_builder(builder)[query_name]
            pages += 1
            edges = connection.get("edges") or []
            for edge in edges:
                yield edge["node"]
            next_cursor = edges[-1]["cursor"] if edges else None
            # Stop on a repeated cursor too, so a stuck hasNextPage cannot loop forever.
            if not connection["pageInfo"]["hasNextPage"] or next_cursor in (
                None,
                cursor,
            ):
                return
            cursor = next_cursor

    def _page_size(self, page_size: int | None) -> int:
        limit = self._client.settings.max_page_size
        size = (
            self._client.settings.default_page_size if page_size is None else page_size
        )
        if not 1 <= size <= limit:
            raise InvalidPageSizeError(size, limit)
        return size

    def execute_query_builder(self, builder: OperationBuilder) -> dict[str, Any]:
        """Execute a query builder and return the response ``data``.

        Raises:
            GraphQLError: If the query fails
        """
        return self._execute(builder)

    def execute_mutation_builder(self, builder: OperationBuilder) -> dict[str, Any]:
        """Execute a mutation builder and return the response ``data``.

        Raises:
            GraphQLError: If the mutation fails
        """
        return self._execute(builder)

    def _execute(self, builder: OperationBuilder) -> dict[str, Any]:
        document = builder.build()
        variables = builder.variables
        logger.debug(
            "Executing %s with variables %s", builder.operation, list(variables)
        )
        response = self._client.execute_query(document, variables)
        return dict(response["data"])
