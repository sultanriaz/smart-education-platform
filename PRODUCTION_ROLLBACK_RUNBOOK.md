# Production Rollback Runbook

Rollback is application-only by default.

Sprint 27 never automatically runs `alembic downgrade`.

## Preconditions

Before application rollback:

```text
incident/abort reason identified
previous immutable release manifest selected
current schema compatibility with previous application reviewed
technical owner explicitly confirms SCHEMA_COMPATIBLE
production rollback approval obtained
```

Run:

```powershell
.\scripts\rollback-production-app.ps1 `
    -PreviousReleaseManifest .\previous-release-manifest.json `
    -CurrentReleaseManifest .\current-release-manifest.json `
    -Confirm PRODUCTION_ROLLBACK `
    -SchemaCompatibility SCHEMA_COMPATIBLE
```

## What the script does

It:

```text
renders previous digest-pinned production release
verifies production bundle
extracts Deployment objects only
applies previous Deployment images
waits for rollouts
```

It does not:

```text
downgrade database schema
delete user data
restore PostgreSQL automatically
change production Secrets
silence alerts
```

## When application rollback is unsafe

Do not use application rollback when:

```text
new schema is not backward compatible
a migration partially corrupted data
production data requires repair
old application would write invalid data to new schema
the incident is infrastructure/security rather than application release
```

Use forward-fix, data repair, PITR/restore, or infrastructure remediation as
appropriate.

## After rollback

Immediately run:

```text
public smoke
role smoke
event smoke
observability checks
DB/broker health review
```

Record the launch outcome as `ROLLED_BACK`, not `SUCCEEDED`.
