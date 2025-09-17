"""Custom GraphQL query builders with field selection."""

from typing import Any, Optional

from shopify_partners_sdk.models.enums import AppEventType, TransactionType

from .fields import FieldSelector


class CustomQueryBuilder:
    """Custom query builder for any GraphQL query with field selection."""

    def __init__(
        self,
        query_name: str,
        fields: Optional[FieldSelector] = None,
        operation_name: Optional[str] = None,
    ) -> None:
        """Initialize custom query builder.

        Args:
            query_name: The root query field name (e.g., 'apps', 'transactions')
            fields: Field selector for the query
            operation_name: Optional GraphQL operation name
        """
        self._query_name = query_name
        self._fields = fields
        self._operation_name = operation_name
        self._variables: dict[str, Any] = {}
        self._fragments: list[str] = []

    @property
    def variables(self) -> dict[str, Any]:
        """Get the current query variables."""
        return self._variables.copy()

    def add_variable(self, name: str, value: Any) -> "CustomQueryBuilder":
        """Add a variable to the query.

        Args:
            name: Variable name (without $ prefix)
            value: Variable value

        Returns:
            Self for method chaining
        """
        if value is not None:
            self._variables[name] = value
        return self

    def add_variables(self, **variables: Any) -> "CustomQueryBuilder":
        """Add multiple variables to the query.

        Args:
            **variables: Variables to add

        Returns:
            Self for method chaining
        """
        for name, value in variables.items():
            if value is not None:
                self._variables[name] = value
        return self

    def with_fields(self, fields: FieldSelector) -> "CustomQueryBuilder":
        """Set the fields to select in the query.

        Args:
            fields: Field selector

        Returns:
            Self for method chaining
        """
        self._fields = fields
        return self

    def with_operation_name(self, name: str) -> "CustomQueryBuilder":
        """Set the operation name for the query.

        Args:
            name: Operation name

        Returns:
            Self for method chaining
        """
        self._operation_name = name
        return self

    def get_query_name(self) -> str:
        """Get the root query field name."""
        return self._query_name

    def build_query(self) -> str:
        """Build the complete GraphQL query string."""
        # Build variable definitions
        variable_defs = self._build_variable_definitions()

        # Build operation name
        operation_name = f" {self._operation_name}" if self._operation_name else ""

        # Build field selection
        field_selection = ""
        if self._fields:
            field_selection = self._fields.build(2)
        else:
            field_selection = "  # No fields specified"

        # Build query arguments
        query_args = ""
        if self._variables:
            args = [f"{name}: ${name}" for name in self._variables]
            query_args = f"({', '.join(args)})"

        # Build fragments
        fragments = "\n".join(self._fragments) if self._fragments else ""

        return f"""
query{operation_name}{variable_defs} {{
  {self._query_name}{query_args} {{
{field_selection}
  }}
}}
{fragments}
        """.strip()

    def _build_variable_definitions(self) -> str:
        """Build GraphQL variable definitions from current variables."""
        if not self._variables:
            return ""

        definitions = []
        for name, value in self._variables.items():
            var_type = self._infer_variable_type(value, name)
            definitions.append(f"${name}: {var_type}")

        return "(" + ", ".join(definitions) + ")"

    def _infer_variable_type(self, value: Any, variable_name: str = "") -> str:
        """Infer GraphQL variable type from Python value."""
        if value is None:
            return "String"
        if isinstance(value, bool):
            return "Boolean"
        if isinstance(value, int):
            return "Int"
        if isinstance(value, float):
            return "Float"
        if isinstance(value, str):
            # Use ID! for fields named "id" or ending with "Id"
            if variable_name == "id" or variable_name.endswith("Id"):
                return "ID!"
            if variable_name == "createdAtMin" or variable_name == "createdAtMax":
                return "DateTime"
            return "String"
        if isinstance(value, list):
            if value:
                item_type = self._infer_variable_type(value[0], variable_name)
                return f"[{item_type}]"
            return "[String]"
        if isinstance(value, AppEventType):
            return "AppEventType"
        if isinstance(value, TransactionType):
            return "TransactionType"
        # Handle pagination and date range inputs as generic objects
        if hasattr(value, "first") or hasattr(value, "last"):
            return "PaginationInput"
        if hasattr(value, "min_date") or hasattr(value, "max_date"):
            return "DateRangeInput"
        return "String"

    def get_result_type(self) -> type:
        """Get the expected result type (returns dict for custom queries)."""
        return dict


