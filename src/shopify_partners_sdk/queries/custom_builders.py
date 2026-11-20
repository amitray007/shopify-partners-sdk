"""Custom GraphQL query builders with field selection."""

from typing import Any, ClassVar, Self

from shopify_partners_sdk.config.defaults import DEFAULT_API_VERSION
from shopify_partners_sdk.exceptions.validation import SchemaValidationError
from shopify_partners_sdk.schema import (
    Operation,
    PartnerSchema,
    load_schema,
    named_type,
)

from .fields import FieldSelector


def connection_fields(node_fields: FieldSelector) -> FieldSelector:
    """Wrap node fields in ``edges { cursor node { ... } } pageInfo { ... }``."""
    edges = FieldSelector(["cursor"]).add_nested_field("node", node_fields)
    page_info = FieldSelector(["hasNextPage", "hasPreviousPage"])
    return (
        FieldSelector()
        .add_nested_field("edges", edges)
        .add_nested_field("pageInfo", page_info)
    )


class OperationBuilder:
    """Builds one top-level query or mutation field, typed by the Partner API schema.

    Variable types come from the schema, so ``$types: [TransactionType!]`` and
    ``$amount: MoneyInput!`` are declared exactly as the API expects. Unknown root
    fields, arguments, and selected fields raise SchemaValidationError with
    suggestions before any request is sent.
    """

    operation: ClassVar[Operation] = "query"

    def __init__(
        self,
        root_field: str,
        fields: FieldSelector | None = None,
        operation_name: str | None = None,
        schema: PartnerSchema | None = None,
    ) -> None:
        """Initialize the builder.

        Args:
            root_field: Top-level field name (e.g. 'transactions', 'appCreditCreate')
            fields: Field selector for the result
            operation_name: Optional GraphQL operation name
            schema: Schema to validate against (defaults to the default API version)

        Raises:
            SchemaValidationError: If ``root_field`` does not exist
        """
        self._schema = schema or load_schema(DEFAULT_API_VERSION)
        self._root_type = self._schema.root_type(self.operation)
        self._schema.root_field(self.operation, root_field)
        self._root_field = root_field
        self._fields = fields
        self._operation_name = operation_name
        self._variables: dict[str, Any] = {}

    @property
    def schema(self) -> PartnerSchema:
        """Schema this builder validates against."""
        return self._schema

    @property
    def variables(self) -> dict[str, Any]:
        """Get the current variables."""
        return self._variables.copy()

    def add_variable(self, name: str, value: Any) -> Self:
        """Pass an argument to the root field as a variable. ``None`` is skipped.

        Raises:
            SchemaValidationError: If the root field has no such argument
        """
        if value is not None:
            self._schema.argument_type(self._root_type, self._root_field, name)
            self._variables[name] = value
        return self

    def add_variables(self, **variables: Any) -> Self:
        """Add several variables; see add_variable()."""
        for name, value in variables.items():
            self.add_variable(name, value)
        return self

    def with_fields(self, fields: FieldSelector) -> Self:
        """Set the fields to select on the result."""
        self._fields = fields
        return self

    def with_operation_name(self, name: str) -> Self:
        """Set the GraphQL operation name."""
        self._operation_name = name
        return self

    def default_fields(self) -> FieldSelector | None:
        """Selection used when none is given."""
        return None

    def build(self) -> str:
        """Build the GraphQL document.

        Raises:
            SchemaValidationError: If a required argument is missing or the selection
                does not match the schema
        """
        self._check_required_variables()
        header = f"{self.operation}{self._render_operation_name()}"
        header += self._render_variable_definitions()
        call = f"{self._root_field}{self._render_arguments()}"
        selection = self._render_selection()
        if selection:
            return f"{header} {{\n  {call} {{\n{selection}\n  }}\n}}"
        return f"{header} {{\n  {call}\n}}"

    def get_result_type(self) -> type:
        """Get the expected result type (always dict)."""
        return dict

    def _render_operation_name(self) -> str:
        return f" {self._operation_name}" if self._operation_name else ""

    def _render_variable_definitions(self) -> str:
        if not self._variables:
            return ""
        definitions = [
            f"${name}: {self._schema.argument_type(self._root_type, self._root_field, name)}"
            for name in self._variables
        ]
        return f"({', '.join(definitions)})"

    def _render_arguments(self) -> str:
        if not self._variables:
            return ""
        return f"({', '.join(f'{name}: ${name}' for name in self._variables)})"

    def _render_selection(self) -> str:
        return_type = named_type(
            self._schema.root_field(self.operation, self._root_field)["type"]
        )
        fields = self._fields or self.default_fields()
        if self._schema.is_leaf(return_type):
            if fields:
                raise SchemaValidationError(
                    f"'{self._root_field}' returns {return_type}, which takes no "
                    "sub-selection."
                )
            return ""
        if not fields:
            raise SchemaValidationError(
                f"Select at least one field of {return_type} for '{self._root_field}'."
            )
        return fields.build(2, self._schema, return_type)

    def _check_required_variables(self) -> None:
        required = self._schema.required_arguments(self._root_type, self._root_field)
        missing = [name for name in required if name not in self._variables]
        if missing:
            raise SchemaValidationError(
                f"'{self._root_field}' requires argument(s): {', '.join(missing)}."
            )


