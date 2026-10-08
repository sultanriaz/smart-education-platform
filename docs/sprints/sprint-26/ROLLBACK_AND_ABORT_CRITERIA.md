# Rollback and Abort Criteria

## Abort before rollout

Abort production launch when any of these occur:

```text
release digest/signature mismatch
backup/PITR checkpoint unavailable
migration target cannot be verified
critical dependency unhealthy
production secret missing/incorrect
DNS/TLS edge misconfiguration
readiness GO decision revoked
```

## Abort during migration

Stop when:

```text
migration fails
unexpected destructive/data-loss behavior appears
lock duration exceeds approved threshold
database enters unsafe/unhealthy state
wrong database target is detected
```

## Abort during application rollout

Stop when:

```text
sustained critical 5xx increase
authorization/privacy regression
data corruption
core role cannot log in/use platform
Attendance/Notification critical SRS regression
outbox/broker backlog grows without recovery
DB saturation/lock storm
unrecoverable crash loop across replicas
```

## Application rollback

Older application images may be redeployed only if the current schema is known
to be backward compatible.

Production rollback is:

```text
digest-pinned
explicit
observed
```

not `latest`.

## Database rollback

Automatic schema downgrade is prohibited by default.

Use one of:

```text
forward-fix migration
data repair
PITR/restore
explicitly tested reversible migration
```

based on incident analysis.

## Authority

The integrated project must name:

```text
deployment owner
migration owner
abort authority
operations incident lead
business/product decision owner
```

before launch.