class CustomConnectionQueryBuilder(CustomQueryBuilder):
    """Custom connection query builder for paginated GraphQL queries."""

    def __init__(
        self,
        query_name: str,
        fields: Optional[FieldSelector] = None,
        operation_name: Optional[str] = None,
    ) -> None:
        """Initialize custom connection query builder.

        Args:
            query_name: The root query field name
            fields: Field selector for the query
            operation_name: Optional GraphQL operation name
        """
        super().__init__(query_name, fields, operation_name)
        self._pagination: Optional[dict] = None

    def paginate(
        self,
        first: Optional[int] = None,
        after: Optional[str] = None,
        last: Optional[int] = None,
        before: Optional[str] = None,
    ) -> "CustomConnectionQueryBuilder":
        """Add pagination parameters.

        Args:
            first: Return first N items
            after: Return items after this cursor
            last: Return last N items
            before: Return items before this cursor

        Returns:
            Self for method chaining
        """
        pagination = {
            "first": first,
            "after": after,
            "last": last,
            "before": before,
        }

        # Basic validation for pagination parameters
        if pagination["first"] and pagination["last"]:
            raise ValueError("Cannot specify both 'first' and 'last' parameters")
        if pagination["after"] and pagination["before"]:
            raise ValueError("Cannot specify both 'after' and 'before' parameters")

        self._pagination = pagination
        # Filter out None values and add as variables
        filtered_pagination = {k: v for k, v in pagination.items() if v is not None}
        return self.add_variables(**filtered_pagination)

    def with_page_size(self, size: int) -> "CustomConnectionQueryBuilder":
        """Set page size for forward pagination.

        Args:
            size: Number of items per page

        Returns:
            Self for method chaining
        """
        return self.paginate(first=size)

    def with_cursor(
        self, cursor: str, forward: bool = True
    ) -> "CustomConnectionQueryBuilder":
        """Continue pagination from a cursor.

        Args:
            cursor: Cursor to start from
            forward: Whether to paginate forward (True) or backward (False)

        Returns:
            Self for method chaining
        """
        if forward:
            return self.add_variable("after", cursor)
        return self.add_variable("before", cursor)

    def build_query(self) -> str:
        """Build the complete GraphQL query string."""
        # Build variable definitions
        variable_defs = self._build_variable_definitions()

        # Build operation name
        operation_name = f" {self._operation_name}" if self._operation_name else ""

        # Build field selection
        field_selection = ""
        if self._fields:
            field_selection = self._fields.build(2)
        else:
            # Default connection fields if none specified
            field_selection = """    edges {
      cursor
      node {
        id
      }
    }
    pageInfo {
      hasNextPage
      hasPreviousPage
    }"""

        # Build query arguments
        query_args = ""
        if self._variables:
            args = [f"{name}: ${name}" for name in self._variables]
            query_args = f"({', '.join(args)})"

        # Build fragments
        fragments = "\n".join(self._fragments) if self._fragments else ""

        return f"""
query{operation_name}{variable_defs} {{
  {self._query_name}{query_args} {{
{field_selection}
  }}
}}
{fragments}
        """.strip()


class CustomFilterableQueryBuilder(CustomQueryBuilder):
    """Custom filterable query builder with date/shop/app filtering."""

    def __init__(
        self,
        query_name: str,
        fields: Optional[FieldSelector] = None,
        operation_name: Optional[str] = None,
    ) -> None:
        """Initialize custom filterable query builder.

        Args:
            query_name: The root query field name
            fields: Field selector for the query
            operation_name: Optional GraphQL operation name
        """
        super().__init__(query_name, fields, operation_name)
        self._date_range: Optional[dict] = None

    def with_date_range(
        self,
        min_date: Optional[str] = None,
        max_date: Optional[str] = None,
    ) -> "CustomFilterableQueryBuilder":
        """Add date range filter.

        Args:
            min_date: Minimum date (ISO-8601)
            max_date: Maximum date (ISO-8601)

        Returns:
            Self for method chaining
        """
        if min_date is not None or max_date is not None:
            date_range = {"min_date": min_date, "max_date": max_date}
            # Basic validation for date range
            if min_date and max_date and min_date > max_date:
                raise ValueError("min_date cannot be greater than max_date")

            self._date_range = date_range
            if min_date:
                self.add_variable("createdAtMin", min_date)
            if max_date:
                self.add_variable("createdAtMax", max_date)

        return self

    def with_shop_filter(
        self,
        shop_id: Optional[str] = None,
        myshopify_domain: Optional[str] = None,
    ) -> "CustomFilterableQueryBuilder":
        """Add shop-based filters.

        Args:
            shop_id: Filter by shop ID
            myshopify_domain: Filter by shop domain

        Returns:
            Self for method chaining
        """
        return self.add_variables(
            shopId=shop_id,
            myshopifyDomain=myshopify_domain,
        )

    def with_app_filter(
        self, app_id: Optional[str] = None
    ) -> "CustomFilterableQueryBuilder":
        """Add app-based filter.

        Args:
            app_id: Filter by app ID

        Returns:
            Self for method chaining
        """
        return self.add_variable("appId", app_id)
