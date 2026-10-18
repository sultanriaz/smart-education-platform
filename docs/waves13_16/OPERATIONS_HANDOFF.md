# Waves 13–16 operational handoff — pending real sign-off

This document is not an acceptance certificate. Assign real individuals to the
roles of release approver, database operator, incident owner and support owner
before go-live. Preserve a checkpoint ledger with timestamp, database name,
archive SHA-256, pg_restore catalog result, restore-test database ID and
operator signature for **identity_db, academic_db, attendance_db, scheduling_db,
notification_db, facility_db, learning_db, assessment_db, reporting_db,
platform_db**.

## Rollback strategy

Stop all writers/workers; validate all original archives and prior migration
heads in isolated temporary DBs; perform an operator-reviewed restore while
writers remain stopped; restore the source checkpoint using the provided
source installer rollback command; restart and run the existing 31 live checks.
A source-only rollback does **not** reverse database migrations. Do not attempt
an Alembic-only downgrade as a substitute for a ten-DB checkpoint restore.

## Alert drills

Prometheus-to-Alertmanager routing is configured, but the included sample
receivers are log-only. Configure a real approved receiver in a protected
environment; trigger a harmless synthetic alert; record the matching rule,
Alertmanager group, delivery receipt, human acknowledgement and timestamp.
No real receiver/acknowledgement evidence has been supplied here.

## WCAG 2.2 AA / pilot

Execute manual keyboard, focus-not-obscured, screen reader, mobile 320px/400%
reflow and accessible authentication checks for student, teacher, admin and
support workflows. Gather real signatories in the UAT record. Use
`scripts/record_wave15_evidence.py` to record SHA-256 over supplied evidence;
this script deliberately leaves acceptance status pending.
