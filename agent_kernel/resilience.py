from __future__ import annotations

import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

from agent_kernel.contracts.budget import RetryPolicy
from agent_kernel.errors import TransientDependencyError

T = TypeVar("T")


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, reset_seconds: float = 30) -> None:
        self.failure_threshold = failure_threshold
        self.reset_seconds = reset_seconds
        self.failures = 0
        self.open_until = 0.0

    def allow(self) -> bool:
        if self.failures >= self.failure_threshold and time.monotonic() < self.open_until:
            return False
        if time.monotonic() >= self.open_until:
            self.failures = 0
        return True

    def record_success(self) -> None:
        self.failures = 0

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_threshold:
            self.open_until = time.monotonic() + self.reset_seconds


class Bulkhead:
    def __init__(self, limit: int) -> None:
        self._sem = asyncio.Semaphore(limit)

    def acquire(self) -> asyncio.Semaphore:
        return self._sem


async def retry_with_jitter(
    fn: Callable[[], Awaitable[T]],
    policy: RetryPolicy,
    *,
    safe_to_repeat: bool,
) -> T:
    last: Exception | None = None
    for attempt in range(1, policy.maximum_attempts + 1):
        try:
            return await fn()
        except TransientDependencyError as exc:
            last = exc
            if not safe_to_repeat or attempt >= policy.maximum_attempts:
                raise
            delay = policy.backoff_seconds * (2 ** (attempt - 1))
            if policy.jitter:
                delay *= 0.5 + random.random()
            await asyncio.sleep(delay)
    assert last is not None
    raise last
