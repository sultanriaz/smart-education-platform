Integrate Sprint 27 Production Deployment into the actual merged Smart
Education Platform from Sprints 1–26.

FIRST inspect:
- exact Sprint 22 release manifest approved by Sprint 26
- Sprint 26 readiness run/report/GO decision
- Sprint 23 production topology/manifests
- Sprint 24 staging deployment evidence
- Sprint 25 UAT evidence
- current production infrastructure automation
- current GitHub production environment/runner configuration

Sprint 27 executes production. Do not weaken the Sprint 26 gate to make
deployment easier.

1. Exact immutable release

   Record:
   - release tag
   - full commit SHA
   - all 12 image digests

   Run:
   `scripts/compare-release-manifests.py`

   Production candidate must exactly match the Sprint 26-approved candidate.

2. Verify readiness

   Run:
   `scripts/verify-readiness-gate.py`

   Require:
   - all mandatory checks PASS
   - final decision GO or GO_WITH_CONDITIONS
   - five approvals
   - no blocking readiness risk

   Do not deploy with a failing readiness run.

3. Reconcile production context

   Set the actual:
   `PRODUCTION_KUBE_CONTEXT`

   Keep the active-context equality guard in:
   `scripts/deploy-production-k8s.ps1`

   Do not replace it with a guessed context-name check.

4. Reconcile production URL

   Set:
   `SMARTEDU_PRODUCTION_URL`

   Must use real HTTPS production DNS.

   No `.example.*` hostname may survive.

5. Sprint 23 production bundle

   Confirm actual:
   - container ports
   - probes
   - ConfigMap keys
   - secret references
   - namespace
   - network policies
   - Ingress class
   - TLS secret
   - HPA/PDB
   - resource budgets

   Render from the exact release manifest.

6. Verify production bundle

   Run both:
   - Sprint 23 `verify-k8s-bundle.py`
   - Sprint 27 `verify-production-bundle.py`

   Preserve:
   - 12 Deployments
   - 12 ClusterIP Services
   - 12 HPAs
   - 12 PDBs
   - digest-pinned images
   - >=2 replicas
   - RollingUpdate
   - maxUnavailable=0
   - probes/resources/security
   - only frontend/API Gateway public

7. Supply-chain verification

   Before deployment verify Sprint 22:
   - release checksum
   - registry digest
   - Cosign signature
   - provenance/attestation
   - SBOM/vulnerability policy

   Add the exact provider/registry verification commands to the production
   workflow if the current release promotion path does not already enforce them.

8. Reconcile migration commands

   Inspect every backend Docker image/workdir.

   Update:
   `config/launch/components.yaml`

   The generated command:
   `python -m alembic -c alembic.ini upgrade head`
   is only a baseline.

   Verify actual:
   - alembic.ini path
   - working directory
   - env names
   - secret keys
   - write paths
   - timeout behavior

9. Reconcile migration set

   Sprint 22 `migration_components` must reflect the actual code/schema changes
   in this release.

   Do not run all ten migrations unconditionally.

10. Migration safety

    Preserve `render-production-migrations.py`.

    Every migration Job must:
    - use exact release digest
    - use only its own service Secret
    - runAsNonRoot
    - disable privilege escalation
    - use read-only root filesystem plus /tmp volume
    - have backoffLimit=0

11. Serial migration execution

    Preserve:
    `run-production-migrations.py`

    Migrations execute one Job at a time.

    If the reviewed release has a specific dependency ordering, encode that
    ordering explicitly rather than relying on set/alphabetical order.

12. Production backup hook

    Implement the real:
    `PRODUCTION_BACKUP_SCRIPT`

    It must:
    - verify/create the approved pre-change recovery point
    - exit non-zero on failure
    - emit backup/PITR reference on final output line

    Test this hook safely before launch.

13. Backup must precede migration

    Keep the sequencing:
    foundation -> Secret validation -> backup -> migrations -> app rollout.

    Do not let application rollout begin if backup/migration fails.

14. Secret checker

    Reconcile:
    `production-secret-check.py`

    with actual workload secret needs.

    If frontend/Gateway no longer reference Secrets, remove those required Secret
    names and reconcile Deployments too.

    Never create dummy secrets simply to make the check green.

15. Foundation ownership

    Decide whether Sprint 27 may apply:
    - Namespace
    - ServiceAccounts
    - ConfigMap
    - NetworkPolicies
    - Ingress

    or whether those are owned by Terraform/provider/platform automation.

    If infrastructure owns them, change the split/deploy flow so application
    deployment cannot unintentionally override infrastructure state.

16. Production runner

    Reconcile:
    `.github/workflows/production-deploy.yml`

    Keep:
    `environment: production`

    Configure required reviewers.

    Use a dedicated production runner or approved production deployment identity.

17. Least privilege

    The runner should have only the required namespace/resource permissions.

    Avoid shared cluster-admin human kubeconfigs.

18. Sprint 26 readiness evidence asset

    The generated workflow expects:
    - release-manifest.json
    - production-readiness-run.json
    - SHA256SUMS

    as release assets.

    Reconcile to the actual evidence store while retaining checksum and identity
    validation.

19. Public smoke

    Reconcile:
    `config/launch/smoke.yaml`

    The generated Gateway path `/api/health` is a baseline only.

    Use a valid safe public route.

    Do not expose internal/metrics routes.

20. Production-safe Student/Teacher/Admin smoke

    Implement:
    `PRODUCTION_ROLE_SMOKE_SCRIPT`

    Use dedicated production smoke identities.

    Prefer read-only/minimally invasive flows:
    - Student login/own context/logout
    - Teacher login/assigned context/logout
    - Admin login/safe dashboard/logout

    Do not mutate real academic/attendance/assessment data unless an explicitly
    designed production canary workflow exists.

