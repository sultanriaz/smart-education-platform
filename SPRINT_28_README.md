# Sprint 28 — Production Stabilization & Operational Closure

Sprint 28 is the final planned phase of the Smart Education Platform FYP
roadmap.

It begins only after Sprint 27 records a successful production launch.

The purpose is to prove that the live platform remains healthy under real
production conditions and can transition from launch mode to normal operations.

## What Sprint 28 adds

New package:

```text
libs/python/smartedu_stabilization
```

It provides:

```text
stabilization checkpoint models
issue and follow-up records
closure approvals
stabilization gate evaluation
structured run persistence
report generation
evidence indexing
```

## Formal stabilization gate

The generated catalog contains 49 mandatory checkpoints.

They cover:

```text
launch integrity
DNS/TLS/public exposure
12 application workloads
SRS latency targets
PostgreSQL
Redis
RabbitMQ/outbox/inbox
observability
security
identity
Student/Teacher/Admin workflows
data integrity/reporting
support
hotfix/change controls
recovery
operations ownership
formal closure
```

Default closure policy:

```text
49/49 mandatory checkpoints PASS
open SEV-1 = 0
open SEV-2 = 0
open SEV-3 = 0
all HIGH follow-ups CLOSED

TechnicalLead approval
OperationsOwner approval
SecurityOwner approval
ProductOwner approval
ProjectSupervisor approval

final disposition:
STABLE
or
STABLE_WITH_FOLLOWUPS
```

SEV-4 issues may remain when explicitly owned and documented.

## Recommended observation windows

The package provides baseline review windows:

```text
T+2 hours
T+24 hours
T+72 hours
closure review
```

These are project operating defaults, not SRS requirements.

Extend them when real traffic patterns require longer observation.

## Preflight

Before starting stabilization:

```powershell
python .\scripts\stabilization-preflight.py `
    .\release-manifest.json `
    --launch-record .\launch\current-launch.json `
    --production-url https://<production-host>
```

It requires:

```text
Sprint 27 outcome SUCCEEDED
all eight mandatory launch phases PASS
no open Sprint 27 SEV-1
same release tag/commit
12 digest-pinned images
same HTTPS production URL
```

## Live image drift check

Read-only verification:

```powershell
python .\scripts\verify-live-release-images.py `
    .\release-manifest.json `
    --context $env:PRODUCTION_KUBE_CONTEXT
```

This compares every live Deployment image to the release manifest's immutable
image reference.

## Stabilization run

Initialize:

```powershell
python .\scripts\initialize-stabilization-run.py `
    .\release-manifest.json `
    --launch-record .\launch\current-launch.json `
    --production-url https://<production-host> `
    --output .\stabilization-runs\current.json
```

Use:

```text
record-stabilization-checkpoint.py
record-stabilization-issue.py
record-stabilization-followup.py
record-stabilization-approval.py
complete-stabilization-run.py
verify-stabilization-gate.py
```

## Read-only production observation

Sprint 28 intentionally avoids automated production mutations.

The workflow:

```text
.github/workflows/production-stabilization.yml
```

uses:

```text
environment: production
runs-on: [self-hosted, production]
```

but its generated behavior is read-only.

It captures Kubernetes state and runs configurable observer hooks for:

```text
metrics
messaging
security
support
```

## Hotfixes

A hotfix is a new immutable release.

Do not patch running containers, manually alter application code in production,
or bypass the release pipeline.

Read:

```text
HOTFIX_PROCESS.md
```

## Final evidence

Generate:

```powershell
python .\scripts\generate-stabilization-report.py `
    .\stabilization-runs\current.json `
    --output .\stabilization\PRODUCTION_STABILIZATION_REPORT.md

python .\scripts\generate-stabilization-evidence-index.py `
    --root .\stabilization\evidence `
    --output .\stabilization\PRODUCTION_STABILIZATION_EVIDENCE_INDEX.json
```

## Closure

A passing Sprint 28 means the service is operationally owned and the current FYP
roadmap is complete.

Future product development should return to the normal release lifecycle rather
than bypassing the controls established by Sprints 18–28.
