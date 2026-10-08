# Sprint 18 Identity Security Integration

Sprint 18 intentionally does not replace Sprint 1's existing authentication
service. It wraps and extends the real implementation.

## 1. Alembic migration

Convert:

```text
services/identity-service/migrations/sprint18_security_tables.sql
```

into a normal Identity Alembic revision using the real current migration head.

Tables:

```text
password_reset_tokens
email_verification_tokens
```

Only SHA-256/HMAC token digests are stored.

Do not store reset/verification plaintext tokens in Identity tables.

## 2. Password policy

Apply `enforce_registration_password(...)` to:

- public Student registration
- Admin-created accounts when an initial password is accepted
- password reset
- any future change-password endpoint

The server policy is authoritative:

```text
minimum 12 characters
maximum 128 characters
uppercase
lowercase
number
symbol
reject common passwords
reject email identifier/name inclusion
```

Do not reject old passwords at login merely because they predate Sprint 18.

## 3. Login lockout

Wrap the existing AuthService login flow:

```python
hooks = LoginSecurityHooks(
    guard=LoginSecurityGuard(login_lockout_store()),
    audit=current_identity_audit_sink,
    settings=security_settings(),
)

await hooks.before_password_check(email)

try:
    user = existing_auth_service.authenticate(...)
except InvalidCredentials:
    await hooks.password_failed(email)
    raise

await hooks.password_succeeded(email, user.id)
```

Important:

- run the failure hook for nonexistent accounts too
- keep the external invalid-credentials message generic
- Gateway adds IP throttling
- Redis lockout adds account-aware throttling
- never log submitted passwords

Default lock:

```text
5 failures in 15 minutes
15-minute lock
```

## 4. HttpOnly refresh cookie

Keep the existing Sprint 1 refresh-token rotation/revocation database logic.

Only storage changes.

### Login

Existing AuthService returns an access/refresh pair internally.

Use:

```python
return hooks.browser_login_response(
    response,
    BrowserTokenPair(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        access_expires_in=...,
    ),
)
```

The JSON response must contain the access token only.

The refresh token is written as:

```text
HttpOnly
Secure in production
SameSite=Strict
Path=/api/v1/identity/auth
```

Never return `refresh_token` to browser JavaScript after Sprint 18.

### Refresh

Read the rotating refresh token with:

```python
refresh_token = hooks.browser_refresh_token(request)
```

Pass it into the existing Sprint 1 refresh flow.

After rotation:

```python
return hooks.browser_refresh_response(response, rotated_pair)
```

This sets the newly rotated refresh cookie.

### Logout

Read the cookie token, pass it to the existing Sprint 1 revocation logic, then:

```python
hooks.clear_browser_session(response)
```

Refresh and logout must require a trusted browser `Origin`.

Do not weaken Sprint 1 refresh rotation/revocation to adopt cookies.

## 5. Password recovery router

Build and include the Sprint 18 router under existing `/api/v1` routing:

```python
router.include_router(
    build_identity_security_router(
        get_db=get_db,
        account_adapter_factory=...,
        notification_sink_factory=...,
        audit_sink_factory=...,
        rate_limiter=identity_rate_limiter(),
        settings=security_settings(),
    )
)
```

Endpoints become:

```text
POST /api/v1/auth/password/forgot
POST /api/v1/auth/password/reset
POST /api/v1/auth/email/verification/request
POST /api/v1/auth/email/verification/confirm
```

Gateway exposes them as:

```text
/api/v1/identity/auth/...
```

Forgot/resend responses are intentionally enumeration-resistant.

## 6. Account adapter

Implement `IdentityAccountAdapter` using the real Sprint 1 repository/service.

It must:

```text
find user by email
read user by UUID
update password through the existing Argon2 hashing path
mark email verified
revoke all refresh sessions
```

Do not duplicate the User ORM model in Sprint 18.

## 7. Notification sink

Implement `IdentitySecurityNotificationSink` as an Identity transactional outbox
writer.

The notification sink must call:

```python
encrypted_security_notification_data(...)
```

before persisting event data.

Allowed outbox data:

```json
{
  "encrypted_payload": "<AES-GCM ciphertext>"
}
```

Forbidden outbox data:

```json
{
  "email": "student@example.edu",
  "token": "plaintext-token"
}
```

Event types:

```text
identity.password_reset.requested
identity.email_verification.requested
```

Notification Service uses:

```text
services/notification-service/app/sprint18_security_events.py
```

to decrypt only in memory and render the email.

Reset/verification URLs use fragments:

```text
/reset-password#token=...
/verify-email#token=...
```

The token therefore is not sent in the frontend HTTP request/access log.

## 8. Security event encryption key

Generate:

```powershell
python .\scripts\generate_security_keys.py
```

Store values in the secret manager:

```text
SECURITY_TOKEN_PEPPER
SECURITY_NOTIFICATION_ENCRYPTION_KEY
```

Identity and Notification both require the notification encryption key.

Do not put it in Platform settings, frontend config, Git, logs, or images.

## 9. Email verification rollout

Do not suddenly lock out pre-Sprint-18 accounts.

Recommended migration:

1. deploy verification columns/flows with `REQUIRE_EMAIL_VERIFICATION=false`
2. determine how existing institutional accounts should be considered verified
3. backfill only according to the institution's approved rule
4. test new registration -> verification
5. set `REQUIRE_EMAIL_VERIFICATION=true` in staging
6. verify Teacher/Admin provisioning behavior
7. enable in production

New public Student registrations should remain unverified until confirmation once
the policy is enabled.

## 10. Session inactivity

Frontend Sprint 18 logs an authenticated browser out after 10 minutes without
pointer/keyboard/scroll/touch activity, matching the original SRS requirement.

The backend must still enforce token expiry independently; frontend idle timeout
is not an authorization boundary.

## 11. Required Identity tests

Add tests for:

```text
registration weak-password rejection
strong-password registration
generic forgot-password response for existing and unknown email
reset token digest-only persistence
reset token expiry
reset token single use
password reset revokes all refresh sessions
email verification token expiry/single use
existing verified account resend behavior
login failure lockout
lockout expiry
successful login clears failure state
refresh cookie flags
no refresh token in JSON response
refresh cookie rotation
logout cookie deletion + DB revocation
untrusted/missing Origin on refresh/logout
Student/Teacher/Admin RBAC regression
```
