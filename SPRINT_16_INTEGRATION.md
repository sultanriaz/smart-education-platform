# Sprint 16 Integration Checklist

## 1. Overlay the package

Extract Sprint 16 at repository root.

## 2. Install the shared Python package

For local virtual environments:

```powershell
.\scripts\build-contract-wheel.ps1
.\scripts\install-contract-wheel.ps1
```

For Docker, apply `infra/docker/SPRINT_16_DOCKER_PATTERN.md`.

Do not publish private service keys into images.

## 3. Wire every FastAPI service

Mechanical helper:

```powershell
python .\scripts\apply_sprint16_wiring.py .
```

Then inspect all ten `app/main.py` files and confirm:

```python
from app.sprint16 import install_sprint16

app = FastAPI(...)

install_sprint16(app)
```

Keep existing domain exception handlers where they preserve domain-specific
codes/status.

## 4. Configure idempotency

Local:

```text
MemoryIdempotencyStore
```

Staging/production:

```text
IDEMPOTENCY_REDIS_URL=redis://...
```

Verify two replicas return the original result for the same key/request and
`409 idempotency_conflict` for the same key/different payload.

## 5. Gateway

Overlay the Sprint 16 Nginx files.

Verify:

- CORS accepts Idempotency-Key and correlation headers.
- X-Request-ID is Gateway-generated.
- safe X-Correlation-ID is propagated.
- invalid correlation IDs fall back to Gateway request ID.
- Gateway 404/413/429/503 bodies include request_id + correlation_id.
- internal namespaces remain blocked.
- idempotency values are not logged.

## 6. Frontend

Keep the Sprint 16 `api-client.ts`.

Verify:

- GET has no Idempotency-Key.
- POST/PUT/PATCH/DELETE has one.
- 401 -> refresh -> retry preserves the same key.
- API errors expose requestId/correlationId for support diagnostics.
- Student, Teacher, and Admin E2E flows remain unchanged functionally.

## 7. Internal service keys

Generate local development key pairs:

```powershell
python .\scripts\generate_internal_service_keys.py
```

Merge `.gitignore.sprint16` entries into the actual `.gitignore`.

Never commit `*.private.pem`.

## 8. Migrate service-to-service HTTP clients

Use `ResilientHttpClient` rather than raw unbounded `httpx` calls where
appropriate.

Priority call graph:

```text
Attendance   -> Academic
Scheduling   -> Academic
Notification -> Identity
Notification -> Academic
Learning     -> Academic
Assessment   -> Academic
Facility     -> Notification
Platform     -> registered service health endpoints
```

For each call:

- finite timeout
- correlation propagation
- signed internal token
- target audience
- least-privilege scope
- bounded retry
- idempotency key for retryable mutations

Do not retry POST/PATCH without idempotency protection.

## 9. Migrate internal token verification

Use `contracts/security/service-scopes.yaml`.

During transition, dual-accept legacy static tokens only as necessary.

Before production, disable legacy static internal tokens.

## 10. Adopt EventEnvelope v1

Newly emitted cross-service events use the canonical envelope.

Existing event consumers may use compatibility adapters temporarily.

Verify:

- UTC occurred_at
- event_id deduplication
- event_version validation
- correlation propagation
- causation propagation
- event producer owns transaction/outbox semantics

Do not break existing outbox/inbox race protection.

## 11. Standardize errors incrementally

Gateway errors are already Sprint 16 shaped.

For each service, migrate domain handlers to:

```json
{
  "error": {
    "code": "...",
    "message": "...",
    "request_id": "...",
    "correlation_id": "...",
    "details": {}
  }
}
```

Preserve existing status codes/domain meanings.

## 12. Pagination

Do not break existing frontend endpoints just to change shape.

Use canonical Page contract for new endpoints and migrate old list endpoints only
with compatibility coverage.

## 13. Contract tests

Run:

```powershell
cd .\libs\python\smartedu_contracts
pytest -q

cd ..\..\..\infra\gateway
pytest -q
```

Also run:

```text
Identity tests
Academic tests
Attendance tests
Scheduling tests
Notification tests
Facility tests
Learning tests
Assessment tests
Reporting tests
Platform tests
Gateway tests
Frontend typecheck/lint/test/build
Student E2E
Teacher E2E
Admin E2E
```

## 14. Failure tests

At minimum verify:

- Academic unavailable -> dependent service fails quickly with 503, not hang.
- repeated dependency 503 -> circuit opens.
- recovery window -> circuit permits traffic again.
- POST without idempotency key is not automatically retried by internal client.
- POST with stable idempotency key can be retried safely.
- duplicate event_id does not repeat side effect.
- wrong internal JWT audience -> 401.
- missing internal scope -> 403.
- expired internal token -> 401.
- untrusted service signing key -> 401.
- malformed correlation ID -> Gateway generates a safe replacement.
- same Idempotency-Key with different payload -> 409.

## 15. Definition of done

Sprint 16 is merged only when:

- all ten services are wired
- shared library is in every Python service image
- Gateway headers/tests pass
- frontend idempotency tests pass
- internal service call graph uses bounded timeouts
- retry rules are documented/tested
- service-token migration is complete or explicitly tracked as a staging-only
  compatibility item
- event envelope adapters are verified
- no cross-service DB access exists
- Student/Teacher/Admin E2E remains green
