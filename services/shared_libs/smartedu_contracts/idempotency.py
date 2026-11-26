from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import time
from dataclasses import dataclass
from enum import StrEnum
from typing import Protocol

from .constants import IDEMPOTENCY_KEY_HEADER, MUTATING_METHODS
from .context import get_correlation_id, get_request_id
from .errors import error_payload


class BeginState(StrEnum):
    NEW = "NEW"
    REPLAY = "REPLAY"
    CONFLICT = "CONFLICT"
    IN_PROGRESS = "IN_PROGRESS"


@dataclass(slots=True)
class StoredResponse:
    fingerprint: str
    status_code: int
    headers: list[tuple[bytes, bytes]]
    body: bytes


@dataclass(slots=True)
class BeginResult:
    state: BeginState
    response: StoredResponse | None = None


class IdempotencyStore(Protocol):
    async def begin(
        self,
        key: str,
        fingerprint: str,
        *,
        ttl_seconds: int,
        processing_ttl_seconds: int,
    ) -> BeginResult: ...

    async def complete(
        self,
        key: str,
        response: StoredResponse,
        *,
        ttl_seconds: int,
    ) -> None: ...

    async def abort(self, key: str) -> None: ...


class MemoryIdempotencyStore:
    def __init__(self):
        self._lock = asyncio.Lock()
        self._processing: dict[str, tuple[str, float]] = {}
        self._responses: dict[str, tuple[StoredResponse, float]] = {}

    def _cleanup(self) -> None:
        now = time.monotonic()
        self._processing = {key: value for key, value in self._processing.items() if value[1] > now}
        self._responses = {key: value for key, value in self._responses.items() if value[1] > now}

    async def begin(
        self,
        key: str,
        fingerprint: str,
        *,
        ttl_seconds: int,
        processing_ttl_seconds: int,
    ) -> BeginResult:
        async with self._lock:
            self._cleanup()

            replay = self._responses.get(key)
            if replay:
                stored, _expires = replay
                if stored.fingerprint != fingerprint:
                    return BeginResult(BeginState.CONFLICT)
                return BeginResult(BeginState.REPLAY, stored)

            processing = self._processing.get(key)
            if processing:
                existing_fingerprint, _expires = processing
                if existing_fingerprint != fingerprint:
                    return BeginResult(BeginState.CONFLICT)
                return BeginResult(BeginState.IN_PROGRESS)

            self._processing[key] = (
                fingerprint,
                time.monotonic() + processing_ttl_seconds,
            )
            return BeginResult(BeginState.NEW)

    async def complete(
        self,
        key: str,
        response: StoredResponse,
        *,
        ttl_seconds: int,
    ) -> None:
        async with self._lock:
            self._processing.pop(key, None)
            self._responses[key] = (
                response,
                time.monotonic() + ttl_seconds,
            )

    async def abort(self, key: str) -> None:
        async with self._lock:
            self._processing.pop(key, None)


