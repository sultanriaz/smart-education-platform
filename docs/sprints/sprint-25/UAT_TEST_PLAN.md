# Sprint 25 UAT Test Plan

## Entry criteria

Before UAT starts:

```text
Sprint 24 staging acceptance completed
exact release manifest available
real staging/UAT HTTPS hostname works
Student/Teacher/Admin QA accounts exist
deterministic QA fixtures exist
no unresolved staging BLOCKER/CRITICAL defect
latest security/QA/performance/observability evidence available
```

## Scenario groups

The catalog currently contains 40 formal scenarios.

Groups:

```text
Student     10
Teacher     10
Admin       10
CrossRole   10
```

The catalog validator reports the exact current counts and requirement coverage.

## Priority

```text
P0  release-critical acceptance/security/data-integrity workflow
P1  required important acceptance workflow
P2  useful but lower release risk
P3  optional/lower-risk scenario when present
```

Default policy requires every P0 and P1 scenario to PASS.

## Execution type

Scenarios may be:

```text
manual
automated
hybrid
```

`hybrid` is preferred for important workflows: automation proves repeatability
while a representative user still validates usability/terminology/outcome.

## Test data

Use only staging/UAT fixtures.

Do not use real student/employee records or production credentials.

Each role should have enough seeded data to exercise its flows without testers
editing databases directly.

## Execution order

Recommended:

```text
1. release/environment preflight
2. CrossRole security-critical P0 scenarios
3. Student P0/P1
4. Teacher P0/P1
5. Admin P0/P1
6. usability/accessibility
7. P2/P3
8. evidence review
9. defect retest
10. sign-off
11. gate evaluation
```

## Defects

Every failed scenario that represents a product defect should have a defect
record.

A scenario may remain BLOCKED for environment/test-data problems, but mandatory
blocked scenarios prevent acceptance unless project governance explicitly
changes the gate.

## Retest

After a fix:

1. deploy a new immutable release candidate
2. rerun the directly affected scenario
3. rerun related regression scenarios
4. update defect state
5. do not copy PASS evidence from the old release without rerunning it

If any image digest changes, the UAT release identity has changed.

## Exit criteria

UAT is complete only when:

```text
all required scenarios executed
defects classified
mandatory retests completed
required evidence stored
stakeholder decisions recorded
gate evaluated
final UAT report generated
```
