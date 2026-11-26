from __future__ import annotations

import json
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

try:
    from redis.asyncio import Redis
except ImportError:  # pragma: no cover - integration dependency
    Redis = None  # type: ignore[assignment]

from .settings import RedisSettings


class RedisCache:
    def __init__(self, client, *, prefix: str):
        self.client = client
        self.prefix = prefix.rstrip(":")

    @classmethod
    def from_settings(cls, settings: RedisSettings) -> RedisCache:
        if Redis is None:
            raise RuntimeError("redis package is required for RedisCache")
        client = Redis.from_url(
            settings.redis_cache_url,
            decode_responses=True,
            socket_timeout=settings.redis_socket_timeout_seconds,
            socket_connect_timeout=settings.redis_socket_timeout_seconds,
        )
        return cls(client, prefix=settings.redis_key_prefix)

    def key(self, namespace: str, value: str) -> str:
        return f"{self.prefix}:{namespace}:{value}"

    async def get_json(self, namespace: str, value: str) -> Any | None:
        raw = await self.client.get(self.key(namespace, value))
        return json.loads(raw) if raw is not None else None

    async def set_json(
        self,
        namespace: str,
        value: str,
        payload: Any,
        *,
        ttl_seconds: int,
    ) -> None:
        await self.client.set(
            self.key(namespace, value),
            json.dumps(payload, separators=(",", ":"), default=str),
            ex=ttl_seconds,
        )

    async def delete(self, namespace: str, value: str) -> None:
        await self.client.delete(self.key(namespace, value))

    @asynccontextmanager
    async def lock(
        self,
        namespace: str,
        value: str,
        *,
        timeout_seconds: int = 15,
        blocking_timeout_seconds: int = 2,
    ) -> AsyncIterator[None]:
        lock = self.client.lock(
            self.key(f"lock:{namespace}", value),
            timeout=timeout_seconds,
            blocking_timeout=blocking_timeout_seconds,
        )
        acquired = await lock.acquire()
        if not acquired:
            raise TimeoutError("Could not acquire Redis lock")
        try:
            yield
        finally:
            try:
                await lock.release()
            except Exception:
                pass
