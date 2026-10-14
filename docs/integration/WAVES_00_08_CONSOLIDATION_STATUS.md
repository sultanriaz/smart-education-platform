# Waves 00–08 consolidation — source and acceptance status (2026-10-14)

**Scope:** Post-B04 + post-B13/B01 v2 + JWT hotfix baseline; existing Wave 00–04 features are preserved and **not reset or replaced**. This is a code consolidation, not an assertion that all 84 backlog findings are closed.

## Added or improved in this patch

- **Wave 05:** Assessment question/type allowlist, cross-course and cross-section assignment checks, offset-aware scheduling inputs, no provisional grades in Student responses, and B01/B13-compatible grading-event dimensions. Existing autosave/teacher review remain intact; CI assessment E2E now **fails** if disposable assignment IDs are omitted rather than silently reporting skips.
- **Wave 06:** Reporting event-time conflict guards, attendance sheet reopen/cancel/re-finalize projection rebuilds, assessment dimensions, and owner-authorized Student/Teacher/Admin academic reporting routes. No Reporting DB schema migration.
- **Wave 07:** Scheduling occurrence audience metadata; SECTION + teacher fan-out; Facility approver role resolution; staged 5/20/80 second durable RabbitMQ retry queues and poison-message DLQ tests. Old retry queue is retained (no queue removal).
- **Wave 08:** HTTPS issuer and origin consistency; Identity signing key volume and key-ID Secret template; S3-only hosted Learning storage and template keys; read-only-compatible frontend runtime generation; staging/production Deployment manifests for ten event workers. These do **not** create actual hosted secrets, apply K8s manifests, or prove a successful hosted rollout.

## Acceptance not yet demonstrated or not implemented by this patch

- **Wave 00–04:** Existing implementations retained; live PostgreSQL races, owner-level authorization matrix, Wave02 Identity–Academic automatic reconciliation, B13 classroom booking conflict and B01 custom grants in *all* services still require corresponding acceptance/engineering work. Institution-dependent F03–F14 policy choices cannot be silently selected by this patch.
- **Wave 05:** B32 autosave network recovery, B33 Teacher comprehensive review, B34 released Student feedback, E02 CI disposable fixture provisioning, D09 actual races, D16 offline recovery verification are not closed by the focused source changes; E02 now fail-closes when IDs missing under CI.
- **Wave 06:** B48 real outbox/backlog gauges from owner databases to a scraped, alertable endpoint remains open. Existing metric definitions alone do not satisfy this.
- **Wave 07:** D07/D10/D12/D23 real DB/broker fault/performance acceptance not run here.
- **Wave 08:** D26 hosted provenance/CVE/signature gates and D27 real staging/production deployment, private storage persistence, TLS, network policy, Kubernetes rollout/worker recovery not run here. Provide a real Secret for `identity-service-signing-key` plus non-default `JWT_KEY_ID` and S3 credentials before deployment.

## Verification completed in build sandbox

- Assessment: 24 passed, 1 skipped.
- Reporting: 18 passed, 1 skipped.
- Notification: 39 passed, 1 skipped (trusted test host configured).
- Scheduling: 36 passed, 1 skipped.
- Learning: 35 passed, 1 skipped.
- Shared infrastructure (including RabbitMQ staging tests): 19 passed.
- Kubernetes manifest tests: 10 passed.
- Portable Python syntax checks / ZIP manifest checks / installer simulation run during packaging.

A full Windows regression, browser E2E, live 31 integrations, local Facility conflict demonstration, CI hosted gates and deployed cluster checks remain mandatory before any claim of complete Waves 00–08 closure.
