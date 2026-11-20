"""Unit tests for ShopifyPartnersSDKSettings."""

from pydantic import ValidationError
import pytest

from shopify_partners_sdk.config import ShopifyPartnersSDKSettings
from shopify_partners_sdk.schema import SUPPORTED_API_VERSIONS
from shopify_partners_sdk.version import __version__

pytestmark = pytest.mark.unit


class TestDefaults:
    def test_api_defaults(self):
        settings = ShopifyPartnersSDKSettings()
        assert settings.api_version == "2026-10"
        assert settings.base_url == "https://partners.shopify.com"
        assert settings.organization_id is None
        assert settings.access_token is None

    def test_numeric_defaults(self):
        settings = ShopifyPartnersSDKSettings()
        assert settings.rate_limit_per_second == 4.0
        assert settings.default_page_size == 50
        assert settings.max_page_size == 250
        assert settings.timeout_seconds == 30.0
        assert settings.max_retry_attempts == 3
        assert settings.log_level == "INFO"


class TestEnvironment:
    def test_api_version_from_env(self, monkeypatch):
        monkeypatch.setenv("SHOPIFY_PARTNERS_API_VERSION", "2026-04")
        assert ShopifyPartnersSDKSettings().api_version == "2026-04"

    def test_organization_id_string_becomes_int(self, monkeypatch):
        monkeypatch.setenv("SHOPIFY_PARTNERS_ORGANIZATION_ID", "42")
        assert ShopifyPartnersSDKSettings().organization_id == 42

    def test_access_token_from_env(self, monkeypatch):
        monkeypatch.setenv("SHOPIFY_PARTNERS_ACCESS_TOKEN", "prtapi_env")
        assert ShopifyPartnersSDKSettings().access_token == "prtapi_env"

    def test_env_names_are_case_insensitive(self, monkeypatch):
        monkeypatch.setenv("shopify_partners_api_version", "2026-07")
        assert ShopifyPartnersSDKSettings().api_version == "2026-07"

    def test_invalid_env_value_rejected(self, monkeypatch):
        monkeypatch.setenv("SHOPIFY_PARTNERS_API_VERSION", "garbage")
        with pytest.raises(ValidationError):
            ShopifyPartnersSDKSettings()

    def test_constructor_beats_env(self, monkeypatch):
        monkeypatch.setenv("SHOPIFY_PARTNERS_API_VERSION", "2026-04")
        monkeypatch.setenv("SHOPIFY_PARTNERS_ORGANIZATION_ID", "42")
        settings = ShopifyPartnersSDKSettings(api_version="2026-07", organization_id=7)
        assert settings.api_version == "2026-07"
        assert settings.organization_id == 7

    def test_dotenv_file_in_cwd_is_read(self, tmp_path):
        (tmp_path / ".env").write_text(
            "SHOPIFY_PARTNERS_API_VERSION=2026-01\n"
            "SHOPIFY_PARTNERS_ORGANIZATION_ID=99\n"
            "SHOPIFY_PARTNERS_ACCESS_TOKEN=prtapi_dotenv\n"
        )
        settings = ShopifyPartnersSDKSettings()
        assert settings.api_version == "2026-01"
        assert settings.organization_id == 99
        assert settings.access_token == "prtapi_dotenv"

    def test_env_beats_dotenv(self, tmp_path, monkeypatch):
        (tmp_path / ".env").write_text("SHOPIFY_PARTNERS_API_VERSION=2026-01\n")
        monkeypatch.setenv("SHOPIFY_PARTNERS_API_VERSION", "2026-04")
        assert ShopifyPartnersSDKSettings().api_version == "2026-04"

    def test_unknown_env_keys_ignored(self, monkeypatch, tmp_path):
        (tmp_path / ".env").write_text("SHOPIFY_PARTNERS_SOMETHING_ELSE=1\n")
        assert ShopifyPartnersSDKSettings().api_version == "2026-10"


