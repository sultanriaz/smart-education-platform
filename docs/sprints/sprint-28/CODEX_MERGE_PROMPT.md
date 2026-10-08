Integrate Sprint 28 Production Stabilization & Operational Closure into the
actual merged Smart Education Platform from Sprints 1–27.

FIRST inspect:
- the real Sprint 27 production launch record/report/evidence
- the exact production release manifest
- Sprint 21 observability implementation
- Sprint 20 performance evidence
- Sprint 18 security hardening
- Sprint 24 recovery evidence
- Sprint 26 operational ownership/runbooks
- actual production monitoring/provider tooling

Sprint 28 is read-only/operational by default. Do not use it as an excuse for
untracked production mutation.

1. Verify Sprint 27 launch

   Run:
   `scripts/stabilization-preflight.py`

   Require:
   - launch outcome SUCCEEDED
   - completed launch record
   - all eight required launch phases PASS
   - no open SEV-1 launch incident
   - same release tag/commit
   - same production URL
   - 12 digest-pinned release images

2. Verify live immutable images

   Reconcile and run:
   `scripts/verify-live-release-images.py`

   Confirm every live Deployment image exactly matches the release manifest.

   Treat unexplained drift as a stabilization issue/security/change-control
   violation.

3. Reconcile checkpoint catalog

   Inspect:
   `config/stabilization/checkpoints.yaml`

   There are 49 generated mandatory checkpoints.

   Map each evidence requirement to a real dashboard/query/runbook/provider
   source.

   Do not delete checkpoints to get closure.

4. Observation windows

   Reconcile:
   `config/stabilization/windows.yaml`

   Generated baseline:
   - T+2h
   - T+24h
   - T+72h
   - closure

   Extend based on real academic usage patterns.

   A quiet weekend is not enough to claim normal Student/Teacher load if the
   system's normal usage is weekday-heavy.

5. Production SLO review

   Read:
   `STABILIZATION_SLO_REVIEW.md`

   Reconcile actual Sprint 21 metrics and Sprint 20 workload definitions.

6. General latency target

   Gather production evidence for:
   `95% normal interactions <=3 seconds`

   State exactly what metric represents the target.

7. Attendance target

   Gather production Attendance evidence for:
   `<=2 seconds`

   Distinguish browser end-to-end vs Gateway/backend latency.

8. Notification target

   Gather end-to-end Notification evidence for:
   `<=5 seconds`

   Include event/outbox/broker/consumer/user-visible latency where possible.

   Do not substitute enqueue response time.

9. 500-user capacity

   Keep Sprint 20 as controlled capacity evidence.

   Sprint 28 should confirm production capacity/headroom assumptions still hold.

   Do not claim normal launch traffic re-proves 500 concurrent users unless it
   actually reaches and measures that load.

10. Availability

    Review the actual Sprint 21 SLO/error-budget series.

    Distinguish stabilization-window availability from the project's >=99%
    availability target.

11. Kubernetes workloads

    Review all 12:
    - available replicas
    - restarts
    - OOMKilled
    - probe failures
    - HPA scaling
    - PDB behavior
    - node/pod events

12. Production snapshot

    Reconcile:
    `scripts/production-stabilization-snapshot.ps1`

    Keep it read-only.

    Never dump Secrets/environment variables into evidence.

13. PostgreSQL

    Review all ten service DB workloads:
    - connection utilization
    - pool exhaustion
    - lock waits
    - deadlocks
    - long transactions
    - storage growth
    - backup/PITR health
    - provider HA/replication

14. DB ownership

    Confirm no new cross-service DB grants/query shortcuts appeared after
    launch.

15. Redis

    Review cache and durable Redis separately.

    Include:
    - memory
    - evictions
    - connections
    - errors
    - latency
    - persistence/replication for durable tier

16. RabbitMQ

    Review:
    - ready/unacked
    - publish/consume rates
    - consumer count
    - retries
    - DLQ
    - connection/channel failures

    Diagnose trends, not only absolute queue counts.

17. Outbox

    Verify outbox backlog and oldest-pending age for event-producing services.

    There should be no growing backlog left unexplained.

18. Inbox/idempotency

    Review duplicate delivery/retry behavior and incidents.

    Confirm no duplicate business side effects.

19. Reporting projections

    Verify selected production-safe events project correctly into Reporting.

    Preserve event-driven read model.

    Do not add direct cross-service DB queries as a stabilization shortcut.

20. Identity

    Review:
    - login errors
    - refresh
    - logout/session revocation
    - JWKS
    - lockout/security anomalies
    - inactivity behavior

21. Student production usability

    Review production-safe smoke plus support issues for:
    - dashboard
    - timetable
    - attendance
    - learning
    - assessment
    - notifications/facilities as deployed

22. Teacher production usability

    Review:
    - assigned sections/rosters
    - attendance
    - learning
    - assessment
    - timetable

23. Admin production usability

    Review:
    - academic/admin workflows
    - scheduling/facility
    - reporting
    - platform operations

24. Security review

    Read:
    `STABILIZATION_SECURITY_REVIEW.md`

    Review:
    - suspicious auth
    - RBAC/privacy reports
    - public exposure drift
    - secret leakage
    - operator/admin access
    - container/runtime alerts
    - upload/security alerts
    - JWT/JWKS errors

