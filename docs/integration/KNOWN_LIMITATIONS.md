# Verification limits and unresolved requirements

Updated 2026-10-08. These are engineering records, not institutional approvals.

| Item | Actual boundary and next verification |
|---|---|
| 500-user capacity | The local generator shares one IP and three demo identities. The enabled gateway limit is 30 requests/s per IP; the 500-user workload exceeds it. A distributed representative workload and approved hardware are needed. Rejected requests are failures, not successful performance samples. |
| Service container images | Native Python APIs are verified. An Identity Docker build failed dependency resolution, then a later download failed SHA-256 verification. The exact corrupt package/cause was not identified. Hash checks remain enforced. Ten service images, image CVEs/signatures and actual Kubernetes deployment are not verified. Gateway and MinIO images were built and started locally. |
| Institutional UAT | Automated checks exercise demo roles. Real stakeholders, institutional eligibility rules, accessibility acceptance and formal signoff remain unavailable. |
| Availability and recovery | 99% availability has no sustained observation window. RTO/RPO acceptance, production backup restore and node/pod failure drills require a real environment. Local successful transactions do not prove disaster recovery or universal no-loss guarantees. |
| Bulk administration jobs | Academic provides bounded owner import/export contracts for departments, programs, years, semesters, courses, sections, students and teachers. Other owners and enrollment bulk contracts are unsupported and return explicit failure. Their imports must use owner APIs until contracts exist. |
| Search coverage | Platform indexes explicit search documents/search upsert events. Complete automatic domain indexing and authorization across domain search results are not verified. The keyboard shortcut searches workspace pages. |
| Timed assessments | Quiz duration is displayed. Automatic expiry/submission and strict duration enforcement are not yet verified or implemented as a complete workflow. Start/deadline/attempt-limit rules, saved progress, result persistence, ownership and grading are verified within their documented tests. |
| Reporting size | Snapshot scalar equality filters are implemented; unsupported filters/report types fail explicitly. Large report streaming/pagination and institutional report formats remain improvements for review. |
| Internal compatibility endpoints | Primary relationship/data-job contracts use scoped Ed25519 JWTs and messaging uses private broker credentials. Legacy event/reservation HTTP endpoints still use generated shared credentials. Full migration of those compatibility paths to scoped credentials and production key rotation requires verification. They are blocked at the public gateway. |
| Malware scanning | Development validates metadata, size, magic bytes and archive paths; required-scanner failure is closed. Production uploads require a reachable scanner. A real infected-file scanner demonstration has not been executed locally. |
| Workflow breadth | Unit suites cover additional domain rules. Browser page visits establish loading, accessibility and layout, not successful execution of every button combination. Manual grading, every campaign template and every exceptional admin workflow have not all been exercised through the browser. |

No feature was removed because the old SRS omitted it. Draft requirements use the latest directive, sprint packages, implemented contracts and working business rules. Do not relabel these limits as PASS without new evidence.
