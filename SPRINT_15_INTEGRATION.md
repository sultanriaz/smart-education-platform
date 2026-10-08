# Sprint 15 Integration Checklist

Sprint 15 assumes Sprints 1–14 are already merged.

## 1. Frontend overlay

Overlay:

- `apps/frontend/src/features/admin`
- `apps/frontend/src/pages/admin`
- updated `AppRouter.tsx`
- updated Admin navigation

Preserve all Student and Teacher routes from Sprints 13–14.

## 2. Identity contract

Sprint 15 is aligned to the Sprint 1 Identity design:

- `GET /api/v1/identity/users`
- `POST /api/v1/identity/users`
- `PATCH /api/v1/identity/users/{id}`
- `DELETE /api/v1/identity/users/{id}`
- `GET /api/v1/identity/roles`
- `POST /api/v1/identity/roles`
- `GET /api/v1/identity/permissions`

Verify the actual merged repository includes the earlier fixes:

- `list_users`, not repository method `list`
- `list_roles`, not repository method `list`

Do not claim password-reset or email-verification flows are implemented unless
they were added after Sprint 1.

## 3. Academic contract — mandatory reconciliation

Sprint 2 was implemented locally by Codex and is not available inside this
packaging runtime.

The Admin adapter currently expects logical resources:

- `/departments`
- `/programs`
- `/academic-years`
- `/semesters`
- `/courses`
- `/sections`
- `/student-profiles`
- `/teacher-profiles`
- `/enrollments`
- `/teaching-assignments`

under the Gateway prefix `/api/v1/academic`.

Inspect the real Sprint 2 OpenAPI and adapt `admin-api.ts` to the exact route and
schema names.

Required Admin capabilities after integration:

- create/update/deactivate Department
- create/update/deactivate Program
- create/update Academic Year
- create/update Semester
- create/update/deactivate Course
- create/update/deactivate Section
- create/update Student academic profile
- create/update Teacher academic profile
- enroll/withdraw Student
- assign/unassign Teacher
- preserve section capacity and duplicate-enrollment concurrency rules

If Sprint 2 uses different concepts such as `course-offerings`, preserve that
domain model rather than flattening it to match the frontend.

## 4. Scheduling contract

Sprint 15 uses Sprint 4's actual routes:

- `GET /api/v1/scheduling/schedules`
- `POST /api/v1/scheduling/schedules`
- `POST /api/v1/scheduling/schedules/{id}/cancel`
- `POST /api/v1/scheduling/schedules/{id}/overrides`

Run conflict tests for:
- Teacher overlap
- section overlap
- room overlap
- effective-date windows
- reschedule conflict
- cancellation/override history

## 5. Facility contract

Sprint 15 uses Sprint 6's actual routes:

- `GET/POST /api/v1/facilities/facilities`
- `PATCH /api/v1/facilities/facilities/{id}`
- `GET /api/v1/facilities/bookings`
- `POST /api/v1/facilities/bookings/{id}/approve`
- `POST /api/v1/facilities/bookings/{id}/reject`
- `GET/POST /api/v1/facilities/blocks`
- `POST /api/v1/facilities/blocks/{id}/cancel`

Verify Admin can see all bookings while Student/Teacher remain scoped to their
own requests.

## 6. Notification contract

Sprint 15 uses Sprint 5 Admin APIs:

- `GET/POST /api/v1/notifications/admin/templates`
- `GET/POST /api/v1/notifications/admin/campaigns`

Verify:
- role campaign recipient resolution
- section campaign recipient resolution
- preferences suppress disabled channels
- email retries remain worker-owned
- Admin can use global campaigns
- Teacher remains limited to Sprint 14 SECTION announcements

## 7. Reporting contract

Sprint 15 uses Sprint 9:

- `GET /api/v1/reporting/dashboard/overview`
- `GET /api/v1/reporting/metrics/attendance`
- `GET /api/v1/reporting/metrics/assessments`
- `GET /api/v1/reporting/metrics/facilities`
- `GET /api/v1/reporting/metrics/notifications`
- `GET /api/v1/reporting/metrics/scheduling`
- `GET /api/v1/reporting/metrics/enrollment`
- `GET/POST /api/v1/reporting/reports/snapshots`
- `GET /api/v1/reporting/reports/{report_type}.csv`

CSV export must retain authenticated Gateway access.

## 8. Platform contract

Sprint 15 uses Sprint 10:

- `GET/PUT /api/v1/platform/admin/services`
- `POST /api/v1/platform/admin/services/health`
- `GET /api/v1/platform/admin/audit`
- `GET/POST /api/v1/platform/admin/jobs`
- `GET /api/v1/platform/admin/settings`
- `PUT /api/v1/platform/admin/settings/{key}`
- `GET /api/v1/platform/features`
- `PUT /api/v1/platform/admin/features/{key}`
- `GET /api/v1/platform/support/tickets`
- `PATCH /api/v1/platform/support/tickets/{id}`

Verify service registry base URLs are internal service addresses and are not
exposed as browser API targets.

## 9. Full Admin E2E smoke flow

1. Login as Admin.
2. Dashboard loads Reporting + Platform + Identity summary.
3. Create Student account.
4. Create Teacher account.
5. Activate/deactivate a test account.
6. Change a test account role.
7. Create a custom role using known permissions.
8. Create Department.
9. Create Program.
10. Create Academic Year.
11. Create Semester.
12. Create Course.
13. Create Section.
14. Create Student academic profile.
15. Create Teacher academic profile.
16. Enroll Student.
17. Assign Teacher.
18. Create timetable schedule.
19. Verify conflicting schedule is rejected.
20. Apply a cancellation override.
21. Create Facility.
22. Disable/re-enable booking.
23. Create a test booking as Student/Teacher.
24. Approve it as Admin.
25. Reject another test booking.
26. Create facility block.
27. Create Notification template.
28. Send role campaign.
29. Send section campaign.
30. Verify recipients receive notifications according to preferences.
31. Open Reporting overview.
32. Open each metric.
33. Create report snapshot.
34. Download CSV.
35. Register/upsert Platform service.
36. Run service health sweep.
37. Change a non-secret Platform setting.
38. Toggle a Feature flag.
39. Create Platform job.
40. Update Support ticket.
41. Open audit trail.
42. Try Admin URL as Student and verify 403/frontend denial.
43. Try Admin API using Student token and verify backend 403.
44. Refresh every deep Admin URL and verify SPA fallback.

## 10. Regression

Run all Sprints 1–15 tests, especially:

- Identity RBAC
- Academic PostgreSQL concurrency tests
- Attendance authorization
- Scheduling conflict tests
- Notification targeting/retries
- Facility booking races
- Learning authorization
- Assessment Student/Teacher security tests
- Reporting ingestion/export
- Platform jobs/settings/audit
- Gateway namespace/internal-route tests
- Student E2E
- Teacher E2E
- Admin E2E
