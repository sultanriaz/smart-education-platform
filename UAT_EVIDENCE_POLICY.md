# Sprint 25 UAT Evidence Policy

## Evidence structure

Recommended run directory:

```text
uat/evidence/<run-id>/
  release/
  student/
  teacher/
  admin/
  cross-role/
  accessibility/
  defects/
  automated/
  signoff/
```

## Acceptable evidence

Depending on the scenario:

```text
screenshot
short screen recording
Playwright trace/report
JUnit/pytest output
API response excerpt with secrets removed
performance report reference
observability dashboard export/reference
recovery drill report
defect ticket/reference
tester notes
```

## Evidence must identify

```text
release/run
scenario
time
tester or automated job
result
```

## Never store in evidence

```text
passwords
JWTs
refresh cookies
private keys
database passwords
RabbitMQ/Redis/S3 secrets
real personal data
production kubeconfig
```

Redact sensitive request headers before saving browser/network artifacts.

## Integrity

Do not modify evidence after sign-off without recording why.

When a scenario is retested on a new release, keep the old evidence and create
new evidence for the new release.

## CI artifacts

Automated evidence can be uploaded as CI artifacts with a bounded retention
period.

Human sign-off records should remain attached to the release/UAT record rather
than living only in ephemeral CI logs.
