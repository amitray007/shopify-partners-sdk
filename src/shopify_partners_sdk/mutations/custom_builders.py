"""Custom GraphQL mutation builders with field selection."""

from typing import Any, Optional

from shopify_partners_sdk.queries.fields import FieldSelector


class CustomMutationBuilder:
    """Flexible mutation builder for any GraphQL mutation."""

    def __init__(
        self,
        mutation_name: str,
        fields: Optional[FieldSelector] = None,
        operation_name: Optional[str] = None,
    ) -> None:
        """Initialize dynamic mutation builder.

        Args:
            mutation_name: The root mutation field name (e.g., 'appCreditCreate')
            fields: Field selector for the mutation result
            operation_name: Optional GraphQL operation name
        """
        self._mutation_name = mutation_name
        self._fields = fields
        self._operation_name = operation_name
        self._variables: dict[str, Any] = {}
        self._fragments: list[str] = []

    @property
    def variables(self) -> dict[str, Any]:
        """Get the current mutation variables."""
        return self._variables.copy()

    def add_variable(self, name: str, value: Any) -> "CustomMutationBuilder":
        """Add a variable to the mutation.

        Args:
            name: Variable name (without $ prefix)
            value: Variable value

        Returns:
            Self for method chaining
        """
        if value is not None:
            self._variables[name] = value
        return self

    def add_variables(self, **variables: Any) -> "CustomMutationBuilder":
        """Add multiple variables to the mutation.

        Args:
            **variables: Variables to add

        Returns:
            Self for method chaining
        """
        for name, value in variables.items():
            if value is not None:
                self._variables[name] = value
        return self

    def get_mutation_name(self) -> str:
        """Get the root mutation field name."""
        return self._mutation_name

    def with_input_variable(
        self, input_data: Any, variable_name: str = "input"
    ) -> "CustomMutationBuilder":
        """Set the input variable for the mutation.

        Args:
            input_data: Input data (usually a Pydantic model)
            variable_name: Variable name (defaults to 'input')

        Returns:
            Self for method chaining
        """
        return self.add_variable(variable_name, input_data)

    def build_variable_definitions(self) -> str:
        """Build GraphQL variable definitions from current variables."""
        if not self._variables:
            return ""

        definitions = []
        for name, value in self._variables.items():
            var_type = self._infer_variable_type(value, name)
            definitions.append(f"${name}: {var_type}")

        return "(" + ", ".join(definitions) + ")"

    def _infer_variable_type(self, value: Any, variable_name: str = "") -> str:
        """Infer GraphQL type from Python value."""
        if isinstance(value, bool):
            return "Boolean!"
        if isinstance(value, int):
            return "Int!"
        if isinstance(value, float):
            return "Float!"
        if isinstance(value, str):
            # Use ID! for fields named "id" or ending with "Id"
            if variable_name == "id" or variable_name.endswith("Id"):
                return "ID!"
            if variable_name == "createdAtMin" or variable_name == "createdAtMax":
                return "DateTime"
            return "String!"
        if isinstance(value, list):
            return "[String!]!"
        if isinstance(value, dict):
            # For mutation input objects, infer from mutation name
            # Most Shopify mutations follow the pattern:
            # mutationName -> MutationNameInput!
            mutation_name = self._mutation_name
            if mutation_name:
                # Convert camelCase to PascalCase and add Input suffix
                return mutation_name[0].upper() + mutation_name[1:] + "Input!"
            return "JSON!"
        return "String!"

    def build_mutation(self) -> str:
        """Build the complete GraphQL mutation string."""
        # Build variable definitions
        variable_defs = self.build_variable_definitions()

        # Build operation name
        operation_name = f" {self._operation_name}" if self._operation_name else ""

        # Build field selection
        field_selection = ""
        if self._fields:
            field_selection = self._fields.build(2)
        else:
            # Default mutation result fields
            field_selection = """    userErrors {
      field
      message
    }"""

        # Build mutation arguments
        mutation_args = ""
        if self._variables:
            args = [f"{name}: ${name}" for name in self._variables]
            mutation_args = f"({', '.join(args)})"

        # Build fragments
        fragments = "\n".join(self._fragments) if self._fragments else ""

        return f"""
mutation{operation_name}{variable_defs} {{
  {self._mutation_name}{mutation_args} {{
{field_selection}
  }}
}}
{fragments}
        """.strip()

    def get_result_type(self) -> type:
        """Get the expected result type (returns dict for dynamic mutations)."""
        return dict
