# Production Go-Live Runbook

Sprint 27 will execute this plan after Sprint 26 passes.

This file defines the production launch sequence; it does not itself perform the
deployment.

## T-1 day / freeze

Confirm:

```text
change freeze active
release tag/commit/digests locked
GO decision recorded
production DNS/TLS ready
production secrets ready
backup baseline ready
support/monitoring coverage scheduled
```

No unrelated code changes enter the release candidate after this checkpoint.

## T-60 minutes

Operations:

```text
open launch dashboard
confirm alert delivery
confirm stateful dependency health
confirm DB capacity/replication
confirm broker/Redis/object storage health
```

Technical lead:

```text
verify release manifest checksum/signatures
verify production rendered bundle
confirm migration component list
confirm migration owner and abort authority
```

Product owner:

```text
confirm maintenance/user communication
confirm support contacts
```

## T-30 minutes

Create/confirm the approved pre-change backup/PITR recovery point.

Record:

```text
backup identifier
timestamp
operator
provider status
```

If backup creation fails, abort the deployment.

## T-15 minutes

Run final production surface/infrastructure prechecks that are safe before
application rollout.

Do not modify production simply to make the precheck pass.

## Migration phase

For each migration-bearing service:

1. verify exact image digest
2. verify service-owned DB target
3. execute the approved migration
4. wait for completion
5. verify Alembic current/head
6. verify dependency health
7. stop immediately on failure

Do not run application rollback as an automatic database downgrade.

## Application rollout

Deploy the exact Sprint 26 approved release.

Recommended order should be reconciled with the real dependency topology, but
the default principle is:

```text
internal APIs/workers first as compatibility allows
API Gateway/frontend after backend readiness
```

All rollouts must respect readiness probes and `maxUnavailable=0`.

## Immediate verification

Run:

```text
public HTTPS smoke
Gateway/internal-route protection smoke
Student login/core smoke
Teacher login/core smoke
Admin login/core smoke
representative event flow
observability target check
```

## First 30 minutes

Watch:

```text
5xx rate
p95/p99 latency
Attendance latency
Notification event lag
DB connections/locks
Redis health
RabbitMQ backlog/DLQ
pod restarts/OOM
outbox backlog
critical alerts
```

## Abort / rollback

Use `ROLLBACK_AND_ABORT_CRITERIA.md`.

The person holding abort authority may stop rollout without waiting for a full
meeting when a predefined blocker occurs.

## T+2 hours

If stable:

```text
record launch status
record incidents/defects
confirm backup/monitoring continues
send stakeholder status
```

Sprint 28 then owns stabilization.
