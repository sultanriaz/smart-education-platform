from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True, slots=True)
class LockoutDecision:
    allowed: bool
    retry_after_seconds: int = 0
    failure_count: int = 0


class LockoutStore(Protocol):
    async def check(self, subject: str) -> LockoutDecision: ...
    async def failure(self, subject: str) -> LockoutDecision: ...
    async def success(self, subject: str) -> None: ...


class MemoryLockoutStore:
    def __init__(
        self,
        *,
        max_failures: int = 5,
        failure_window_seconds: int = 900,
        lock_seconds: int = 900,
        clock=time.monotonic,
    ):
        self.max_failures = max_failures
        self.failure_window_seconds = failure_window_seconds
        self.lock_seconds = lock_seconds
        self.clock = clock
        self._lock = asyncio.Lock()
        self._failures: dict[str, list[float]] = {}
        self._locked_until: dict[str, float] = {}

    def _normalize(self, subject: str) -> str:
        return subject.strip().casefold()

    def _cleanup_subject(self, subject: str, now: float) -> None:
        failures = [
            timestamp
            for timestamp in self._failures.get(subject, [])
            if now - timestamp <= self.failure_window_seconds
        ]
        if failures:
            self._failures[subject] = failures
        else:
            self._failures.pop(subject, None)

        if self._locked_until.get(subject, 0) <= now:
            self._locked_until.pop(subject, None)

    async def check(self, subject: str) -> LockoutDecision:
        subject = self._normalize(subject)
        async with self._lock:
            now = self.clock()
            self._cleanup_subject(subject, now)
            locked_until = self._locked_until.get(subject)
            failures = len(self._failures.get(subject, []))
            if locked_until and locked_until > now:
                return LockoutDecision(
                    allowed=False,
                    retry_after_seconds=max(1, int(locked_until - now)),
                    failure_count=failures,
                )
            return LockoutDecision(
                allowed=True,
                failure_count=failures,
            )

    async def failure(self, subject: str) -> LockoutDecision:
        subject = self._normalize(subject)
        async with self._lock:
            now = self.clock()
            self._cleanup_subject(subject, now)
            failures = self._failures.setdefault(subject, [])
            failures.append(now)

            if len(failures) >= self.max_failures:
                locked_until = now + self.lock_seconds
                self._locked_until[subject] = locked_until
                return LockoutDecision(
                    allowed=False,
                    retry_after_seconds=self.lock_seconds,
                    failure_count=len(failures),
                )

            return LockoutDecision(
                allowed=True,
                failure_count=len(failures),
            )

    async def success(self, subject: str) -> None:
        subject = self._normalize(subject)
        async with self._lock:
            self._failures.pop(subject, None)
            self._locked_until.pop(subject, None)


class RedisLockoutStore:
    def __init__(
        self,
        redis_client,
        *,
        namespace: str = "smartedu:auth-lockout",
        max_failures: int = 5,
        failure_window_seconds: int = 900,
        lock_seconds: int = 900,
    ):
        self.redis = redis_client
        self.namespace = namespace.rstrip(":")
        self.max_failures = max_failures
        self.failure_window_seconds = failure_window_seconds
        self.lock_seconds = lock_seconds

    def _subject_hash(self, subject: str) -> str:
        import hashlib

        return hashlib.sha256(subject.strip().casefold().encode()).hexdigest()

    def _failure_key(self, subject: str) -> str:
        return f"{self.namespace}:fail:{self._subject_hash(subject)}"

    def _lock_key(self, subject: str) -> str:
        return f"{self.namespace}:lock:{self._subject_hash(subject)}"

    async def check(self, subject: str) -> LockoutDecision:
        lock_key = self._lock_key(subject)
        ttl = await self.redis.ttl(lock_key)
        if ttl and ttl > 0:
            count_raw = await self.redis.get(self._failure_key(subject))
            count = int(count_raw or 0)
            return LockoutDecision(
                allowed=False,
                retry_after_seconds=int(ttl),
                failure_count=count,
            )

        count_raw = await self.redis.get(self._failure_key(subject))
        return LockoutDecision(
            allowed=True,
            failure_count=int(count_raw or 0),
        )

    async def failure(self, subject: str) -> LockoutDecision:
        key = self._failure_key(subject)
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.failure_window_seconds)
        count, _ = await pipe.execute()
        count = int(count)

        if count >= self.max_failures:
            await self.redis.set(
                self._lock_key(subject),
                "1",
                ex=self.lock_seconds,
            )
            return LockoutDecision(
                allowed=False,
                retry_after_seconds=self.lock_seconds,
                failure_count=count,
            )

        return LockoutDecision(
            allowed=True,
            failure_count=count,
        )

    async def success(self, subject: str) -> None:
        await self.redis.delete(
            self._failure_key(subject),
            self._lock_key(subject),
        )
