# Sprint 16 Adoption Matrix

The shared package and Gateway/frontend changes are implementation-complete in
this Sprint package. Service wiring must be merged into the actual service source
because Identity, Academic and Attendance were created outside this packaging
runtime and later sprints may have changed service entrypoints.

| Component | Sprint 16 change |
|---|---|
| API Gateway | request/correlation propagation, idempotency header, CORS exposure, structured context logging |
| Frontend | automatic per-mutation Idempotency-Key preserved across 401 refresh retry |
| All FastAPI services | `app/sprint16.py` bridge included |
| Shared Python | `smartedu-contracts` package included |
| HTTP | canonical error/page/retry/context contracts |
| Events | canonical EventEnvelope v1 + event catalog |
| Internal auth | Ed25519/EdDSA short-lived service JWT contract |
| Resilience | bounded retry + timeout + circuit breaker client |
| Idempotency | Memory and Redis stores + ASGI middleware |
| Ownership | canonical service ownership manifest |

## Mandatory service wiring

After overlaying Sprint 16, each FastAPI `app/main.py` needs:

```python
from app.sprint16 import install_sprint16

app = FastAPI(...)

install_sprint16(app)
```

The included `scripts/apply_sprint16_wiring.py` performs only this mechanical
edit and is safe to rerun. Codex must still inspect the result and run each
service's tests.

## Durable idempotency

Development may use the in-memory store.

Production refuses in-memory idempotency unless explicitly overridden. Configure:

```text
IDEMPOTENCY_REDIS_URL=redis://redis:6379/<db>
```

Use a separate logical namespace per service; the bridge already prefixes keys
with the service name.

## Existing domain errors

Do not delete domain-specific handlers merely to obtain the common error shape.
Migrate them intentionally so their status codes and domain codes remain stable.

## Existing static internal tokens

Do not remove static token support in one service before all callers have
migrated. Run a dual-acceptance migration, then disable static tokens in staging,
then production.
