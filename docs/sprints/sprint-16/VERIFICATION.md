# Sprint 16 Verification

The following checks were executed against the generated Sprint 16 package.

## Shared contracts package

```text
pytest -q
12 passed
```

Coverage includes:

- EventEnvelope correlation and UTC validation
- request/correlation middleware
- idempotency replay
- idempotency conflict
- sensitive-path idempotency exclusion
- bounded retry
- safe/non-safe mutation retry rules
- circuit breaker opening
- Ed25519 internal token audience/scope/correlation verification

## Shared package wheel

Built successfully with:

```text
python -m pip wheel . --no-deps --no-build-isolation
```

Generated:

```text
smartedu_contracts-0.1.0-py3-none-any.whl
```

The wheel is intentionally not committed into the Sprint ZIP; the reproducible
source package and PowerShell build script are included.

## Gateway regression

Sprint 11 Gateway was reconstructed, Sprint 16 Gateway files were overlaid, and
the combined test suite was run:

```text
17 passed
```

This includes the original Sprint 11 routing/security checks plus Sprint 16
context/idempotency checks.

## Frontend TypeScript

A merged frontend was reconstructed from:

```text
Sprint 12
Sprint 13
Sprint 14
Sprint 15
Sprint 16
```

Then:

```text
tsc --noEmit --pretty false
PASS
```

## Python syntax

All Python files in the Sprint 16 package compile successfully.

## Service bridge coverage

Sprint 16 includes additive `app/sprint16.py` bridges for all ten services:

```text
identity-service
academic-service
attendance-service
scheduling-service
notification-service
facility-service
learning-service
assessment-service
reporting-service
platform-service
```

## Contract schemas

All JSON contract/schema files parse successfully.

## Gateway-only browser architecture

Sprint 16 frontend source contains no direct references to service ports
`:8001` through `:8010`.

## Encoding

UTF-8 BOM scan:

```text
0 BOM files
```

## Mechanical wiring script

`scripts/apply_sprint16_wiring.py` was executed against a disposable FastAPI
service and successfully inserted:

```python
from app.sprint16 import install_sprint16
...
install_sprint16(app)
```

without duplicating the application definition.

## Not claimed as verified in this packaging runtime

The user's fully merged local repository is not available here. Identity,
Academic and Attendance were created outside this packaging runtime, and later
sprints may have modified several other service clients.

Therefore the following remain repository integration checks for Codex:

- install the shared package into every real service virtualenv/image
- wire every real `app/main.py`
- run all ten service regression suites
- migrate existing raw `httpx` dependency clients to the resilience wrapper
- migrate static internal tokens to signed service JWTs
- verify legacy-token removal
- adopt EventEnvelope adapters in actual outbox/inbox producers/consumers
- Redis multi-replica idempotency test
- frontend `npm run lint`
- frontend Vitest runtime
- frontend production build
- all Docker images
- Student E2E
- Teacher E2E
- Admin E2E
- full Gateway/CORS integration with live services

Those checks are explicitly required by `CODEX_MERGE_PROMPT.md` and
`SPRINT_16_INTEGRATION.md`.
