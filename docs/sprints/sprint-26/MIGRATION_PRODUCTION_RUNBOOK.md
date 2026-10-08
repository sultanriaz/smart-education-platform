# Production Migration Runbook

Database changes are one of the highest-risk parts of launch.

## Before migration

For every component in the release manifest's migration list confirm:

```text
migration reviewed
single Alembic head
service owns target DB
backup/PITR checkpoint exists
estimated duration known
lock/table-rewrite risk reviewed
backward compatibility understood
abort authority assigned
```

## Execution

Run migrations serially unless the actual reviewed migration set has a specific
reason to run concurrently.

Use the exact application release image.

The migration environment receives only the service's own database credentials.

## Long-running migrations

For migrations that may lock or rewrite large tables, establish:

```text
maintenance expectation
statement/lock timeout
progress observation method
abort threshold
forward-fix strategy
```

Do not discover a multi-hour table rewrite during go-live.

## Failure

If migration fails:

```text
stop application rollout
capture migration logs
determine transaction state
verify DB integrity
decide forward fix vs restore
```

Do not automatically call `alembic downgrade` in production.

## Post-migration

Verify:

```text
current revision == intended head
readiness
critical query behavior
DB locks/connections
error logs
```

Record the migration result as launch evidence.