21. Production-safe event smoke

    Implement:
    `PRODUCTION_EVENT_SMOKE_SCRIPT`

    Use a harmless canary event.

    Verify selected:
    - outbox
    - RabbitMQ
    - consumer
    - inbox/idempotency
    - Reporting/Notification projection where safe

    Never notify real users accidentally.

22. Production observability hook

    Implement:
    `PRODUCTION_OBSERVABILITY_CHECK_SCRIPT`

    It should fail on:
    - missing critical targets
    - critical alert
    - unsafe DB/broker/Redis state
    - clearly broken telemetry pipeline

23. Deploy

    Execute:
    `deploy-production-k8s.ps1 -Confirm PRODUCTION_DEPLOY`

    Do not remove explicit confirmation or context checks.

24. Migration failure

    On failure:
    - stop rollout
    - capture Job logs
    - verify DB state
    - assess transaction state
    - choose forward-fix vs restore

    Never automatically call Alembic downgrade.

25. Application rollout

    Apply exact rendered application resources.

    Wait for all 12 Deployment rollouts.

    `kubectl apply` success alone is not rollout success.

26. Rollout monitoring

    Watch Sprint 21 dashboards during rollout:
    - 5xx
    - p95/p99
    - DB connections/locks
    - RabbitMQ queues/DLQ
    - Redis
    - pod restarts/OOM
    - outbox backlog

27. Postdeploy validation

    Run:
    `production-postdeploy-validation.ps1 -Confirm PRODUCTION_SAFE_VALIDATION`

    All role/event/observability hooks must PASS.

28. Monitoring snapshots

    Use:
    `production-monitoring-snapshot.ps1`

    Capture Kubernetes state without Secret values.

29. Abort authority

    Reconcile:
    `config/launch/abort-criteria.yaml`
    and Sprint 26 rollback/abort criteria.

    Name the operator who can halt deployment immediately.

30. Launch incidents

    Use:
    `record-launch-incident.py`

    Keep incident evidence/timeline.

    Open SEV1 blocks successful launch gate.

31. Application rollback

    Use the separate protected rollback workflow.

    Require:
    - explicit PRODUCTION_ROLLBACK
    - explicit SCHEMA_COMPATIBLE

    Render the previous immutable release and update Deployments only.

32. No DB downgrade

    Preserve the hard boundary:
    application rollback != database downgrade.

    If previous application is schema-incompatible, use:
    - forward fix
    - data repair
    - PITR/restore
    as approved by the incident plan.

33. Rollback supply chain

    Before redeploying a previous release, verify that previous release manifest
    is trusted, digest-pinned, and approved as the rollback candidate.

34. Launch record

    Use:
    - initialize-launch-record.py
    - record-launch-phase.py
    - record-launch-backup-reference.py
    - record-launch-incident.py
    - complete-launch-record.py
    - verify-launch-gate.py

    Do not manually edit PASS statuses to manufacture a successful record.

35. Successful launch definition

    Required phases PASS:
    - preflight
    - backup
    - migrations
    - application-rollout
    - public-smoke
    - role-smoke
    - event-smoke
    - observability

    Plus:
    - no open SEV1
    - completed record
    - outcome SUCCEEDED

36. Launch evidence

    Follow:
    `LAUNCH_EVIDENCE_POLICY.md`

    Never archive:
    - passwords
    - cookies/JWTs
    - private keys
    - DB/broker/S3 credentials
    - kubeconfig
    - Secret values
    - real PII

37. Evidence index

    Generate:
    `PRODUCTION_LAUNCH_EVIDENCE_INDEX.json`

    Review evidence files before uploading CI artifacts.

38. Launch report

    Generate:
    `PRODUCTION_LAUNCH_REPORT.md`

    Verify phase/incident/outcome information matches the structured record.

39. GitHub workflow failure

    Keep production workflow behavior:
    capture state, do not auto-rollback.

    Recovery decision remains explicit.

40. Production rollback workflow

    Reconcile:
    `.github/workflows/production-rollback.yml`

    Keep environment approval and explicit schema-compatibility input.

41. Post-launch monitoring

    Follow:
    `PRODUCTION_LAUNCH_MONITORING.md`

    Maintain intensive monitoring for the defined initial window, then extended
    observation.

42. Sprint 28 handoff

    Read:
    `SPRINT_28_HANDOFF.md`

    Handoff:
    - exact production release
    - launch record/report/index
    - backup reference
    - migration evidence
    - open incidents/issues
    - monitoring observations
    - Sprint 26 conditions/risks

Do not solve Sprint 27 by:
- deploying a different build than UAT/readiness
- using mutable `latest`
- running migrations after new app pods start
- skipping the backup checkpoint
- applying migrations to another service DB
- running destructive smoke tests against real users/data
- exposing `/internal` or `/metrics`
- auto-rolling back the DB
- auto-rolling back application when schema compatibility is unknown
- marking failed/skipped phases PASS
- hiding launch alerts/incidents
- storing secrets/kubeconfig in evidence
- bypassing protected production environment approval
- calling `kubectl apply` success a completed launch

At completion report:
- production release tag/commit/12 digests
- readiness run ID/decision
- backup/PITR reference
- migration components and results
- 12 Deployment rollout results
- production DNS/TLS/public smoke
- Student safe smoke
- Teacher safe smoke
- Admin safe smoke
- event smoke
- observability/critical-alert result
- first 30-minute launch metrics
- launch incidents
- rollback/abort actions if any
- final launch outcome
- launch gate result
- launch evidence/report/index paths
- exact Sprint 28 handoff state
