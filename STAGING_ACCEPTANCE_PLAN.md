# Staging Acceptance Plan

A staging deployment is accepted only after the immutable release passes all
required gates.

## Gate 1 — Environment

Verify:

```text
correct staging kubectl context
smartedu-staging namespace
real staging hostname
TLS certificate valid
required Secrets present
private dependency connectivity
```

## Gate 2 — Migrations

Only services listed in the Sprint 22 release manifest's
`migration_components` run migration Jobs.

Each Job must:

```text
use the exact release image digest
run once for the release
complete successfully
use only its own DATABASE_URL
```

A migration failure blocks application promotion.

## Gate 3 — Application rollout

All 12 Deployments must become Available.

Check:

```text
desired replicas
ready replicas
restart count
readiness
liveness
HPA
PDB
Ingress
```

## Gate 4 — Public smoke

Verify:

```text
HTTPS works
frontend loads
Gateway public health/known public path works
HTTP redirects to HTTPS where configured
certificate hostname is correct
```

The final Gateway smoke route must be reconciled to the actual Sprint 11/16
Gateway contract.

## Gate 5 — Distributed contracts

Run Sprint 19 live contract/security checks.

At minimum:

```text
Gateway internal APIs blocked
role authorization
service readiness
event contracts
idempotency
failure behavior
```

## Gate 6 — Role E2E

Run complete:

```text
Student
Teacher
Admin
```

browser workflows from Sprint 19.

Do not shorten acceptance to login-only smoke tests.

## Gate 7 — Messaging/event flow

Prove representative paths:

```text
Attendance -> outbox -> Reporting
Assessment -> outbox -> Reporting
domain event -> Notification
retry/DLQ path
```

where supported by the merged platform.

## Gate 8 — Observability

Sprint 21 must show:

```text
10/10 service metric targets
structured logs
traces
event traces
no unresolved critical alert
```

## Gate 9 — Performance smoke

Run Sprint 20 `smoke`.

This does not replace the 500-user performance run, but prevents promotion of an
obviously degraded build.

Before production readiness, staging must also run the formal Sprint 20
acceptance profile on production-like capacity.

## Gate 10 — Failure drills

Run:

```text
pod deletion/recovery
rolling update
node drain where staging cluster topology permits it
```

No unacceptable user-visible outage should occur.

## Gate 11 — Recovery drills

Rehearse:

```text
PostgreSQL backup + isolated restore + integrity verification
object-storage backup/version restore + verification
release manifest redeploy
secret recovery/rotation
```

The generated recovery drill wrapper requires provider-specific scripts.

## Gate 12 — Security

Rerun Sprint 18 and container/supply-chain gates.

Staging acceptance fails on unresolved critical security regressions.

## Promotion decision

The release is promotable only when all required gates pass or a documented,
time-bounded release exception is approved.

A skipped mandatory gate is not automatically a pass.
