# Sprint 26 — Production Readiness

Sprint 26 is the final go/no-go engineering and governance gate before the Smart
Education Platform is allowed to enter Sprint 27 production deployment.

It does **not** deploy production.

Its job is to prove that the exact Sprint 25 accepted release candidate has:

```text
immutable release identity
accepted UAT
production infrastructure
security
performance
observability
backup/recovery
migration/rollback plans
operational ownership
launch communications
formal approvals
```

## Readiness toolkit

New package:

```text
libs/python/smartedu_readiness
```

It provides:

```text
readiness check models
check-result records
risk register records
approval records
go/no-go decision records
readiness gate evaluation
structured JSON persistence
```

## Readiness catalog

Machine-readable source:

```text
config/readiness/checks.yaml
```

The generated catalog contains 59 mandatory checks grouped across:

```text
Release
UAT
Infrastructure
Data
Security
Performance
Reliability
Operations
Change
DisasterRecovery
Communications
FinalGate
```

## Default gate

The default policy requires:

```text
all mandatory checks PASS
mandatory waivers disabled

0 open BLOCKER risks
0 open CRITICAL risks
0 open HIGH risks

TechnicalLead approval
OperationsOwner approval
SecurityOwner approval
ProductOwner approval
ProjectSupervisor approval

final decision GO or GO_WITH_CONDITIONS
```

A `NO_GO` decision always fails the gate.

## Immutable release identity

The production candidate must still match the exact candidate accepted in
Sprint 25:

```text
release tag
commit SHA
12 application image digests
```

Use:

```powershell
python .\scripts\compare-release-manifests.py `
    .\accepted-uat-release.json `
    .\production-candidate-release.json
```

A digest difference means the release candidate changed.

## Production preflight

Use:

```powershell
python .\scripts\production-readiness-preflight.py `
    .\release-manifest.json `
    --uat-run .\uat-runs\accepted.json `
    --production-url https://<real-production-host> `
    --staging-release-manifest .\staging-accepted-release.json
```

This checks:

```text
HTTPS
non-placeholder production hostname
12 digest-pinned images
release/UAT tag and commit match
staging/production digest match when supplied
production topology placeholder protection when available
```

## Production deployment bundle

Sprint 23 should render the final bundle from the same release manifest.

Validate it:

```powershell
python .\scripts\verify-production-bundle.py `
    .\deploy\kubernetes\rendered-production.yaml
```

The verifier checks:

```text
12 Deployments
12 ClusterIP Services
12 HPAs
12 PDBs
digest-pinned images
>=2 replicas
RollingUpdate
maxUnavailable=0
probes
resource requests/limits
pod security
TLS Ingress
only frontend/API Gateway public
no placeholder secret values
```

## Live edge validation

When production DNS/TLS is provisioned but before application go-live:

```powershell
python .\scripts\check-production-surface.py `
    --url https://<real-production-host> `
    --gateway-path /api/health
```

Reconcile the Gateway health path with the actual merged Sprint 11/16 contract.

## Readiness execution

Initialize:

```powershell
python .\scripts\initialize-readiness-run.py `
    .\release-manifest.json `
    --production-url https://<real-production-host> `
    --output .\readiness-runs\current.json
```

Record checks:

```text
record-readiness-check.py
```

Record risks:

```text
record-readiness-risk.py
```

Record approvals:

```text
record-readiness-approval.py
```

Complete:

```text
complete-readiness-run.py
```

Evaluate:

```text
verify-readiness-gate.py
```

## Evidence

Create an evidence hash index:

```powershell
python .\scripts\generate-evidence-index.py `
    --root .\readiness\evidence `
    --output .\PRODUCTION_EVIDENCE_INDEX.generated.json
```

Generate the final report:

```powershell
python .\scripts\generate-readiness-report.py `
    .\readiness-runs\current.json `
    --output .\PRODUCTION_READINESS_REPORT.generated.md
```

## Important operational documents

```text
PRODUCTION_READINESS_PLAN.md
GO_NO_GO_PROCESS.md
GO_LIVE_RUNBOOK.md
MIGRATION_PRODUCTION_RUNBOOK.md
ROLLBACK_AND_ABORT_CRITERIA.md
OPERATIONS_OWNERSHIP.md
INCIDENT_RESPONSE_HANDOFF.md
PRODUCTION_SECRETS_DNS_TLS.md
CHANGE_FREEZE_POLICY.md
DR_RTO_RPO_DECISION.md
LAUNCH_COMMUNICATIONS.md
PRODUCTION_DATA_BOOTSTRAP.md
SPRINT_27_HANDOFF.md
```

## CI

`.github/workflows/production-readiness.yml` validates the readiness tooling and
downloads/verifies the immutable release manifest.

It intentionally does **not** deploy production.

Production deployment remains Sprint 27.
