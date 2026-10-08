# Stabilization Hotfix Process

A production hotfix is a new immutable release.

It is not an in-place edit of the running container, ConfigMap, source tree, or
database.

## When a hotfix is justified

Examples:

```text
production regression
security issue
data-integrity issue
important operational defect
```

Avoid mixing unrelated feature work into a stabilization hotfix.

## Required path

1. create the smallest reviewed code/config change
2. run affected unit/integration/security tests
3. build new immutable images
4. generate SBOM/provenance/signatures through Sprint 22 pipeline
5. produce a new release manifest
6. verify migrations explicitly
7. run focused staging/regression as risk requires
8. obtain hotfix approvals
9. deploy through protected Sprint 27 production flow
10. monitor and link the new release to the stabilization issue

## Database hotfix

A database migration still follows service ownership.

Do not:

```text
manual cross-service SQL
edit production schema outside release tracking
use automatic downgrade as rollback
```

## Emergency does not mean invisible

An emergency may shorten review time, but should increase:

```text
operator attention
evidence collection
monitoring
post-incident review
```

not remove release identity and auditability.
