# Support and Operations Handoff

Sprint 28 closes only when ongoing operations are clearly owned.

## Operations accepts

```text
production architecture
service inventory
production DNS/TLS ownership
Kubernetes ownership
database/Redis/RabbitMQ/object-storage ownership
backup/recovery ownership
observability/alert ownership
incident runbooks
credential rotation ownership
deployment/release process
```

## Support accepts

```text
issue intake route
severity/triage guidance
known issues
escalation contacts
role/workflow terminology
expected user communication path
```

## Application team retains

Define who owns:

```text
application defects
schema changes
contract changes
performance remediation
security fixes
future releases
```

## Documentation review

Before closure ensure docs use current:

```text
hostnames
service names
owner roles
alert/runbook references
release process
```

Never place live passwords/tokens in operational documentation.

## Handoff evidence

Record the five closure approvals in the structured stabilization run.

Approval means the owner has reviewed the relevant evidence and accepts the
ongoing responsibilities, not merely that their name was entered.