class CustomQueryBuilder(OperationBuilder):
    """Custom query builder for any top-level Partner API query."""

    operation: ClassVar[Operation] = "query"

    def get_query_name(self) -> str:
        """Get the root query field name."""
        return self._root_field

    def build_query(self) -> str:
        """Build the complete GraphQL query string."""
        return self.build()


class CustomConnectionQueryBuilder(CustomQueryBuilder):
    """Custom connection query builder for paginated GraphQL queries."""

    def paginate(
        self,
        first: int | None = None,
        after: str | None = None,
        last: int | None = None,
        before: str | None = None,
    ) -> Self:
        """Add pagination arguments.

        Raises:
            ValueError: If both first and last, or both after and before, are given
        """
        if first is not None and last is not None:
            raise ValueError("Cannot specify both 'first' and 'last' parameters")
        if after is not None and before is not None:
            raise ValueError("Cannot specify both 'after' and 'before' parameters")
        self.add_variables(first=first, after=after, last=last, before=before)
        return self

    def with_page_size(self, size: int) -> Self:
        """Set page size for forward pagination."""
        return self.paginate(first=size)

    def with_cursor(self, cursor: str, forward: bool = True) -> Self:
        """Continue pagination after (forward) or before (backward) a cursor."""
        self.add_variable("after" if forward else "before", cursor)
        return self

    def default_fields(self) -> FieldSelector | None:
        """Edges with cursor and node id, plus pageInfo."""
        return connection_fields(FieldSelector(["id"]))


class CustomFilterableQueryBuilder(CustomQueryBuilder):
    """Query builder with date, shop, and app filter helpers for ``transactions``."""

    def with_date_range(
        self,
        min_date: str | None = None,
        max_date: str | None = None,
    ) -> Self:
        """Filter by creation date (ISO-8601 strings).

        Raises:
            ValueError: If min_date is after max_date
        """
        if min_date and max_date and min_date > max_date:
            raise ValueError("min_date cannot be greater than max_date")
        self.add_variables(createdAtMin=min_date, createdAtMax=max_date)
        return self

    def with_shop_filter(
        self,
        shop_id: str | None = None,
        myshopify_domain: str | None = None,
    ) -> Self:
        """Filter by shop ID or myshopify domain."""
        self.add_variables(shopId=shop_id, myshopifyDomain=myshopify_domain)
        return self

    def with_app_filter(self, app_id: str | None = None) -> Self:
        """Filter by app ID."""
        self.add_variable("appId", app_id)
        return self
