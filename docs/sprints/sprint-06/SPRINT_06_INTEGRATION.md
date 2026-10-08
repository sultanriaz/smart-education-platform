# Sprint 6 Integration — Facility & Room Booking Service

## Additions

This package adds:

- `services/facility-service/`
- `docker-compose.facility.yml`
- `.github/workflows/facility-service-ci.yml`

Default local ports:

- Facility API: `8006`
- Facility PostgreSQL: `5439`

## Merge order

1. Extract the ZIP at repository root.
2. Preserve existing Sprint 1-5 services.
3. Inspect Sprint 4 Scheduling's real room/facility representation.
4. Align room IDs with Facility Service UUIDs.
5. Configure Scheduling to use Facility Service's internal reservation contract for authoritative room reservations.
6. Keep Scheduling's teacher/section conflict logic in Scheduling.
7. Configure Notification event relay for Facility outbox events using Sprint 5's actual event envelope.
8. Run all existing service test suites plus Facility tests.

## Cross-service rules

Facility Service owns facilities and availability. Other services must not query `facility_db`.

Scheduling should eventually reserve room occurrences through:

- `POST /api/v1/internal/reservations`
- `DELETE /api/v1/internal/reservations/{source_service}/{source_reference_id}`

Notification Service should receive facility outbox events through its supported internal event contract.

## Recommended combined smoke flow

1. Admin creates a facility.
2. Student creates a booking request.
3. Admin approves it.
4. Availability reports the slot unavailable.
5. Notification relay produces a booking-approved notification.
6. Scheduling attempts an overlapping room reservation and receives conflict.
7. Student cancels booking.
8. Scheduling reservation can then succeed.
