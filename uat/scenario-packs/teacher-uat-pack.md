# Teacher UAT Scenario Pack

Release tag: ____________________  
Commit SHA: ____________________  
Staging/UAT URL: ____________________  
Execution date: ____________________

Use the structured CLI run record as the source of truth for final gate evaluation. This document is a human-friendly execution worksheet.

## UAT-TCH-001 — Teacher login and assigned teaching context

**Role:** Teacher  
**Domain:** Identity  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-IDENTITY-AUTH, REQ-RBAC, REQ-ACADEMIC-MASTER

### Steps

1. Authenticate with Teacher QA account.
2. Open Teacher dashboard.
3. Inspect assigned sections/classes.

### Expected results

- Teacher workspace loads.
- Only authorized teaching assignments are shown.
- Admin-only capabilities are not available.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-002 — View section roster

**Role:** Teacher  
**Domain:** Academic  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ACADEMIC-MASTER, REQ-PRIVACY

### Steps

1. Open an assigned section.
2. View roster.
3. Attempt an unassigned section if the UI/API permits navigation.

### Expected results

- Assigned roster is correct.
- Unassigned section roster is denied or not exposed.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-003 — Create and finalize attendance

**Role:** Teacher  
**Domain:** Attendance  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ATTENDANCE, REQ-PERF-ATTENDANCE

### Steps

1. Open assigned section attendance.
2. Create/open a session.
3. Mark roster attendance.
4. Finalize the session.

### Expected results

- Session/records persist atomically.
- Finalized state is shown.
- Operation meets the Attendance acceptance target in the staging performance evidence.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-004 — Correct attendance with audit reason

**Role:** Teacher  
**Domain:** Attendance  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-ATTENDANCE

### Steps

1. Open a finalized/eligible attendance record.
2. Submit an allowed correction with reason.
3. Inspect resulting record/history if exposed.

### Expected results

- Correction follows server rules.
- Reason is required when specified by contract.
- Audit/history reflects the correction without silently rewriting history.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-005 — Publish a learning resource

**Role:** Teacher  
**Domain:** Learning  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-LEARNING, REQ-RBAC

### Steps

1. Create a resource for an assigned course/section.
2. Save as draft.
3. Publish it.
4. Verify Student visibility using authorized Student account.

### Expected results

- Teacher can author within assignment scope.
- Draft is not Student-visible.
- Published resource becomes visible only to intended audience.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-006 — Create and assign quiz

**Role:** Teacher  
**Domain:** Assessment  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ASSESSMENT, REQ-ACADEMIC-MASTER

### Steps

1. Create/select a question bank.
2. Create questions.
3. Create quiz and add questions.
4. Publish and assign to an authorized section.

### Expected results

- Quiz rules are validated.
- Assignment respects Teacher's authorized section/course scope.
- Published assignment becomes available to intended Students.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-007 — Grade submitted assessment

**Role:** Teacher  
**Domain:** Assessment  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ASSESSMENT, REQ-RBAC

### Steps

1. Open submissions for an assigned assessment.
2. Open a submitted attempt.
3. Grade required manual answers.
4. Save/finalize grading.

### Expected results

- Teacher can grade authorized attempts.
- Grade is persisted/audited.
- Teacher cannot grade unrelated sections.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-008 — View own teaching timetable

**Role:** Teacher  
**Domain:** Scheduling  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-SCHEDULING

### Steps

1. Open Teacher timetable.
2. Inspect today's and upcoming occurrences.

### Expected results

- Only the Teacher's authorized schedule is shown.
- Rescheduled/cancelled occurrences are represented consistently.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-009 — Teacher notification workflow

**Role:** Teacher  
**Domain:** Notifications  
**Priority:** P2  
**Execution:** hybrid  
**Requirements:** REQ-NOTIFICATIONS

### Steps

1. Open notifications.
2. Read a targeted notification.
3. Mark it read and review preferences.

### Expected results

- Notification state persists.
- Teacher receives only authorized targets.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-TCH-010 — Admin action denied

**Role:** Teacher  
**Domain:** Security  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-RBAC, REQ-PRIVACY

### Steps

1. Attempt an Admin-only action via UI if link can be reached.
2. Attempt the corresponding protected API through approved test tooling.

### Expected results

- UI does not offer unauthorized Admin action.
- Server rejects unauthorized request regardless of client behavior.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---
