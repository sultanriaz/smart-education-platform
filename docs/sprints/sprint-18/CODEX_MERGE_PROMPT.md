Integrate Sprint 18 Security Hardening into the existing Smart Education
Platform.

FIRST inspect the actual merged Sprints 1–17. Preserve working contracts,
migrations, outbox/inbox reliability, RBAC, and domain boundaries.

Do not create a second authentication system just to fit Sprint 18 helper code.

1. Install shared security package

   Integrate:

   `libs/python/smartedu_security`

   Build/install it in all Python service environments and Docker images.

2. Wire security middleware

   All ten services have additive `app/sprint18.py`.

   Run:

   `python scripts/apply_sprint18_wiring.py .`

   Inspect every diff afterward.

   Preserve existing Sprint 16 request/correlation/idempotency middleware and
   Sprint 17 infrastructure wiring.

3. Identity is the highest-priority integration

   Read `IDENTITY_SECURITY_INTEGRATION.md` completely.

   Inspect the REAL Sprint 1:
   - User model/repository
   - AuthService
   - TokenRepository
   - Role/RBAC implementation
   - Security audit implementation
   - JWT/JWKS implementation
   - current Alembic head

   Integrate Sprint 18 around those existing components.

4. Identity Alembic

   Convert `sprint18_security_tables.sql` to a real Alembic revision.

   Add:
   - password_reset_tokens
   - email_verification_tokens

   Store token digests only.

   Run:
   - upgrade head
   - current
   - schema drift check
   - downgrade/round-trip where supported

5. Password policy

   Enforce server-side policy for:
   - Student registration
   - Admin-created initial passwords
   - password reset
   - any password-change endpoint found in repo

   Policy:
   - 12–128 chars
   - uppercase/lowercase/digit/symbol
   - reject common passwords
   - reject email/name inclusion

   Do not block login for valid legacy passwords solely because they do not meet
   the new creation policy.

6. Login lockout

   Wrap the existing login flow with `LoginSecurityHooks`.

   Use durable Redis.

   Default:
   - 5 failures
   - 15-minute window
   - 15-minute lock

   Keep invalid-credential responses generic for unknown/known accounts.

   Gateway IP rate limiting and account Redis lockout are both required.

7. HttpOnly refresh-token migration

   Preserve the existing Sprint 1 refresh-token rotation/revocation database
   logic.

   Change only browser transport:

   - access JWT -> JSON, memory-only frontend storage
   - refresh token -> HttpOnly SameSite=Strict cookie

   Login/refresh JSON must not expose refresh_token.

   Refresh/logout must validate trusted Origin.

   Production cookie must be Secure.

   Verify old rotated refresh tokens remain invalid.

8. Frontend auth

   Merge the Sprint 18 frontend files.

   Verify:
   - no access/refresh tokens in sessionStorage
   - no tokens in localStorage
   - refresh token cannot be read by JS
   - reload uses refresh cookie
   - logout clears/revokes session
   - 10-minute inactivity logs out
   - Student/Teacher/Admin routing still works

9. Password reset

   Integrate:
   - POST /api/v1/auth/password/forgot
   - POST /api/v1/auth/password/reset

   External Gateway namespace remains `/api/v1/identity/...`.

   Requirements:
   - generic forgot response
   - 30-minute default token TTL
   - digest-only Identity persistence
   - single use
   - strong new password
   - successful reset revokes all refresh tokens

10. Email verification

   Integrate:
   - POST /api/v1/auth/email/verification/request
   - POST /api/v1/auth/email/verification/confirm

   Do NOT enable mandatory verification before deciding how existing accounts
   are backfilled.

   Use staged rollout from `IDENTITY_SECURITY_INTEGRATION.md`.

11. Security notification events

   Use Sprint 17 transactional outbox.

   Identity must encrypt `{email, token}` BEFORE outbox persistence with:
   `encrypted_security_notification_data(...)`.

   Outbox/RabbitMQ must not contain plaintext token/email pair.

   Notification Service decrypts only in memory through:
   `sprint18_security_events.py`.

   Reset/verification links must use URL fragments:
   - /reset-password#token=...
   - /verify-email#token=...

   Never log decrypted values.

12. Security event key

   Generate secrets using:

   `python scripts/generate_security_keys.py`

   Store:
   - SECURITY_TOKEN_PEPPER
   - SECURITY_NOTIFICATION_ENCRYPTION_KEY

   in the deployment secret store only.

   Identity and Notification receive the event-encryption key.

