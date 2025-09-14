"""Base model classes for the Shopify Partners SDK."""

from typing import Any, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .scalars import GlobalID

T = TypeVar("T", bound="ShopifyPartnersBaseModel")


class ShopifyPartnersBaseModel(BaseModel):
    """Base model for all Shopify Partners API objects.

    Provides common functionality and configuration for all API models.
    """

    model_config = ConfigDict(
        # Allow population by field name or alias
        populate_by_name=True,
        # Use enum values instead of enum objects
        use_enum_values=True,
        # Validate assignment of new values
        validate_assignment=True,
        # Allow extra fields that might be added by Shopify
        extra="ignore",
        # Use JSON-compatible serialization
        arbitrary_types_allowed=False,
        # Strict validation
        str_strip_whitespace=True,
    )

    def model_dump_graphql(self, exclude_none: bool = True) -> dict[str, Any]:
        """Dump model for GraphQL query variables.

        Args:
            exclude_none: Whether to exclude None values

        Returns:
            Dictionary suitable for GraphQL variables
        """
        return self.model_dump(
            by_alias=True,
            exclude_none=exclude_none,
            mode="json",
        )

    @classmethod
    def from_graphql(cls: type[T], data: dict[str, Any]) -> T:
        """Create model instance from GraphQL response data.

        Args:
            data: GraphQL response data

        Returns:
            Model instance
        """
        return cls.model_validate(data)


class Node(ShopifyPartnersBaseModel):
    """Base class for objects that implement the Node interface.

    The Node interface is used by objects that can be refetched by ID.
    """

    id: GlobalID = Field(..., description="Globally unique identifier")

    def __str__(self) -> str:
        """String representation showing type and ID."""
        return f"{self.__class__.__name__}(id='{self.id}')"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"{self.__class__.__name__}(id='{self.id}')"


class Actor(Node):
    """Base class for objects that implement the Actor interface.

    Actors are entities that can perform actions (Users, Organizations).
    """

    avatar_url: Optional[str] = Field(None, description="Avatar URL", alias="avatarUrl")
    name: str = Field(..., description="Name of the actor")

    def __str__(self) -> str:
        """String representation showing name."""
        return f"{self.__class__.__name__}(name='{self.name}')"


class Connection(ShopifyPartnersBaseModel):
    """Base class for GraphQL Connection types.

    Connections represent paginated lists of objects following the Relay specification.
    """

    page_info: "PageInfo" = Field(
        ..., description="Pagination information", alias="pageInfo"
    )

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


class Edge(ShopifyPartnersBaseModel):
    """Base class for GraphQL Edge types.

    Edges connect nodes in a connection and contain a cursor.
    """

    cursor: str = Field(..., description="Cursor for this edge")

    def __str__(self) -> str:
        """String representation showing cursor."""
        return f"{self.__class__.__name__}(cursor='{self.cursor[:20]}...')"


class PageInfo(ShopifyPartnersBaseModel):
    """Information about pagination in a connection.

    Follows the Relay Cursor Connections specification.
    """

    has_next_page: bool = Field(
        ..., description="Whether there are more pages", alias="hasNextPage"
    )
    has_previous_page: bool = Field(
        ..., description="Whether there are previous pages", alias="hasPreviousPage"
    )

    def __str__(self) -> str:
        """String representation showing pagination state."""
        return (
            f"PageInfo("
            f"has_next={self.has_next_page}, "
            f"has_prev={self.has_previous_page}"
            f")"
        )


class UserError(ShopifyPartnersBaseModel):
    """Represents a user error from a mutation.

    User errors are validation errors that can be shown to users.
    """

    field: Optional[str] = Field(None, description="Field that caused the error")
    message: str = Field(..., description="Error message")

    def __str__(self) -> str:
        """String representation of the error."""
        if self.field:
            return f"UserError(field='{self.field}', message='{self.message}')"
        return f"UserError(message='{self.message}')"


# Forward reference resolution
PageInfo.model_rebuild()
Connection.model_rebuild()
