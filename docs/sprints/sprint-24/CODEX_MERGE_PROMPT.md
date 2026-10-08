Integrate Sprint 24 Staging Environment into the actual merged Smart Education
Platform from Sprints 1–23.

FIRST inspect the real repository and current staging-related files/workflows.
Do not create a second competing staging path if Sprint 22 already contains a
stronger equivalent. Merge into one canonical flow.

The objective is to deploy and prove the exact Sprint 22 release candidate in a
production-like, isolated staging environment.

1. Staging architecture

   Read:
   - SPRINT_24_README.md
   - STAGING_ARCHITECTURE.md
   - STAGING_ACCEPTANCE_PLAN.md
   - STAGING_DATA_POLICY.md
   - STAGING_RECOVERY_DRILLS.md
   - STAGING_PROMOTION_GATE.md

   Preserve Sprint 23 architecture.

2. Reconcile actual runtime contracts

   Inspect all 12 real images:
   - internal ports
   - health route
   - readiness route
   - writable filesystem paths
   - settings/env variables
   - graceful shutdown behavior

   Update Sprint 24 staging manifests to match the real merged images.

3. No staging architecture fork

   Staging should be a smaller production-like deployment, not a separate
   monolithic/docker-only architecture.

   Keep:
   - API Gateway boundary
   - service-per-domain processes
   - DB ownership
   - Redis split
   - RabbitMQ
   - object storage
   - observability
   - Kubernetes security model

4. Real staging DNS

   Replace:
   `staging.smartedu.example.edu`

   with the approved staging hostname.

   Run:
   `python scripts/staging-preflight.py --strict`

   Placeholder DNS must fail strict mode.

5. TLS

   Provision the real staging certificate.

   Prefer the same certificate-management mechanism intended for production.

   Verify certificate chain/hostname/renewal and HTTPS redirect.

6. Kubernetes cluster

   Confirm:
   - multiple worker nodes where available
   - network-policy capable CNI
   - metrics-server
   - ingress controller
   - Pod Security Admission
   - private dependency access

   If the actual staging cluster has one node, document that node-failure testing
   remains unresolved; do not falsely mark the drill passed.

7. Stateful staging dependencies

   Reconcile `config/staging/dependencies.yaml`.

   Provision isolated staging:
   - PostgreSQL
   - Redis cache
   - Redis durable
   - RabbitMQ
   - object storage
   - email sandbox
   - observability

   Verify none use production endpoints/credentials.

8. PostgreSQL

   Create ten databases and ten least-privilege service accounts.

   Verify each service account cannot read another service DB.

   Enable backup/PITR or the staging equivalent required for restore rehearsal.

9. Redis

   Keep cache and durable state separate.

   Verify authentication/ACLs and persistence for durable Redis.

10. RabbitMQ

    Reconcile real Sprint 17 exchanges/queues/retry/DLQ.

    Enable metrics.

    Use isolated staging vhost/users.

11. Object storage

    Create staging-only private buckets/credentials.

    Enable versioning and encryption.

    Verify Sprint 18 least privilege.

12. Email

    Configure a sandbox/test provider.

    Do not use real university mailing lists.

13. Secrets

    Inspect each service Settings class.

    Rebuild the exact `<component>-secrets` contract.

    Do not apply the generated example Secret values.

    Use staging secret storage / External Secrets / equivalent approved method.

14. QA accounts

    Create dedicated staging:
    - Student
    - Teacher
    - Admin

    Credentials live only in staging CI/secret storage.

15. Deterministic QA fixtures

    Reconcile:
    `config/staging/fixture-plan.yaml`

    Build/reuse an idempotent seeder using supported APIs/service-owned commands.

    Do not directly write across service databases.

    All data must be clearly marked staging QA.

16. Sprint 22 release manifest

    Download/verify:
    - release-manifest.json
    - checksum
    - Cosign signatures
    - provenance/attestation

    All 12 application images must come from the same release candidate.

17. Staging renderer

    Run:
    `scripts/render-staging-release.py`

    Verify:
    `scripts/verify-staging-bundle.py`

    There must be no:
    - bootstrap images
    - mutable tag-only images
    - Secret examples
    - unexpected public service types

18. Migration selection

    Only components in Sprint 22 `migration_components` should produce migration
    Jobs for that release.

    Ensure every migration Job:
    - uses exact release digest
    - sees only own DB credentials
    - completes before application rollout
    - reaches exactly one Alembic head

    Migration failure must stop deployment.

19. Deployment

    Reconcile:
    `scripts/deploy-staging-k8s.ps1`

    Keep staging context guardrails.

    Never let this script silently target production.

20. Public Gateway smoke

    Inspect final Sprint 11/16 Gateway routing.

    Reconcile the default `/api/health` smoke path with an actually valid safe
    public Gateway route.

    Do not expose service `/metrics` or `/internal` merely to make the smoke pass.

