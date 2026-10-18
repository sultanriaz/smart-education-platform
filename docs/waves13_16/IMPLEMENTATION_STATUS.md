# Waves 13–16 — snapshot-derived development patch (NOT a final-wave release)

Input: uploaded `SmartEdu_Platform_Complete_Review.zip`, compared byte-for-byte.
Wave 17 is outside scope. The material herein **does not** satisfy the proposed
33-deliverable acceptance contract. Its implemented work is a meaningful subset.

## Implemented changes subject to target-environment verification

- Wave 13: Identity audit redaction/history and admin search; Platform audit
  correlation, outcome and bounded filters; setting and feature revision tables;
  optimistic concurrency, history, rollback-as-new-revision; deterministic
  percentage evaluation; search lifecycle digest/ACL revisions/de-index.
- Wave 14: Platform job input digest/idempotency and dry-run forwarding; Academic
  catalog/enrollment dry-run; Identity-owned idempotent account imports;
  support ticket requester-note filtration, bounded state changes, due dates and
  a worker-driven one-time escalation event. Reporting CSV cells neutralized.
- Wave 15: existing data-backed role dashboards preserved, filtered report paging
  and CSV consistency, governance UI revision protection, profile security
  history, additional keyboard focus defaults, real evidence hashing helper.
- Wave 16: public-edge telemetry deny routes and explicit negative exposure
  checks; existing instrumentation/rules kept; operator handoff guidance below.

## Outstanding work / acceptance blockers

**Not complete:** entire 272-scenario acceptance catalog and its 266 automated
implementations; six manual/hybrid accessibility sessions; staging 500-user
capacity; owner-verified report SQL pagination at full scale; robust export
artifact/expiry/download ACL lifecycle; all frontend import/export UX;
end-to-end support requester conversation UI; alert delivery to an actual
receiver and acknowledgement; full PostgreSQL migration and rollback drill;
UAT/pilot acceptance and operations signatories.

Do not present the patch as production-ready or run additive migrations without
independent database backups. The package contains a guarded **source-only**
installer; it does not touch the ten service databases.

## Local post-install verification (must run in the real environment)

1. Stop application writers and create verified PostgreSQL `pg_dump -Fc`
   archives of all ten service-owned DBs, preserving PostgreSQL roles/config,
   before migration. Test restore to separate temporary databases.
2. Use `scripts/local_stack.py migrate` only after reviewing Alembic heads and
   taking backups. Never use `docker compose down -v` or `git reset --hard`.
3. Run `python scripts/verify_waves13_16.py --full`. The run fails on any suite
   failure. It does **not** claim all 266 scenarios were executed.
4. Run `python scripts/verify_wave16_exposure.py --gateway http://127.0.0.1:18080`
   after bringing up the local gateway.
5. Manually verify frontend mobile/reflow/keyboard and the support conversation
   path; record actual UAT/pilot results and sign-offs.
