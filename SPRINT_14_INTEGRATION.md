# Sprint 14 Integration Checklist

Sprint 14 assumes Sprints 1–13 are already present.

## 1. Frontend overlay

Overlay:
- `apps/frontend/src/features/teacher`
- `apps/frontend/src/pages/teacher`
- updated AppRouter
- updated navigation
- Student subjective-answer compatibility patch

Do not remove working Student routes from Sprint 13.

## 2. Academic Service reconciliation

The Teacher UI currently expects:

- `GET /api/v1/academic/teachers/me/sections`
- `GET /api/v1/academic/sections/{section_id}/roster`

Inspect the real Sprint 2 Academic Service.

If route names differ:
- adapt `teacher-api.ts`, or
- add a clean Academic alias endpoint.

Do not query `academic_db` from frontend, Attendance, Notification, Learning, or
Assessment.

Teacher section and roster authorization must stay server-side.

## 3. Attendance Service reconciliation

Expected logical calls through Gateway:

- list sessions for one assigned section
- create attendance session
- get session attendance sheet
- bulk upsert attendance
- finalize session
- correct one attendance record with a reason

The current frontend adapter uses:

```text
GET   /api/v1/attendance/sections/{section}/sessions
POST  /api/v1/attendance/sessions
GET   /api/v1/attendance/sessions/{session}/attendance
PUT   /api/v1/attendance/sessions/{session}/attendance
POST  /api/v1/attendance/sessions/{session}/finalize
PATCH /api/v1/attendance/records/{record}
```

Reconcile these against the actual Sprint 3 service.

Required backend rules:
- Teacher can operate only assigned sections.
- Bulk updates are transactional.
- Finalized/locked sheets obey correction policy.
- Correction requires audit reason.
- Attendance percentages remain backend-owned.

## 4. Scheduling

Sprint 4's actual `/timetable/me` requires:
- `start_date`
- `end_date`

Sprint 14 supplies a Monday-based two-week window and normalizes the actual
Occurrence schema where `occurrence_date`, `starts_at`, and `ends_at` are
separate values.

## 5. Learning

Sprint 14 is aligned to Sprint 7's actual routes:

- `GET /api/v1/learning/resources`
- `POST /api/v1/learning/resources`
- `POST /api/v1/learning/resources/{id}/versions`
- `POST /api/v1/learning/resources/{id}/upload`
- `POST /api/v1/learning/resources/{id}/publish`
- `POST /api/v1/learning/resources/{id}/archive`

Verify target IDs are real assigned Section/Course UUIDs.

## 6. Assessment

Overlay:
- `teacher_read.py`
- hardened `authoring.py`
- hardened `grading.py`
- router update
- tests

Verify Sprint 13 `student_read.py` remains present.

Required security tests:
- Teacher cannot edit another Teacher's bank/quiz.
- Teacher cannot assign an unassigned section.
- Teacher cannot grade an unassigned section.
- In-progress Student attempts do not appear in Teacher attempt API.
- Submitted and graded attempts do.
- Admin still has global Assessment management rights.
- Student answer-key protection from Sprint 13 remains intact.

## 7. Notification

Overlay:
- Academic client assignment validation
- Teacher announcement endpoint
- router update
- tests

Teacher announcements must:
- target SECTION only
- validate current Teacher assignment before recipient resolution
- use the existing Notification preferences/delivery machinery
- never expose Admin role/global campaign capability to Teacher

## 8. Facility

Sprint 14 aligns to Sprint 6's actual BookingCreate/BookingCancel schemas.

Run Teacher create/list/cancel smoke tests.

Teacher must not gain approve/reject permissions.

## 9. Full Teacher E2E flow

1. Login as Teacher.
2. Dashboard loads assigned sections/classes.
3. Open an assigned section.
4. View roster.
5. Create attendance session.
6. Bulk mark Present/Absent/Late/Excused.
7. Save.
8. Finalize.
9. Apply an allowed correction with reason.
10. Open teaching timetable.
11. Create Learning Note and publish.
12. Create Learning File and upload version.
13. Create question bank.
14. Create objective question.
15. Create subjective question.
16. Create quiz.
17. Attach questions.
18. Publish quiz.
19. Assign quiz to assigned section.
20. Submit a Student attempt.
21. Verify Teacher cannot see it while IN_PROGRESS.
22. Submit attempt.
23. Verify Teacher can review it.
24. Manually grade Short Text answer.
25. Verify final result.
26. Create Teacher facility booking.
27. Cancel permitted booking with reason.
28. Send announcement to assigned section.
29. Verify Student receives in-app announcement.
30. Try announcement to unassigned section and verify 403.
31. Open notification inbox/preferences.
32. Open profile.
33. Try Student/Admin-only frontend routes and verify denial.
34. Refresh deep Teacher URLs and verify SPA routing.

## 10. Regression

Run all relevant tests for:
- Academic
- Attendance
- Scheduling
- Notification
- Facility
- Learning
- Assessment
- Gateway
- Frontend
- Student Sprint 13 flows
