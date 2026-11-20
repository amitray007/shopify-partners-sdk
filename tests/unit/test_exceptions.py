"""Unit tests for the SDK exception hierarchy."""

import pytest

from shopify_partners_sdk import exceptions
from shopify_partners_sdk.exceptions import (
    AccessTokenError,
    AuthenticationError,
    ForbiddenError,
    GraphQLError,
    GraphQLExecutionError,
    GraphQLMultipleErrors,
    GraphQLResponseError,
    GraphQLSyntaxError,
    GraphQLValidationError,
    InvalidCursorError,
    InvalidDateRangeError,
    InvalidGlobalIdError,
    InvalidPageSizeError,
    OrganizationIdError,
    RateLimitError,
    RateLimitExceededError,
    RateLimitServerError,
    SchemaValidationError,
    ShopifyPartnersSDKError,
    UnauthorizedError,
    ValidationError,
)

pytestmark = pytest.mark.unit


class TestHierarchy:
    def test_every_exported_error_derives_from_base(self):
        for name in exceptions.__all__:
            assert issubclass(getattr(exceptions, name), ShopifyPartnersSDKError), name

    def test_base_is_an_exception(self):
        assert issubclass(ShopifyPartnersSDKError, Exception)

    @pytest.mark.parametrize(
        "cls",
        [AccessTokenError, OrganizationIdError, UnauthorizedError, ForbiddenError],
    )
    def test_auth_errors(self, cls):
        assert issubclass(cls, AuthenticationError)

    @pytest.mark.parametrize(
        "cls", [GraphQLValidationError, GraphQLSyntaxError, GraphQLExecutionError]
    )
    def test_graphql_subtypes(self, cls):
        assert issubclass(cls, GraphQLError)

    def test_response_and_multiple_are_not_graphql_error(self):
        assert not issubclass(GraphQLResponseError, GraphQLError)
        assert not issubclass(GraphQLMultipleErrors, GraphQLError)

    @pytest.mark.parametrize("cls", [RateLimitExceededError, RateLimitServerError])
    def test_rate_limit_subtypes(self, cls):
        assert issubclass(cls, RateLimitError)

    @pytest.mark.parametrize(
        "cls",
        [
            InvalidGlobalIdError,
            InvalidPageSizeError,
            InvalidCursorError,
            InvalidDateRangeError,
            SchemaValidationError,
        ],
    )
    def test_validation_subtypes(self, cls):
        assert issubclass(cls, ValidationError)

    def test_schema_validation_error_is_also_value_error(self):
        assert issubclass(SchemaValidationError, ValueError)
        assert issubclass(SchemaValidationError, ValidationError)

    def test_schema_validation_error_caught_as_value_error(self):
        with pytest.raises(ValueError, match="bad field"):
            raise SchemaValidationError("bad field")

    def test_other_validation_errors_are_not_value_errors(self):
        assert not issubclass(InvalidCursorError, ValueError)

    def test_auth_and_rate_limit_are_distinct_branches(self):
        assert not issubclass(AuthenticationError, RateLimitError)
        assert not issubclass(RateLimitError, AuthenticationError)


class TestBaseFormatting:
    def test_message_and_default_details(self):
        error = ShopifyPartnersSDKError("boom")
        assert error.message == "boom"
        assert error.details == {}
        assert error.args == ("boom",)

    def test_str_without_details(self):
        assert str(ShopifyPartnersSDKError("boom")) == "boom"

    def test_str_with_details(self):
        error = ShopifyPartnersSDKError("boom", {"k": 1})
        assert str(error) == "boom. Details: {'k': 1}"

    def test_repr(self):
        error = ShopifyPartnersSDKError("boom", {"k": 1})
        assert repr(error) == (
            "ShopifyPartnersSDKError(message='boom', details={'k': 1})"
        )

    def test_repr_uses_subclass_name(self):
        assert repr(ValidationError("x")) == (
            "ValidationError(message='x', details={})"
        )

    def test_none_details_become_empty_dict(self):
        assert ShopifyPartnersSDKError("m", None).details == {}


class TestAuthErrors:
    @pytest.mark.parametrize(
        ("cls", "message"),
        [
            (AccessTokenError, "Invalid or missing access token"),
            (OrganizationIdError, "Invalid or missing organization ID"),
            (UnauthorizedError, "API request was not authorized"),
            (
                ForbiddenError,
                "API request was forbidden - insufficient permissions",
            ),
        ],
    )
    def test_default_messages(self, cls, message):
        assert str(cls()) == message

    def test_custom_message(self):
        assert str(UnauthorizedError("nope")) == "nope"

    def test_authentication_error_requires_message(self):
        with pytest.raises(TypeError):
            AuthenticationError()  # type: ignore[call-arg]


class TestGraphQLError:
    def test_all_fields(self):
        error = GraphQLError(
            "bad",
            locations=[{"line": 2, "column": 4}],
            path=["app", 0],
            extensions={"code": "X"},
        )
        assert error.message == "bad"
        assert error.locations == [{"line": 2, "column": 4}]
        assert error.path == ["app", 0]
        assert error.extensions == {"code": "X"}
        assert error.details == {
            "locations": [{"line": 2, "column": 4}],
            "path": ["app", 0],
            "extensions": {"code": "X"},
        }

    def test_minimal(self):
        error = GraphQLError("bad")
        assert error.locations is None
        assert error.path is None
        assert error.extensions is None
        assert error.details == {}
        assert str(error) == "bad"

    def test_empty_values_left_out_of_details(self):
        error = GraphQLError("bad", locations=[], path=[], extensions={})
        assert error.details == {}

    def test_str_includes_details(self):
        assert str(GraphQLError("bad", path=["a"])) == "bad. Details: {'path': ['a']}"

    def test_subclasses_keep_fields(self):
        error = GraphQLSyntaxError("syntax", path=["q"])
        assert error.path == ["q"]


