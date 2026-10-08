from __future__ import annotations

REQUEST_ID_HEADER = "X-Request-ID"
CORRELATION_ID_HEADER = "X-Correlation-ID"
CAUSATION_ID_HEADER = "X-Causation-ID"
IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
SERVICE_NAME_HEADER = "X-Service-Name"
TRACEPARENT_HEADER = "traceparent"

MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
RETRYABLE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "PUT", "DELETE"})
RETRYABLE_STATUS_CODES = frozenset({429, 502, 503, 504})
