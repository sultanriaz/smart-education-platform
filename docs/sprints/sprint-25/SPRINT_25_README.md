# Sprint 25 — User Acceptance Testing

Sprint 25 adds a formal UAT layer for the Smart Education Platform.

The sprint does not invent a new release candidate. It validates the exact
digest-pinned Sprint 22 release already deployed and accepted in Sprint 24.

## UAT scope

The formal catalog contains 40 scenarios:

```text
Student     10
Teacher     10
Admin       10
CrossRole   10
```

The scenarios cover:

```text
authentication/session
academic context
attendance
scheduling
notifications
facilities
learning resources
assessments
reporting
platform operations
RBAC/privacy
responsive behavior
accessibility/usability
performance evidence
availability/recovery evidence
```

## UAT toolkit

New package:

```text
libs/python/smartedu_uat
```

It provides:

```text
scenario models
run/result models
defect models
sign-off models
catalog loading
release-gate evaluation
run JSON persistence
```

## Default acceptance gate

```text
all P0 scenarios PASS
all P1 scenarios PASS
overall pass rate >= 95%
0 open BLOCKER
0 open CRITICAL
0 open MAJOR
StudentRepresentative sign-off
TeacherRepresentative sign-off
AdminRepresentative sign-off
ProductOwner sign-off
ProjectSupervisor sign-off
no REJECT sign-off
```

This is a project release policy.

Do not lower it during execution just to obtain a green result.

## Release preflight

UAT can compare the candidate release manifest to the manifest recorded by
Sprint 24.

```powershell
python .\scripts\uat-preflight.py `
    .\release-manifest.json `
    --staging-release-manifest .\staging-accepted-release.json `
    --staging-url https://<uat-host>
```

It verifies:

```text
HTTPS
non-placeholder hostname
full commit SHA
12 image components
digest-pinned images
release tag match
commit match
image digest match
```

## Execution record

Initialize:

```powershell
python .\scripts\initialize-uat-run.py `
    .\release-manifest.json `
    --staging-url https://<uat-host> `
    --output .\uat-runs\current.json
```

Record scenario results with:

```text
record-uat-result.py
```

Record defects with:

```text
record-uat-defect.py
```

Record stakeholder decisions with:

```text
record-uat-signoff.py
```

Evaluate:

```powershell
python .\scripts\verify-uat-gate.py `
    .\uat-runs\current.json
```

## Human scenario packs

Generate readable worksheets:

```powershell
python .\scripts\generate-uat-scenario-packs.py
```

The package also ships pre-generated role packs under:

```text
uat/scenario-packs/
```

## Traceability

Sprint 25 uses normalized requirement aliases because exact SRS requirement IDs
were not available to the package generator.

`config/uat/requirements.yaml` explicitly marks which source references must be
reconciled with the final SRS.

Generate:

```powershell
python .\scripts\generate-traceability-report.py `
    --output .\UAT_REQUIREMENTS_TRACEABILITY.generated.md
```

Codex must map aliases to actual final SRS IDs without inventing unsupported
requirements.

## Accessibility

The known SRS requires responsive desktop/mobile behavior.

Sprint 25 also includes a practical accessibility baseline for keyboard,
labels, accessible names, focus, errors, and assistive-technology smoke.

The exact formal accessibility standard must be reconciled with the final SRS;
Sprint 25 does not falsely claim the SRS mandates WCAG 2.2 AA unless the actual
document says so.

## CI

`.github/workflows/uat.yml` provides a manually triggered UAT precheck on the
staging runner.

It:

```text
downloads the Sprint 22 release manifest
verifies checksum
checks UAT catalog
verifies release/staging identity
optionally runs Sprint 19 E2E
initializes the UAT run
generates traceability
uploads automated evidence
```

Human UAT and human sign-off remain explicit; CI does not fabricate them.

## Handoff

A passing Sprint 25 release becomes eligible for:

```text
Sprint 26 — Production Readiness
```

It does not itself deploy production.
