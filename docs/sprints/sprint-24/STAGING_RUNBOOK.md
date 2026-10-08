# Staging Operations Runbook

## Deployment failed before migrations

Do not proceed manually with application rollout.

Check:

```text
release manifest
Kubernetes context
required Secrets
private dependency connectivity
image pull/signature/registry access
```

Then rerun the same immutable release.

## Migration failed

1. stop the deployment attempt
2. inspect the failed Job logs
3. verify the Job used the correct service DB
4. verify Alembic head/history
5. determine whether the migration transaction rolled back
6. fix through a new release/migration when needed

Do not bypass a migration by marking the Job complete.

## Deployment failed after migrations

Database downgrade is not automatic.

Determine whether:

```text
old application image is compatible with new schema
forward fix is required
data repair is required
```

Use Sprint 22 rollback policy.

## Public TLS/Ingress failure

Check:

```text
DNS
load-balancer address
Ingress status
certificate Secret
Ingress controller logs
frontend/Gateway Services
NetworkPolicy
```

Do not expose domain service ports as a workaround.

## Pod crash loop

Check:

```text
container logs
events
secret/config names
read-only filesystem violations
dependency readiness
resource OOM/throttling
```

Fix required writable paths with bounded volumes rather than disabling all pod
security.

## QA fixture failure

Reset/reseed only positively identified staging QA resources.

Never use database-wide destructive commands without verifying the staging
target.

## RabbitMQ backlog

Use Sprint 21 runbooks.

Confirm:

```text
consumer count
consumer failures
dependency latency
retry/DLQ
outbox backlog
```

Do not delete queued events merely to make dashboards green.

## Recovery drill failure

Treat a failed restore as a release-readiness blocker until the backup or
restore process is corrected and re-tested.

## Emergency staging reset

A full staging reset may recreate:

```text
application namespace
service databases
Redis staging state
RabbitMQ staging vhost
staging buckets/prefixes
QA fixtures
```

but only through environment-specific reset tooling with explicit staging
confirmation.

Production endpoints and credentials must never appear in a staging reset
script.
