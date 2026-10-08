# Sprint 25 UAT Charter

## Purpose

User Acceptance Testing validates that the Smart Education Platform is usable
and acceptable for its intended Student, Teacher, and Admin roles on the exact
immutable release candidate that passed Sprint 24 staging acceptance.

UAT is not a replacement for unit, integration, security, performance, or
staging validation. It answers a different question:

> Can representative users complete the intended business workflows correctly,
> safely, and understandably enough to accept this release candidate?

## Scope

The formal UAT catalog covers:

```text
Student
Teacher
Admin
Cross-role security/privacy
Responsive behavior
Accessibility baseline
Performance/recovery evidence review
```

The scenario catalog lives in:

```text
config/uat/scenarios/
```

## Release under test

UAT must use the exact Sprint 22 release manifest deployed and accepted in
Sprint 24.

Do not rebuild images for UAT.

The following must match:

```text
release tag
commit SHA
all 12 image digests
```

## Environment

UAT runs against staging or a dedicated UAT environment with the same release
candidate.

It must use:

```text
non-production data
dedicated QA/UAT users
HTTPS
production-like service boundaries
real authorization
real migrations
real message broker/event flow
```

## Participants

Required acceptance roles:

```text
Student Representative
Teacher Representative
Admin Representative
Product Owner
Project Supervisor
```

Actual names are supplied at execution time.

## Default gate

Sprint 25 configures the following default release gate:

```text
all P0 scenarios PASS
all P1 scenarios PASS
overall pass rate >= 95%
0 open BLOCKER
0 open CRITICAL
0 open MAJOR
all required sign-off roles approve or approve-with-conditions
```

Changing these thresholds is a release-governance decision, not a way to make a
failed run pass.

## Out of scope

UAT does not independently prove:

```text
500-user capacity
database restore correctness
container vulnerability status
cryptographic implementation
migration concurrency
```

Those are validated by earlier sprint evidence and reviewed where relevant in
cross-role acceptance scenarios.

## Evidence

Each scenario result records:

```text
scenario ID
PASS/FAIL/BLOCKED/WAIVED
tester
timestamp
notes
evidence paths
linked defect IDs
```

Evidence artifacts remain external files rather than being embedded in the run
JSON.

## Acceptance principle

A skipped mandatory scenario is not a PASS.

A workaround does not convert a security/data-integrity failure into acceptance.

The final UAT decision is tied to one immutable release candidate.