class TestApiVersion:
    @pytest.mark.parametrize("version", SUPPORTED_API_VERSIONS)
    def test_supported_versions_accepted(self, version):
        assert ShopifyPartnersSDKSettings(api_version=version).api_version == version

    def test_bundled_versions_include_known_releases(self):
        assert {"2026-01", "2026-04", "2026-07", "2026-10", "2027-01"} <= set(
            SUPPORTED_API_VERSIONS
        )

    @pytest.mark.parametrize(
        "version", ["2025-04", "2025-07", "2024-10", "garbage", ""]
    )
    def test_unsupported_versions_rejected(self, version):
        with pytest.raises(ValidationError) as info:
            ShopifyPartnersSDKSettings(api_version=version)
        message = str(info.value)
        assert "api_version must be one of" in message
        assert "2026-10" in message
        assert "2026-01" in message


class TestAccessToken:
    def test_valid_prefix(self):
        assert ShopifyPartnersSDKSettings(access_token="prtapi_abc").access_token == (
            "prtapi_abc"
        )

    @pytest.mark.parametrize("token", ["abc", "shpat_abc", "PRTAPI_abc", ""])
    def test_invalid_prefix_rejected(self, token):
        with pytest.raises(ValidationError, match="must start with 'prtapi_'"):
            ShopifyPartnersSDKSettings(access_token=token)

    def test_none_allowed(self):
        assert ShopifyPartnersSDKSettings(access_token=None).access_token is None


class TestOrganizationId:
    def test_none_allowed(self):
        assert ShopifyPartnersSDKSettings(organization_id=None).organization_id is None

    def test_positive_accepted(self):
        assert ShopifyPartnersSDKSettings(organization_id=1).organization_id == 1

    @pytest.mark.parametrize("value", [0, -1, -123])
    def test_non_positive_rejected(self, value):
        with pytest.raises(ValidationError, match="positive integer"):
            ShopifyPartnersSDKSettings(organization_id=value)

    def test_non_numeric_rejected(self):
        with pytest.raises(ValidationError):
            ShopifyPartnersSDKSettings(organization_id="abc")


class TestLogLevel:
    @pytest.mark.parametrize(
        ("given", "expected"),
        [
            ("debug", "DEBUG"),
            ("Info", "INFO"),
            ("WARNING", "WARNING"),
            ("error", "ERROR"),
            ("critical", "CRITICAL"),
        ],
    )
    def test_uppercased(self, given, expected):
        assert ShopifyPartnersSDKSettings(log_level=given).log_level == expected

    @pytest.mark.parametrize("value", ["verbose", "trace", ""])
    def test_invalid_rejected(self, value):
        with pytest.raises(ValidationError, match="log_level must be one of"):
            ShopifyPartnersSDKSettings(log_level=value)


class TestCrossFieldLimits:
    def test_keepalive_override_alone_succeeds(self):
        settings = ShopifyPartnersSDKSettings(max_keepalive_connections=3)
        assert settings.max_keepalive_connections == 3
        assert settings.max_connections == 10

    def test_default_page_size_override_alone_succeeds(self):
        settings = ShopifyPartnersSDKSettings(default_page_size=10)
        assert settings.default_page_size == 10
        assert settings.max_page_size == 250

    def test_keepalive_equal_to_max_connections_allowed(self):
        settings = ShopifyPartnersSDKSettings(
            max_connections=8, max_keepalive_connections=8
        )
        assert settings.max_keepalive_connections == 8

    def test_keepalive_above_max_connections_rejected(self):
        with pytest.raises(ValidationError, match="cannot exceed max_connections"):
            ShopifyPartnersSDKSettings(max_connections=4, max_keepalive_connections=5)

    def test_keepalive_above_default_max_connections_rejected(self):
        with pytest.raises(ValidationError, match="cannot exceed max_connections"):
            ShopifyPartnersSDKSettings(max_keepalive_connections=11)

    def test_page_size_above_max_rejected(self):
        with pytest.raises(ValidationError, match="cannot exceed max_page_size"):
            ShopifyPartnersSDKSettings(default_page_size=100, max_page_size=50)

    def test_page_size_equal_to_max_allowed(self):
        settings = ShopifyPartnersSDKSettings(default_page_size=60, max_page_size=60)
        assert settings.default_page_size == 60

    def test_cross_field_check_applies_to_env(self, monkeypatch):
        monkeypatch.setenv("SHOPIFY_PARTNERS_MAX_CONNECTIONS", "2")
        monkeypatch.setenv("SHOPIFY_PARTNERS_MAX_KEEPALIVE_CONNECTIONS", "3")
        with pytest.raises(ValidationError):
            ShopifyPartnersSDKSettings()


