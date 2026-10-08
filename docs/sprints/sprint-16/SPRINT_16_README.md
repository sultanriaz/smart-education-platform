# Sprint 16 — Distributed Contract & Resilience Hardening

Sprint 16 hardens the boundaries created by Sprints 1–15. It does not add a new
business domain. It standardizes how independently deployable services identify
requests, call each other, retry safely, authenticate internally, publish
events, and evolve contracts.

## Deliverables

### 1. Shared Python contracts package

Location:

```text
libs/python/smartedu_contracts
```

Provides:

- request ID / correlation ID / causation ID context
- canonical error envelope helpers
- pagination contract
- EventEnvelope v1
- bounded resilient HTTP client
- timeout policy
- retry policy
- process-local circuit breaker
- Ed25519/EdDSA internal service JWTs
- FastAPI internal-auth dependency
- idempotency middleware
- in-memory idempotency store for development
- Redis idempotency store for multi-replica environments
- FastAPI installation helper

The package is cross-cutting infrastructure only. It contains no Academic,
Attendance, Facility, Assessment, or other domain ORM models.

### 2. Gateway hardening

Sprint 11 Gateway is extended to propagate:

```text
X-Request-ID
X-Correlation-ID
X-Causation-ID
Idempotency-Key
traceparent
```

Gateway-generated errors now carry both request and correlation IDs.

CORS allows the Sprint 16 workflow/idempotency headers.

Structured Gateway logs include:

- request ID
- correlation ID
- traceparent
- whether an idempotency key was present

The actual idempotency-key value is intentionally not logged.

### 3. Frontend mutation idempotency

The shared frontend API client now generates an `Idempotency-Key` for:

```text
POST
PUT
PATCH
DELETE
```

A token-refresh retry reuses the same key. Therefore a normal JSON mutation cannot
become a duplicate solely because the first request received a 401 and was retried
after refresh.

GET requests do not receive idempotency keys.

Sensitive Identity token endpoints (`login`, `refresh`, `logout`) are excluded so
access/refresh-token responses are not cached in an idempotency store. FormData
uploads are also excluded from automatic browser keys; callers may opt in with an
explicit stable key when the server is configured for the upload size.

### 4. Internal service authentication

A signed short-lived internal-token contract is provided.

Algorithm:

```text
EdDSA / Ed25519
```

Claims include:

```text
iss
sub
aud
iat
nbf
exp
jti
scope
token_type=service
correlation_id
```

Each service owns its private key. Other services receive public keys only.

This is separate from Identity's end-user JWT/JWKS contract.

### 5. Event contract

Canonical EventEnvelope v1:

```text
event_id
event_type
event_version
source
occurred_at
correlation_id
causation_id
actor_user_id
subject
data
metadata
```

Events use timezone-aware UTC timestamps.

Consumers deduplicate by `event_id`.

### 6. Service ownership contract

`contracts/service-ownership.yaml` explicitly records database/domain ownership.

Core rule:

```text
No service imports another service's ORM/repository.
No service queries another service database.
```

Reporting remains an event/API projection service rather than a cross-database
join service.

### 7. Resilience contract

Default service-to-service behavior:

```text
finite timeout
bounded retry
retry 429/502/503/504 and transport failures
circuit breaker
no blind retry of non-idempotent mutations
```

POST/PATCH retries require an Idempotency-Key.

### 8. Per-service bridges

Every service receives:

```text
services/<service>/app/sprint16.py
```

for all ten services:

- Identity
- Academic
- Attendance
- Scheduling
- Notification
- Facility
- Learning
- Assessment
- Reporting
- Platform

The bridge installs request context, standard error support, and idempotency,
and exposes internal token signer/verifier factories.

## Important migration behavior

Sprint 16 does not force-remove existing static internal service tokens in one
step.

The safe migration is:

1. add signed-token verification while temporarily accepting legacy token
2. migrate each caller to signed tokens + scopes
3. verify staging
4. disable legacy tokens
5. rotate/remove old static secrets

Likewise, existing domain error handlers should be migrated without changing
their HTTP semantics.

## Production idempotency

Development defaults to an in-memory store.

Production requires:

```text
IDEMPOTENCY_REDIS_URL
```

unless an explicit temporary override is provided.

This prevents a retry from reaching a different replica and executing the same
logical mutation twice.

## Source files intentionally not overwritten

Identity, Academic and Attendance were built outside this packaging runtime, and
later sprints modified Notification/Assessment routes.

Therefore Sprint 16 uses additive `app/sprint16.py` bridge files plus a mechanical
wiring script rather than replacing service `main.py` files blindly.

Run:

```powershell
python .\scripts\apply_sprint16_wiring.py .
```

Then inspect the diff and run every service test suite.
