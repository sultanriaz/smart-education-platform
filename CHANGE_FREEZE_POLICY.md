# Production Change Freeze Policy

## Purpose

The release candidate accepted by UAT and Sprint 26 must not drift during final
launch preparation.

## Freeze start

Recommended freeze begins when:

```text
Sprint 25 UAT passes
Sprint 26 readiness review starts
```

## Allowed changes

During freeze, changes require explicit review and should be limited to:

```text
release-blocking defect fixes
production configuration correction
security-critical remediation
launch/runbook correction
```

A code/image change creates a new release candidate.

## New candidate consequences

When image digests change:

```text
rebuild/sign/attest release
redeploy staging
rerun affected Sprint 24 checks
rerun affected UAT/regression
rerun Sprint 26 release identity checks
```

## Not allowed

Do not add unrelated features or refactors between UAT acceptance and launch.

## Freeze end

Freeze ends only after:

```text
launch stability window completes
or
GO decision is revoked
```

Sprint 28 can then manage post-launch change normalization.