25. Secret evidence review

    Inspect Sprint 27/Sprint 28 evidence before archiving.

    Remove/redact:
    - passwords
    - tokens/cookies
    - private keys
    - connection strings with credentials
    - kubeconfig
    - PII

26. Observer hooks

    Implement:
    - STABILIZATION_METRICS_CHECK_SCRIPT
    - STABILIZATION_MESSAGING_CHECK_SCRIPT
    - STABILIZATION_SECURITY_CHECK_SCRIPT
    - STABILIZATION_SUPPORT_CHECK_SCRIPT

    These must be read-only.

    Exit non-zero on material validation failure.

27. Stabilization workflow

    Reconcile:
    `.github/workflows/production-stabilization.yml`

    Keep:
    - manual workflow
    - production protected environment
    - dedicated production runner
    - PRODUCTION_READ_ONLY confirmation
    - read-only commands

    Do not add deploy/migrate/delete/restart actions.

28. Support review

    Review all production support intake from launch window.

    Classify and own each real issue.

29. Issue severity

    Read:
    `STABILIZATION_INCIDENT_TRIAGE.md`

    Do not lower severity to pass closure.

30. Structured issues

    Use:
    `record-stabilization-issue.py`

    Link issue to launch incident and/or hotfix release when appropriate.

31. Closure issue policy

    Default:
    - open SEV1 = 0
    - open SEV2 = 0
    - open SEV3 = 0

    Do not convert unresolved SEV3 into a follow-up merely for closure.

32. Follow-ups

    Use:
    `record-stabilization-followup.py`

    HIGH follow-ups must be CLOSED before gate pass.

    MEDIUM/LOW need owner/target.

33. Hotfix process

    Read:
    `HOTFIX_PROCESS.md`
    and
    `config/stabilization/hotfix-policy.yaml`

    Every hotfix is a new immutable release.

34. Hotfix release path

    Reuse:
    - Sprint 22 build/SBOM/sign/provenance
    - Sprint 23/24 staging where risk warrants
    - affected Sprint 18/19 tests
    - protected Sprint 27 production deployment
    - Sprint 27 rollback guardrails

35. Security hotfix

    Require SecurityOwner review.

36. User-visible behavior hotfix

    Require ProductOwner review.

37. Database hotfix

    Preserve service DB ownership.

    No manual cross-service SQL.

38. Recovery

    Confirm backup schedule remained healthy after go-live.

    Review owners/escalation from Sprint 26.

39. Operations docs

    Update only actual current:
    - hostnames
    - owners
    - alert links
    - provider names
    - runbook paths
    - release procedures

    Do not put secrets in docs.

40. Support/operations handoff

    Read:
    `SUPPORT_OPERATIONS_HANDOFF.md`

    Record actual ownership acceptance.

41. Structured stabilization run

    Use:
    - initialize-stabilization-run.py
    - record-stabilization-checkpoint.py
    - record-stabilization-issue.py
    - record-stabilization-followup.py
    - record-stabilization-approval.py
    - complete-stabilization-run.py
    - verify-stabilization-gate.py

    Do not bulk-mark checkpoints PASS without evidence.

42. Closure approvals

    Record actual:
    - TechnicalLead
    - OperationsOwner
    - SecurityOwner
    - ProductOwner
    - ProjectSupervisor

    CI must not fabricate approvals.

43. Disposition

    Allowed passing dispositions:
    - STABLE
    - STABLE_WITH_FOLLOWUPS

    UNSTABLE must fail.

44. Evidence index

    Generate:
    `PRODUCTION_STABILIZATION_EVIDENCE_INDEX.json`

    Review contents before archival.

45. Final report

    Generate:
    `PRODUCTION_STABILIZATION_REPORT.md`

    Verify it matches the structured run.

46. FYP closure

    Read:
    `FYP_OPERATIONAL_CLOSURE.md`

    Archive non-secret:
    - requirements/traceability
    - architecture
    - test/security/performance
    - UAT
    - readiness
    - launch
    - stabilization
    - release manifests
    - evidence indexes
    - follow-up register

47. Future changes

    Make clear that future releases repeat the controlled lifecycle.

    Sprint 28 completion does not authorize direct untracked production edits.

Do not solve Sprint 28 by:
- marking a quiet snapshot as long-term availability proof
- claiming launch traffic re-proves 500-user load
- hiding SEV1/SEV2/SEV3 as follow-ups
- bulk-marking checkpoints PASS
- mutating production from the stabilization workflow
- manually patching running containers
- bypassing release identity for hotfixes
- adding direct cross-service DB queries
- suppressing critical alerts without explanation
- deleting RabbitMQ/DLQ/outbox evidence to look healthy
- archiving secrets or PII
- fabricating operational approvals
- closing the FYP while ownership/backups/support are unresolved

At completion report:
- final production release tag/commit/12 image digests
- Sprint 27 launch ID
- observation window used
- 12 workload health result
- general/Attendance/Notification latency evidence
- availability observation
- DB connection/lock/backup status
- Redis cache/durable status
- RabbitMQ retry/DLQ/backlog status
- outbox/inbox status
- security review result
- Student/Teacher/Admin production status
- support issue summary
- stabilization issues by severity/status
- hotfix releases, if any
- follow-ups by severity/owner
- five approval decisions
- 49-checkpoint result
- final disposition
- evidence/report/index paths
- final operations/FYP closure statement
