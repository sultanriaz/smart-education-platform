# Sprint 9 Integration — Reporting & Analytics Service

Extract into the Smart Education Platform repository root.

Expected additions:

- `services/reporting-service`
- `docker-compose.reporting.yml`
- `.github/workflows/reporting-service-ci.yml`

## Mandatory contract reconciliation

Inspect the actual Sprints 1-8 before declaring integration complete.

Map the real source event names and payloads from:

1. Academic Service
   - enrollment created/activated/dropped
   - optional section/program events

2. Attendance Service
   - attendance recorded
   - attendance corrected/updated
   - session finalized
   - actual percentage semantics

3. Scheduling Service
   - schedule created/updated/cancelled
   - occurrence changed/rescheduled

4. Notification Service
   - sent/delivered/failed events
   - channel and delivery identifiers

5. Facility Service
   - booking lifecycle events

6. Assessment Service
   - attempt graded event
   - include quiz/course/section identifiers if available

Do not make Reporting Service query any source database.

## Source-service integration pattern

Preferred:

source transaction
-> source outbox
-> relay
-> Reporting `/api/v1/internal/events`

Reporting is a non-critical downstream consumer. A Reporting outage must not fail
attendance submission, grading, booking approval, etc.

## Required smoke test

Generate one real event from each available source service and verify that the
corresponding projection/dashboard metric changes exactly once.

Then repeat one event with the same event_id and verify no double counting.
