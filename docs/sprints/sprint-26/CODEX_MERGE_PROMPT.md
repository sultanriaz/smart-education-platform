Integrate Sprint 26 Production Readiness into the actual merged Smart Education
Platform from Sprints 1–25.

FIRST inspect:
- the final SRS
- the exact Sprint 22 release manifest
- Sprint 23 production topology/manifests
- Sprint 24 staging acceptance evidence
- Sprint 25 UAT run/report/sign-offs
- Sprint 18–21 security/performance/observability evidence

Sprint 26 is a GO/NO-GO gate. It must not deploy production.

1. Preserve exact release identity

   Identify the immutable release accepted by Sprint 25.

   Verify:
   - release tag
   - full commit SHA
   - all 12 image digests

   Run:
   `scripts/compare-release-manifests.py`

   The Sprint 27 candidate must be identical.

2. Reconcile readiness catalog

   Inspect:
   `config/readiness/checks.yaml`

   There are 59 generated mandatory checks.

   Reconcile titles/evidence references with the actual repository and
   institutional deployment environment.

   Do not remove a check merely because evidence is inconvenient to obtain.

3. Reconcile governance roles

   Generated roles:
   - TechnicalLead
   - OperationsOwner
   - SecurityOwner
   - ProductOwner
   - ProjectSupervisor

   Map them to actual project/institution owners.

   Preserve five independent approval responsibilities unless there is a
   documented organizational reason to merge roles.

4. UAT evidence

   Confirm Sprint 25:
   - completed run
   - P0 PASS
   - P1 PASS
   - >=95% overall pass rate
   - 0 open BLOCKER/CRITICAL/MAJOR
   - five UAT sign-offs
   - gate PASS

   Mark PR-UAT checks PASS only from real evidence.

5. Production hostname

   Replace every remaining placeholder production hostname.

   Read:
   `config/deployment/production-topology.yaml`

   Strict readiness must fail while example domains remain.

6. Production bundle

   Render the Sprint 23 production bundle from the same release manifest.

   Run:
   `scripts/verify-production-bundle.py`

   Confirm:
   - 12 Deployments
   - 12 ClusterIP Services
   - 12 HPAs
   - 12 PDBs
   - exact @sha256 images
   - >=2 replicas
   - RollingUpdate
   - maxUnavailable=0
   - readiness/liveness
   - resources
   - pod security
   - TLS Ingress
   - only frontend/API Gateway public

7. DNS/TLS

   Validate the real production hostname and certificate.

   Reconcile:
   `scripts/check-production-surface.py`

   Use the actual safe public Gateway health/smoke route.

   Do not expose an internal route to make this check pass.

8. Kubernetes cluster

   Verify the actual production cluster:
   - multiple worker nodes / HA design
   - ingress controller
   - metrics-server
   - network-policy capable CNI
   - Pod Security Admission
   - namespace/deployment identity permissions
   - access auditing

9. Public exposure

   Audit Services, Ingress, cloud load balancers, firewalls/security groups.

   Public:
   - frontend
   - API Gateway

   Private:
   - 10 domain/platform APIs
   - PostgreSQL
   - Redis
   - RabbitMQ
   - object-storage admin plane
   - observability/admin surfaces unless explicitly protected
   - Kubernetes API except approved management access

10. PostgreSQL

    Verify:
    - 10 service databases
    - 10 least-privilege accounts
    - no cross-service DB grants
    - TLS/private networking
    - HA/failover
    - PITR
    - monitoring
    - connection limits

11. Restore evidence

    Use the latest successful Sprint 24 restore drill.

    If production uses a materially different provider/topology, run an
    appropriate provider-specific recovery rehearsal before GO.

12. RTO/RPO

    Complete:
    `DR_RTO_RPO_DECISION.md`

    Reconcile with the real SRS recovery requirements.

    Do not claim an RTO/RPO that has not been demonstrated or contractually
    supported.

13. Redis

    Keep:
    - cache tier
    - durable tier

    Verify ACL/auth, private networking, HA/persistence/recovery according to
    their reliability roles.

14. RabbitMQ

    Verify:
    - HA
    - durable/quorum topology where required
    - retry/DLQ
    - metrics
    - private access
    - outbox/inbox reliability preserved

15. Object storage

    Verify:
    - private buckets
    - encryption
    - versioning
    - lifecycle
    - least privilege
    - recovery path

16. Production secrets

    Inspect actual service settings and secret inventory.

    Confirm no secret appears in:
    - Git
    - images
    - logs
    - CI artifacts
    - readiness evidence

    Verify rotation plans for all credential classes.

17. Identity keys

    Confirm production JWT/JWKS keys, issuer/audience, rotation, reset peppers,
    encryption keys, and downstream trust.

    Do not introduce a different auth contract from staging.

18. Sprint 18 security

    Confirm current release evidence for:
    - authentication
    - RBAC/ownership
    - Origin/cookie protections
    - upload security
    - secret scan
    - dependency/container scan
    - least privilege

19. Sprint 22 supply chain

    Verify all 12:
    - digest
    - checksum
    - SBOM
    - provenance
    - Cosign signature/attestation

20. Sprint 20 performance

    Confirm release/environment evidence for:
    - general p95 <=3s
    - Attendance p95 <=2s
    - Notification p95 <=5s
    - >=500 concurrent users

    Do not substitute smoke-test evidence for the 500-user acceptance result.

