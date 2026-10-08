from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    retry_after_seconds: int = 0


class MemoryFixedWindowLimiter:
    def __init__(self, *, limit: int, window_seconds: int, clock=time.monotonic):
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self._lock = asyncio.Lock()
        self._buckets: dict[str, tuple[int, float]] = {}

    async def hit(self, key: str) -> RateLimitDecision:
        async with self._lock:
            now = self.clock()
            count, expires = self._buckets.get(
                key,
                (0, now + self.window_seconds),
            )
            if now >= expires:
                count = 0
                expires = now + self.window_seconds

            count += 1
            self._buckets[key] = (count, expires)
            retry_after = max(1, int(expires - now))

            return RateLimitDecision(
                allowed=count <= self.limit,
                remaining=max(0, self.limit - count),
                retry_after_seconds=0 if count <= self.limit else retry_after,
            )


class RedisFixedWindowLimiter:
    def __init__(self, redis_client, *, namespace: str = "smartedu:rate"):
        self.redis = redis_client
        self.namespace = namespace.rstrip(":")

    async def hit(
        self,
        key: str,
        *,
        limit: int,
        window_seconds: int,
    ) -> RateLimitDecision:
        redis_key = f"{self.namespace}:{key}"
        pipe = self.redis.pipeline()
        pipe.incr(redis_key)
        pipe.ttl(redis_key)
        count, ttl = await pipe.execute()
        count = int(count)
        ttl = int(ttl)

        if count == 1 or ttl < 0:
            await self.redis.expire(redis_key, window_seconds)
            ttl = window_seconds

        return RateLimitDecision(
            allowed=count <= limit,
            remaining=max(0, limit - count),
            retry_after_seconds=0 if count <= limit else max(1, ttl),
        )
