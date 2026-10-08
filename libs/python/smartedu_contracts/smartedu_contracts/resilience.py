from __future__ import annotations

import email.utils
import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime

import httpx

from .constants import (
    CAUSATION_ID_HEADER,
    CORRELATION_ID_HEADER,
    IDEMPOTENCY_KEY_HEADER,
    REQUEST_ID_HEADER,
    RETRYABLE_METHODS,
    RETRYABLE_STATUS_CODES,
    SERVICE_NAME_HEADER,
)
from .context import (
    get_causation_id,
    get_correlation_id,
    get_request_id,
)
from .service_auth import InternalTokenSigner


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 3
    backoff_seconds: float = 0.05
    max_backoff_seconds: float = 1.0
    retry_status_codes: frozenset[int] = RETRYABLE_STATUS_CODES


@dataclass(slots=True)
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_seconds: float = 15.0


class CircuitOpenError(RuntimeError):
    pass


class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig | None = None):
        self.config = config or CircuitBreakerConfig()
        self.failures = 0
        self.opened_at: float | None = None

    def before_call(self) -> None:
        if self.opened_at is None:
            return
        if time.monotonic() - self.opened_at >= self.config.recovery_seconds:
            self.failures = 0
            self.opened_at = None
            return
        raise CircuitOpenError("Downstream circuit is open")

    def success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def failure(self) -> None:
        self.failures += 1
        if self.failures >= self.config.failure_threshold:
            self.opened_at = time.monotonic()


def _retry_after_seconds(response: httpx.Response) -> float | None:
    raw = response.headers.get("Retry-After")
    if not raw:
        return None
    try:
        return max(0.0, float(raw))
    except ValueError:
        pass
    try:
        target = email.utils.parsedate_to_datetime(raw)
        if target.tzinfo is None:
            target = target.replace(tzinfo=UTC)
        return max(0.0, (target - datetime.now(UTC)).total_seconds())
    except Exception:
        return None


class ResilientHttpClient:
    def __init__(
        self,
        *,
        base_url: str,
        service_name: str,
        audience: str | None = None,
        token_signer: InternalTokenSigner | None = None,
        scopes: Iterable[str] = (),
        timeout_seconds: float = 3.0,
        retry_policy: RetryPolicy | None = None,
        circuit_breaker: CircuitBreaker | None = None,
        transport: httpx.BaseTransport | None = None,
        sleeper: Callable[[float], None] = time.sleep,
    ):
        self.base_url = base_url.rstrip("/")
        self.service_name = service_name
        self.audience = audience
        self.token_signer = token_signer
        self.scopes = tuple(scopes)
        self.retry_policy = retry_policy or RetryPolicy()
        self.circuit_breaker = circuit_breaker or CircuitBreaker()
        self.sleeper = sleeper
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout_seconds,
            transport=transport,
        )

    def close(self) -> None:
        self.client.close()

    def _headers(
        self,
        headers: dict[str, str] | None,
        *,
        idempotency_key: str | None,
    ) -> dict[str, str]:
        result = dict(headers or {})
        request_id = get_request_id()
        correlation_id = get_correlation_id()
        causation_id = get_causation_id()

        if request_id:
            result.setdefault(REQUEST_ID_HEADER, request_id)
        if correlation_id:
            result.setdefault(CORRELATION_ID_HEADER, correlation_id)
        if causation_id:
            result.setdefault(CAUSATION_ID_HEADER, causation_id)

        result.setdefault(SERVICE_NAME_HEADER, self.service_name)

        if idempotency_key:
            result.setdefault(IDEMPOTENCY_KEY_HEADER, idempotency_key)

        if self.token_signer and self.audience:
            token = self.token_signer.issue(
                audience=self.audience,
                scopes=self.scopes,
                correlation_id=correlation_id,
            )
            result["Authorization"] = f"Bearer {token}"
        return result

    def request(
        self,
        method: str,
        url: str,
        *,
        idempotency_key: str | None = None,
        headers: dict[str, str] | None = None,
        **kwargs,
    ) -> httpx.Response:
        method_upper = method.upper()
        can_retry = method_upper in RETRYABLE_METHODS or idempotency_key is not None

        self.circuit_breaker.before_call()
        attempts = self.retry_policy.max_attempts if can_retry else 1
        last_error: Exception | None = None

        for attempt in range(1, attempts + 1):
            try:
                response = self.client.request(
                    method_upper,
                    url,
                    headers=self._headers(
                        headers,
                        idempotency_key=idempotency_key,
                    ),
                    **kwargs,
                )
            except httpx.TransportError as exc:
                last_error = exc
                self.circuit_breaker.failure()
                if attempt >= attempts:
                    raise
                delay = min(
                    self.retry_policy.backoff_seconds * (2 ** (attempt - 1)),
                    self.retry_policy.max_backoff_seconds,
                )
                self.sleeper(delay)
                continue

            if response.status_code not in self.retry_policy.retry_status_codes:
                if response.status_code < 500:
                    self.circuit_breaker.success()
                else:
                    self.circuit_breaker.failure()
                return response

            self.circuit_breaker.failure()
            if attempt >= attempts:
                return response

            retry_after = _retry_after_seconds(response)
            delay = retry_after
            if delay is None:
                delay = min(
                    self.retry_policy.backoff_seconds * (2 ** (attempt - 1)),
                    self.retry_policy.max_backoff_seconds,
                )
            self.sleeper(delay)

        if last_error:
            raise last_error
        raise RuntimeError("Resilient request failed without response")
