"""Unit tests for ExponentialBackoff and RetryHandler."""

from types import SimpleNamespace

import pytest
import requests

from shopify_partners_sdk.client import retry as retry_module
from shopify_partners_sdk.client.retry import ExponentialBackoff, RetryHandler
from shopify_partners_sdk.exceptions.auth import AuthenticationError
from shopify_partners_sdk.exceptions.rate_limit import RateLimitServerError

pytestmark = pytest.mark.unit


@pytest.fixture
def sleeps(monkeypatch: pytest.MonkeyPatch) -> list[float]:
    recorded: list[float] = []
    monkeypatch.setattr(
        retry_module,
        "time",
        SimpleNamespace(sleep=recorded.append),
    )
    return recorded


def http_error(status: int | None, headers: dict[str, str] | None = None):
    """Build a requests.HTTPError carrying a real Response (or none)."""
    if status is None:
        return requests.HTTPError("boom")
    response = requests.Response()
    response.status_code = status
    response.headers.update(headers or {})
    return requests.HTTPError(f"{status} error", response=response)


def no_jitter_backoff(**kwargs: float) -> ExponentialBackoff:
    return ExponentialBackoff(jitter=False, **kwargs)


class Flaky:
    """Callable failing with the given exceptions, then returning a value."""

    def __init__(self, failures: list[Exception], result: str = "ok") -> None:
        self.failures = list(failures)
        self.result = result
        self.calls = 0

    def __call__(self, *args: object, **kwargs: object) -> str:
        self.calls += 1
        if self.failures:
            raise self.failures.pop(0)
        return self.result


class TestExponentialBackoff:
    def test_delay_grows_by_factor(self) -> None:
        backoff = no_jitter_backoff(base_delay=0.5, backoff_factor=3.0)
        assert [backoff.calculate_delay(n) for n in range(4)] == [0.5, 1.5, 4.5, 13.5]

    def test_delay_is_capped_at_max_delay(self) -> None:
        backoff = no_jitter_backoff(base_delay=1.0, max_delay=10.0)
        assert backoff.calculate_delay(3) == 8.0
        assert backoff.calculate_delay(4) == 10.0
        assert backoff.calculate_delay(50) == 10.0

    def test_jitter_stays_within_25_percent(self) -> None:
        backoff = ExponentialBackoff(base_delay=4.0, max_delay=100.0)
        delays = [backoff.calculate_delay(0) for _ in range(500)]
        assert all(3.0 <= d <= 5.0 for d in delays)
        assert len(set(delays)) > 1

    def test_jitter_applies_after_cap(self) -> None:
        backoff = ExponentialBackoff(base_delay=1.0, max_delay=8.0)
        delays = [backoff.calculate_delay(10) for _ in range(500)]
        assert all(6.0 <= d <= 10.0 for d in delays)

    def test_delay_is_never_negative(self) -> None:
        backoff = ExponentialBackoff(base_delay=0.0)
        assert backoff.calculate_delay(2) == 0.0


class TestShouldRetry:
    @pytest.mark.parametrize("status", [429, 500, 502, 503, 599])
    def test_retries_http_429_and_5xx(self, status: int) -> None:
        assert RetryHandler().should_retry(http_error(status), 0) is True

    @pytest.mark.parametrize("status", [400, 401, 403, 404, 422, 499, 600])
    def test_does_not_retry_other_statuses(self, status: int) -> None:
        assert RetryHandler().should_retry(http_error(status), 0) is False

    def test_http_error_without_response_is_retried(self) -> None:
        # Old code raised AttributeError on `None.status_code`.
        assert RetryHandler().should_retry(http_error(None), 0) is True

    def test_retries_server_rate_limit_error(self) -> None:
        assert RetryHandler().should_retry(RateLimitServerError(), 0) is True

    @pytest.mark.parametrize(
        "exc", [requests.ConnectionError("x"), requests.Timeout("x")]
    )
    def test_retries_network_errors(self, exc: Exception) -> None:
        assert RetryHandler().should_retry(exc, 0) is True

    @pytest.mark.parametrize(
        "exc", [ValueError("x"), AuthenticationError("x"), KeyError("x")]
    )
    def test_does_not_retry_unrelated_errors(self, exc: Exception) -> None:
        assert RetryHandler().should_retry(exc, 0) is False

    def test_stops_when_attempts_exhausted(self) -> None:
        handler = RetryHandler(max_attempts=2)
        error = RateLimitServerError()
        assert handler.should_retry(error, 1) is True
        assert handler.should_retry(error, 2) is False


class TestConstruction:
    def test_default_comes_from_settings(self) -> None:
        assert RetryHandler().max_attempts == 3

    def test_zero_is_honored(self) -> None:
        # Old code used `max_attempts or settings`, turning 0 into 3.
        assert RetryHandler(max_attempts=0).max_attempts == 0

    def test_negative_is_rejected(self) -> None:
        with pytest.raises(ValueError, match="negative"):
            RetryHandler(max_attempts=-1)

    def test_default_backoff_uses_settings(self) -> None:
        backoff = RetryHandler().backoff
        assert (backoff.base_delay, backoff.max_delay, backoff.backoff_factor) == (
            1.0,
            60.0,
            2.0,
        )


