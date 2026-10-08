# UAT Requirements Traceability

This matrix uses project-level normalized requirement aliases. Where the final SRS has formal requirement IDs, Codex must map them without changing the supported requirement meaning.

| Requirement | Domain | Acceptance statement | UAT scenarios | Source reference |
| --- | --- | --- | --- | --- |
| REQ-IDENTITY-AUTH | Identity | Authorized users can authenticate and access only permitted role capabilities. | UAT-ADM-001, UAT-ADM-003, UAT-STU-001, UAT-TCH-001 | Reconcile with final SRS functional requirement ID. |
| REQ-IDENTITY-SESSION | Identity | Sessions support secure refresh/logout and inactivity/session controls. | UAT-STU-010, UAT-X-002 | SRS includes 10-minute inactivity logout; reconcile exact implementation and ID. |
| REQ-ACADEMIC-MASTER | Academic | Academic master data, sections, profiles, enrollments, and teacher assignments are maintained consistently. | UAT-ADM-002, UAT-TCH-001, UAT-TCH-002, UAT-TCH-006 | Reconcile with final SRS functional requirement ID. |
| REQ-ATTENDANCE | Attendance | Teachers can manage attendance and Students can view authorized attendance data. | UAT-STU-003, UAT-TCH-003, UAT-TCH-004 | Reconcile with final SRS functional requirement ID. |
| REQ-SCHEDULING | Scheduling | Users can view authorized timetables and scheduling conflicts are prevented. | UAT-ADM-004, UAT-STU-002, UAT-TCH-008 | Reconcile with final SRS functional requirement ID. |
| REQ-NOTIFICATIONS | Notifications | Users receive authorized notifications and can manage notification state/preferences. | UAT-STU-008, UAT-TCH-009 | Reconcile with final SRS functional requirement ID. |
| REQ-FACILITY | Facility | Authorized users can browse/book facilities and conflicts are prevented. | UAT-ADM-005, UAT-STU-007 | Reconcile with final SRS functional requirement ID. |
| REQ-LEARNING | Learning | Teachers can publish learning resources and Students can access only authorized published resources. | UAT-STU-004, UAT-TCH-005 | Reconcile with final SRS functional requirement ID. |
| REQ-ASSESSMENT | Assessment | Teachers can author/assign/grade assessments and Students can attempt assigned assessments securely. | UAT-STU-005, UAT-STU-006, UAT-TCH-006, UAT-TCH-007 | Reconcile with final SRS functional requirement ID. |
| REQ-REPORTING | Reporting | Admins can view reporting/analytics derived from authorized platform data. | UAT-ADM-006, UAT-ADM-007 | Reconcile with final SRS functional requirement ID. |
| REQ-PLATFORM | Platform | Admins can operate platform settings/support/audit/search/jobs within authorization boundaries. | UAT-ADM-008, UAT-ADM-009 | Reconcile with final SRS functional requirement ID. |
| REQ-RBAC | Security | Student, Teacher, and Admin access is enforced server-side with least privilege. | UAT-ADM-001, UAT-ADM-003, UAT-ADM-008, UAT-ADM-010, UAT-STU-001, UAT-STU-010, UAT-TCH-001, UAT-TCH-005, UAT-TCH-007, UAT-TCH-010, UAT-X-001, UAT-X-003 | Reconcile with final SRS security requirements. |
| REQ-PRIVACY | Security | Users cannot access another user's protected data without authorization. | UAT-ADM-007, UAT-ADM-010, UAT-STU-002, UAT-STU-003, UAT-STU-004, UAT-STU-005, UAT-STU-006, UAT-STU-007, UAT-TCH-002, UAT-TCH-010, UAT-X-001, UAT-X-003 | Reconcile with final SRS security/privacy requirements. |
| REQ-PERF-GENERAL | Performance | At least 95% of normal page/API interactions complete within 3 seconds in the acceptance environment. | UAT-X-004 | Known SRS NFR target; reconcile exact SRS ID. |
| REQ-PERF-ATTENDANCE | Performance | Attendance operations complete within 2 seconds at the required percentile/acceptance definition. | UAT-STU-003, UAT-TCH-003 | Known SRS NFR target; reconcile exact SRS ID. |
| REQ-PERF-NOTIFICATION | Performance | Representative notification delivery/visibility completes within 5 seconds. | UAT-STU-008 | Known SRS NFR target; reconcile exact SRS ID. |
| REQ-CONCURRENCY | Performance | The platform supports at least 500 concurrent users under the defined workload mix. | UAT-X-004 | Known SRS NFR target; reconcile exact SRS ID. |
| REQ-AVAILABILITY | Reliability | Platform availability target is at least 99%. | UAT-X-005 | Known SRS NFR target; reconcile exact SRS ID. |
| REQ-RECOVERY | Reliability | Normal operation avoids data loss and recovery meets the documented recovery target. | UAT-X-006 | Known SRS recovery requirement; reconcile exact SRS ID and realistic provider implementation. |
| REQ-RESPONSIVE | Usability | Core workflows are usable on desktop and mobile/responsive layouts. | UAT-STU-009, UAT-X-009, UAT-X-010 | Known SRS responsive requirement; reconcile exact SRS ID. |
| REQ-ACCESSIBILITY | Usability | Core workflows meet the project's agreed accessibility baseline. | UAT-X-007, UAT-X-008 | Project acceptance baseline; confirm whether SRS explicitly assigns an accessibility standard. |
