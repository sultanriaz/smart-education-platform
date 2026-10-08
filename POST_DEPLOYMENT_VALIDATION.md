# Post-Deployment Validation

A successful Kubernetes rollout is not enough to call production launch
successful.

Sprint 27 requires four post-rollout validation phases.

## 1. Public smoke

Automated:

```text
frontend HTTPS
safe public Gateway health/smoke path
valid TLS path
```

Reconcile `/api/health` with the final Sprint 11/16 Gateway contract.

Do not expose `/internal` or `/metrics` publicly simply to make the smoke pass.

## 2. Role smoke

Production-safe Student, Teacher, and Admin smoke tests must use dedicated
production smoke identities and operations that cannot corrupt real academic
data.

Recommended minimal validation:

```text
Student: login, dashboard/read-only own context, logout
Teacher: login, assigned-context read-only check, logout
Admin: login, safe operational dashboard/read-only check, logout
```

Do not create a real attendance session, assessment grade, user role mutation,
or academic master-data mutation merely for launch smoke unless a carefully
designed canary workflow exists.

Sprint 27 calls an environment-specific `PRODUCTION_ROLE_SMOKE_SCRIPT`.

## 3. Event smoke

Use a production-safe canary event designed by the integrated platform.

It should prove selected:

```text
outbox publish
RabbitMQ delivery
consumer/inbox handling
Reporting/Notification projection where safe
```

Do not generate fake user notifications to real recipients.

Sprint 27 calls `PRODUCTION_EVENT_SMOKE_SCRIPT`.

## 4. Observability

Verify:

```text
all expected service targets
no critical alert
HTTP traces
event traces
normal broker/DB/Redis health
launch dashboards updating
```

Sprint 27 calls `PRODUCTION_OBSERVABILITY_CHECK_SCRIPT`.

All three environment-specific hooks must return non-zero on failure.

## Final launch gate

The production launch record requires PASS for:

```text
preflight
backup
migrations
application-rollout
public-smoke
role-smoke
event-smoke
observability
```

Only then may the launch outcome be set to `SUCCEEDED`.
