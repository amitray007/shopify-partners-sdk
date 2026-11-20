"""Field selection utilities for dynamic GraphQL query building."""

from typing import TYPE_CHECKING, Any, Union

from shopify_partners_sdk.exceptions.validation import SchemaValidationError
from shopify_partners_sdk.values import graphql_literal

if TYPE_CHECKING:
    from shopify_partners_sdk.schema import PartnerSchema

FRAGMENT_PREFIX = "... on "
TYPENAME = "__typename"


class FieldSelector:
    """Builder for selecting GraphQL fields dynamically."""

    def __init__(self, base_fields: list[str] | None = None) -> None:
        """Initialize field selector.

        Args:
            base_fields: Base fields to always include
        """
        self._fields: dict[str, str | FieldSelector] = {}
        self._args: dict[str, Any] = {}
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
        **connection_args: Any,
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

        connection_selector._args = dict(connection_args)

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

    def build(
        self,
        indent: int = 0,
        schema: "PartnerSchema | None" = None,
        type_name: str | None = None,
    ) -> str:
        """Build the GraphQL field selection string.

        Args:
            indent: Indentation level
            schema: Partner API schema to validate against (optional)
            type_name: GraphQL type these fields are selected on; required with schema

        Returns:
            GraphQL fields string

        Raises:
            SchemaValidationError: If a field, argument, enum value, or fragment does
                not exist on ``type_name`` in ``schema``
        """
        lines: list[str] = []
        for name, value in self._fields.items():
            lines.extend(self._render(name, value, indent, schema, type_name))
        return "\n".join(lines)

    def _render(
        self,
        name: str,
        value: Union[str, "FieldSelector"],
        indent: int,
        schema: "PartnerSchema | None",
        parent: str | None,
    ) -> list[str]:
        pad = "  " * indent
        if schema is None or parent is None:
            schema, parent = None, None
        child_type: str | None = None
        args = ""
        if name.startswith(FRAGMENT_PREFIX):
            child_type = name[len(FRAGMENT_PREFIX) :].strip()
            if schema is not None and parent is not None:
                schema.check_fragment(parent, child_type)
        else:
            if schema is not None and parent is not None:
                child_type = _check_field(schema, parent, name, value)
            args = _render_args(name, value, schema, parent)

        if isinstance(value, FieldSelector):
            nested = value.build(indent + 1, schema, child_type)
            if nested:
                return [f"{pad}{name}{args} {{", nested, f"{pad}}}"]
        return [f"{pad}{name}{args}"]

    def __str__(self) -> str:
        """String representation."""
        return self.build()

    def copy(self) -> "FieldSelector":
        """Create a deep copy of this field selector, including field arguments.

        Returns:
            New FieldSelector instance
        """
        new_selector = FieldSelector()
        new_selector._args = dict(self._args)
        for field_name, field_value in self._fields.items():
            if isinstance(field_value, FieldSelector):
                new_selector._fields[field_name] = field_value.copy()
            else:
                new_selector._fields[field_name] = field_value
        return new_selector


def _check_field(
    schema: "PartnerSchema",
    parent: str,
    name: str,
    value: str | FieldSelector,
) -> str | None:
    """Validate one selected field and return the type its sub-fields select on."""
    if name == TYPENAME:
        if isinstance(value, FieldSelector):
            raise SchemaValidationError(f"'{TYPENAME}' takes no sub-selection.")
        return None

    field_type: str = schema.field(parent, name)["type"].strip("[]!")
    has_subfields = isinstance(value, FieldSelector) and bool(value._fields)
    if schema.is_leaf(field_type) and isinstance(value, FieldSelector):
        raise SchemaValidationError(
            f"Field '{parent}.{name}' returns {field_type}, which takes no "
            "sub-selection. Add it with add_field()."
        )
    if not schema.is_leaf(field_type) and not has_subfields:
        raise SchemaValidationError(
            f"Field '{parent}.{name}' returns {field_type}; select at least one of "
            f"its fields with add_nested_field() or add_connection_field()."
        )
    return field_type


def _render_args(
    name: str,
    value: str | FieldSelector,
    schema: "PartnerSchema | None",
    parent: str | None,
) -> str:
    args = value._args if isinstance(value, FieldSelector) else {}
    if schema is not None and parent is not None:
        _check_required_args(schema, parent, name, args)
    if not args:
        return ""
    rendered = []
    for arg_name, arg_value in args.items():
        arg_type = (
            schema.argument_type(parent, name, arg_name)
            if schema is not None and parent is not None
            else None
        )
        rendered.append(f"{arg_name}: {graphql_literal(arg_value, arg_type, schema)}")
    return f"({', '.join(rendered)})"


def _check_required_args(
    schema: "PartnerSchema", parent: str, name: str, args: dict[str, Any]
) -> None:
    if name == TYPENAME:
        return
    missing = [a for a in schema.required_arguments(parent, name) if a not in args]
    if missing:
        raise SchemaValidationError(
            f"Field '{parent}.{name}' requires argument(s): {', '.join(missing)}."
        )


# Predefined common field selectors
class CommonFields:
    """Common field selectors for frequent use cases."""

    @staticmethod
    def basic_node() -> FieldSelector:
        """Fields every Node has (id)."""
        return FieldSelector(["id"])

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
        """Basic App fields."""
        return FieldSelector(["id", "name", "apiKey"])

    @staticmethod
    def basic_transaction() -> FieldSelector:
        """Fields shared by every Transaction type, plus its concrete type name.

        Amounts differ per transaction type; select them with add_interface_field().
        """
        return FieldSelector(["id", "createdAt", TYPENAME])

    @staticmethod
    def basic_shop() -> FieldSelector:
        """Basic Shop fields."""
        return FieldSelector(["id", "name", "myshopifyDomain"])
