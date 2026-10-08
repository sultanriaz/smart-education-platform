# Sprint 27 Production Deployment Execution

Sprint 27 executes the exact immutable release approved by Sprint 26.

The deployment sequence is intentionally conservative:

```text
Sprint 26 GO
   ↓
release/readiness preflight
   ↓
render + verify exact digest-pinned production bundle
   ↓
render + verify release migration Jobs
   ↓
apply foundation
   ↓
verify production Secrets
   ↓
create/confirm backup/PITR recovery point
   ↓
run migrations
   ↓
wait for every migration
   ↓
deploy 12 application workloads
   ↓
wait for all rollouts
   ↓
public HTTPS smoke
   ↓
Student/Teacher/Admin production-safe smoke
   ↓
representative event smoke
   ↓
observability/alert validation
   ↓
initial monitoring window
   ↓
launch record + evidence
```

## Hard guardrails

`deploy-production-k8s.ps1` requires:

```text
-Confirm PRODUCTION_DEPLOY
exact expected kubectl context
Sprint 26 readiness run
HTTPS production URL
backup/PITR hook
Sprint 23 immutable renderer
production bundle verification
migration bundle verification
```

The script refuses to continue when the configured Kubernetes context differs
from the active context.

## Backup contract

`PRODUCTION_BACKUP_SCRIPT` must:

1. create or verify the approved pre-change recovery point
2. exit non-zero on failure
3. print the backup/PITR reference on its final output line

If the backup hook fails, migrations do not start.

Provider-specific backup commands are intentionally not guessed by Sprint 27.

## Migrations

Only services listed in the release manifest's `migration_components` receive
migration Jobs.

Each Job:

```text
uses the exact release digest
uses the service's own Secret
uses the service's own migration command
backoffLimit=0
runs before application rollout
```

`config/launch/components.yaml` contains candidate Alembic commands. Codex must
reconcile those commands with the real images before production.

## Application rollout

The production application bundle remains:

```text
12 Deployments
12 ClusterIP Services
12 HPAs
12 PDBs
TLS Ingress
```

All workloads retain rolling updates and `maxUnavailable=0`.

## No automatic rollback

A failed deployment does **not** automatically trigger rollback.

Why:

```text
database schema compatibility may be unknown
an automatic rollback can worsen a migration/data incident
operators need the evidence needed to choose forward-fix vs app rollback vs restore
```

Application rollback is a separate approval-gated workflow.
