"""Core query result container for GraphQL queries."""

from typing import Any, Optional


class QueryResult:
    """Container for query results with metadata."""

    def __init__(
        self,
        data: Any,
        query: str,
        variables: dict[str, Any],
        raw_response: dict[str, Any],
    ) -> None:
        """Initialize query result.

        Args:
            data: Parsed result data
            query: GraphQL query string
            variables: Query variables
            raw_response: Raw GraphQL response
        """
        self.data = data
        self.query = query
        self.variables = variables
        self.raw_response = raw_response

    @property
    def extensions(self) -> Optional[dict[str, Any]]:
        """Get extensions from GraphQL response."""
        return self.raw_response.get("extensions")

    def __repr__(self) -> str:
        """String representation of query result."""
        return f"QueryResult(data_type={type(self.data).__name__})"
