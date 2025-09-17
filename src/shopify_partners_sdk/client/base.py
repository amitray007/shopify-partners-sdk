"""Base HTTP client for the Shopify Partners GraphQL API."""

from contextlib import suppress
import json
import logging
from typing import Any, Optional

import requests

from shopify_partners_sdk.client.auth import AuthenticationHandler
from shopify_partners_sdk.client.rate_limiter import RateLimiter
from shopify_partners_sdk.client.retry import RetryHandler
from shopify_partners_sdk.config import ShopifyPartnersSDKSettings
from shopify_partners_sdk.exceptions.auth import ForbiddenError, UnauthorizedError
from shopify_partners_sdk.exceptions.graphql import (
    GraphQLError,
    GraphQLMultipleErrors,
    GraphQLResponseError,
)
from shopify_partners_sdk.exceptions.rate_limit import RateLimitServerError

logger = logging.getLogger(__name__)


class BaseGraphQLClient:
    """Base GraphQL client for the Shopify Partners API.

    Handles HTTP requests, authentication, rate limiting, and retry logic.
    """

    def __init__(
        self,
        organization_id: Optional[str] = None,
        access_token: Optional[str] = None,
        settings: Optional[ShopifyPartnersSDKSettings] = None,
        http_client: Optional[requests.Session] = None,
    ) -> None:
        """Initialize the GraphQL client.

        Args:
            organization_id: Shopify Partners organization ID
            access_token: Shopify Partners API access token
            settings: SDK settings instance
            http_client: Custom HTTP client (optional)
        """
        self._settings = settings or ShopifyPartnersSDKSettings()
        self._auth = AuthenticationHandler(
            organization_id, access_token, self._settings
        )
        self._rate_limiter = RateLimiter(settings=self._settings)
        self._retry_handler = RetryHandler(settings=self._settings)

        # HTTP client configuration
        if http_client:
            self._http_client = http_client
            self._owns_http_client = False
        else:
            self._http_client = requests.Session()
            # Configure session settings
            adapter = requests.adapters.HTTPAdapter(
                pool_connections=self._settings.max_connections,
                pool_maxsize=self._settings.max_keepalive_connections,
            )
            self._http_client.mount("http://", adapter)
            self._http_client.mount("https://", adapter)
            self._owns_http_client = True

        self._request_count = 0
        self._error_count = 0

    @property
    def settings(self) -> ShopifyPartnersSDKSettings:
        """Get the SDK settings."""
        return self._settings

    @property
    def auth(self) -> AuthenticationHandler:
        """Get the authentication handler."""
        return self._auth

    @property
    def rate_limiter(self) -> RateLimiter:
        """Get the rate limiter."""
        return self._rate_limiter

    @property
    def retry_handler(self) -> RetryHandler:
        """Get the retry handler."""
        return self._retry_handler

    @property
    def request_count(self) -> int:
        """Get the total number of requests made."""
        return self._request_count

    @property
    def error_count(self) -> int:
        """Get the total number of errors encountered."""
        return self._error_count

    def execute_query(
        self,
        query: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL query.

        Args:
            query: GraphQL query string
            variables: Query variables
            operation_name: Operation name (for multi-operation queries)

        Returns:
            GraphQL response data

        Raises:
            AuthenticationError: If authentication fails
            GraphQLError: If GraphQL errors occur
            RateLimitError: If rate limits are exceeded
            requests.HTTPError: If HTTP errors occur
        """
        # Validate authentication
        self._auth.validate_credentials()

        # Print query for debugging
        # TODO: Remove once debugging is done
        print("🔍 Executing GraphQL Query:")
        print("=" * 50)
        print(query)
        if variables:
            print(f"\n📝 Variables: {variables}")
        if operation_name:
            print(f"\n🏷️  Operation: {operation_name}")
        print("=" * 50)

        # Prepare request
        payload = {"query": query}
        if variables:
            payload["variables"] = variables
        if operation_name:
            payload["operationName"] = operation_name

        # Execute with rate limiting and retry
        response_data = self._retry_handler.execute_with_retry(
            self._execute_request_with_rate_limiting,
            payload,
        )

        # Process GraphQL response
        return self._process_graphql_response(response_data)

    def _execute_request_with_rate_limiting(
        self,
        payload: dict[str, Any],
    ) -> dict[str, Any]:
        """Execute HTTP request with rate limiting.

        Args:
            payload: GraphQL request payload

        Returns:
            Raw response data
        """
        # Acquire rate limit token
        self._rate_limiter.acquire()

        # Execute HTTP request
        return self._execute_http_request(payload)

    def _execute_http_request(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Execute the actual HTTP request.

        Args:
            payload: GraphQL request payload

        Returns:
            Raw response data

        Raises:
            requests.HTTPError: If HTTP errors occur
            AuthenticationError: If authentication fails
            RateLimitServerError: If server rate limits are hit
        """
        endpoint = self._auth.get_api_endpoint()
        headers = self._auth.get_request_headers()

        self._request_count += 1

        logger.info(
            "Executing GraphQL request",
            endpoint=endpoint,
            operation=payload.get("operationName"),
            variables_count=len(payload.get("variables", {})),
        )

        try:
            response = self._http_client.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=self._settings.timeout_seconds,
            )

            # Handle HTTP status codes
            if response.status_code == 401:
                self._error_count += 1
                raise UnauthorizedError("API request was not authorized")
            if response.status_code == 403:
                self._error_count += 1
                raise ForbiddenError(
                    "API request was forbidden - insufficient permissions"
                )
            if response.status_code == 429:
                self._error_count += 1
                retry_after = None
                if "retry-after" in response.headers:
                    with suppress(ValueError):
                        retry_after = float(response.headers["retry-after"])
                raise RateLimitServerError(retry_after=retry_after)

            # Raise for other HTTP errors
            response.raise_for_status()

            # Parse JSON response
            try:
                return response.json()
            except json.JSONDecodeError as e:
                self._error_count += 1
                raise GraphQLResponseError(
                    "Failed to parse JSON response",
                    response_data=response.text,
                ) from e

        except requests.HTTPError as e:
            self._error_count += 1
            logger.warning(
                "HTTP request failed",
                error=str(e),
                endpoint=endpoint,
            )
            raise

    def _process_graphql_response(
        self, response_data: dict[str, Any]
    ) -> dict[str, Any]:
        """Process and validate GraphQL response.

        Args:
            response_data: Raw response data from server

        Returns:
            Validated GraphQL response data

        Raises:
            GraphQLError: If GraphQL errors are present
            GraphQLResponseError: If response format is invalid
        """
        if not isinstance(response_data, dict):
            raise GraphQLResponseError(
                "Response is not a JSON object",
                response_data=response_data,
            )

        # Check for GraphQL errors
        errors = response_data.get("errors")
        if errors:
            self._error_count += 1
            graphql_errors = []

            for error_data in errors:
                if not isinstance(error_data, dict):
                    continue

                message = error_data.get("message", "Unknown GraphQL error")
                locations = error_data.get("locations")
                path = error_data.get("path")
                extensions = error_data.get("extensions")

                graphql_errors.append(
                    GraphQLError(
                        message=message,
                        locations=locations,
                        path=path,
                        extensions=extensions,
                    )
                )

            if len(graphql_errors) == 1:
                raise graphql_errors[0]
            if graphql_errors:
                raise GraphQLMultipleErrors(graphql_errors)

        # Validate response structure
        if "data" not in response_data:
            raise GraphQLResponseError(
                "Response missing 'data' field",
                response_data=response_data,
            )

        logger.info(
            "GraphQL request successful",
            has_data=response_data.get("data") is not None,
            has_extensions=response_data.get("extensions") is not None,
        )

        return response_data

    def execute_mutation(
        self,
        mutation: str,
        variables: Optional[dict[str, Any]] = None,
        operation_name: Optional[str] = None,
    ) -> dict[str, Any]:
        """Execute a GraphQL mutation.

        This is an alias for execute_query since GraphQL treats queries and mutations
        the same way at the HTTP level.

        Args:
            mutation: GraphQL mutation string
            variables: Mutation variables
            operation_name: Operation name

        Returns:
            GraphQL response data
        """
        return self.execute_query(mutation, variables, operation_name)

    def get_stats(self) -> dict[str, Any]:
        """Get client statistics.

        Returns:
            Dictionary with client statistics
        """
        return {
            "request_count": self._request_count,
            "error_count": self._error_count,
            "error_rate": (self._error_count / max(1, self._request_count)) * 100,
            "rate_limiter": self._rate_limiter.get_stats(),
            "retry_handler": self._retry_handler.get_stats(),
            "auth_configured": self._auth.is_authenticated(),
        }

    def close(self) -> None:
        """Close the HTTP client."""
        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def __repr__(self) -> str:
        """String representation of the client."""
        return (
            f"BaseGraphQLClient("
            f"requests={self._request_count}, "
            f"errors={self._error_count}, "
            f"authenticated={self._auth.is_authenticated()}"
            f")"
        )