class RedisIdempotencyStore:
    def __init__(self, redis_client, *, namespace: str = "smartedu:idempotency"):
        self.redis = redis_client
        self.namespace = namespace.rstrip(":")

    def _lock_key(self, key: str) -> str:
        return f"{self.namespace}:lock:{key}"

    def _response_key(self, key: str) -> str:
        return f"{self.namespace}:response:{key}"

    async def begin(
        self,
        key: str,
        fingerprint: str,
        *,
        ttl_seconds: int,
        processing_ttl_seconds: int,
    ) -> BeginResult:
        # One atomic decision prevents a completion between GET(response) and
        # SET(lock) from allowing the same operation to execute a second time.
        decision = await self.redis.eval(
            """
            local response = redis.call('GET', KEYS[1])
            if response then return {2, response} end
            local pending = redis.call('GET', KEYS[2])
            if pending then
                if pending == ARGV[1] then return {3} else return {4} end
            end
            redis.call('SET', KEYS[2], ARGV[1], 'EX', ARGV[2])
            return {1}
            """,
            2,
            self._response_key(key),
            self._lock_key(key),
            fingerprint,
            processing_ttl_seconds,
        )
        state = int(decision[0])
        if state == 2:
            raw_response = decision[1]
            data = json.loads(raw_response)
            stored = StoredResponse(
                fingerprint=data["fingerprint"],
                status_code=int(data["status_code"]),
                headers=[
                    (base64.b64decode(name), base64.b64decode(value))
                    for name, value in data["headers"]
                ],
                body=base64.b64decode(data["body"]),
            )
            if stored.fingerprint != fingerprint:
                return BeginResult(BeginState.CONFLICT)
            return BeginResult(BeginState.REPLAY, stored)

        if state == 1:
            return BeginResult(BeginState.NEW)
        if state == 4:
            return BeginResult(BeginState.CONFLICT)
        return BeginResult(BeginState.IN_PROGRESS)

    async def complete(
        self,
        key: str,
        response: StoredResponse,
        *,
        ttl_seconds: int,
    ) -> None:
        payload = {
            "fingerprint": response.fingerprint,
            "status_code": response.status_code,
            "headers": [
                [
                    base64.b64encode(name).decode(),
                    base64.b64encode(value).decode(),
                ]
                for name, value in response.headers
            ],
            "body": base64.b64encode(response.body).decode(),
        }
        pipe = self.redis.pipeline()
        pipe.set(
            self._response_key(key),
            json.dumps(payload),
            ex=ttl_seconds,
        )
        pipe.delete(self._lock_key(key))
        await pipe.execute()

    async def abort(self, key: str) -> None:
        await self.redis.delete(self._lock_key(key))


def _header(scope, name: str) -> str | None:
    target = name.lower().encode()
    for raw_name, raw_value in scope.get("headers", []):
        if raw_name.lower() == target:
            return raw_value.decode()
    return None


async def _read_body(receive, max_bytes: int) -> bytes:
    chunks: list[bytes] = []
    size = 0
    more = True
    while more:
        message = await receive()
        if message["type"] == "http.disconnect":
            raise ConnectionError("Request disconnected before its body completed")
        if message["type"] != "http.request":
            continue
        chunk = message.get("body", b"")
        size += len(chunk)
        if size > max_bytes:
            raise ValueError("Request body exceeds idempotency limit")
        chunks.append(chunk)
        more = bool(message.get("more_body", False))
    return b"".join(chunks)


def _fingerprint(scope, body: bytes) -> str:
    method = scope.get("method", "").upper()
    path = scope.get("path", "")
    query = scope.get("query_string", b"")
    digest = hashlib.sha256()
    digest.update(method.encode())
    digest.update(b"\0")
    digest.update(path.encode())
    digest.update(b"\0")
    digest.update(query)
    digest.update(b"\0")
    digest.update(body)
    return digest.hexdigest()


def _error_response(status_code: int, code: str, message: str) -> tuple[list, bytes]:
    payload = error_payload(
        code,
        message,
        request_id=get_request_id(),
        correlation_id=get_correlation_id(),
    )
    body = json.dumps(payload, separators=(",", ":")).encode()
    headers = [
        (b"content-type", b"application/json"),
        (b"content-length", str(len(body)).encode()),
    ]
    return headers, body


