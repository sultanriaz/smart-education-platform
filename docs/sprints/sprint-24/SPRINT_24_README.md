# Sprint 24 — Staging Environment

Sprint 24 turns the Sprint 23 deployment architecture into a repeatable,
production-like staging environment.

The staging release flow is:

```text
Sprint 22 release tag
        ↓
release-manifest.json
        ↓
Sprint 24 staging renderer
        ↓
digest-pinned staging Kubernetes bundle
        ↓
foundation
        ↓
required secrets
        ↓
release migrations
        ↓
12 application workloads
        ↓
public smoke
        ↓
Sprint 19 contracts + E2E
        ↓
Sprint 20 performance smoke
        ↓
Sprint 21 observability
        ↓
failure/recovery drills
        ↓
promotion evidence
```

## Staging workload model

All 12 application workloads run with at least two replicas so staging can test:

```text
rolling updates
pod failure
multi-replica service behavior
distributed idempotency
database concurrency
shared Redis state
```

The exact HPA/resource values are intentionally smaller than production
candidates but preserve the architecture.

## Kubernetes resources

Generated staging source contains:

```text
12 Deployments
12 ClusterIP Services
12 HPAs
12 PDBs
10 migration Jobs
1 TLS Ingress
NetworkPolicies
ServiceAccounts
ConfigMap
Secret examples
```

Migration Jobs are included in a rendered release only when that component is in
Sprint 22's `migration_components`.

## Release immutability

Staging never needs a staging-only application image.

The renderer consumes the exact Sprint 22 digest:

```text
ghcr.io/.../<component>@sha256:...
```

so the candidate tested in staging can later be promoted without rebuilding.

## Data

Staging uses dedicated synthetic QA data.

The package includes:

```text
config/staging/fixture-plan.yaml
config/staging/qa-accounts.example.yaml
STAGING_DATA_POLICY.md
```

The actual merged repository seeder must use supported APIs/service-owned
commands and remain idempotent.

## Stateful dependencies

Staging requires production-like:

```text
PostgreSQL
Redis cache
Redis durable
RabbitMQ
object storage
observability
```

plus a sandbox/test email provider.

The specific managed/in-cluster products are environment-specific and must be
chosen during integration.

## Deployment

Set:

```text
STAGING_KUBE_CONTEXT
SMARTEDU_STAGING_URL
```

Then:

```powershell
.\scripts\deploy-staging-k8s.ps1 `
    -ReleaseManifest .\release-manifest.json
```

The script:

1. validates the kubectl context
2. refuses production-looking contexts
3. runs staging preflight
4. renders digest-pinned manifests
5. verifies the bundle
6. applies foundation resources
7. verifies required Secrets
8. runs release migration Jobs
9. waits for successful migrations
10. deploys application resources
11. waits for all rollouts
12. runs a public smoke when URL is configured

## Acceptance

Run:

```powershell
.\scripts\run-staging-acceptance.ps1 `
    -ReleaseManifest .\release-manifest.json `
    -E2E `
    -PerformanceSmoke `
    -Observability
```

This reuses the QA/performance/observability tooling from Sprints 19–21.

## Failure drills

Pod failure:

```powershell
.\scripts\staging-pod-failure-drill.ps1 `
    -Component attendance-service
```

Rolling update:

```powershell
.\scripts\staging-rolling-update-drill.ps1 `
    -Component api-gateway
```

Node drain is intentionally guarded:

```powershell
.\scripts\staging-node-failure-drill.ps1 `
    -Confirm STAGING_ONLY
```

## Recovery drill

Provider-specific backup/restore commands are intentionally externalized:

```powershell
.\scripts\staging-backup-restore-drill.ps1 `
    -Mode DATABASE `
    -Confirm STAGING_ONLY
```

This prevents generated code from pretending it knows how a not-yet-selected
managed database product performs PITR.

## CI

`.github/workflows/staging-environment.yml` is a manually approved staging
environment workflow on a `self-hosted, staging` runner.

It downloads the Sprint 22 release manifest, verifies its checksum, deploys it,
runs acceptance gates, and uploads staging evidence.

It does not receive production cluster credentials.

## Promotion

Sprint 24 does not deploy production.

It creates evidence that the immutable release can move to Sprint 25 UAT and
Sprint 26 production-readiness review.