21. Full live contract tests

    Run Sprint 19 live tests against staging:
    - health/readiness
    - Gateway security
    - contracts
    - authorization matrix
    - resource ownership
    - failure semantics
    - distributed idempotency

22. Student E2E

    Run full Student workflow:
    - login
    - academic context
    - timetable
    - attendance
    - learning
    - assessment attempt/submit/result
    - notification
    - facility booking
    - logout

23. Teacher E2E

    Run full Teacher workflow:
    - assigned sections
    - attendance create/finalize
    - learning publish
    - quiz publish/assign
    - manual grading
    - notification target
    - admin action denied

24. Admin E2E

    Run:
    - academic master data
    - scheduling/conflict
    - facility approval
    - reporting
    - platform operations
    - internal Gateway path blocked

25. Event paths

    Prove representative live flows:
    - Attendance -> Reporting
    - Assessment -> Reporting
    - domain event -> Notification
    - retry/DLQ/replay

    Verify idempotent inbox/outbox behavior after process restart.

26. Security

    Run Sprint 18 staging regression:
    - auth security
    - RBAC
    - Origin/cookie controls
    - upload controls
    - secret scan
    - container scan
    - least privilege

27. Performance

    Every release: Sprint 20 smoke.

    Before production readiness: run the formal SRS 500-user profile on staging
    or a dedicated production-like performance environment.

    Do not mark 500-user capability proven by smoke.

28. Observability

    Verify Sprint 21:
    - 10/10 service metric targets
    - Gateway metrics
    - JSON logs
    - HTTP traces
    - event traces
    - alerts

    There must be no unresolved critical alert at acceptance.

29. Pod failure

    Use:
    `scripts/staging-pod-failure-drill.ps1`

    Test at least:
    - api-gateway
    - attendance-service
    - assessment-service

    Verify available replicas recover.

30. Rolling update

    Use:
    `scripts/staging-rolling-update-drill.ps1`

    Confirm zero planned unavailable pods and no meaningful 5xx spike.

31. Node failure

    On multi-node staging only:
    `scripts/staging-node-failure-drill.ps1 -Confirm STAGING_ONLY`

    Verify PDB and rescheduling behavior.

32. Database recovery

    Implement provider-specific scripts for:
    - backup
    - isolated restore
    - restored-data verification

    Run:
    `staging-backup-restore-drill.ps1 -Mode DATABASE -Confirm STAGING_ONLY`

    Record RTO/result.

33. Object-storage recovery

    Implement provider-specific:
    - backup/version operation
    - restore
    - checksum/access verification

    Run the OBJECT_STORAGE drill.

34. Secret recovery and rotation

    Recreate one Secret entirely from source-of-truth secret storage.

    Rotate at least one staging DB/RabbitMQ/internal-service credential.

    Verify application recovery.

35. Network tests

    Verify:
    - only frontend/Gateway public
    - domain-service public access fails
    - DB/Redis/RabbitMQ not public
    - internal service calls still work

    If enabling strict egress, add all dependency rules first.

36. CI workflow

    Reconcile:
    `.github/workflows/staging-environment.yml`

    with any existing Sprint 22 staging workflow.

    Keep one canonical, approval-gated staging path.

    PR workflows get no staging or production kube credentials.

37. Acceptance evidence

    Archive release-scoped:
    - release manifest
    - Kubernetes rollout state
    - migration results
    - JUnit
    - Playwright
    - performance
    - observability
    - recovery drill evidence

    Never upload secrets or kubeconfig.

38. Promotion

    Read:
    `STAGING_PROMOTION_GATE.md`

    Promotion means the same image digests progress to UAT/readiness.

    Do not rebuild a "production version" after staging passed.

39. Regressions

    Run all service suites plus Sprint 18–23 verification.

Do not solve Sprint 24 by:
- using production accounts/data
- pointing staging at production DB/Redis/RabbitMQ/S3
- using one replica for everything
- rebuilding different staging images
- running migration Jobs in parallel with application rollout
- writing QA fixtures directly across service databases
- disabling NetworkPolicy/RBAC for tests
- exposing internal metrics/internal APIs
- skipping failed recovery drills
- calling a one-node local cluster a passed node-failure drill
- silently turning skipped E2E/performance/security gates into passes

At completion report:
- staging hostname/TLS status
- Kubernetes cluster/node topology
- all stateful dependency products/endpoints classification
- per-service DB/secret isolation result
- release tag + 12 digests
- migration job results
- 12 Deployment availability results
- Student E2E
- Teacher E2E
- Admin E2E
- event-flow/retry/DLQ results
- Sprint 18 security result
- Sprint 19 QA result
- Sprint 20 smoke and latest 500-user result
- Sprint 21 observability result
- pod failure results
- rolling update result
- node drain result or explicit topology limitation
- DB restore elapsed/result
- object restore result
- secret rotation result
- unresolved defects/blockers
- final staging promotion verdict
