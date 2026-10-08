# Sprint 25 Integration Checklist

Sprint 25 assumes Sprints 1–24 are merged.

## 1. Install UAT toolkit

```powershell
python -m pip install -e .\libs\python\smartedu_uat
```

Run:

```powershell
python .\scripts\validate-uat-catalog.py
python -m pytest -q .\libs\python\smartedu_uat\tests
python -m pytest -q .\tests\uat
```

## 2. Reconcile exact SRS requirement IDs

Read the real final SRS.

Inspect:

```text
config/uat/requirements.yaml
```

The package uses normalized aliases such as:

```text
REQ-ATTENDANCE
REQ-ASSESSMENT
REQ-PERF-GENERAL
```

Map them to the real SRS IDs if formal IDs exist.

Do not invent requirement IDs or change the SRS meaning.

If the final SRS does not support a requirement, mark it as project acceptance
scope rather than claiming it came from the SRS.

## 3. Reconcile final UAT scope

Review all 40 scenarios with the final merged product.

Update only where the real product contract requires it.

Preserve coverage of:

```text
Student
Teacher
Admin
RBAC/privacy
responsive behavior
recovery/performance evidence
```

## 4. Map automated references

For `hybrid` scenarios, add links/references to the real Sprint 19 E2E,
integration, security, performance, or observability test that supports the
scenario.

Do not turn manual usability acceptance into an automated-only result.

## 5. Exact release identity

Obtain the exact Sprint 22 release manifest accepted by Sprint 24.

Run:

```powershell
python .\scripts\uat-preflight.py `
    <candidate-release-manifest> `
    --staging-release-manifest <accepted-staging-release-manifest> `
    --staging-url https://<real-host>
```

The UAT candidate must match:

```text
release tag
commit SHA
all image digests
```

## 6. UAT environment

Use the accepted staging environment or an equivalent dedicated UAT environment.

Do not use production.

Verify:

```text
real HTTPS hostname
QA/UAT data only
QA/UAT accounts only
all 12 workloads
production-like service boundaries
```

## 7. QA/UAT fixtures

Reuse Sprint 24 deterministic fixtures.

Add only the minimum additional data needed for human acceptance.

Do not create data directly in another service's database.

## 8. UAT participants

Assign actual people to:

```text
Student Representative
Teacher Representative
Admin Representative
Product Owner
Project Supervisor
```

Keep participant names out of reusable project templates until execution.

## 9. Scenario packs

Generate:

```powershell
python .\scripts\generate-uat-scenario-packs.py
```

Review terminology with representative users before execution.

## 10. UAT run initialization

```powershell
python .\scripts\initialize-uat-run.py `
    <release-manifest> `
    --staging-url https://<real-host> `
    --output .\uat-runs\<run-id>.json
```

## 11. Automated precheck

Run:

```powershell
.\scripts\run-uat-automated.ps1 `
    -ReleaseManifest <release-manifest> `
    -StagingUrl https://<real-host> `
    -StagingReleaseManifest <accepted-staging-release-manifest> `
    -E2E
```

Do not consider automated precheck a human UAT sign-off.

## 12. Student acceptance

Execute all Student P0/P1 scenarios first.

Pay particular attention to:

```text
own-data privacy
assessment answer leakage
facility conflict behavior
protected resource download
logout/session behavior
responsive usability
```

## 13. Teacher acceptance

Execute all Teacher P0/P1 scenarios.

Pay particular attention to:

```text
assigned-section authorization
attendance finalize/correction
learning publication audience
assessment assignment/grading authorization
Admin operation denial
```

## 14. Admin acceptance

Execute all Admin P0/P1 scenarios.

Pay particular attention to:

```text
academic data integrity
user/role administration
schedule conflict prevention
report accuracy
public internal-route blocking
```

## 15. Cross-role acceptance

Execute:

```text
role isolation
cross-user privacy
inactivity/session behavior
availability evidence
recovery evidence
accessibility
responsive behavior
failure messaging
```

## 16. Accessibility/usability

Read:

```text
UAT_ACCESSIBILITY_USABILITY.md
```

Reconcile the formal accessibility standard with the real SRS/institution
requirements.

Do not label an accessibility defect cosmetic unless it truly has no usability
or accessibility impact.

## 17. Defects

Use:

```powershell
python .\scripts\record-uat-defect.py ...
```

Follow:

```text
UAT_DEFECT_POLICY.md
config/uat/defect-policy.yaml
```

Every FAIL should have clear observed-vs-expected notes and a defect when the
failure is a product issue.

## 18. Retest

A code/image change produces a new release candidate.

Do not retain old PASS evidence as if it were executed against a new image
digest.

Rerun directly affected and appropriate regression scenarios.

## 19. Evidence

Follow:

```text
UAT_EVIDENCE_POLICY.md
```

Do not capture:

```text
passwords
JWTs
refresh cookies
private keys
real personal data
```

## 20. Sign-offs

Record all five required decisions.

Use:

```powershell
python .\scripts\record-uat-signoff.py ...
```

Do not automate a human approval.

## 21. Gate

Complete the run:

```powershell
python .\scripts\complete-uat-run.py .\uat-runs\<run-id>.json
```

Evaluate:

```powershell
python .\scripts\verify-uat-gate.py .\uat-runs\<run-id>.json
```

A non-zero exit means the release is not accepted.

## 22. Report

Generate:

```powershell
python .\scripts\generate-uat-report.py `
    .\uat-runs\<run-id>.json `
    --output .\UAT_REPORT.generated.md
```

Generate traceability:

```powershell
python .\scripts\generate-traceability-report.py `
    --output .\UAT_REQUIREMENTS_TRACEABILITY.generated.md
```

## 23. Promotion decision

Complete:

```text
UAT_RELEASE_DECISION_TEMPLATE.md
```

The next-stage candidate must use the same accepted image digests.

## 24. Definition of done

Sprint 25 is complete only when:

- real SRS requirement mapping is reconciled
- exact staged release identity is verified
- all mandatory scenarios executed
- all P0 PASS
- all P1 PASS
- overall pass rate >=95%
- no open BLOCKER
- no open CRITICAL
- no open MAJOR
- Student representative signs off
- Teacher representative signs off
- Admin representative signs off
- Product Owner signs off
- Project Supervisor signs off
- UAT report generated
- requirement traceability generated
- evidence archived safely
- exact immutable release is approved for Sprint 26 readiness review
