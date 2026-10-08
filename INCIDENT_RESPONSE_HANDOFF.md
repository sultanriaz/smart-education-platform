# Incident Response Handoff

Sprint 26 connects the Sprint 21 technical runbooks to actual production
ownership.

## Severity

Suggested operational classification:

```text
SEV-1  platform unavailable, data/security emergency, core role blocked broadly
SEV-2  major degradation or important workflow unavailable
SEV-3  limited defect with workaround
SEV-4  low-impact/cosmetic issue
```

Reconcile this with any institutional incident standard.

## SEV-1 actions

```text
declare incident
assign incident lead
protect data/security first
stop deployment if related
preserve evidence/logs
use rollback/forward-fix/restore decision tree
communicate status
```

## Evidence capture

Capture:

```text
release tag
time
request/correlation IDs
trace IDs
alerts
affected services
deployment/migration state
DB/broker health
```

Do not export secrets/environment dumps.

## Production launch incidents

During the launch window, any incident meeting abort criteria may halt the
release immediately.

After service is restored, record:

```text
timeline
impact
root cause/hypothesis
corrective action
follow-up owner
```

## Security incidents

For suspected credential compromise or unauthorized data exposure:

```text
restrict access
rotate affected credentials/keys
preserve audit logs
involve SecurityOwner
assess affected data/users
follow institutional reporting requirements
```
