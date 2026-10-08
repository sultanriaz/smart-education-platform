# Sprint 14 — Complete Teacher UX

Sprint 14 replaces the Teacher placeholders from Sprint 12 with connected
Teacher workflows across Academic, Attendance, Scheduling, Learning,
Assessment, Facility, Notification, and Identity.

## Teacher experience implemented

- Teacher dashboard
- Assigned section list
- Section roster
- Attendance session creation
- Bulk attendance marking
- Attendance notes
- Attendance finalization
- Attendance correction with reason
- Two-week teaching timetable
- Learning resource creation
- Section-targeted learning resources
- Note/link/video/file content versions
- File upload
- Publish/archive learning resources
- Question banks
- MCQ / True-False / Short-text question authoring
- Quiz creation/composition/publishing
- Quiz assignment to assigned sections
- Submitted-attempt review
- Manual grading with feedback and audit reason
- Teacher facility booking
- Booking cancellation with reason
- Section-scoped announcements
- Notification inbox/preferences through the common Sprint 13 screen
- Identity profile through the common profile screen
- Teacher-only RBAC routes

## Browser architecture

All frontend traffic remains behind Sprint 11 Gateway:

```text
Teacher Browser
      |
      v
API Gateway
      |
      +--> Academic
      +--> Attendance
      +--> Scheduling
      +--> Learning
      +--> Assessment
      +--> Facility
      +--> Notification
      +--> Identity
```

There is no frontend database access and no direct service development-port use.

## Teacher routes

- `/app/teacher`
- `/app/teacher/attendance`
- `/app/teacher/timetable`
- `/app/teacher/learning`
- `/app/teacher/assessments`
- `/app/teacher/announcements`
- `/app/teacher/facilities`
- `/app/notifications`
- `/app/profile`

## Assessment hardening included

Sprint 14 adds Teacher read APIs because the original Sprint 8 Assessment Service
had authoring mutations but no Teacher list/read workspace.

Added:

- `GET /api/v1/teachers/me/banks`
- `GET /api/v1/teachers/me/questions`
- `GET /api/v1/teachers/me/quizzes`
- `GET /api/v1/teachers/me/assignments`
- `GET /api/v1/teachers/me/assignments/{assignment_id}/attempts`

The Gateway exposes these beneath `/api/v1/assessments/...`.

Security improvements:

- Teacher can add questions only to their own banks.
- Teacher can attach only their own questions to their own quizzes.
- Teacher can publish only their own quizzes.
- Teacher can assign only their own quizzes.
- Existing Academic assignment validation still restricts Teacher section access.
- Teacher manual grading requires a submitted attempt.
- Teacher grading is restricted to assigned/owned assessment sections.
- Teacher attempt listing excludes `IN_PROGRESS` attempts so Teachers cannot
  inspect a Student's partial answers before submission.
- Admin remains able to manage Assessment authoring globally.

Sprint 14 also patches the Student assessment UI so blank Short Text answers are
persisted as explicit answer rows. This prevents a submitted subjective question
from becoming impossible to manually grade merely because the Student left it
blank.

## Teacher announcements included

Sprint 5 originally made Notification campaigns Admin-only.

Sprint 14 adds a narrowly scoped Teacher endpoint:

- `POST /api/v1/teacher/announcements`
- `GET /api/v1/teacher/announcements`

Teacher announcements are restricted to `SECTION` targets.

Before creating the campaign, Notification Service asks Academic Service whether
the authenticated Teacher is assigned to that section. Teachers cannot use this
endpoint for arbitrary roles, direct recipients, or unassigned sections.

The existing Notification campaign/delivery system still performs recipient
resolution, preferences, in-app delivery, and optional email delivery.

## Learning resource security

No Learning backend relaxation is required.

Sprint 7 already enforces:

- Teacher must be assigned to selected academic targets.
- Teacher may modify only their own resources unless Admin.
- Published resources require a content version and target.
- File type/size rules remain backend-owned.
- Storage remains behind Learning Service.

## Facility security

Sprint 6 already permits Student, Teacher, and Admin booking creation while
keeping approval/rejection Admin-only.

Sprint 14 uses the real Sprint 6 booking payload including:

- facility
- purpose
- starts/ends
- attendee count

Cancellation includes the required reason.

## Academic and Attendance contracts

Sprint 14 frontend adapters expect Teacher Academic/Attendance capabilities from
Sprints 2–3. Because those generated service packages are not part of the Sprint
14 packaging runtime, their exact merged route names must be reconciled by Codex.

Expected logical capabilities:

Academic:
- list current Teacher assigned sections
- list one section roster

Attendance:
- list section attendance sessions
- create session
- load attendance sheet
- bulk save attendance
- finalize attendance
- correct a record with reason

Do not add direct Academic/Attendance database access if route names differ.
Adapt the HTTP contract instead.
