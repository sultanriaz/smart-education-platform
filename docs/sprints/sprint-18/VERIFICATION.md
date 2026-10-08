# Sprint 18 Verification

The generated Sprint 18 package was verified in the packaging environment.

## Shared `smartedu-security` package

```text
pytest -q
23 passed
```

Coverage includes:

- strong/weak password policy
- one-time token hashing and expiry
- memory account lockout
- fixed-window rate limiting
- trusted Origin enforcement
- Secure/HttpOnly/SameSite refresh-cookie attributes
- filename sanitization
- upload size/extension/MIME checks
- PDF magic validation
- ClamAV response parsing
- security log redaction
- AES-GCM sensitive-event payload encryption/decryption

## Wheel build

Built successfully with:

```text
python -m pip wheel . --no-deps --no-build-isolation
```

Generated:

```text
smartedu_security-0.1.0-py3-none-any.whl
```

The wheel itself is not committed to the Sprint ZIP. Reproducible source and
PowerShell build/install scripts are included.

## Frontend TypeScript

A merged frontend was reconstructed from:

```text
Sprint 12
Sprint 13
Sprint 14
Sprint 15
Sprint 16
Sprint 18
```

Sprint 17 contains no frontend source changes.

Then:

```text
tsc --noEmit --pretty false
PASS
```

Verified routes:

```text
/forgot-password
/reset-password
/verify-email
/verify-email/request
```

Student, Teacher, and Admin routes remained present.

The Sprint 18 token store contains no `localStorage` or `sessionStorage`
persistence.

## Gateway regression

Sprint 11 Gateway + Sprint 16 hardening + Sprint 18 security controls were
reconstructed and tested:

```text
23 passed
```

This includes the original routing/internal-route tests plus Sprint 16 workflow
context and Sprint 18 auth-rate/security-header checks.

## Secret scan

```text
python scripts/secret_scan.py . --strict
PASS
```

No high-confidence secret findings were detected in the generated Sprint 18
package.

## Container static audit

```text
python scripts/container_security_audit.py . --strict
PASS
```

The Sprint 18 frontend Dockerfile has a non-root final runtime user.

The user's older service Dockerfiles are not available in this packaging
runtime and remain integration targets.

## Python syntax

All generated Python files compile successfully.

## Configuration

All generated JSON/YAML files parse successfully.

The hardened Sprint 17 infrastructure Compose still contains:

```text
infra-postgres
redis-cache
redis-durable
rabbitmq
minio
minio-bootstrap
```

Insecure default database/RabbitMQ/MinIO passwords were removed from Compose.

## Shell syntax

Passed `sh -n`:

```text
apps/frontend/docker/45-security-headers.sh
infra/minio/bootstrap-security.sh
infra/postgres/init/01-create-service-databases.sh
```

## Service bridge coverage

Sprint 18 includes additive `app/sprint18.py` bridges for all ten services:

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

## Wiring helper

`scripts/apply_sprint18_wiring.py` was run against a disposable FastAPI service.

It correctly inserted:

```python
from app.sprint18 import install_sprint18
...
install_sprint18(app)
```

without replacing the FastAPI application.

## Encoding

UTF-8 BOM scan:

```text
0 BOM files
```

## Not claimed as verified in this packaging runtime

Docker is unavailable here, and the user's fully merged local Sprints 1–17
repository is not available.

Therefore the following remain repository-integration checks:

- real Identity Alembic revision/upgrades
- real Sprint 1 User/Auth/Token/Audit adapters
- live login lockout against durable Redis
- live browser refresh-cookie rotation/revocation
- password reset end-to-end email flow
- email verification end-to-end flow
- Identity transactional encrypted outbox implementation
- Notification decrypt-and-email worker
- staged REQUIRE_EMAIL_VERIFICATION rollout
- live Gateway Nginx startup with new rate-limit variables
- frontend Vitest runtime
- frontend lint
- frontend production build
- frontend non-root Docker build/runtime
- all real service Dockerfiles converted to non-root
- live ClamAV scan
- Learning upload integration
- PostgreSQL cross-database denial using real service accounts
- MinIO least-privilege user bootstrap/cross-bucket denial
- RabbitMQ per-service credential bootstrap/permission tests
- Bandit
- pip-audit
- npm audit
- Trivy
- all ten service regression suites
- Student E2E
- Teacher E2E
- Admin E2E

These checks are mandatory in `SPRINT_18_INTEGRATION.md`,
`SECURITY_TEST_MATRIX.md`, and `CODEX_MERGE_PROMPT.md`.