13. Gateway

   Merge Sprint 18 Gateway templates and compose settings.

   Preserve Sprint 11/16 routing and internal-route blocking.

   Verify stricter edge zones for:
   - login
   - refresh/logout
   - recovery
   - email verification

   Keep credentialed CORS limited to the configured frontend origin.

   Run the entire Gateway suite.

14. CSP and security headers

   Merge the frontend Nginx/Docker changes.

   Validate the actual runtime API origin is in `connect-src`.

   Do not add `unsafe-inline` or `unsafe-eval` simply to make CSP errors disappear.

   Enable HSTS only on correctly deployed HTTPS production.

15. Upload security

   Read `UPLOAD_SECURITY_INTEGRATION.md`.

   Inspect Sprint 7 Learning upload code and any Sprint 10 import endpoints.

   Preserve authorization.

   Add:
   - filename sanitization
   - extension allowlist
   - MIME allowlist
   - size limit
   - magic validation
   - private object storage
   - malware scanning when required

   Production `MALWARE_SCAN_REQUIRED=true` should fail closed when scanner is
   unavailable.

16. Database least privilege

   Merge the tightened Sprint 17 PostgreSQL init logic.

   Test every service account:
   - own DB connect succeeds
   - another service DB connect fails
   - not superuser
   - no CREATEDB
   - no CREATEROLE

   Do not give services the postgres superuser password.

17. Object-storage least privilege

   Merge:
   - infra/minio/policies/*
   - bootstrap-security.sh
   - required Compose secrets

   Replace root credentials in Learning/Platform/Reporting application configs.

   Verify cross-bucket denial.

18. RabbitMQ least privilege

   Run/configure `bootstrap_rabbitmq_security.py`.

   Replace shared application broker credentials with one account per service.

   Keep bootstrap/admin credentials out of application containers.

19. Containers

   Modify EVERY actual final runtime Dockerfile.

   Target:
   - non-root
   - no embedded secrets
   - no-new-privileges
   - cap_drop ALL where compatible
   - read-only rootfs where compatible
   - tmpfs only for required writable temp paths

   Do not break file uploads/workers by making required paths unwritable.

   Run:
   `python scripts/container_security_audit.py . --strict`

20. Secrets

   Merge `.gitignore.sprint18`.

   Run:
   `python scripts/secret_scan.py . --strict`

   Search Git history if real credentials were previously committed.

   Rotate any exposed real credentials. Do not assume deleting the latest file
   makes a leaked secret safe.

21. Dependency/static security

   Reconcile `.github/workflows/security.yml` with the existing CI.

   Required checks:
   - secret scan
   - Bandit
   - pip-audit
   - npm audit high+
   - Trivy high/critical
   - smartedu-security tests
   - frontend tests

   Do not blanket-ignore vulnerabilities to make CI green.

22. Logging

   Search current logs/structured logging code.

   Apply `redact_mapping` or equivalent before serializing user-controlled or
   auth data.

   Never log:
   - password
   - Authorization
   - Cookie/Set-Cookie
   - access/refresh token
   - reset/verification token
   - private key
   - security pepper
   - encrypted security payload

23. Run `SECURITY_TEST_MATRIX.md`

   Include all RBAC regressions:
   - Student cannot Teacher/Admin APIs
   - Teacher cannot Admin APIs
   - no IN_PROGRESS assessment answer exposure
   - no Student answer keys
   - Teacher notifications remain section-only
   - Facility approval remains Admin-only

24. Full regression

   Run every service suite plus:
   - Gateway
   - frontend typecheck/lint/test/build
   - Docker builds
   - Student E2E
   - Teacher E2E
   - Admin E2E

25. Do not solve Sprint 18 by:
   - weakening password checks in backend
   - returning refresh tokens to JavaScript
   - storing tokens in localStorage/sessionStorage
   - disabling CORS/Origin validation
   - using wildcard credentialed CORS
   - disabling RBAC
   - exposing private buckets
   - giving every service DB/S3/RabbitMQ admin credentials
   - storing reset tokens in plaintext
   - logging security-event plaintext
   - committing private keys/passwords
   - disabling scanners just to pass CI

At completion report:
- Identity Alembic revision and tests
- password policy integration points
- lockout behavior/tests
- exact cookie flags and browser session behavior
- refresh-rotation regression
- reset/verification test totals
- security-event encryption/outbox implementation
- Gateway rate-limit/security tests
- CSP/header results
- upload validation/malware scanning integration
- per-service DB permissions
- S3 users/policies
- RabbitMQ users/permissions
- non-root Docker status per service
- secret/dependency/static scan results
- frontend results
- every service test total
- Student/Teacher/Admin E2E results
- any explicitly accepted security risk with reason
