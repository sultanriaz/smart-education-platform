# Sprint 27 → Sprint 28 Handoff

Sprint 28 owns post-launch stabilization.

Sprint 27 hands over:

```text
exact production release tag
commit SHA
12 production image digests
production launch record
launch report
launch evidence index
backup/PITR reference
migration results
rollout results
launch incidents
open SEV-2/SEV-3/SEV-4 issues
monitoring observations
accepted readiness risks/conditions
```

## Stabilization priorities

Sprint 28 should watch:

```text
real traffic/error behavior
latency/SRS targets
DB pool/lock behavior
RabbitMQ backlog and retries
outbox/inbox health
notification delivery
pod/HPA behavior
support tickets
security alerts
```

## Change discipline

Do not immediately resume normal feature development.

Stabilization changes should be:

```text
small
reviewed
observable
release-tracked
```

A severe launch issue follows the rollback/incident process rather than being
hidden as a "quick fix."
