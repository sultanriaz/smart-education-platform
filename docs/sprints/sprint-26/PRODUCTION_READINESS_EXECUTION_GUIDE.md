# Production Readiness Execution Guide

## 1. Confirm the release candidate

Use the exact Sprint 25 accepted release manifest.

```powershell
python .\scripts\compare-release-manifests.py `
    .\uat-accepted-release.json `
    .\production-candidate-release.json
```

Expected:

```text
exact_identity_match=true
```

## 2. Validate readiness configuration

```powershell
python .\scripts\validate-readiness-catalog.py
```

Generate a human worksheet:

```powershell
python .\scripts\generate-launch-checklist.py `
    --output .\PRODUCTION_READINESS_CHECKLIST.generated.md
```

## 3. Run production preflight

```powershell
python .\scripts\production-readiness-preflight.py `
    .\release-manifest.json `
    --uat-run .\uat-runs\accepted.json `
    --production-url https://<real-production-host> `
    --staging-release-manifest .\staging-accepted-release.json
```

## 4. Verify the rendered production bundle

```powershell
python .\scripts\verify-production-bundle.py `
    .\deploy\kubernetes\rendered-production.yaml
```

## 5. Initialize a readiness run

```powershell
New-Item -ItemType Directory -Force .\readiness-runs | Out-Null

python .\scripts\initialize-readiness-run.py `
    .\release-manifest.json `
    --production-url https://<real-production-host> `
    --output .\readiness-runs\current.json
```

## 6. Gather evidence

For each readiness check:

1. inspect the required evidence in `config/readiness/checks.yaml`
2. verify it belongs to the exact release/environment
3. copy/reference only non-secret evidence
4. record PASS only after verification

Example:

```powershell
python .\scripts\record-readiness-check.py `
    .\readiness-runs\current.json `
    PR-PERF-004 `
    --status PASS `
    --verified-by "Technical Lead" `
    --evidence "readiness/evidence/<run-id>/performance/srs-500-report.json"
```

## 7. Record risks

```powershell
python .\scripts\record-readiness-risk.py `
    .\readiness-runs\current.json `
    PR-RISK-001 `
    --title "Example risk" `
    --severity MEDIUM `
    --owner "Operations" `
    --mitigation "Concrete mitigation"
```

Default gate rejects open BLOCKER, CRITICAL, and HIGH risks.

## 8. Record approvals

```powershell
python .\scripts\record-readiness-approval.py `
    .\readiness-runs\current.json `
    --role OperationsOwner `
    --approver "Name" `
    --decision APPROVE
```

Repeat for all five required roles.

## 9. Record go/no-go decision

```powershell
python .\scripts\complete-readiness-run.py `
    .\readiness-runs\current.json `
    --decision GO `
    --notes "Approved for Sprint 27 production deployment."
```

## 10. Evaluate gate

```powershell
python .\scripts\verify-readiness-gate.py `
    .\readiness-runs\current.json
```

A non-zero exit means production deployment is not approved.

## 11. Hash evidence

```powershell
python .\scripts\generate-evidence-index.py `
    --root .\readiness\evidence `
    --output .\PRODUCTION_EVIDENCE_INDEX.generated.json
```

## 12. Generate report

```powershell
python .\scripts\generate-readiness-report.py `
    .\readiness-runs\current.json `
    --output .\PRODUCTION_READINESS_REPORT.generated.md
```

## 13. Sprint 27 handoff

Hand off only after the gate passes.

The handoff must include the exact release manifest, readiness run/report,
evidence index, migration/rollback runbooks, open accepted MEDIUM/LOW risks, and
launch ownership.