class IdempotencyMiddleware:
    def __init__(
        self,
        app,
        *,
        store: IdempotencyStore,
        ttl_seconds: int = 24 * 60 * 60,
        processing_ttl_seconds: int = 30,
        max_body_bytes: int = 2 * 1024 * 1024,
        excluded_path_prefixes: tuple[str, ...] = (),
    ):
        self.app = app
        self.store = store
        self.ttl_seconds = ttl_seconds
        self.processing_ttl_seconds = processing_ttl_seconds
        self.max_body_bytes = max_body_bytes
        self.excluded_path_prefixes = excluded_path_prefixes

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "").upper()
        path = scope.get("path", "")
        key = _header(scope, IDEMPOTENCY_KEY_HEADER)
        if (
            method not in MUTATING_METHODS
            or not key
            or any(path.startswith(prefix) for prefix in self.excluded_path_prefixes)
        ):
            await self.app(scope, receive, send)
            return

        key = key.strip()
        if not key or len(key) > 200:
            headers, body = _error_response(
                400,
                "invalid_idempotency_key",
                "Idempotency-Key must contain 1 to 200 characters",
            )
            await send(
                {
                    "type": "http.response.start",
                    "status": 400,
                    "headers": headers,
                }
            )
            await send({"type": "http.response.body", "body": body})
            return

        try:
            body = await _read_body(receive, self.max_body_bytes)
        except ConnectionError:
            return
        except ValueError:
            headers, response_body = _error_response(
                413,
                "idempotency_body_too_large",
                "Request body is too large for idempotency protection",
            )
            await send(
                {
                    "type": "http.response.start",
                    "status": 413,
                    "headers": headers,
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": response_body,
                }
            )
            return

        # Scope stored responses to the exact credential. Never trust unverified
        # JWT claims to select a private cached response.
        credential = _header(scope, "Authorization") or _header(scope, "Cookie") or "anonymous"
        effective_ttl = self.ttl_seconds
        if credential.lower().startswith("bearer "):
            # Unverified expiry can only shorten cache retention. Domain auth
            # still verifies the signature/issuer/roles on an original request.
            # An expired credential must pass through that auth again and may
            # never retrieve a previously authorized cached response.
            try:
                encoded = credential.split()[1].split(".")[1]
                claims = json.loads(base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)))
                expiry = claims.get("exp")
                if isinstance(expiry, (int, float)) and not isinstance(expiry, bool):
                    effective_ttl = min(effective_ttl, int(expiry - time.time()))
            except (IndexError, ValueError, TypeError, OverflowError):
                pass
            if effective_ttl <= 0:
                sent = False

                async def expired_receive():
                    nonlocal sent
                    if sent:
                        return {"type": "http.request", "body": b"", "more_body": False}
                    sent = True
                    return {"type": "http.request", "body": body, "more_body": False}

                await self.app(scope, expired_receive, send)
                return
        key = hashlib.sha256(f"{credential}\0{key}".encode()).hexdigest()
        fingerprint = _fingerprint(scope, body)
        result = await self.store.begin(
            key,
            fingerprint,
            ttl_seconds=effective_ttl,
            processing_ttl_seconds=self.processing_ttl_seconds,
        )

        if result.state == BeginState.CONFLICT:
            headers, response_body = _error_response(
                409,
                "idempotency_conflict",
                "This Idempotency-Key was already used for a different request",
            )
            await send(
                {
                    "type": "http.response.start",
                    "status": 409,
                    "headers": headers,
                }
            )
            await send({"type": "http.response.body", "body": response_body})
            return

        if result.state == BeginState.IN_PROGRESS:
            headers, response_body = _error_response(
                409,
                "idempotency_in_progress",
                "A request with this Idempotency-Key is still being processed",
            )
            headers.append((b"retry-after", b"1"))
            await send(
                {
                    "type": "http.response.start",
                    "status": 409,
                    "headers": headers,
                }
            )
            await send({"type": "http.response.body", "body": response_body})
            return

        if result.state == BeginState.REPLAY and result.response:
            replay = result.response
            headers = [
                (name, value)
                for name, value in replay.headers
                if name.lower() not in {b"content-length"}
            ]
            headers.append((b"content-length", str(len(replay.body)).encode()))
            headers.append((b"x-idempotent-replay", b"true"))
            await send(
                {
                    "type": "http.response.start",
                    "status": replay.status_code,
                    "headers": headers,
                }
            )
            await send(
                {
                    "type": "http.response.body",
                    "body": replay.body,
                }
            )
            return

        request_sent = False

        async def replay_receive():
            nonlocal request_sent
            if request_sent:
                return {"type": "http.request", "body": b"", "more_body": False}
            request_sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        response_start = None
        response_chunks: list[bytes] = []

        async def capture_send(message):
            nonlocal response_start
            if message["type"] == "http.response.start":
                response_start = message.copy()
            elif message["type"] == "http.response.body":
                response_chunks.append(message.get("body", b""))
            await send(message)

        try:
            await self.app(scope, replay_receive, capture_send)
        except Exception:
            await self.store.abort(key)
            raise

        if response_start is None:
            await self.store.abort(key)
            return

        status_code = int(response_start["status"])
        if status_code < 500:
            await self.store.complete(
                key,
                StoredResponse(
                    fingerprint=fingerprint,
                    status_code=status_code,
                    headers=list(response_start.get("headers", [])),
                    body=b"".join(response_chunks),
                ),
                ttl_seconds=effective_ttl,
            )
        else:
            await self.store.abort(key)
