"""Unit tests for AuthenticationHandler."""

import pytest

from shopify_partners_sdk.client.auth import AuthenticationHandler
from shopify_partners_sdk.config import DEFAULT_API_VERSION, ShopifyPartnersSDKSettings
from shopify_partners_sdk.exceptions.auth import AuthenticationError

pytestmark = pytest.mark.unit

TOKEN = "prtapi_abc123"


def make(**kwargs: object) -> AuthenticationHandler:
    settings = kwargs.pop("settings", None) or ShopifyPartnersSDKSettings()
    return AuthenticationHandler(settings=settings, **kwargs)  # type: ignore[arg-type]


def test_endpoint_url_format() -> None:
    handler = make(organization_id="12345", access_token=TOKEN)
    assert handler.get_api_endpoint() == (
        f"https://partners.shopify.com/12345/api/{DEFAULT_API_VERSION}/graphql.json"
    )


def test_endpoint_uses_settings_base_url_and_version() -> None:
    settings = ShopifyPartnersSDKSettings(
        base_url="https://example.test", api_version="unstable"
    )
    handler = make(organization_id="7", access_token=TOKEN, settings=settings)
    assert (
        handler.get_api_endpoint() == "https://example.test/7/api/unstable/graphql.json"
    )


def test_auth_headers_carry_token() -> None:
    handler = make(organization_id="1", access_token=TOKEN)
    assert handler.get_auth_headers() == {"X-Shopify-Access-Token": TOKEN}


def test_request_headers_are_complete() -> None:
    headers = make(organization_id="1", access_token=TOKEN).get_request_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"
    assert headers["X-Shopify-Access-Token"] == TOKEN
    assert headers["User-Agent"].startswith("shopify-partners-sdk-python/")


def test_credentials_fall_back_to_settings() -> None:
    settings = ShopifyPartnersSDKSettings(organization_id=99, access_token=TOKEN)
    handler = AuthenticationHandler(settings=settings)
    assert handler.organization_id == "99"
    assert handler.access_token == TOKEN


def test_explicit_credentials_override_settings() -> None:
    settings = ShopifyPartnersSDKSettings(organization_id=99, access_token=TOKEN)
    handler = AuthenticationHandler("5", "prtapi_other", settings)
    assert handler.organization_id == "5"
    assert handler.access_token == "prtapi_other"


def test_int_organization_id_in_constructor_is_normalized_to_str() -> None:
    handler = make(organization_id=12345, access_token=TOKEN)
    assert handler.organization_id == "12345"
    assert isinstance(handler.organization_id, str)
    assert "/12345/api/" in handler.get_api_endpoint()


def test_settings_int_organization_id_is_returned_as_str() -> None:
    settings = ShopifyPartnersSDKSettings(organization_id=42)
    assert AuthenticationHandler(settings=settings).organization_id == "42"


def test_organization_id_setter_accepts_int_and_digit_string() -> None:
    handler = make()
    handler.organization_id = 77
    assert handler.organization_id == "77"
    handler.organization_id = "88"
    assert handler.organization_id == "88"


@pytest.mark.parametrize("bad", ["", "abc", "12a", "-5", " 12", "1.5", "²", -5, True])
def test_organization_id_setter_rejects_invalid(bad: object) -> None:
    handler = make()
    with pytest.raises(AuthenticationError, match="Organization ID"):
        handler.organization_id = bad  # type: ignore[assignment]


def test_constructor_rejects_non_digit_organization_id() -> None:
    with pytest.raises(AuthenticationError, match="Organization ID"):
        make(organization_id="not-a-number")


def test_missing_organization_id_error_is_actionable() -> None:
    handler = make(access_token=TOKEN)
    with pytest.raises(AuthenticationError, match="SHOPIFY_PARTNERS_ORGANIZATION_ID"):
        _ = handler.organization_id
    with pytest.raises(AuthenticationError, match="Organization ID is required"):
        handler.get_api_endpoint()


def test_missing_access_token_error_is_actionable() -> None:
    handler = make(organization_id="1")
    with pytest.raises(AuthenticationError, match="SHOPIFY_PARTNERS_ACCESS_TOKEN"):
        _ = handler.access_token
    with pytest.raises(AuthenticationError, match="Access token is required"):
        handler.get_auth_headers()
    with pytest.raises(AuthenticationError):
        handler.get_request_headers()


def test_access_token_setter_requires_prtapi_prefix() -> None:
    handler = make()
    handler.access_token = TOKEN
    assert handler.access_token == TOKEN
    for bad in ["", "shpat_123", "prtapi"]:
        with pytest.raises(AuthenticationError, match="prtapi_"):
            handler.access_token = bad


def test_is_authenticated_checks_presence_only() -> None:
    assert make(organization_id="1", access_token=TOKEN).is_authenticated() is True
    assert make(organization_id="1").is_authenticated() is False
    assert make(access_token=TOKEN).is_authenticated() is False
    assert make().is_authenticated() is False
    # Format is not checked: a token without the prtapi_ prefix still counts as set.
    assert make(organization_id="1", access_token="anything").is_authenticated() is True
    assert "presence only" in (AuthenticationHandler.is_authenticated.__doc__ or "")


def test_validate_credentials_lists_every_missing_field() -> None:
    with pytest.raises(AuthenticationError) as info:
        make().validate_credentials()
    message = str(info.value)
    assert "organization_id" in message
    assert "access_token" in message


def test_validate_credentials_names_only_missing_field() -> None:
    with pytest.raises(AuthenticationError) as info:
        make(organization_id="1").validate_credentials()
    assert "access_token" in str(info.value)
    assert "organization_id," not in str(info.value)


def test_validate_credentials_passes_when_complete() -> None:
    make(organization_id="1", access_token=TOKEN).validate_credentials()


def test_repr_masks_secrets() -> None:
    text = repr(make(organization_id="123456", access_token="prtapi_secretvalue"))
    assert "secretvalue" not in text
    assert "123456" not in text
