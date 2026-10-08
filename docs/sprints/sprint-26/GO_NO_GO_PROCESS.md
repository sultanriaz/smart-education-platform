# Production Go / No-Go Process

## Participants

The generated governance roles are:

```text
TechnicalLead
OperationsOwner
SecurityOwner
ProductOwner
ProjectSupervisor
```

Map these to actual project/institutional owners during integration.

## Decisions

Final readiness decision:

```text
GO
GO_WITH_CONDITIONS
NO_GO
```

`GO_WITH_CONDITIONS` is appropriate only when every configured mandatory gate
still passes and the remaining conditions are low enough risk to proceed.

It cannot override:

```text
failed mandatory readiness check
open BLOCKER
open CRITICAL
open HIGH under the default policy
REJECT approval
failed UAT gate
release digest mismatch
failed restore evidence
```

## Meeting input

Review:

```text
release identity
UAT report
open defects/risks
production infrastructure status
security evidence
performance results
observability/alerting
backup/restore evidence
migration plan
rollback/abort criteria
launch communications/support plan
```

## Meeting output

Record:

```text
decision
decision time
approvers
conditions
open MEDIUM/LOW risks
deployment window
abort authority
exact release tag/commit/digests
```

## No-Go examples

Typical NO_GO conditions include:

```text
production secrets not provisioned
real DNS/TLS not validated
DB restore drill failed
500-user target not demonstrated where required
critical security issue
image digests differ from UAT
migration has no backup/abort strategy
observability/critical alert routing unavailable
```

## Integrity

Do not edit old evidence to create a GO result.

Fix the issue, gather new evidence, and re-run the gate.
