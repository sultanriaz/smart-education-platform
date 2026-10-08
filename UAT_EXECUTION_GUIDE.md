# Sprint 25 UAT Execution Guide

## 1. Confirm the immutable release

UAT must use the exact release that passed Sprint 24 staging acceptance.

Run:

```powershell
python .\scripts\uat-preflight.py `
    .\release-manifest.json `
    --staging-release-manifest .\staging-accepted-release.json `
    --staging-url https://<real-staging-or-uat-host>
```

The command fails when the release tag, commit, or image digests differ.

## 2. Validate the catalog

```powershell
python .\scripts\validate-uat-catalog.py
```

This checks:

```text
unique scenario IDs
known requirement references
non-empty steps
non-empty expected outcomes
requirement coverage
```

## 3. Generate tester scenario packs

```powershell
python .\scripts\generate-uat-scenario-packs.py
```

Generated worksheets are written to:

```text
uat/scenario-packs/
```

They are convenience documents. The structured JSON run record remains the
machine-readable source of truth.

## 4. Initialize a UAT run

```powershell
New-Item -ItemType Directory -Force .\uat-runs | Out-Null

python .\scripts\initialize-uat-run.py `
    .\release-manifest.json `
    --staging-url https://<real-staging-or-uat-host> `
    --output .\uat-runs\current.json
```

## 5. Execute a scenario

Read the corresponding role pack.

After execution record the result.

Example PASS:

```powershell
python .\scripts\record-uat-result.py `
    .\uat-runs\current.json `
    UAT-STU-001 `
    --status PASS `
    --executed-by "Student Representative" `
    --evidence "uat/evidence/<run-id>/student/UAT-STU-001-login.png"
```

Example FAIL:

```powershell
python .\scripts\record-uat-result.py `
    .\uat-runs\current.json `
    UAT-TCH-003 `
    --status FAIL `
    --executed-by "Teacher Representative" `
    --defect UAT-D-003 `
    --notes "Attendance finalization did not complete."
```

## 6. Record a defect

```powershell
python .\scripts\record-uat-defect.py `
    .\uat-runs\current.json `
    UAT-D-003 `
    --scenario-id UAT-TCH-003 `
    --severity MAJOR `
    --title "Teacher cannot finalize attendance" `
    --owner "Engineering"
```

Do not downgrade severity merely to satisfy the release gate.

## 7. Retest

When a defect is fixed, confirm whether the image digest changed.

If the candidate changed, treat it as a new immutable release candidate and
record fresh acceptance evidence for affected/regression scenarios.

Update defect state only after retest.

## 8. Record sign-offs

Example:

```powershell
python .\scripts\record-uat-signoff.py `
    .\uat-runs\current.json `
    --role StudentRepresentative `
    --signer "Representative Name" `
    --decision APPROVE
```

Repeat for:

```text
StudentRepresentative
TeacherRepresentative
AdminRepresentative
ProductOwner
ProjectSupervisor
```

## 9. Mark execution complete

```powershell
python .\scripts\complete-uat-run.py `
    .\uat-runs\current.json
```

## 10. Evaluate the gate

```powershell
python .\scripts\verify-uat-gate.py `
    .\uat-runs\current.json
```

Default acceptance requires:

```text
all P0 PASS
all P1 PASS
>=95% overall pass rate
0 open BLOCKER
0 open CRITICAL
0 open MAJOR
all required sign-offs present
no rejecting sign-off
```

## 11. Generate the final report

```powershell
python .\scripts\generate-uat-report.py `
    .\uat-runs\current.json `
    --output .\UAT_REPORT.generated.md
```

Generate requirement traceability:

```powershell
python .\scripts\generate-traceability-report.py `
    --output .\UAT_REQUIREMENTS_TRACEABILITY.generated.md
```

## 12. Archive evidence

Archive together:

```text
release-manifest.json
UAT run JSON
final UAT report
traceability report
tester scenario packs
evidence artifacts
defect references
sign-off evidence
Sprint 24 acceptance references
```

Do not archive secrets, cookies, JWTs, private keys, or kubeconfigs.
