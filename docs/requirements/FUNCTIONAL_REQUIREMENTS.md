# Draft functional requirements

Updated 2026-10-08. As-built engineering draft, not an approved SRS.

| ID | Implemented behavior | Verification boundary |
|---|---|---|
| FR-01 | Registration, login, roles/permissions, account/profile administration, refresh-cookie rotation, logout, recovery/verification | Identity/security suites; real role login, cookie/storage/idle browser checks and single-use SMTP recovery; institutional verification policy unresolved |
| FR-02 | Departments, programs, years, semesters, courses, sections, profiles, enrollment and assignments | Academic tests and real linked demo records; signed relationship contracts wired |
| FR-03 | Attendance sessions, marks, finalization, corrections/reopening/cancellation, history and summaries | 99 tests; five real finalized demo sessions, live 80% summary and finalized-write/role rejection; real bulk-write/read-back timing recorded; dedicated write-load target not verified |
| FR-04 | Conflict-aware recurring schedules, occurrence changes, history and timetables | Scheduling suite; real recurring Student/Teacher timetable and browser loading; exceptional workflows primarily unit verified |
| FR-05 | Notifications/read state/preferences, campaigns/templates, teacher announcements and event delivery | Notification suite; real RabbitMQ/SMTP workers, announcement visible in 0.906s and mark-read; live failure drills NOT RUN |
| FR-06 | Facilities/equipment, availability, booking review/cancellation, blocks, internal reservations | Facility suite; real booking approval, overlap conflict and requester isolation; role pages loaded |
| FR-07 | Targeted notes/links/videos/files, versions, publication/archive, downloads and recommendations | Learning suite; real notes/recommendations and private S3 upload/download/checksum; MIME, Student upload and anonymous/cross-bucket denial verified |
| FR-08 | Banks/questions/quizzes, assignments, attempts, saved answers, automatic/manual grading, timer/deadline enforcement and results | Assessment regression suite; safe persisted answers/results and browser save/reload/resume; expiry worker and late-edit checks recorded separately in the delivery report; manual grading and blank written responses unit verified |
| FR-09 | Event projections, overview/reports, filtered snapshots, audited CSV export | Reporting suite; real RabbitMQ grade projection and Admin CSV; snapshot equality/unsupported-filter tests; large reports unverified |
| FR-10 | Support, settings, feature flags, registry/health, audit/search and durable jobs | Platform suite; real Redis retry/ticket isolation, ten-service health, reindex and signed Academic export; broader owner adapters/search coverage incomplete |
| FR-11 | Protected responsive role workspaces, keyboard page search/navigation, light/dark themes, shared forms/tables/states | Build/lint/40 frontend tests; real role routes, five widths, axe, mobile/keyboard focus and screenshots; final timing rerun separately recorded |
| FR-12 | Independent runtime, migrations, messaging, telemetry and deployment/readiness/UAT tooling | Isolated suites and ten local migrations executed; external deployment/UAT not verified |

No feature is removed because it is absent from the old SRS. UI counts/charts use real APIs; demo fixtures are explicitly labelled. Source implementation alone does not imply full-system verification.