class TestBounds:
    @pytest.mark.parametrize(
        ("field", "low", "high"),
        [
            ("rate_limit_per_second", 0.1, 10.0),
            ("max_retry_attempts", 0, 10),
            ("retry_base_delay", 0.1, 10.0),
            ("retry_max_delay", 1.0, 300.0),
            ("retry_backoff_factor", 1.0, 5.0),
            ("timeout_seconds", 5.0, 300.0),
            ("default_page_size", 1, 250),
            ("max_page_size", 250, 1000),
        ],
    )
    def test_inclusive_bounds_accepted(self, field, low, high):
        assert getattr(ShopifyPartnersSDKSettings(**{field: low}), field) == low
        assert getattr(ShopifyPartnersSDKSettings(**{field: high}), field) == high

    @pytest.mark.parametrize(
        ("field", "bad"),
        [
            ("rate_limit_per_second", 0.05),
            ("rate_limit_per_second", 10.5),
            ("max_retry_attempts", -1),
            ("max_retry_attempts", 11),
            ("retry_base_delay", 0.0),
            ("retry_max_delay", 0.5),
            ("retry_max_delay", 301.0),
            ("retry_backoff_factor", 0.9),
            ("retry_backoff_factor", 5.1),
            ("timeout_seconds", 4.9),
            ("timeout_seconds", 300.1),
            ("max_connections", 0),
            ("max_connections", 101),
            ("max_keepalive_connections", 0),
            ("max_keepalive_connections", 51),
            ("default_page_size", 0),
            ("default_page_size", 251),
            ("max_page_size", 0),
            ("max_page_size", 1001),
        ],
    )
    def test_out_of_range_rejected(self, field, bad):
        with pytest.raises(ValidationError):
            ShopifyPartnersSDKSettings(**{field: bad})


class TestConnectionBounds:
    def test_max_connections_bounds(self):
        low = ShopifyPartnersSDKSettings(max_connections=1, max_keepalive_connections=1)
        assert low.max_connections == 1
        assert ShopifyPartnersSDKSettings(max_connections=100).max_connections == 100

    def test_keepalive_bounds(self):
        assert (
            ShopifyPartnersSDKSettings(
                max_keepalive_connections=1
            ).max_keepalive_connections
            == 1
        )
        high = ShopifyPartnersSDKSettings(
            max_connections=100, max_keepalive_connections=50
        )
        assert high.max_keepalive_connections == 50


class TestEndpointAndHeaders:
    def test_endpoint_with_organization(self):
        settings = ShopifyPartnersSDKSettings(organization_id=123)
        assert settings.get_api_endpoint() == (
            "https://partners.shopify.com/123/api/2026-10/graphql.json"
        )

    def test_endpoint_follows_version_and_base_url(self):
        settings = ShopifyPartnersSDKSettings(
            organization_id=5, api_version="2027-01", base_url="https://example.test"
        )
        assert settings.get_api_endpoint() == (
            "https://example.test/5/api/2027-01/graphql.json"
        )

    def test_endpoint_without_organization_raises(self):
        with pytest.raises(ValueError, match="organization_id is required"):
            ShopifyPartnersSDKSettings().get_api_endpoint()

    def test_headers_with_token(self):
        headers = ShopifyPartnersSDKSettings(access_token="prtapi_t").get_headers()
        assert headers == {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": f"shopify-partners-sdk-python/{__version__}",
            "X-Shopify-Access-Token": "prtapi_t",
        }

    def test_headers_without_token(self):
        headers = ShopifyPartnersSDKSettings().get_headers()
        assert "X-Shopify-Access-Token" not in headers
        assert headers["Content-Type"] == "application/json"
