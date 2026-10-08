# Sprint 27 Integration Checklist

Sprint 27 assumes Sprints 1–26 are merged and Sprint 26 has a genuine GO or
GO_WITH_CONDITIONS decision.

## 1. Install launch toolkit

```powershell
python -m pip install -e .\libs\python\smartedu_launch
```

Also retain:

```text
smartedu_deploy
smartedu_readiness
```

from Sprints 23 and 26.

## 2. Confirm immutable release

Identify:

```text
release tag
commit SHA
12 image digests
```

from the exact Sprint 26 approved release.

Run:

```powershell
python .\scripts\compare-release-manifests.py `
    <accepted-release> `
    <production-candidate>
```

Must PASS.

## 3. Confirm readiness run

Run:

```powershell
python .\scripts\verify-readiness-gate.py `
    <production-readiness-run.json>
```

Do not deploy on a failing Sprint 26 gate.

## 4. Reconcile real production context

Set the exact context:

```text
PRODUCTION_KUBE_CONTEXT
```

`deploy-production-k8s.ps1` compares active context with expected context and
fails on mismatch.

Do not disable this guard.

## 5. Reconcile production URL

Set:

```text
SMARTEDU_PRODUCTION_URL
```

It must use the final HTTPS hostname and no placeholder domain.

## 6. Reconcile Sprint 23 renderer

Confirm:

```text
scripts/render-k8s-release.py
scripts/verify-k8s-bundle.py
config/deployment/production-topology.yaml
deploy/kubernetes/production
```

match the actual merged infrastructure.

## 7. Verify final production bundle

Run:

```powershell
python .\scripts\verify-production-bundle.py `
    .\deploy\kubernetes\rendered-production.yaml
```

Verify 12/12 workload digests manually/automatically against the release manifest.

## 8. Reconcile migration commands

Inspect every migration-bearing service image.

Update:

```text
config/launch/components.yaml
```

The generated Alembic command is a candidate only.

Check:

```text
working directory
alembic.ini path
module invocation
required env
read-only filesystem compatibility
migration timeout/lock behavior
```

## 9. Migration list

Compare the actual Sprint 22 release manifest:

```text
migration_components
```

to the real code/database changes.

Do not omit a service with a required migration.

Do not run unrelated migrations just because the service supports Alembic.

## 10. Production Secrets

Reconcile:

```text
production-secret-check.py
```

with the final production secret mechanism.

If frontend/Gateway do not need Secrets after Sprint 23 reconciliation, update
the required set and Deployment `envFrom` consistently.

Do not add dummy production Secrets merely to satisfy the checker.

## 11. Backup hook

Implement:

```text
PRODUCTION_BACKUP_SCRIPT
```

for the actual PostgreSQL/provider design.

The hook must:

```text
create/confirm approved pre-change recovery point
fail non-zero if unavailable
return backup/PITR identifier on final line
```

Test it safely before launch day.

## 12. Production foundation

Determine whether production Namespace, ServiceAccounts, ConfigMap,
NetworkPolicies, and Ingress foundation is pre-provisioned by infrastructure
automation.

Reconcile `split-production-bundle.py` and deployment sequencing accordingly.

Do not accidentally replace infrastructure-owned objects without review.

## 13. Deployment permissions

The production runner/identity should have only required Kubernetes permissions.

It must not use an unrestricted shared human cluster-admin kubeconfig.

## 14. GitHub production environment

Configure:

```text
environment: production
```

with required reviewers.

Configure a dedicated:

```text
self-hosted, production
```

runner or reconcile to the approved production automation environment.

## 15. Sprint 26 evidence asset

`production-deploy.yml` expects:

```text
release-manifest.json
production-readiness-run.json
SHA256SUMS
```

as approved release assets.

If your Sprint 26 evidence store uses another mechanism, reconcile the download
step without weakening release identity verification.

## 16. Verify supply chain

Before `kubectl apply`, verify Sprint 22:

```text
checksum
Cosign signatures
provenance/attestation
SBOM
vulnerability policy
```

Integrate signature verification into the production workflow if not already
done by the protected release promotion path.

## 17. Public smoke path

`config/launch/smoke.yaml` defaults Gateway smoke to:

```text
/api/health
```

Reconcile it with the final actual public Gateway health/safe smoke route.

Never expose `/internal` or `/metrics`.

## 18. Production-safe role smoke

Implement:

```text
PRODUCTION_ROLE_SMOKE_SCRIPT
```

Use dedicated smoke identities.

