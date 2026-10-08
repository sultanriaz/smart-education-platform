# Stabilization Incident and Defect Triage

## Incident vs follow-up

Use a stabilization **issue** when live behavior is currently wrong, risky, or
degraded.

Use a **follow-up** when production is stable but a bounded improvement,
documentation task, or low-risk operational action remains.

## Severity baseline

```text
SEV-1
  broad outage, serious data/security emergency, major core-role failure

SEV-2
  major degradation or important workflow unavailable for a meaningful user group

SEV-3
  limited functional/operational defect with manageable impact

SEV-4
  low-impact/cosmetic/low-risk issue
```

Reconcile with any institutional incident policy.

## Closure gate

Default Sprint 28 policy requires:

```text
SEV-1 open = 0
SEV-2 open = 0
SEV-3 open = 0
```

SEV-4 may remain only if clearly owned and documented.

## Triage fields

Every issue should record:

```text
ID
severity
title
owner
opened time
current status
linked launch incident
linked release/hotfix
mitigation
notes
```

## Root cause

Do not wait for a perfect root-cause analysis before restoring service.

After stabilization, preserve:

```text
timeline
trigger
impact
root cause or strongest evidence-based hypothesis
corrective action
prevention
owner
```

## Defect hiding

Do not reclassify an unresolved service defect as a follow-up merely to pass the
closure gate.
