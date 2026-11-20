"""Shared fixtures: a scripted HTTP session so client tests never touch the network."""

import json
from typing import Any

import pytest
import requests

from shopify_partners_sdk import ShopifyPartnersClient

ORG_ID = 1234567
TOKEN = "prtapi_test_token"


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(
        self,
        status_code: int = 200,
        body: Any = None,
        headers: dict[str, str] | None = None,
        text: str | None = None,
    ) -> None:
        self.status_code = status_code
        self._body = body
        self.headers = headers or {}
        self.text = text if text is not None else json.dumps(body)

    def json(self) -> Any:
        return json.loads(self.text)

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(f"{self.status_code} error", response=self)  # type: ignore[arg-type]


class FakeSession:
    """Records each POST and answers with the next scripted response."""

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self._responses: list[FakeResponse] = []
        self.closed = False

    def queue(self, *responses: FakeResponse) -> "FakeSession":
        self._responses.extend(responses)
        return self

    def queue_data(self, *payloads: dict[str, Any]) -> "FakeSession":
        return self.queue(*(FakeResponse(body={"data": p}) for p in payloads))

    def post(
        self, url: str, headers: dict[str, str], json: Any, timeout: float
    ) -> FakeResponse:
        self.calls.append(
            {"url": url, "headers": headers, "json": json, "timeout": timeout}
        )
        if not self._responses:
            raise AssertionError(f"Unexpected request #{len(self.calls)}: {json}")
        return self._responses.pop(0)

    def close(self) -> None:
        self.closed = True

    @property
    def last_payload(self) -> dict[str, Any]:
        return dict(self.calls[-1]["json"])


@pytest.fixture(autouse=True)
def _isolate_environment(monkeypatch: pytest.MonkeyPatch, tmp_path: Any) -> None:
    """Keep real SHOPIFY_PARTNERS_* variables and any local .env out of every test."""
    import os

    for key in list(os.environ):
        if key.startswith("SHOPIFY_PARTNERS_"):
            monkeypatch.delenv(key)
    monkeypatch.chdir(tmp_path)


@pytest.fixture
def no_wait(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip rate-limit waits and retry sleeps."""
    from shopify_partners_sdk.client import rate_limiter, retry

    monkeypatch.setattr(rate_limiter.time, "sleep", lambda _s: None)
    monkeypatch.setattr(retry.time, "sleep", lambda _s: None)


@pytest.fixture
def session() -> FakeSession:
    return FakeSession()


@pytest.fixture
def client(session: FakeSession, no_wait: None) -> ShopifyPartnersClient:
    return ShopifyPartnersClient(
        organization_id=ORG_ID,
        access_token=TOKEN,
        http_client=session,  # type: ignore[arg-type]
    )
