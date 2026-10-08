# Student UAT Scenario Pack

Release tag: ____________________  
Commit SHA: ____________________  
Staging/UAT URL: ____________________  
Execution date: ____________________

Use the structured CLI run record as the source of truth for final gate evaluation. This document is a human-friendly execution worksheet.

## UAT-STU-001 — Student login and workspace access

**Role:** Student  
**Domain:** Identity  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-IDENTITY-AUTH, REQ-RBAC

### Preconditions

- Student QA account exists and is active.

### Steps

1. Open staging login page.
2. Authenticate with the approved Student QA account.
3. Open the Student workspace.

### Expected results

- Authentication succeeds.
- Student workspace loads.
- Teacher/Admin-only navigation and actions are unavailable.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-002 — View own timetable

**Role:** Student  
**Domain:** Scheduling  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-SCHEDULING, REQ-PRIVACY

### Steps

1. Open Student timetable.
2. Inspect current week/date groups.
3. Attempt to navigate available timetable views.

### Expected results

- Only the signed-in Student's authorized timetable is shown.
- Course/section/date information is understandable.
- No other Student's data is exposed.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-003 — View attendance summary and records

**Role:** Student  
**Domain:** Attendance  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ATTENDANCE, REQ-PERF-ATTENDANCE, REQ-PRIVACY

### Steps

1. Open attendance page.
2. Inspect summary percentage/status.
3. Inspect detailed records.

### Expected results

- Summary and records correspond to the Student's enrollment.
- Displayed percentage matches backend result rather than a contradictory client calculation.
- Interaction remains within the accepted Attendance performance target.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-004 — Access authorized learning resources

**Role:** Student  
**Domain:** Learning  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-LEARNING, REQ-PRIVACY

### Steps

1. Open learning resources.
2. Open a published resource assigned to the Student's course/section.
3. Download a protected file resource if available.

### Expected results

- Published authorized resources are visible.
- Protected download succeeds through authenticated application flow.
- Draft/unassigned resources are not exposed.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-005 — Complete an assigned assessment

**Role:** Student  
**Domain:** Assessment  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ASSESSMENT, REQ-PRIVACY

### Steps

1. Open assigned assessments.
2. Start an available assessment.
3. Answer objective and/or short-text questions.
4. Save answers and submit.

### Expected results

- Attempt rules are enforced.
- Answers save successfully.
- Submission completes once.
- Correct-answer keys are not exposed before/through Student read APIs.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-006 — View assessment result without answer leakage

**Role:** Student  
**Domain:** Assessment  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-ASSESSMENT, REQ-PRIVACY

### Steps

1. Open results after a graded attempt.
2. Inspect score/status and permitted feedback.

### Expected results

- Only the Student's result is visible.
- Score/status match the graded attempt.
- No protected grading data or other Student results are exposed.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-007 — Book an available facility

**Role:** Student  
**Domain:** Facility  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-FACILITY, REQ-PRIVACY

### Steps

1. Open facilities.
2. Choose a bookable facility and valid time.
3. Submit booking.
4. Open own bookings.

### Expected results

- Valid booking is accepted according to backend rules.
- Booking appears in the Student's own list.
- Conflicting/invalid time requests are rejected authoritatively.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-008 — Receive and manage notifications

**Role:** Student  
**Domain:** Notifications  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-NOTIFICATIONS, REQ-PERF-NOTIFICATION

### Steps

1. Open notifications.
2. Open an unread notification.
3. Mark it read.
4. Update available notification preferences.

### Expected results

- Unread state changes correctly.
- Preferences persist.
- Representative notification flow meets the accepted end-to-end notification target when timed.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-009 — Responsive Student core workflow

**Role:** Student  
**Domain:** Usability  
**Priority:** P1  
**Execution:** hybrid  
**Requirements:** REQ-RESPONSIVE

### Steps

1. Repeat dashboard, timetable, learning, and assessment navigation at desktop width.
2. Repeat at a mobile-width viewport.

### Expected results

- Core controls remain usable without hidden mandatory actions.
- Content does not require impractical horizontal scrolling.
- Navigation remains understandable on both layouts.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---

## UAT-STU-010 — Logout and protected-route denial

**Role:** Student  
**Domain:** Identity  
**Priority:** P0  
**Execution:** hybrid  
**Requirements:** REQ-IDENTITY-SESSION, REQ-RBAC

### Steps

1. Log out from the Student workspace.
2. Attempt to revisit a protected Student route using browser history/direct URL.

### Expected results

- Session is ended.
- Protected route is not usable after logout.
- User is redirected/re-authenticated according to the final auth contract.

### Evidence

- screenshot or test artifact
- tester notes

**Result:** ☐ PASS  ☐ FAIL  ☐ BLOCKED  ☐ WAIVED

**Tester:** ____________________

**Defect IDs / notes:** ____________________________________________

---
