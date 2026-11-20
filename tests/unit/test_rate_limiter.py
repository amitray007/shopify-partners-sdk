"""Unit tests for the token bucket RateLimiter."""

import threading
from types import SimpleNamespace

import pytest

from shopify_partners_sdk.client import rate_limiter as rl
from shopify_partners_sdk.client.rate_limiter import RateLimiter
from shopify_partners_sdk.exceptions.rate_limit import RateLimitExceededError

pytestmark = pytest.mark.unit


class FakeClock:
    """Deterministic replacement for the `time` module used by rate_limiter."""

    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


@pytest.fixture
def clock(monkeypatch: pytest.MonkeyPatch) -> FakeClock:
    fake = FakeClock()
    monkeypatch.setattr(
        rl, "time", SimpleNamespace(monotonic=fake.monotonic, sleep=fake.sleep)
    )
    return fake


def test_defaults_come_from_settings(clock: FakeClock) -> None:
    limiter = RateLimiter()
    assert limiter.rate_limit == 4.0
    assert limiter.available_tokens == 4.0


def test_explicit_rate_limit_sets_capacity(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=2.0)
    assert limiter.rate_limit == 2.0
    assert limiter.get_stats()["bucket_capacity"] == 2.0


def test_capacity_is_at_least_one_token(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=0.5)
    assert limiter.get_stats()["bucket_capacity"] == 1.0


@pytest.mark.parametrize("bad", [0, 0.0, -1.0])
def test_non_positive_rate_limit_is_rejected(clock: FakeClock, bad: float) -> None:
    # Old code treated 0 as "unset" via `or`, silently using the settings value.
    with pytest.raises(ValueError, match="rate_limit"):
        RateLimiter(rate_limit=bad)


def test_burst_consumes_full_bucket_without_sleeping(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    for _ in range(4):
        limiter.acquire()
    assert clock.sleeps == []
    assert limiter.available_tokens == pytest.approx(0.0)
    assert limiter.total_requests == 4


def test_acquire_blocks_until_token_refills(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    for _ in range(4):
        limiter.acquire()

    limiter.acquire()

    assert clock.sleeps == [pytest.approx(0.25)]
    assert limiter.total_requests == 5


def test_acquire_waits_for_requested_token_count(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    for _ in range(4):
        limiter.acquire()

    limiter.acquire(tokens=2.0)

    assert clock.sleeps == [pytest.approx(0.5)]


def test_refill_is_proportional_to_elapsed_time(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    for _ in range(4):
        limiter.acquire()
    clock.now += 0.5

    assert limiter.try_acquire() is True
    assert limiter.try_acquire() is True
    assert limiter.try_acquire() is False


def test_refill_never_exceeds_capacity(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    limiter.acquire()
    clock.now += 60.0

    assert limiter.try_acquire(4.0) is True
    assert limiter.try_acquire() is False


def test_acquire_timeout_raises_with_retry_after(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    for _ in range(4):
        limiter.acquire()

    with pytest.raises(RateLimitExceededError) as info:
        limiter.acquire(timeout=0.1)

    assert info.value.retry_after == pytest.approx(0.25)
    assert info.value.max_rate == 4.0
    assert limiter.blocked_requests == 1
    assert clock.sleeps == []


def test_acquire_timeout_long_enough_succeeds(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    for _ in range(4):
        limiter.acquire()

    limiter.acquire(timeout=1.0)

    assert limiter.blocked_requests == 0
    assert limiter.total_requests == 5


@pytest.mark.parametrize("tokens", [0, -1])
def test_acquire_rejects_non_positive_tokens(clock: FakeClock, tokens: float) -> None:
    with pytest.raises(ValueError, match="positive"):
        RateLimiter().acquire(tokens=tokens)


def test_acquire_rejects_tokens_over_capacity(clock: FakeClock) -> None:
    with pytest.raises(ValueError, match="capacity"):
        RateLimiter(rate_limit=4.0).acquire(tokens=5)


def test_try_acquire_consumes_a_token(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=2.0)

    assert limiter.try_acquire() is True
    assert limiter.available_tokens == pytest.approx(1.0)
    assert limiter.total_requests == 1


def test_try_acquire_exhausts_bucket_then_fails(clock: FakeClock) -> None:
    # Old code never consumed, so this returned True forever.
    limiter = RateLimiter(rate_limit=2.0)

    results = [limiter.try_acquire() for _ in range(4)]

    assert results == [True, True, False, False]
    assert limiter.total_requests == 2
    assert clock.sleeps == []


def test_try_acquire_failure_keeps_refill_but_takes_nothing(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=2.0)
    limiter.acquire(tokens=2)
    clock.now += 0.25

    assert limiter.try_acquire() is False
    assert limiter.available_tokens == pytest.approx(0.5)  # 0.25s * 2 tokens/s
    assert limiter.get_stats()["total_requests"] == 1


def test_try_acquire_over_capacity_returns_false(clock: FakeClock) -> None:
    assert RateLimiter(rate_limit=2.0).try_acquire(3.0) is False


def test_try_acquire_rejects_non_positive(clock: FakeClock) -> None:
    with pytest.raises(ValueError):
        RateLimiter().try_acquire(0)


def test_try_acquire_and_acquire_share_one_bucket(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=2.0)
    assert limiter.try_acquire() is True
    limiter.acquire()
    assert limiter.try_acquire() is False


def test_acquire_multiple_batches_by_capacity(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)

    limiter.acquire_multiple(6)

    # 4 tokens immediately, then 2 more need 0.5s of refill.
    assert limiter.total_requests == 2
    assert clock.sleeps == [pytest.approx(0.5)]


def test_acquire_multiple_validates_arguments(clock: FakeClock) -> None:
    limiter = RateLimiter()
    with pytest.raises(ValueError, match="count"):
        limiter.acquire_multiple(0)
    with pytest.raises(ValueError, match="batch_size"):
        limiter.acquire_multiple(2, batch_size=0)


def test_current_rate_counts_only_last_second(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    limiter.acquire()
    clock.now += 0.6
    limiter.acquire()
    assert limiter.current_rate == 2

    clock.now += 0.5  # first request is now 1.1s old
    assert limiter.current_rate == 1

    clock.now += 2.0
    assert limiter.current_rate == 0


def test_stats_snapshot(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    limiter.acquire()
    limiter.acquire()

    assert limiter.get_stats() == {
        "rate_limit": 4.0,
        "current_rate": 2,
        "available_tokens": pytest.approx(2.0),
        "total_requests": 2,
        "blocked_requests": 0,
        "bucket_capacity": 4.0,
    }


def test_reset_restores_initial_state(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    for _ in range(4):
        limiter.acquire()
    with pytest.raises(RateLimitExceededError):
        limiter.acquire(timeout=0.01)

    limiter.reset()

    assert limiter.available_tokens == 4.0
    assert limiter.total_requests == 0
    assert limiter.blocked_requests == 0
    assert limiter.current_rate == 0


def test_repr_does_not_deadlock_and_shows_values(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=4.0)
    limiter.acquire()
    assert repr(limiter) == (
        "RateLimiter(rate_limit=4.0, available_tokens=3.00, current_rate=1.00)"
    )


def test_threads_never_overdraw_the_bucket(clock: FakeClock) -> None:
    limiter = RateLimiter(rate_limit=10.0)
    results: list[bool] = []

    def worker() -> None:
        results.append(limiter.try_acquire())

    threads = [threading.Thread(target=worker) for _ in range(30)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert results.count(True) == 10
    assert limiter.total_requests == 10
