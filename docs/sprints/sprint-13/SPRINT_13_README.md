# Sprint 13 — Student UX

Sprint 13 replaces the Student placeholders from Sprint 12 with connected
Student workflows across the distributed Smart Education Platform.

## Student experience implemented

- Student dashboard
- Attendance summary and history
- Timetable
- Learning resources
- Deterministic resource recommendations
- Authenticated file downloads
- Assessment assignment list
- Assessment attempt flow
- Objective/short-text answer capture
- Save progress
- Assessment submission
- Assessment results
- Facility discovery
- Facility booking request
- Booking cancellation
- Notification inbox
- Unread count
- Mark read / mark all read
- Notification preferences
- Existing Identity profile screen
- Student-only RBAC routes

## Browser service boundaries

All browser requests use Sprint 11 public namespaces.

```text
Frontend
   |
   v
API Gateway
   |
   +--> Attendance
   +--> Scheduling
   +--> Learning
   +--> Assessment
   +--> Facility
   +--> Notification
   +--> Identity
```

There is no direct browser access to service databases or service development
ports.

## Student routes

- `/app/student`
- `/app/student/attendance`
- `/app/student/timetable`
- `/app/student/learning`
- `/app/student/assessments`
- `/app/student/assessments/:assignmentId`
- `/app/student/facilities`
- `/app/notifications`
- `/app/profile`

## Assessment compatibility addition

The original Sprint 8 package had mutation APIs for Student attempts but did not
contain the Student read endpoints needed by a complete UI.

Sprint 13 therefore includes an additive Assessment Service patch providing:

- `GET /api/v1/students/me/assignments`
- `GET /api/v1/students/me/assignments/{assignment_id}`
- `GET /api/v1/students/me/results`
- `GET /api/v1/attempts/{attempt_id}`

The assignment-detail response deliberately omits:

- correct choice flags
- correct text answers
- explanations

so answer keys are not exposed to Students before grading.

During repository integration, Codex must reconcile these routes with any
Assessment changes already made while merging Sprint 8.

## Authenticated resource downloads

Learning resource downloads use the shared authenticated API client rather than
plain browser links. This preserves bearer authentication and the one-time
access-token refresh behavior.

## Attendance display

The frontend displays the percentage returned by Attendance Service and does not
recalculate the authoritative percentage itself.

This avoids silently diverging from Attendance Service rules for LATE/EXCUSED.

## Facility booking

The UI validates only basic client-side time ordering.

Authoritative checks such as:

- booking notice window
- maximum duration
- facility blocks
- timetable reservations
- existing bookings
- concurrency conflicts

remain Facility Service responsibilities.

## Assessment grading

The frontend never grades answers.

Objective auto-grading and subjective/manual grading remain Assessment Service
responsibilities.

## Responsive behavior

Student pages use responsive cards, horizontally scrollable tables where needed,
and the Sprint 12 mobile navigation shell.

## Integration requirement

The exact source contracts must be verified against the merged Sprint 1–12
repository. See `CODEX_MERGE_PROMPT.md`.
