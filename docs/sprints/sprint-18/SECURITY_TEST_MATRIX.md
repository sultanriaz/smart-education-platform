# Sprint 18 Security Test Matrix

Use this matrix for staging security validation after the Sprint 18 merge.

## Authentication and account security

| Test | Expected |
|---|---|
| valid login | succeeds |
| invalid password | generic authentication failure |
| unknown email | same external failure shape as invalid password |
| 5 failed attempts inside window | account login lock applies |
| locked login | 429 + Retry-After |
| lock timeout expires | login can be attempted again |
| successful login after failures | failure counter cleared |
| weak new registration password | 422 |
| strong registration password | accepted |
| password containing email/name | rejected |
| password reset success | password changes |
| password reset success | all refresh sessions revoked |
| reset token second use | rejected |
| expired reset token | rejected |
| unknown forgot-password email | same 202 body as known email |
| known forgot-password email | same 202 body as unknown email |
| email verification token second use | rejected |
| expired verification token | rejected |
| already verified resend request | generic 202 response |

## Browser session

| Test | Expected |
|---|---|
| login response JSON | no refresh_token |
| login response Set-Cookie | HttpOnly |
| production refresh cookie | Secure |
| refresh cookie | SameSite=Strict |
| refresh cookie | Path=/api/v1/identity/auth |
| JavaScript token store | access token only in memory |
| sessionStorage/localStorage | no auth tokens |
| browser reload | refresh cookie obtains new access token |
| refresh rotation | new cookie replaces old refresh token |
| old rotated refresh token | rejected |
| logout | DB refresh token revoked |
| logout | refresh cookie deleted |
| missing Origin on refresh/logout | rejected |
| untrusted Origin on refresh/logout | rejected |
| 10 minutes browser inactivity | frontend logout executes |

## Authorization regression

Run every pre-Sprint-18 RBAC regression:

```text
Student cannot call Teacher/Admin endpoints
Teacher cannot call Admin endpoints
Teacher cannot inspect IN_PROGRESS Student assessment answers
Student cannot see assessment answer keys
Teacher notification campaigns remain section-only
Student/Teacher cannot approve Facility bookings
Admin routes remain backend-protected
```

Frontend route hiding alone never counts as authorization.

## Password recovery privacy

Inspect:

```text
response status
response body
timing distribution
logs
events
database records
```

Known and unknown account requests must not reveal account existence.

Identity tables contain only one-time-token digests.

Identity outbox must not contain plaintext reset/verification token/email pairs.

## Reset-link exposure

Generated links must be:

```text
/reset-password#token=...
/verify-email#token=...
```

not query-string tokens.

Verify:

- frontend Nginx access log does not contain token
- Gateway access log does not contain token
- browser history URL is scrubbed after page load
- token does not appear in Referer header

## Rate limiting

Verify both layers:

```text
Gateway IP throttling
Identity Redis account/request throttling
```

Exercise:

```text
login
refresh
forgot password
password reset
verification request
verification confirm
```

429 responses must include `Retry-After`.

## CORS / CSRF / origin

Verify:

```text
only configured frontend origin receives credentialed CORS
Origin: evil-site -> no credentialed CORS
cookie refresh from trusted origin -> succeeds
cookie refresh without trusted Origin -> rejected
internal service requests do not rely on browser cookies
```

Do not use `Access-Control-Allow-Origin: *` with credentials.

## Headers / CSP

Frontend responses should contain:

```text
Content-Security-Policy
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy
Permissions-Policy
Cross-Origin-Opener-Policy
X-Permitted-Cross-Domain-Policies: none
X-DNS-Prefetch-Control: off
```

Production HTTPS should also include:

```text
Strict-Transport-Security
```

CSP should not require `unsafe-inline` or `unsafe-eval`.

## Upload security

Try:

```text
allowed PDF
PDF extension with EXE magic
oversized file
.exe file
../ path filename
double-extension executable
invalid image magic
malware test sample in isolated staging scanner
scanner unavailable with MALWARE_SCAN_REQUIRED=true
unauthorized resource upload
unauthorized object download
```

Expected: fail closed for prohibited/unscanned content.

## Secrets

Run:

```powershell
python .\scripts\secret_scan.py . --strict
```

Verify no:

```text
private keys
real database passwords
RabbitMQ passwords
MinIO root credentials
JWT signing secrets
security peppers
security-event encryption keys
cloud access keys
```

exist in Git.

## Dependency and static analysis

CI must execute:

```text
Bandit
pip-audit
npm audit --audit-level=high
Trivy filesystem scan
secret scan
container static audit
```

Any accepted exception needs an explicit documented reason and expiry/review date.

## Containers

For each final runtime image verify:

```text
non-root user
no embedded secret ENV values
no writable source tree requirement
no unnecessary Linux capabilities
no-new-privileges where runtime permits
health endpoint still works
```

## PostgreSQL

For every application DB credential:

```text
can connect to owned DB
cannot connect to another service DB
not superuser
cannot create roles
cannot create databases
PUBLIC schema privileges revoked
```

Cross-service SQL remains prohibited.

## S3 / MinIO

Verify:

```text
learning_svc cannot access platform-imports
platform_svc cannot access learning-resources
reporting_svc cannot access learning-resources
anonymous bucket access denied
application services do not use MinIO root credential
```

## RabbitMQ

Verify each service uses its own credential.

An application credential should not:

```text
access management-admin functions
read another service queue
configure arbitrary resources
```

## Security-event encryption

Inspect Identity outbox and RabbitMQ payload:

```text
email plaintext absent
one-time token plaintext absent
encrypted_payload present
```

Notification decrypts only in memory.

A wrong encryption key must fail delivery rather than emit malformed reset links.

## Logging

Search logs after security tests.

The following must be absent:

```text
password
Authorization bearer token
Cookie / Set-Cookie value
refresh token
reset token
verification token
security notification encryption key
private signing key
```

Request/correlation IDs should remain present.

## Recovery and operational safety

Verify security controls do not break:

```text
database restore
RabbitMQ retry/DLQ
Redis idempotency
service health checks
Student E2E
Teacher E2E
Admin E2E
```
