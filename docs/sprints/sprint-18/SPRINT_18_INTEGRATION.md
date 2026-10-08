# Sprint 18 Integration Checklist

Sprint 18 assumes Sprints 1–17 are merged.

## 1. Overlay files

Extract the Sprint ZIP at repository root.

## 2. Build/install shared package

```powershell
.\scripts\build-security-wheel.ps1
.\scripts\install-security-wheel.ps1
```

Add `smartedu-security` to all Python service images.

## 3. Wire service middleware

Run:

```powershell
python .\scripts\apply_sprint18_wiring.py .
```

Inspect every changed `app/main.py`.

All ten FastAPI services should call:

```python
install_sprint18(app)
```

Do not duplicate existing FastAPI app instances.

## 4. Identity migration

Read:

```text
IDENTITY_SECURITY_INTEGRATION.md
```

Create the real Alembic revision for:

```text
password_reset_tokens
email_verification_tokens
```

Use the actual Identity migration head.

Run migration upgrade/drift tests.

## 5. Identity account adapter

Implement `IdentityAccountAdapter` using the real Sprint 1:

```text
UserRepository
AuthService
TokenRepository
AuditRepository
```

Do not introduce a second User model or password hashing implementation.

Password writes must continue through the existing Argon2 path.

## 6. Registration policy

Apply Sprint 18 password validation to:

```text
public Student registration
Admin account provisioning with password
password reset
future password changes
```

Add regression tests for weak/strong passwords.

## 7. Login lockout

Wire `LoginSecurityHooks` around the real authentication flow.

Use:

```text
AUTH_SECURITY_REDIS_URL
```

against durable Redis, not volatile cache Redis.

Verify:

```text
failure count
lock
Retry-After
lock expiry
success clears failure counter
unknown-user failures follow same external behavior
```

## 8. Browser refresh cookies

Adapt existing login/refresh/logout endpoints.

Keep Sprint 1 refresh rotation/revocation logic.

Change browser transport only:

```text
refresh token -> HttpOnly cookie
access token -> JSON
```

The login/refresh JSON response must no longer expose `refresh_token`.

Production must use:

```text
REFRESH_COOKIE_SECURE=true
REFRESH_COOKIE_SAMESITE=strict
```

Refresh/logout require trusted Origin validation.

## 9. Frontend

Merge Sprint 18:

```text
token-store.ts
api-client.ts
AuthContext.tsx
auth-api.ts
security UX pages
LoginPage
RegisterPage
AppRouter
```

Verify:

```text
no auth tokens in localStorage
no auth tokens in sessionStorage
access token memory-only
reload bootstraps using refresh cookie
logout clears browser session
10-minute inactivity logout
```

## 10. Password reset and verification delivery

Generate security values:

```powershell
python .\scripts\generate_security_keys.py
```

Place them in secret storage.

Implement the Identity notification sink as a transactional outbox writer.

Use:

```python
encrypted_security_notification_data(...)
```

before persistence.

Notification Service must use:

```text
sprint18_security_events.py
```

to decrypt in memory.

Verify plaintext email/token pair is absent from:

```text
Identity token tables
Identity outbox payload
application logs
RabbitMQ payload
Notification persisted delivery record
```

## 11. Email verification rollout

Start with:

```text
REQUIRE_EMAIL_VERIFICATION=false
```

Decide/backfill the verification status of existing accounts according to the
institution's actual policy.

Then test and enable the policy in staging before production.

Do not blanket-lock existing accounts without an approved migration decision.

## 12. Gateway

Overlay:

```text
infra/gateway/templates/default.conf.template
infra/gateway/snippets/proxy_common.conf
infra/gateway/nginx.conf
docker-compose.gateway.yml
```

Verify strict zones for:

```text
login
refresh/logout
password recovery
email verification
```

Run all Gateway regression tests.

## 13. Frontend CSP

Merge:

```text
apps/frontend/docker/nginx.conf
apps/frontend/docker/45-security-headers.sh
apps/frontend/Dockerfile
docker-compose.frontend.yml
```

Test runtime CSP with the actual `API_BASE_URL`.

Production:

```text
ENABLE_HSTS=true
```

only after HTTPS is correctly deployed.

Verify SPA deep links still work.

## 14. Upload validation

Read:

```text
UPLOAD_SECURITY_INTEGRATION.md
```

Reconcile the actual Sprint 7 Learning upload implementation.

Preserve current authorization and object-storage ownership.

Add extension/MIME/size/magic checks.

When production scanning is required, configure ClamAV and fail closed.

## 15. Database permissions

Reconcile the Sprint 18 PostgreSQL init script with the current Sprint 17
infrastructure.

Test each service login:

```text
connect to own DB -> succeeds
connect to another service DB -> fails
```

Application users must not be PostgreSQL superusers.

## 16. Object-storage credentials

Use the least-privilege policies/users in:

```text
infra/minio/policies
infra/minio/bootstrap-security.sh
```

Replace application use of MinIO root credentials.

Verify cross-bucket denial.

## 17. RabbitMQ credentials

Set one password per service and run:

```powershell
python .\scripts\bootstrap_rabbitmq_security.py
```

Replace the shared application `smartedu` AMQP credential.

Keep bootstrap/management credentials outside application containers.

## 18. Container hardening

Use:

```text
infra/security/python.Dockerfile.pattern
infra/security/compose-service-hardening.example.yml
```

as the baseline.

Modify every real final runtime Dockerfile to run non-root.

Then:

```powershell
python .\scripts\container_security_audit.py . --strict
```

Do not blindly use a read-only root filesystem if a service genuinely requires
a writable path; explicitly mount only the needed volume/tmpfs.

## 19. Secrets

Merge `.gitignore.sprint18`.

Run:

```powershell
python .\scripts\secret_scan.py . --strict
```

Remove any real credentials from Git history as well as the working tree.

If a real secret was committed, rotate it; deletion from the latest commit alone
is not sufficient.

## 20. Dependency/static audit

Install/run:

```text
Bandit
pip-audit
npm audit
Trivy
```

The included CI workflow is a baseline. Reconcile it with the repository's
actual branch names and existing CI.

Do not auto-ignore high/critical findings merely to make the pipeline green.

## 21. Security-event logging

Use `redact_mapping(...)` or equivalent in structured logs.

Never log:

```text
Authorization
Cookie
Set-Cookie
password
refresh token
reset token
verification token
private key
security pepper
event-encryption key
```

## 22. Security test matrix

Run everything in:

```text
SECURITY_TEST_MATRIX.md
```

including RBAC regressions.

## 23. Full regression

Run all existing service suites:

```text
Identity
Academic
Attendance
Scheduling
Notification
Facility
Learning
Assessment
Reporting
Platform
Gateway
Frontend
```

Then:

```text
Student E2E
Teacher E2E
Admin E2E
```

## 24. Definition of done

Sprint 18 is merged only when:

- strong-password policy is server-enforced
- login lockout/rate limit is live
- reset/verification endpoints are live
- reset/verification tokens are single-use and expire
- reset revokes refresh sessions
- refresh token is HttpOnly cookie only
- browser storage contains no auth tokens
- Origin protection is verified
- 10-minute inactivity behavior works
- Gateway auth throttles pass
- CSP/security headers pass
- uploads enforce validation/scanning policy
- application containers run non-root
- DB/S3/RabbitMQ least privilege is verified
- security scans run in CI
- no real secrets are committed
- all RBAC and role E2E flows remain green