Avoid destructive write paths by default.

Verify safe:

```text
Student login/read/logout
Teacher login/assigned-context read/logout
Admin login/safe operational read/logout
```

## 19. Event smoke

Implement:

```text
PRODUCTION_EVENT_SMOKE_SCRIPT
```

Use a designed canary event that cannot affect real users/data incorrectly.

Verify appropriate outbox/broker/consumer behavior.

## 20. Observability hook

Implement:

```text
PRODUCTION_OBSERVABILITY_CHECK_SCRIPT
```

It should fail if:

```text
critical service targets missing
critical alert firing
broker/database health unsafe
telemetry pipeline clearly broken
```

## 21. Backup checkpoint

Before migrations, record:

```text
backup/PITR identifier
timestamp
operator
provider status
```

If unavailable: ABORT.

## 22. Execute migrations

Run production migration Jobs serially/under controlled orchestration.

The generated bundle may include multiple Jobs, but Codex/operations must ensure
the Kubernetes execution model does not violate reviewed ordering.

If strict serial ordering is required, update deployment automation to apply and
wait one Job at a time.

## 23. Migration failure

On failure:

```text
stop rollout
preserve logs/evidence
verify DB transaction/schema state
apply rollback/forward-fix/restore decision tree
```

Do not automatically downgrade.

## 24. Application rollout

Deploy exact digest-pinned resources.

Wait for all 12 Deployment rollouts.

Do not mark application-rollout PASS merely because `kubectl apply` returned 0.

## 25. Public smoke

Run:

```text
production-public-smoke.py
```

against final HTTPS URL.

## 26. Role/event/observability validation

Run:

```powershell
.\scripts\production-postdeploy-validation.ps1 `
    -LaunchRecord <record> `
    -Confirm PRODUCTION_SAFE_VALIDATION
```

All hooks must PASS.

## 27. Monitoring window

Use:

```text
PRODUCTION_LAUNCH_MONITORING.md
config/launch/monitoring-window.yaml
```

Capture Kubernetes monitoring snapshots.

Also monitor Sprint 21 dashboards.

## 28. Abort criteria

Review:

```text
config/launch/abort-criteria.yaml
Sprint 26 ROLLBACK_AND_ABORT_CRITERIA.md
```

Name the person with abort authority.

Do not wait for a committee meeting when a predefined critical abort condition
occurs.

## 29. Incidents

Record launch incidents with:

```text
record-launch-incident.py
```

An open SEV-1 prevents the final launch gate.

## 30. Application rollback

Only when schema compatibility is explicitly confirmed:

```powershell
.\scripts\rollback-production-app.ps1 `
    -PreviousReleaseManifest <previous> `
    -CurrentReleaseManifest <current> `
    -Confirm PRODUCTION_ROLLBACK `
    -SchemaCompatibility SCHEMA_COMPATIBLE
```

No database downgrade.

## 31. Failed rollback case

If old application is incompatible with the schema, use the approved:

```text
forward fix
data repair
PITR/restore
```

path instead.

## 32. Launch record

Do not finalize `SUCCEEDED` until:

```text
preflight PASS
backup PASS
migrations PASS
application-rollout PASS
public-smoke PASS
role-smoke PASS
event-smoke PASS
observability PASS
no open SEV-1
```

## 33. Generate evidence

Run:

```text
generate-launch-report.py
generate-launch-evidence-index.py
```

Review evidence for secrets before archival.

## 34. Workflow failure

`production-deploy.yml` captures Kubernetes state on workflow failure.

It deliberately does not auto-rollback.

Human/approved automation selects the correct recovery action.

## 35. Full production launch evidence

Archive:

```text
release manifest
readiness run reference
backup reference
migration status
rollout status
public smoke
role smoke
event smoke
observability result
monitoring snapshots
incident records
launch record/report/index
```

## 36. Sprint 28 handoff

Read:

```text
SPRINT_28_HANDOFF.md
```

Pass launch incidents/observations/conditions into stabilization.

## 37. Definition of done

Sprint 27 is complete only when:

- Sprint 26 gate genuinely passed
- exact release identity verified
- backup/PITR checkpoint succeeded
- all required production migrations succeeded
- all 12 workloads rolled out
- real HTTPS public smoke passed
- Student/Teacher/Admin safe smoke passed
- representative event smoke passed
- observability validation passed
- no open SEV-1
- launch outcome is SUCCEEDED
- production launch gate passes
- launch evidence/report/index archived
- Sprint 28 stabilization handoff is complete
