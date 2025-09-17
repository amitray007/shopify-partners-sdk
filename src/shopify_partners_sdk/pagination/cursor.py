"""Cursor-based pagination utilities for GraphQL connections."""

import base64
import json
from typing import Any, Optional

from shopify_partners_sdk.models.base import Connection, PageInfo


class CursorManager:
    """Manages cursor encoding/decoding for pagination."""

    @staticmethod
    def encode_cursor(data: dict[str, Any]) -> str:
        """Encode data into a base64 cursor.

        Args:
            data: Data to encode

        Returns:
            Base64-encoded cursor string
        """
        json_str = json.dumps(data, sort_keys=True)
        encoded_bytes = base64.b64encode(json_str.encode("utf-8"))
        return encoded_bytes.decode("ascii")

    @staticmethod
    def decode_cursor(cursor: str) -> dict[str, Any]:
        """Decode a base64 cursor into data.

        Args:
            cursor: Base64-encoded cursor string

        Returns:
            Decoded data dictionary

        Raises:
            ValueError: If cursor cannot be decoded
        """
        try:
            decoded_bytes = base64.b64decode(cursor.encode("ascii"))
            json_str = decoded_bytes.decode("utf-8")
            return json.loads(json_str)
        except Exception as e:
            raise ValueError(f"Invalid cursor format: {cursor}") from e

    @staticmethod
    def create_cursor(node_id: str, timestamp: Optional[str] = None) -> str:
        """Create a cursor for a node.

        Args:
            node_id: Node ID
            timestamp: Optional timestamp for ordering

        Returns:
            Encoded cursor string
        """
        data = {"id": node_id}
        if timestamp:
            data["timestamp"] = timestamp
        return CursorManager.encode_cursor(data)

    @staticmethod
    def extract_node_id(cursor: str) -> Optional[str]:
        """Extract node ID from a cursor.

        Args:
            cursor: Cursor to extract from

        Returns:
            Node ID if found, None otherwise
        """
        try:
            data = CursorManager.decode_cursor(cursor)
            return data.get("id")
        except ValueError:
            return None


class PaginationInfo:
    """Information about the current pagination state."""

    def __init__(self, page_info: PageInfo, total_count: Optional[int] = None) -> None:
        """Initialize pagination info.

        Args:
            page_info: GraphQL PageInfo object
            total_count: Total number of items (if available)
        """
        self.page_info = page_info
        self.total_count = total_count

    @property
    def has_next_page(self) -> bool:
        """Check if there are more pages available."""
        return self.page_info.has_next_page

    @property
    def has_previous_page(self) -> bool:
        """Check if there are previous pages available."""
        return self.page_info.has_previous_page

    @property
    def start_cursor(self) -> Optional[str]:
        """Get the cursor for the first item."""
        return self.page_info.start_cursor

    @property
    def end_cursor(self) -> Optional[str]:
        """Get the cursor for the last item."""
        return self.page_info.end_cursor

    def next_page_args(self, page_size: int = 50) -> dict[str, Any]:
        """Get arguments for the next page.

        Args:
            page_size: Number of items per page

        Returns:
            Dictionary with pagination arguments

        Raises:
            ValueError: If no next page is available
        """
        if not self.has_next_page:
            raise ValueError("No next page available")

        return {
            "first": page_size,
            "after": self.end_cursor,
        }

    def previous_page_args(self, page_size: int = 50) -> dict[str, Any]:
        """Get arguments for the previous page.

        Args:
            page_size: Number of items per page

        Returns:
            Dictionary with pagination arguments

        Raises:
            ValueError: If no previous page is available
        """
        if not self.has_previous_page:
            raise ValueError("No previous page available")

        return {
            "last": page_size,
            "before": self.start_cursor,
        }

    def __str__(self) -> str:
        """String representation of pagination info."""
        total_str = f", total={self.total_count}" if self.total_count else ""
        return (
            f"PaginationInfo("
            f"has_next={self.has_next_page}, "
            f"has_prev={self.has_previous_page}"
            f"{total_str}"
            f")"
        )


class PaginationHelper:
    """Helper class for working with paginated GraphQL connections."""

    @staticmethod
    def extract_pagination_info(connection: Connection) -> PaginationInfo:
        """Extract pagination information from a connection.

        Args:
            connection: GraphQL connection object

        Returns:
            PaginationInfo object
        """
        return PaginationInfo(connection.page_info)

    @staticmethod
    def get_all_cursors(connection: Connection) -> list[str]:
        """Get all cursors from a connection's edges.

        Args:
            connection: GraphQL connection object

        Returns:
            List of cursor strings
        """
        return [edge.cursor for edge in connection.edges]

    @staticmethod
    def find_cursor_for_node_id(connection: Connection, node_id: str) -> Optional[str]:
        """Find the cursor for a specific node ID in a connection.

        Args:
            connection: GraphQL connection object
            node_id: Node ID to find

        Returns:
            Cursor string if found, None otherwise
        """
        for edge in connection.edges:
            if hasattr(edge.node, "id") and edge.node.id == node_id:
                return edge.cursor
        return None

    @staticmethod
    def validate_cursor(cursor: str) -> bool:
        """Validate that a cursor is properly formatted.

        Args:
            cursor: Cursor string to validate

        Returns:
            True if cursor is valid, False otherwise
        """
        try:
            CursorManager.decode_cursor(cursor)
            return True
        except ValueError:
            return False

    @staticmethod
    def estimate_progress(
        connection: Connection,
        current_page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """Estimate pagination progress (rough approximation).

        Args:
            connection: GraphQL connection object
            current_page: Current page number (1-based)
            page_size: Items per page

        Returns:
            Dictionary with progress information
        """
        items_fetched = (current_page - 1) * page_size + len(connection.edges)

        return {
            "current_page": current_page,
            "items_on_page": len(connection.edges),
            "items_fetched": items_fetched,
            "has_more": connection.page_info.has_next_page,
            "estimated_remaining": "unknown",  # GraphQL doesn't provide total counts
        }