21. Connection budget

    Recalculate database connections at maximum HPA replicas.

    Include:
    `max_replicas × (pool_size + max_overflow)`

    Verify provider/admin reserve remains safe.

22. Sprint 21 observability

    Confirm production/managed equivalents for:
    - metrics
    - logs
    - traces
    - alerts
    - SLO dashboards
    - critical alert routing
    - runbooks

    Verify telemetry failure does not break business APIs.

23. Operations ownership

    Complete:
    `OPERATIONS_OWNERSHIP.md`

    Assign primary/backup owners for launch.

24. Incident response

    Reconcile:
    `INCIDENT_RESPONSE_HANDOFF.md`

    Name:
    - incident lead
    - technical lead
    - operations owner
    - security escalation
    - product/business contact

25. Change freeze

    Activate:
    `CHANGE_FREEZE_POLICY.md`

    A changed application digest means a new release candidate and requires
    appropriate staging/UAT/readiness reruns.

26. Migration plan

    Read:
    `MIGRATION_PRODUCTION_RUNBOOK.md`

    For each migration component document:
    - target DB
    - exact image digest
    - expected duration
    - lock/table rewrite risk
    - backup checkpoint
    - owner
    - abort threshold
    - post-migration verification
    - forward-fix strategy

27. Rollback and abort

    Read:
    `ROLLBACK_AND_ABORT_CRITERIA.md`

    Confirm:
    - previous digest-pinned release exists
    - schema compatibility known
    - abort authority assigned
    - forward-fix/PITR path ready

    Do not use automatic production DB downgrade.

28. Production data bootstrap

    Reconcile:
    `PRODUCTION_DATA_BOOTSTRAP.md`

    Do not seed Sprint 24 QA data in production.

    Real academic data import needs owner, validation, dry run, error counts, and
    correction strategy.

29. Launch communications

    Complete:
    `LAUNCH_COMMUNICATIONS.md`

    Define maintenance/user impact, support route, status channel, and post-launch
    communication.

30. Readiness evidence

    Store non-secret evidence under:
    `readiness/evidence/<run-id>/`

    Generate:
    `PRODUCTION_EVIDENCE_INDEX.generated.json`

    Review files before archiving. Do not include secrets/kubeconfig.

31. Structured readiness run

    Use:
    - initialize-readiness-run.py
    - record-readiness-check.py
    - record-readiness-risk.py
    - record-readiness-approval.py
    - complete-readiness-run.py
    - verify-readiness-gate.py

    Do not bulk-mark checks PASS without real evidence.

32. Risk policy

    Default gate permits:
    - 0 open BLOCKER
    - 0 open CRITICAL
    - 0 open HIGH

    MEDIUM/LOW risks still require owner and mitigation/acceptance.

    Do not downgrade risk severity solely to pass the gate.

33. Approvals

    Record actual decisions from:
    - TechnicalLead
    - OperationsOwner
    - SecurityOwner
    - ProductOwner
    - ProjectSupervisor

    CI must not fabricate approvals.

34. Go/no-go

    Follow:
    `GO_NO_GO_PROCESS.md`

    Record:
    - GO
    - GO_WITH_CONDITIONS
    - NO_GO

    NO_GO must fail the gate.

35. Human launch runbook

    Reconcile:
    `GO_LIVE_RUNBOOK.md`

    Add actual:
    - time window
    - step owners
    - commands/deployment mechanism
    - monitoring links
    - backup identifier method
    - abort communication channel

36. CI workflow

    Merge:
    `.github/workflows/production-readiness.yml`

    with existing CI.

    This workflow validates readiness tooling/release identity only.

    It must not deploy production.

37. Generate final report

    Run:
    `scripts/generate-readiness-report.py`

    Verify it matches the structured run.

38. Sprint 27 handoff

    Read:
    `SPRINT_27_HANDOFF.md`

    Handoff must include:
    - exact release manifest
    - checksum/signature evidence
    - rendered production bundle
    - readiness run JSON/report
    - evidence index
    - risk register
    - GO decision
    - migration plan
    - rollback/abort plan
    - operations ownership

39. Full regression evidence

    Confirm current evidence from Sprints 18–25 is tied to the exact release.

Do not solve Sprint 26 by:
- marking missing evidence PASS
- changing image digests after UAT
- lowering performance/SRS targets
- lowering risk severity to get GO
- inventing human approvals
- using production secrets in evidence
- exposing internal services for convenience
- skipping restore evidence
- assuming DB downgrade is safe
- using `latest`
- calling placeholder DNS/TLS production-ready
- deploying production from this sprint's readiness workflow

At completion report:
- exact release tag/commit/12 image digests
- final production hostname/TLS status
- Kubernetes production topology/status
- DB ownership/HA/PITR status
- Redis/RabbitMQ/object-storage status
- secret/key rotation status
- Sprint 18 security result
- Sprint 20 performance/500-user result
- Sprint 21 observability/alerts result
- Sprint 25 UAT result
- migration plan status
- rollback/abort readiness
- restore drill/RTO/RPO status
- open risks by severity
- five approval decisions
- 59-check readiness result
- final GO/GO_WITH_CONDITIONS/NO_GO decision
- exact Sprint 27 handoff artifact identity
