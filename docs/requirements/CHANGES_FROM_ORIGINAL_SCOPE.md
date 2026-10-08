# Changes from original scope — draft

Updated 2026-10-08. The old SRS is outdated; no approved revision was supplied. These are engineering changes, not invented institutional scope approvals.

Implemented: chronological integration of available sprints 4–28; runtime contracts/security/telemetry; browser cookie authentication; missing Academic downstream contracts; encrypted Identity recovery delivery; durable publishers/consumers; migration/dependency/gateway/local infrastructure repairs; premium responsive shared frontend; route splitting; private cache cleanup; bounded requests; stronger upload validation; draft as-built requirements.

Additional verified repairs: PostgreSQL JSON query compatibility; real attendance totals and obsolete UI routes; safe persisted assessment grade/answer responses and resumption; bounded connection reuse without shared caller credentials/cookies; report equality filters; service registry origin allowlist; non-root gateway/MinIO runtime; scoped Academic administration jobs. The 500-user target and security throttles are retained even when local measurements fail acceptance.

Preserved: ten independent services/schemas; Student/Teacher/Admin functionality; existing business rules and quality targets; original sprint archives and Git recovery checkpoint. The legacy backend scaffold is retained but is not the active ten-service runtime.

Unresolved/proposed: production sizing/environment; institutional eligibility/verification policy; approved load profile; formal availability/DR acceptance; supported remote import/export adapters; institutional UAT/signoff. These are not silently presented as verified features.

See [functional status](FUNCTIONAL_REQUIREMENTS.md) and [quality status](NON_FUNCTIONAL_REQUIREMENTS.md) for features not yet verified. Status updates must derive from actual test evidence.
