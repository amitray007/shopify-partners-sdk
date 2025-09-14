"""Core mutation result container for GraphQL mutations."""

from typing import Any, Optional


class MutationResult:
    """Container for mutation results with metadata."""

    def __init__(
        self,
        data: Any,
        mutation: str,
        variables: dict[str, Any],
        raw_response: dict[str, Any],
        errors: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        """Initialize mutation result.

        Args:
            data: Parsed result data
            mutation: GraphQL mutation string
            variables: Mutation variables
            raw_response: Raw GraphQL response
            errors: GraphQL errors if any
        """
        self.data = data
        self.mutation = mutation
        self.variables = variables
        self.raw_response = raw_response
        self.errors = errors or []

    @property
    def extensions(self) -> Optional[dict[str, Any]]:
        """Get extensions from GraphQL response."""
        return self.raw_response.get("extensions")

    @property
    def has_errors(self) -> bool:
        """Check if the mutation has errors."""
        return len(self.errors) > 0

    def __repr__(self) -> str:
        """String representation of mutation result."""
        error_info = f", errors={len(self.errors)}" if self.has_errors else ""
        return f"MutationResult(data_type={type(self.data).__name__}{error_info})"
