"""Custom GraphQL mutation builders with field selection."""

from typing import Any, ClassVar, Self

from shopify_partners_sdk.queries.custom_builders import OperationBuilder
from shopify_partners_sdk.queries.fields import FieldSelector
from shopify_partners_sdk.schema import Operation


class CustomMutationBuilder(OperationBuilder):
    """Mutation builder for any top-level Partner API mutation."""

    operation: ClassVar[Operation] = "mutation"

    def get_mutation_name(self) -> str:
        """Get the root mutation field name."""
        return self._root_field

    def with_input_variable(
        self, input_data: Any, variable_name: str = "input"
    ) -> Self:
        """Pass a value (dict or Pydantic model) as the named argument."""
        self.add_variable(variable_name, input_data)
        return self

    def build_variable_definitions(self) -> str:
        """Render the ``($name: Type, ...)`` variable definitions."""
        return self._render_variable_definitions()

    def build_mutation(self) -> str:
        """Build the complete GraphQL mutation string."""
        return self.build()

    def default_fields(self) -> FieldSelector | None:
        """``userErrors { field message }``, which every Partner API payload has."""
        return FieldSelector().add_nested_field(
            "userErrors", FieldSelector(["field", "message"])
        )
