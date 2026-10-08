# Sprint 13 Integration Checklist

## 1. Overlay order

Sprint 13 expects Sprint 12 Frontend Foundation and Sprint 8 Assessment Service
to exist in the repository before this overlay is integrated.

## 2. Reconcile each real API

### Attendance

Expected frontend calls:

- `GET /api/v1/attendance/students/me/attendance`
- `GET /api/v1/attendance/students/me/attendance/summary`

Confirm exact response shapes and preserve the backend's attendance percentage
rule.

### Scheduling

Expected:

- `GET /api/v1/scheduling/timetable/me`

Confirm whether the real API returns recurring schedules or expanded
occurrences. The Student UI should render actual occurrences suitable for dates.

### Learning

Expected:

- `GET /api/v1/learning/students/me/resources`
- `GET /api/v1/learning/students/me/recommendations`
- `GET /api/v1/learning/resources/{resource_id}/download`

Preserve authenticated downloads.

### Assessment

Expected after the Sprint 13 compatibility patch:

- `GET /api/v1/assessments/students/me/assignments`
- `GET /api/v1/assessments/students/me/assignments/{id}`
- `GET /api/v1/assessments/students/me/results`
- `POST /api/v1/assessments/assignments/{id}/attempts`
- `PUT /api/v1/assessments/attempts/{attempt}/answers/{question}`
- `POST /api/v1/assessments/attempts/{attempt}/submit`

The Gateway strips `/api/v1/assessments/`, so Assessment Service itself receives
its normal `/api/v1/...` paths.

Do not expose answer keys in assignment detail.

### Facility

Expected:

- `GET /api/v1/facilities/facilities`
- `GET /api/v1/facilities/bookings`
- `POST /api/v1/facilities/bookings`
- `POST /api/v1/facilities/bookings/{id}/cancel`

Reconcile booking request field names with the actual Sprint 6 schemas.

### Notification

Expected:

- `GET /api/v1/notifications/notifications`
- `GET /api/v1/notifications/notifications/unread-count`
- `POST /api/v1/notifications/notifications/{id}/read`
- `POST /api/v1/notifications/notifications/read-all`
- `GET /api/v1/notifications/preferences/me`
- `PATCH /api/v1/notifications/preferences/me`

## 3. End-to-end Student smoke flow

1. Login as Student.
2. Open dashboard.
3. Verify attendance percentage.
4. Open attendance history.
5. Open timetable.
6. Open a published Learning resource.
7. Download a protected file resource.
8. Open recommendations.
9. Open assigned assessment.
10. Start attempt.
11. Save objective and short-text answers.
12. Submit.
13. Verify objective-only quiz can be graded immediately.
14. Verify subjective quiz remains pending until Teacher grading.
15. Open facility list.
16. Create booking.
17. Verify booking status.
18. Cancel a permitted booking.
19. Open notification inbox.
20. Mark one read.
21. Mark all read.
22. Update notification preferences.
23. Open Profile.
24. Try an Admin/Teacher URL and verify denial.
25. Reload each deep Student URL and verify SPA routing.

## 4. Negative/security checks

- Student cannot see another Student's attendance.
- Student cannot retrieve another Student's attempt.
- Student assignment detail contains no `is_correct`, correct answer, or
  explanation fields.
- Student cannot bypass attempt limits.
- Student cannot submit after backend deadline policy.
- Student cannot mutate finalized attendance.
- Student cannot approve bookings.
- Student cannot access Notification admin campaigns/templates.
- Browser traffic targets Gateway, not service host ports.
