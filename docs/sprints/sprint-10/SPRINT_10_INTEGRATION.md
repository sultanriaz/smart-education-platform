# Sprint 10 Integration — Platform Operations Service

Extract this package into the repository root.

Expected additions:

- `services/platform-service`
- `docker-compose.platform.yml`
- `.github/workflows/platform-service-ci.yml`

## Mandatory integration work

Inspect the real Sprint 1-9 implementations before considering Sprint 10 merged.

### Identity

Reconcile:
- JWKS endpoint
- issuer
- audience
- algorithm
- access-token type
- subject UUID
- roles

### Source service event integration

Platform Service must receive explicit events; it must never query another
service's operational database.

Recommended event-producing services:

- Identity: account/security audit events and searchable user metadata only if
  institution policy permits it.
- Academic: searchable courses/sections/programs and admin audit events.
- Attendance: audit metadata for corrections.
- Scheduling: searchable timetable metadata if useful and change audits.
- Notification: delivery/administration audits where useful.
- Facility: searchable facilities and booking administration audits.
- Learning: searchable published learning resource metadata.
- Assessment: quiz metadata if search should expose it.
- Reporting: normally no search ownership is needed.

### Notification integration

Support ticket lifecycle events should be relayed to the actual Sprint 5
Notification Service contract so users can be notified of ticket updates.

### Search

Reconcile source URL/path conventions with the actual frontend routing strategy.
Do not index authorization-sensitive records into an audience that should not
see them.

### Background import/export

Do not implement cross-service imports by database access.

If a domain service does not expose an explicit internal import/export API, keep
the Platform job disabled for that resource until the source service contract is
added and tested.

## Required smoke flow

1. Emit searchable metadata from a real source service.
2. Confirm it appears exactly once in Platform search.
3. Update it and confirm one logical search document remains.
4. Delete/deactivate it and confirm it disappears from user search.
5. Emit an audit event and confirm admin audit view.
6. Create a support ticket as a student.
7. Update it as admin.
8. Confirm Notification integration if enabled.
9. Register all running services and execute health aggregation.
10. Replay an existing event_id and verify idempotency.
