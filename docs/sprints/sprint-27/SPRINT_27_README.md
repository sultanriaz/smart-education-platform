# Sprint 27 — Production Deployment

Sprint 27 is the production launch execution layer for the Smart Education
Platform.

It consumes the exact Sprint 26 approved immutable release and provides guarded
production deployment, migration sequencing, rollback controls, production-safe
validation, launch evidence, and the Sprint 28 stabilization handoff.

## Launch flow

```text
Sprint 26 GO
        ↓
production-launch-preflight.py
        ↓
Sprint 23 render-k8s-release.py
        ↓
verify immutable production bundle
        ↓
render release migration Jobs
        ↓
apply foundation
        ↓
verify production Secrets
        ↓
required backup/PITR checkpoint
        ↓
run all release migrations
        ↓
wait for migration success
        ↓
deploy all 12 workloads
        ↓
wait for rollouts
        ↓
public HTTPS smoke
        ↓
production-safe role smoke
        ↓
production-safe event smoke
        ↓
observability validation
        ↓
monitoring snapshots
        ↓
launch record/report/evidence
```

## Safety guardrails

Production deployment requires:

```text
explicit PRODUCTION_DEPLOY confirmation
exact configured kubectl context
Sprint 26 readiness run
GO / GO_WITH_CONDITIONS
all readiness checks PASS
five readiness approvals
no blocking readiness risk
real HTTPS production URL
exact accepted release identity when supplied
pre-change backup/PITR hook
digest-pinned images
```

The deployment script never performs an automatic application or database
rollback.

## Migration safety

Only `migration_components` in `release-manifest.json` receive migration Jobs.

Jobs are rendered from:

```text
config/launch/components.yaml
```

The candidate command is:

```text
python -m alembic -c alembic.ini upgrade head
```

for backend services.

Codex must reconcile this against every real service image before launch.

Migration Jobs use the exact release image digest and service-owned Secret.

Application rollout begins only after every migration Job succeeds.

## Production backup contract

Set:

```text
PRODUCTION_BACKUP_SCRIPT
```

The script must create/verify the approved recovery point and print the resulting
backup/PITR reference on its final output line.

A failed backup stops the launch before migrations.

## Deployment command

After integration:

```powershell
$env:PRODUCTION_KUBE_CONTEXT = "<production-context>"
$env:SMARTEDU_PRODUCTION_URL = "https://<production-host>"
$env:PRODUCTION_BACKUP_SCRIPT = "<approved-backup-script>"

.\scripts\deploy-production-k8s.ps1 `
    -ReleaseManifest .\release-manifest.json `
    -ReadinessRun .\production-readiness-run.json `
    -Confirm PRODUCTION_DEPLOY
```

## Post-deployment validation

Environment-specific, production-safe hooks are required:

```text
PRODUCTION_ROLE_SMOKE_SCRIPT
PRODUCTION_EVENT_SMOKE_SCRIPT
PRODUCTION_OBSERVABILITY_CHECK_SCRIPT
```

Then:

```powershell
.\scripts\production-postdeploy-validation.ps1 `
    -LaunchRecord .\launch\current-launch.json `
    -Confirm PRODUCTION_SAFE_VALIDATION
```

These hooks must return non-zero when acceptance fails.

## Launch record

Sprint 27 records:

```text
preflight
backup
migrations
application rollout
public smoke
role smoke
event smoke
observability
incidents
backup reference
final outcome
```

A successful launch gate requires every mandatory phase PASS and outcome
`SUCCEEDED`.

## Rollback

Application-only rollback requires both:

```text
PRODUCTION_ROLLBACK
SCHEMA_COMPATIBLE
```

It deploys previous digest-pinned Deployment images.

It never runs a database downgrade.

## GitHub Actions

Two protected production workflows are included:

```text
.github/workflows/production-deploy.yml
.github/workflows/production-rollback.yml
```

Both use:

```text
environment: production
runs-on: [self-hosted, production]
```

Configure GitHub Environment approval/protection before enabling them.

## Scope boundary

Sprint 27 supplies production deployment execution tooling.

The package itself does not claim that a real production cluster was modified in
the generation environment.

A successful production launch exists only when the scripts/workflow execute
against the approved real production environment and the resulting launch gate
passes.
