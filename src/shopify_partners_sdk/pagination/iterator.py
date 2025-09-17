"""Iterators for paginated GraphQL results."""

from typing import Any, Callable, Optional, TypeVar

from shopify_partners_sdk.models.base import Connection, Node

T = TypeVar("T", bound=Node)
ConnectionType = TypeVar("ConnectionType", bound=Connection)


class PageIterator:
    """Iterator for paginating through GraphQL connections."""

    def __init__(
        self,
        fetch_func: Callable[..., ConnectionType],
        initial_args: dict[str, Any],
        page_size: int = 50,
        max_pages: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> None:
        """Initialize the page iterator.

        Args:
            fetch_func: Function to fetch connection pages
            initial_args: Initial query arguments
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch
            max_items: Maximum number of items to fetch
        """
        self._fetch_func = fetch_func
        self._initial_args = initial_args.copy()
        self._page_size = page_size
        self._max_pages = max_pages
        self._max_items = max_items

        # State tracking
        self._current_page = 0
        self._total_items = 0
        self._has_more = True
        self._next_cursor: Optional[str] = None

    def __iter__(self) -> "PageIterator":
        """Return iterator."""
        return self

    def __next__(self) -> ConnectionType:
        """Get the next page of results.

        Returns:
            Connection object with page data

        Raises:
            StopIteration: When no more pages are available
        """
        if not self._has_more:
            raise StopIteration

        if self._max_pages and self._current_page >= self._max_pages:
            raise StopIteration

        # Build query arguments for this page
        query_args = self._initial_args.copy()
        query_args["first"] = self._page_size

        if self._next_cursor:
            query_args["after"] = self._next_cursor

        # Fetch the page
        try:
            connection = self._fetch_func(**query_args)
        except Exception:
            raise StopIteration

        # Update state
        self._current_page += 1
        self._total_items += len(connection.edges)
        self._has_more = connection.page_info.has_next_page
        self._next_cursor = connection.page_info.end_cursor

        # Check item limit
        if self._max_items and self._total_items >= self._max_items:
            self._has_more = False

        return connection

    @property
    def current_page(self) -> int:
        """Get current page number (0-based)."""
        return self._current_page

    @property
    def total_items_fetched(self) -> int:
        """Get total number of items fetched so far."""
        return self._total_items

    @property
    def has_more_pages(self) -> bool:
        """Check if more pages are available."""
        return self._has_more


class NodeIterator:
    """Iterator for individual nodes across paginated results."""

    def __init__(
        self,
        page_iterator: PageIterator,
    ) -> None:
        """Initialize the node iterator.

        Args:
            page_iterator: Page iterator to get data from
        """
        self._page_iterator = page_iterator
        self._current_page_nodes: list[T] = []
        self._current_node_index = 0

    def __iter__(self) -> "NodeIterator":
        """Return iterator."""
        return self

    def __next__(self) -> T:
        """Get the next node.

        Returns:
            Next node from the results

        Raises:
            StopIteration: When no more nodes are available
        """
        # If we've exhausted current page nodes, get next page
        while self._current_node_index >= len(self._current_page_nodes):
            try:
                connection = self._page_iterator.__next__()
                self._current_page_nodes = [edge.node for edge in connection.edges]
                self._current_node_index = 0
            except StopIteration:
                raise StopIteration

            # If the page was empty, continue to next page
            if not self._current_page_nodes:
                continue

        # Return current node and advance index
        node = self._current_page_nodes[self._current_node_index]
        self._current_node_index += 1
        return node

    @property
    def total_nodes_fetched(self) -> int:
        """Get total number of nodes fetched so far."""
        return (
            self._page_iterator.total_items_fetched
            - len(self._current_page_nodes)
            + self._current_node_index
        )


class PaginatedResult:
    """Container for paginated query results with iteration capabilities."""

    def __init__(
        self,
        fetch_func: Callable[..., ConnectionType],
        initial_args: dict[str, Any],
        page_size: int = 50,
        max_pages: Optional[int] = None,
        max_items: Optional[int] = None,
    ) -> None:
        """Initialize paginated result.

        Args:
            fetch_func: Function to fetch connection pages
            initial_args: Initial query arguments
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch
            max_items: Maximum number of items to fetch
        """
        self._fetch_func = fetch_func
        self._initial_args = initial_args
        self._page_size = page_size
        self._max_pages = max_pages
        self._max_items = max_items

    def pages(self) -> PageIterator:
        """Get iterator for pages.

        Returns:
            Iterator yielding Connection objects
        """
        return PageIterator(
            self._fetch_func,
            self._initial_args,
            self._page_size,
            self._max_pages,
            self._max_items,
        )

    def nodes(self) -> NodeIterator:
        """Get iterator for individual nodes.

        Returns:
            Iterator yielding individual node objects
        """
        page_iterator = self.pages()
        return NodeIterator(page_iterator)

    def first_page(self) -> ConnectionType:
        """Get just the first page of results.

        Returns:
            First page connection
        """
        page_iterator = self.pages()
        return page_iterator.__next__()

    def all_nodes(self, max_items: Optional[int] = None) -> list[T]:
        """Fetch all nodes from all pages.

        Args:
            max_items: Maximum number of items to fetch

        Returns:
            List of all nodes

        Warning:
            This can fetch a large amount of data. Use with caution.
        """
        nodes = []
        items_limit = max_items or self._max_items

        for node in self.nodes():
            nodes.append(node)
            if items_limit and len(nodes) >= items_limit:
                break

        return nodes

    def collect_pages(self, max_pages: Optional[int] = None) -> list[ConnectionType]:
        """Collect multiple pages into a list.

        Args:
            max_pages: Maximum number of pages to collect

        Returns:
            List of connection objects
        """
        pages = []
        page_limit = max_pages or self._max_pages

        for page_count, page in enumerate(self.pages(), 1):
            pages.append(page)
            if page_limit and page_count >= page_limit:
                break

        return pages

    def with_page_size(self, size: int) -> "PaginatedResult":
        """Create a new paginated result with different page size.

        Args:
            size: New page size

        Returns:
            New PaginatedResult with updated page size
        """
        return PaginatedResult(
            self._fetch_func,
            self._initial_args,
            size,
            self._max_pages,
            self._max_items,
        )

    def limit(self, max_items: int) -> "PaginatedResult":
        """Create a new paginated result with item limit.

        Args:
            max_items: Maximum number of items to fetch

        Returns:
            New PaginatedResult with item limit
        """
        return PaginatedResult(
            self._fetch_func,
            self._initial_args,
            self._page_size,
            self._max_pages,
            max_items,
        )

    def max_pages(self, pages: int) -> "PaginatedResult":
        """Create a new paginated result with page limit.

        Args:
            pages: Maximum number of pages to fetch

        Returns:
            New PaginatedResult with page limit
        """
        return PaginatedResult(
            self._fetch_func,
            self._initial_args,
            self._page_size,
            pages,
            self._max_items,
        )
