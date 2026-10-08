from .bootstrap import install_platform_contracts
from .constants import (
    CAUSATION_ID_HEADER,
    CORRELATION_ID_HEADER,
    IDEMPOTENCY_KEY_HEADER,
    REQUEST_ID_HEADER,
    SERVICE_NAME_HEADER,
)
from .context import (
    ensure_correlation_id,
    get_causation_id,
    get_correlation_id,
    get_request_id,
)
from .errors import SmartEduError, error_payload
from .events import EventEnvelope, new_event
from .http import Page, PageMeta, page
from .idempotency import (
    IdempotencyMiddleware,
    MemoryIdempotencyStore,
    RedisIdempotencyStore,
)
from .resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitOpenError,
    ResilientHttpClient,
    RetryPolicy,
)
from .service_auth import (
    InternalPrincipal,
    InternalTokenSigner,
    InternalTokenVerifier,
    internal_auth_dependency,
)

__all__ = [
    "CAUSATION_ID_HEADER",
    "CORRELATION_ID_HEADER",
    "IDEMPOTENCY_KEY_HEADER",
    "REQUEST_ID_HEADER",
    "SERVICE_NAME_HEADER",
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitOpenError",
    "EventEnvelope",
    "IdempotencyMiddleware",
    "InternalPrincipal",
    "InternalTokenSigner",
    "InternalTokenVerifier",
    "MemoryIdempotencyStore",
    "Page",
    "PageMeta",
    "RedisIdempotencyStore",
    "ResilientHttpClient",
    "RetryPolicy",
    "SmartEduError",
    "ensure_correlation_id",
    "error_payload",
    "get_causation_id",
    "get_correlation_id",
    "get_request_id",
    "install_platform_contracts",
    "internal_auth_dependency",
    "new_event",
    "page",
]