class TestRetryDelay:
    def test_uses_backoff_for_generic_errors(self) -> None:
        handler = RetryHandler(backoff=no_jitter_backoff(base_delay=2.0))
        assert handler.get_retry_delay(requests.Timeout(), 2) == 8.0

    def test_honors_retry_after_of_server_rate_limit_error(self) -> None:
        handler = RetryHandler(backoff=no_jitter_backoff(base_delay=1.0))
        assert handler.get_retry_delay(RateLimitServerError(retry_after=7.5), 0) == 7.5

    def test_server_rate_limit_without_retry_after_falls_back(self) -> None:
        handler = RetryHandler(backoff=no_jitter_backoff(base_delay=1.0))
        assert handler.get_retry_delay(RateLimitServerError(), 1) == 2.0

    def test_honors_retry_after_header_on_429(self) -> None:
        handler = RetryHandler()
        error = http_error(429, {"Retry-After": "12"})
        assert handler.get_retry_delay(error, 0) == 12.0

    def test_unparseable_retry_after_header_falls_back(self) -> None:
        handler = RetryHandler(backoff=no_jitter_backoff(base_delay=1.0))
        error = http_error(429, {"Retry-After": "Wed, 21 Oct 2026 07:28:00 GMT"})
        assert handler.get_retry_delay(error, 0) == 1.0

    def test_retry_after_header_ignored_on_5xx(self) -> None:
        handler = RetryHandler(backoff=no_jitter_backoff(base_delay=1.0))
        error = http_error(503, {"Retry-After": "30"})
        assert handler.get_retry_delay(error, 0) == 1.0

    def test_http_error_without_response_uses_backoff(self) -> None:
        handler = RetryHandler(backoff=no_jitter_backoff(base_delay=1.0))
        assert handler.get_retry_delay(http_error(None), 2) == 4.0


class TestExecuteWithRetry:
    def test_returns_first_success_without_sleeping(self, sleeps: list[float]) -> None:
        func = Flaky([])
        handler = RetryHandler()

        assert handler.execute_with_retry(func, "a", key="b") == "ok"

        assert func.calls == 1
        assert sleeps == []
        assert handler.get_stats()["success_rate"] == 100.0

    def test_passes_arguments_through(self, sleeps: list[float]) -> None:
        seen: list[tuple] = []

        def func(*args: object, **kwargs: object) -> str:
            seen.append((args, kwargs))
            return "done"

        RetryHandler().execute_with_retry(func, 1, 2, x=3)
        assert seen == [((1, 2), {"x": 3})]

    def test_retries_then_succeeds_with_growing_delays(
        self, sleeps: list[float]
    ) -> None:
        func = Flaky([requests.Timeout(), requests.ConnectionError()])
        handler = RetryHandler(
            max_attempts=3, backoff=no_jitter_backoff(base_delay=1.5)
        )

        assert handler.execute_with_retry(func) == "ok"

        assert func.calls == 3
        assert sleeps == [1.5, 3.0]
        assert handler.total_attempts == 3
        assert handler.failed_attempts == 2
        assert handler.successful_attempts == 1
        assert handler.success_rate == pytest.approx(100 / 3)

    def test_reraises_last_exception_after_exhaustion(
        self, sleeps: list[float]
    ) -> None:
        errors = [requests.Timeout(f"t{i}") for i in range(3)]
        func = Flaky(list(errors))
        handler = RetryHandler(max_attempts=2, backoff=no_jitter_backoff())

        with pytest.raises(requests.Timeout) as info:
            handler.execute_with_retry(func)

        assert info.value is errors[2]
        assert func.calls == 3
        assert len(sleeps) == 2

    def test_zero_max_attempts_calls_once(self, sleeps: list[float]) -> None:
        func = Flaky([requests.Timeout("only")])
        handler = RetryHandler(max_attempts=0)

        with pytest.raises(requests.Timeout, match="only"):
            handler.execute_with_retry(func)

        assert func.calls == 1
        assert sleeps == []

    def test_non_retryable_error_raises_immediately(self, sleeps: list[float]) -> None:
        func = Flaky([http_error(401), requests.Timeout()])

        with pytest.raises(requests.HTTPError):
            RetryHandler().execute_with_retry(func)

        assert func.calls == 1
        assert sleeps == []

    def test_http_error_without_response_is_retried_end_to_end(
        self, sleeps: list[float]
    ) -> None:
        func = Flaky([http_error(None)])
        handler = RetryHandler(backoff=no_jitter_backoff(base_delay=0.5))

        assert handler.execute_with_retry(func) == "ok"
        assert sleeps == [0.5]

    def test_server_retry_after_is_slept_verbatim(self, sleeps: list[float]) -> None:
        func = Flaky([RateLimitServerError(retry_after=9.0)])

        RetryHandler().execute_with_retry(func)

        assert sleeps == [9.0]

    def test_zero_delay_skips_sleep(self, sleeps: list[float]) -> None:
        func = Flaky([requests.Timeout()])
        handler = RetryHandler(backoff=ExponentialBackoff(base_delay=0.0, jitter=False))

        handler.execute_with_retry(func)

        assert sleeps == []


class TestStats:
    def test_stats_and_reset(self, sleeps: list[float]) -> None:
        handler = RetryHandler(max_attempts=1, backoff=no_jitter_backoff())
        handler.execute_with_retry(Flaky([requests.Timeout()]))

        stats = handler.get_stats()
        assert stats["max_attempts"] == 1
        assert stats["total_attempts"] == 2
        assert stats["failed_attempts"] == 1
        assert stats["success_rate"] == 50.0
        assert stats["backoff_factor"] == 2.0

        handler.reset_stats()
        assert handler.total_attempts == 0
        assert handler.success_rate == 0.0

    def test_repr(self) -> None:
        assert repr(RetryHandler(max_attempts=2)) == (
            "RetryHandler(max_attempts=2, success_rate=0.0%)"
        )
