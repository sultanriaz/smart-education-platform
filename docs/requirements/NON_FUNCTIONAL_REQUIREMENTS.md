# Draft non-functional requirements

Updated 2026-10-08. Targets retained from the directive and sprint quality documents.

| ID | Target / implemented controls | Evidence status |
|---|---|---|
| NFR-01 | At least 95% of normal interactions within 3 seconds; route splitting/bounded fetch | Corrected 20-user/120s diagnostic CSV: 799 requests, zero failures, P95 65 ms/P99 980 ms; browser timing records in delivery report; institutional workload not approved |
| NFR-02 | 500 concurrent users under approved workload; sprint `srs-500`: 500 users, spawn 25/s, 600s | Local diagnostic exceeds the enabled per-IP throttle; fails the no-errors expectation. Approved distributed workload/hardware acceptance remains pending; exact clean-run counts in delivery report |
| NFR-03 | Attendance operations within 2 seconds; bounded pools/transactional bulk writes | Read operations measured in mixed smoke profile; one real bulk-write/read-back sample 0.063s; successful write-load percentile target not verified |
| NFR-04 | Notification delivery/visibility within 5 seconds; durable workers and 4s foreground polling | Real announcement visibility under one second in recorded local samples; delivery under load is not a universal guarantee |
| NFR-05 | JWT/RBAC/ownership, Argon2, scoped service JWTs, HttpOnly rotation, policy/lockout, private caches/storage, upload validation | Isolated suites and real cookie/recovery/ownership/internal-scope/S3 checks pass; image CVEs, legacy internal credential migration, rotation and real scanner verification pending |
| NFR-06 | Approximately 10-minute inactivity protection; frontend timer/revocation/cache cleanup | Real browser clock: still signed in after 9 minutes, logout after another 61 seconds, reload remains logged out |
| NFR-07 | At least 99% availability; health/readiness/retry/monitoring tooling | Sustained availability not measured locally |
| NFR-08 | No normal-operation data loss; owned transactions/outbox confirmations/durable queues/inbox deduplication | Real committed broker effects and recovery delivery; duplicate/retry controls unit verified; failure/recovery drills pending; SMTP is at least once across a post-send crash |
| NFR-09 | Accepted recovery objectives; backup/restore/DR tooling | Final RTO/RPO decision and real drills unresolved |
| NFR-10 | Usable at 320/375/768/1024/1440+; mobile navigation/table overflow/touch controls | All role pages checked at five widths without overflow; real mobile drawer verified |
| NFR-11 | Keyboard/labels/focus/contrast/reduced motion | Zero axe violations in recorded WCAG 2 A/AA and 2.1 AA page scans; keyboard focus/Escape verified; human acceptance still pending |
| NFR-12 | Independent ownership, bounded resources, reproducible delivery | Per-service tests/migrations/local scripts and ten real container/API checks verified; external delivery unverified |

Security throttles remain enabled. Single-IP load rejection must be distinguished from service capacity. Smoke measurements do not establish production scalability, availability, or disaster recovery guarantees. Required-scanner failure rejects new uploads; development scanning is optional and labelled.
