"""Field selection utilities for dynamic GraphQL query building."""

from typing import Optional, Union


class FieldSelector:
    """Builder for selecting GraphQL fields dynamically."""

    def __init__(self, base_fields: Optional[list[str]] = None) -> None:
        """Initialize field selector.

        Args:
            base_fields: Base fields to always include
        """
        self._fields: dict[str, Union[str, FieldSelector, list[str]]] = {}
        if base_fields:
            for field in base_fields:
                self._fields[field] = field

    def add_field(self, field: str) -> "FieldSelector":
        """Add a simple field.

        Args:
            field: Field name

        Returns:
            Self for chaining
        """
        self._fields[field] = field
        return self

    def add_fields(self, *fields: str) -> "FieldSelector":
        """Add multiple simple fields.

        Args:
            *fields: Field names

        Returns:
            Self for chaining
        """
        for field in fields:
            self._fields[field] = field
        return self

    def add_nested_field(
        self, field: str, subfields: "FieldSelector"
    ) -> "FieldSelector":
        """Add a nested field with subfields.

        Args:
            field: Parent field name
            subfields: Field selector for nested fields

        Returns:
            Self for chaining
        """
        self._fields[field] = subfields
        return self

    def add_nested_fields(
        self, field_subfields: dict[str, "FieldSelector"]
    ) -> "FieldSelector":
        """Add a nested field with multiple subfields."""
        for field, subfields in field_subfields.items():
            self.add_nested_field(field, subfields)
        return self

    def add_interface_field(
        self, field: str, subfields: "FieldSelector"
    ) -> "FieldSelector":
        """Add a GraphQL interface field with inline fragment syntax."""
        return self.add_nested_field(f"... on {field}", subfields)

    def add_interface_fields(
        self, field_subfields: dict[str, "FieldSelector"]
    ) -> "FieldSelector":
        """Add multiple GraphQL interface fields with inline fragment syntax."""
        for field, subfields in field_subfields.items():
            self.add_interface_field(field, subfields)
        return self

    def add_connection_field(
        self,
        field: str,
        node_fields: "FieldSelector",
        include_page_info: bool = True,
        include_edges: bool = True,
        **connection_args,
    ) -> "FieldSelector":
        """Add a GraphQL connection field with edges and pageInfo.

        Args:
            field: Connection field name
            node_fields: Fields to select on the node
            include_page_info: Whether to include pageInfo
            include_edges: Whether to include edges wrapper
            **connection_args: Connection arguments (first, after, last, before, etc.)

        Returns:
            Self for chaining
        """
        connection_selector = FieldSelector()

        if include_edges:
            edge_selector = FieldSelector(["cursor"])
            edge_selector.add_nested_field("node", node_fields)
            connection_selector.add_nested_field("edges", edge_selector)
        else:
            # Direct node selection (for some GraphQL schemas)
            connection_selector.add_nested_field("nodes", node_fields)

        if include_page_info:
            page_info_selector = FieldSelector(["hasNextPage", "hasPreviousPage"])
            connection_selector.add_nested_field("pageInfo", page_info_selector)

        # Store connection arguments if provided
        if connection_args:
            connection_selector._connection_args = connection_args

        self._fields[field] = connection_selector
        return self

    def add_money_field(self, field: str) -> "FieldSelector":
        """Add a Money type field with amount and currencyCode.

        Args:
            field: Money field name

        Returns:
            Self for chaining
        """
        money_selector = FieldSelector(["amount", "currencyCode"])
        self._fields[field] = money_selector
        return self

    def remove_field(self, field: str) -> "FieldSelector":
        """Remove a field from selection.

        Args:
            field: Field name to remove

        Returns:
            Self for chaining
        """
        self._fields.pop(field, None)
        return self

    def build(self, indent: int = 0) -> str:
        """Build the GraphQL field selection string.

        Args:
            indent: Indentation level

        Returns:
            GraphQL fields string
        """
        if not self._fields:
            return ""

        lines = []
        base_indent = "  " * indent

        for field_name, field_value in self._fields.items():
            if isinstance(field_value, str):
                # Simple field
                lines.append(f"{base_indent}{field_name}")
            elif isinstance(field_value, FieldSelector):
                # Nested field - check if it has connection arguments
                field_args = ""
                if (
                    hasattr(field_value, "_connection_args")
                    and field_value._connection_args
                ):
                    args = []
                    for arg_name, arg_value in field_value._connection_args.items():
                        if isinstance(arg_value, str):
                            args.append(f'{arg_name}: "{arg_value}"')
                        else:
                            args.append(f"{arg_name}: {arg_value}")
                    field_args = f"({', '.join(args)})"

                nested_fields = field_value.build(indent + 1)
                if nested_fields:
                    lines.append(f"{base_indent}{field_name}{field_args} {{")
                    lines.append(nested_fields)
                    lines.append(f"{base_indent}}}")
                else:
                    lines.append(f"{base_indent}{field_name}{field_args}")
            elif isinstance(field_value, list):
                # List of simple fields (shouldn't happen with current API)
                for subfield in field_value:
                    lines.append(f"{base_indent}{field_name}.{subfield}")

        return "\n".join(lines)

    def __str__(self) -> str:
        """String representation."""
        return self.build()

    def copy(self) -> "FieldSelector":
        """Create a deep copy of this field selector.

        Returns:
            New FieldSelector instance
        """
        new_selector = FieldSelector()
        for field_name, field_value in self._fields.items():
            if isinstance(field_value, str):
                new_selector._fields[field_name] = field_value
            elif isinstance(field_value, FieldSelector):
                new_selector._fields[field_name] = field_value.copy()
            else:
                new_selector._fields[field_name] = field_value

        return new_selector


# Predefined common field selectors
class CommonFields:
    """Common field selectors for frequent use cases."""

    @staticmethod
    def basic_node() -> FieldSelector:
        """Basic node fields (id, createdAt, updatedAt)."""
        return FieldSelector(["id", "createdAt", "updatedAt"])

    @staticmethod
    def money_fields() -> FieldSelector:
        """Money type fields."""
        return FieldSelector(["amount", "currencyCode"])

    @staticmethod
    def page_info() -> FieldSelector:
        """Standard pagination info."""
        return FieldSelector(["hasNextPage", "hasPreviousPage"])

    @staticmethod
    def user_error() -> FieldSelector:
        """User error fields."""
        return FieldSelector(["field", "message"])

    @staticmethod
    def basic_app() -> FieldSelector:
        """Basic app fields."""
        return (
            FieldSelector()
            .add_fields("id", "title", "handle", "appStoreAppUrl", "developerName")
            .add_field("createdAt")
            .add_field("updatedAt")
        )

    @staticmethod
    def basic_transaction() -> FieldSelector:
        """Basic transaction fields."""
        return (
            FieldSelector()
            .add_fields("id", "createdAt", "test")
            .add_money_field("netAmount")
            .add_money_field("grossAmount")
        )

    @staticmethod
    def basic_shop() -> FieldSelector:
        """Basic shop fields."""
        return (
            FieldSelector()
            .add_fields("id", "name", "myshopifyDomain", "url")
            .add_field("createdAt")
        )
