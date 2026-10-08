# Staging Promotion Gate

Sprint 24 does not deploy production.

It produces evidence that a specific immutable release candidate is eligible to
enter Sprint 25 UAT / Sprint 26 production-readiness review.

## Required promotion evidence

```text
release tag
commit SHA
12 image digests
migration results
all Deployment rollout results
Student E2E
Teacher E2E
Admin E2E
contract/security results
event flow result
performance smoke result
observability result
pod failure result
rolling-update result
backup/restore result
open critical defects
```

## Blockers

Promotion is blocked by:

```text
failed migration
unavailable critical workload
data corruption/integrity failure
critical security regression
authorization bypass
internal API exposure
unresolved critical alert
failed backup/restore drill
release image/signature mismatch
```

## Exceptions

If a non-critical gate is exceptionally waived, record:

```text
owner
reason
risk
scope
compensating control
expiry/review date
```

Exceptions do not redefine the underlying requirement.

## Immutability

Do not rebuild images between successful staging acceptance and the next
promotion step.

Promote the same digest-pinned release candidate.
