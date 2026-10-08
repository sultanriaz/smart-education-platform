# Sprint 18 — Security Hardening

Sprint 18 hardens the Smart Education Platform across Identity, browser
sessions, Gateway controls, uploads, secrets, containers, dependencies, and
infrastructure permissions.

It builds on Sprints 1–17 and preserves the modular distributed architecture.

## 1. Shared security package

New package:

```text
libs/python/smartedu_security
```

It provides:

- password policy enforcement
- login lockout abstractions
- Redis-backed account lockout
- fixed-window rate limiting
- one-time token generation/digests
- trusted Origin checks
- HttpOnly refresh-cookie helpers
- strict request models
- upload metadata validation
- file magic validation
- filename sanitization
- optional ClamAV scanning
- sensitive log redaction
- AES-GCM protection for security-event payloads
- backend TrustedHost middleware

## 2. Password policy

New passwords use:

```text
12–128 characters
uppercase
lowercase
number
symbol
common-password rejection
email/name inclusion rejection
```

The policy applies to:

```text
registration
Admin-created initial passwords
password reset
future password-change flows
```

It does not reject a valid legacy credential at login merely because the password
predates Sprint 18.

## 3. Login brute-force protection

Default account-aware policy:

```text
5 failures / 15-minute window
15-minute lock
```

Gateway also applies IP-based rate limiting.

This creates two independent layers:

```text
client/IP edge throttle
        +
account-aware Redis lockout
```

Security events are recorded for failed/locked/successful authentication.

## 4. Password reset

New Identity APIs:

```text
POST /api/v1/auth/password/forgot
POST /api/v1/auth/password/reset
```

External Gateway paths:

```text
POST /api/v1/identity/auth/password/forgot
POST /api/v1/identity/auth/password/reset
```

Properties:

- enumeration-resistant forgot response
- cryptographically random 256-bit token
- only HMAC/SHA-256 digest stored in Identity DB
- 30-minute default expiry
- single-use semantics
- password policy enforced
- all refresh sessions revoked after successful reset
- reset link token travels in URL fragment instead of query string

## 5. Email verification

New APIs:

```text
POST /api/v1/auth/email/verification/request
POST /api/v1/auth/email/verification/confirm
```

Default token expiry:

```text
24 hours
```

The verification rollout is staged so existing Sprint 1 accounts are not
accidentally locked out.

## 6. Security notification events

Password-reset and verification delivery can use the Sprint 17 outbox/RabbitMQ
pipeline.

Sensitive values are AES-GCM encrypted before persistence.

Outbox event data contains:

```json
{
  "encrypted_payload": "<ciphertext>"
}
```

It must not contain plaintext:

```text
email
reset token
verification token
```

Notification Service decrypts only in memory when creating the email.

## 7. Browser token strategy

Sprint 12 originally stored access + refresh JWTs in sessionStorage.

Sprint 18 changes this.

Access token:

```text
memory only
```

Refresh token:

```text
Secure HttpOnly cookie
SameSite=Strict
Path=/api/v1/identity/auth
```

Browser JavaScript no longer reads or stores refresh tokens.

On browser reload:

```text
HttpOnly refresh cookie
        ↓
Identity refresh rotation
        ↓
new access token
        ↓
memory
```

The existing Sprint 1 database-backed refresh-token rotation/revocation remains
authoritative.

## 8. CSRF/origin protection

Refresh/logout use the cookie and therefore require a trusted browser `Origin`.

Missing/untrusted origins are rejected.

Credentialed CORS remains limited to the configured frontend origin.

## 9. 10-minute inactivity

The frontend now automatically logs an authenticated user out after ten minutes
without user interaction.

This implements the original SRS inactivity requirement.

Backend JWT expiry and RBAC remain authoritative independently of this UX timer.

## 10. Frontend security

New public pages:

```text
/forgot-password
/reset-password
/verify-email
/verify-email/request
```

Reset/verification token links use:

```text
#token=...
```

rather than:

```text
?token=...
```

The fragment is removed from browser history immediately after extraction.

## 11. Security headers

Frontend adds a runtime-generated CSP using the configured API origin.

Baseline:

```text
default-src 'self'
base-uri 'self'
frame-ancestors 'none'
object-src 'none'
form-action 'self'
script-src 'self'
style-src 'self'
connect-src 'self' <API_BASE_URL>
```

No `unsafe-inline` or `unsafe-eval` is introduced.

Other headers include:

```text
X-Content-Type-Options
X-Frame-Options
Referrer-Policy
Permissions-Policy
Cross-Origin-Opener-Policy
X-Permitted-Cross-Domain-Policies
X-DNS-Prefetch-Control
```

HSTS is generated only when explicitly enabled for HTTPS production.

## 12. Gateway high-risk rate limits

Sprint 18 adds dedicated rate-limit zones for:

```text
login
refresh/logout
password recovery
email verification
```

These are stricter than the general Identity namespace limit.

Sensitive auth responses also receive:

```text
Cache-Control: no-store
```

## 13. Upload hardening

New helpers validate:

```text
filename
extension
declared MIME
size
known file magic
dangerous executable extensions
```

An optional ClamAV INSTREAM client is included.

When:

```text
MALWARE_SCAN_REQUIRED=true
```

production upload integration should fail closed if content cannot be scanned.

## 14. Secrets

New secret scanner checks for:

```text
private-key blocks
AWS access keys
GitHub tokens
Slack tokens
generic password/secret/token assignments
high-entropy secret-like literals
```

Run:

```powershell
python .\scripts\secret_scan.py . --strict
```

Sprint 17 local infrastructure passwords are no longer embedded as Compose
defaults. Password variables must be explicitly supplied.

## 15. Static/dependency security

The included security workflow runs:

```text
secret scan
Bandit
pip-audit
npm audit
container static audit
Trivy filesystem scan
smartedu-security tests
frontend checks
```

## 16. Container hardening

Frontend runtime moves to an unprivileged Nginx image and port 8080.

Backend target pattern:

```text
non-root UID/GID
no-new-privileges
cap_drop: ALL
read-only root filesystem where compatible
tmpfs for /tmp
no embedded secrets
```

A container audit script flags missing/non-root USER directives and other common
issues.

## 17. PostgreSQL least privilege

Sprint 18 additionally:

```text
REVOKE CONNECT ON DATABASE <db> FROM PUBLIC
GRANT CONNECT only to owning service role
REVOKE ALL ON public schema FROM PUBLIC
```

This reinforces Sprint 17's database-per-service ownership.

## 18. S3 / MinIO least privilege

Application services no longer need MinIO root credentials.

Local policies:

```text
learning_svc
    learning-resources only

platform_svc
    platform-imports
    platform-exports

reporting_svc
    report-exports only
```

## 19. RabbitMQ least privilege

A bootstrap utility creates one application RabbitMQ account per service.

Shared broker admin/bootstrap credentials are not intended for application use
after Sprint 18.

## 20. Logging redaction

The security package includes recursive redaction for fields such as:

```text
Authorization
Cookie
Set-Cookie
password
access_token
refresh_token
reset/verification token
secret
private_key
encrypted_payload
```

Later observability code should apply the same rules.

## 21. Service bridges

All ten services receive:

```text
services/<service>/app/sprint18.py
```

Identity gets additional helpers for:

```text
login lockout
registration policy
browser cookie session adaptation
password reset
email verification
security event delivery
```

Because Sprint 1–3 were implemented in the user's local repository, Codex must
wire these helpers into the real service contracts rather than replacing the
working authentication/repository code.