class TestGraphQLResponseError:
    def test_defaults(self):
        error = GraphQLResponseError()
        assert error.message == "Invalid GraphQL response format"
        assert error.response_data is None
        assert error.details == {}

    def test_with_response_data(self):
        error = GraphQLResponseError("bad", response_data=["x"])
        assert error.response_data == ["x"]
        assert error.details == {"response_data": ["x"]}

    def test_falsy_response_data_still_recorded(self):
        error = GraphQLResponseError("bad", response_data={})
        assert error.details == {"response_data": {}}


class TestGraphQLMultipleErrors:
    def make(self):
        return GraphQLMultipleErrors(
            [
                GraphQLError("one", path=["a"]),
                GraphQLError("two", extensions={"code": "X"}),
            ]
        )

    def test_message_and_errors(self):
        error = self.make()
        assert error.message == "Multiple GraphQL errors occurred (2 errors)"
        assert [e.message for e in error.errors] == ["one", "two"]

    def test_details(self):
        assert self.make().details == {
            "error_count": 2,
            "errors": [
                {
                    "message": "one",
                    "locations": None,
                    "path": ["a"],
                    "extensions": None,
                },
                {
                    "message": "two",
                    "locations": None,
                    "path": None,
                    "extensions": {"code": "X"},
                },
            ],
        }

    def test_iterable(self):
        assert [e.message for e in self.make()] == ["one", "two"]

    def test_empty_list_rejected(self):
        with pytest.raises(ValueError, match="cannot be empty"):
            GraphQLMultipleErrors([])


class TestRateLimitErrors:
    def test_defaults(self):
        error = RateLimitError()
        assert error.message == "API rate limit exceeded"
        assert error.retry_after is None
        assert str(error) == "API rate limit exceeded"

    def test_str_with_retry_after(self):
        error = RateLimitError(retry_after=2.5)
        assert str(error) == "API rate limit exceeded. Retry after 2.5 seconds."

    def test_str_with_details_and_retry_after(self):
        error = RateLimitError("slow", retry_after=1.0, details={"k": 1})
        assert str(error) == "slow. Details: {'k': 1}. Retry after 1.0 seconds."

    def test_zero_retry_after_not_rendered(self):
        assert str(RateLimitError(retry_after=0)) == "API rate limit exceeded"

    def test_server_error(self):
        error = RateLimitServerError(retry_after=3.0)
        assert error.message == "Server rate limit exceeded (HTTP 429)"
        assert error.retry_after == 3.0
        assert str(error) == (
            "Server rate limit exceeded (HTTP 429). Retry after 3.0 seconds."
        )

    def test_server_error_without_retry_after(self):
        error = RateLimitServerError()
        assert error.retry_after is None
        assert str(error) == "Server rate limit exceeded (HTTP 429)"

    def test_server_error_details(self):
        assert RateLimitServerError(details={"body": "x"}).details == {"body": "x"}

    def test_exceeded_error(self):
        error = RateLimitExceededError(5.0, 4.0, retry_after=0.25)
        assert error.message == "Rate limit exceeded: 5.00 req/s > 4.00 req/s"
        assert error.current_rate == 5.0
        assert error.max_rate == 4.0
        assert error.retry_after == 0.25
        assert error.details == {"current_rate": 5.0, "max_rate": 4.0}


class TestValidationErrors:
    def test_invalid_global_id(self):
        error = InvalidGlobalIdError("gid://bad")
        assert error.message == "Invalid Global ID format: gid://bad"
        assert error.global_id == "gid://bad"
        assert error.details == {"global_id": "gid://bad"}

    def test_invalid_page_size(self):
        error = InvalidPageSizeError(500, 250)
        assert error.message == "Invalid page size: 500 (max: 250)"
        assert (error.page_size, error.max_size) == (500, 250)
        assert error.details == {"page_size": 500, "max_size": 250}

    def test_invalid_cursor(self):
        error = InvalidCursorError("abc")
        assert error.message == "Invalid cursor format: abc"
        assert error.cursor == "abc"
        assert error.details == {"cursor": "abc"}

    def test_invalid_date_range(self):
        error = InvalidDateRangeError("2026-02-01", "2026-01-01")
        assert error.message == "Invalid date range: 2026-02-01 to 2026-01-01"
        assert (error.start_date, error.end_date) == ("2026-02-01", "2026-01-01")
        assert error.details == {
            "start_date": "2026-02-01",
            "end_date": "2026-01-01",
        }

    def test_schema_validation_error_suggestions(self):
        error = SchemaValidationError("Unknown field 'titel'", ["title", "handle"])
        assert error.message == "Unknown field 'titel'"
        assert error.suggestions == ["title", "handle"]
        assert str(error) == "Unknown field 'titel'"

    def test_schema_validation_error_default_suggestions(self):
        assert SchemaValidationError("x").suggestions == []

    def test_schema_validation_error_none_suggestions(self):
        assert SchemaValidationError("x", None).suggestions == []

    def test_suggestions_not_shared_between_instances(self):
        first = SchemaValidationError("a")
        first.suggestions.append("z")
        assert SchemaValidationError("b").suggestions == []
