# Sprint 22 Integration Checklist

Sprint 22 assumes Sprints 1–21 are merged.

1. Extract at repository root and install `libs/python/smartedu_cicd`.
2. Inspect actual Dockerfile locations/service names and reconcile `config/cicd/components.yaml`; do not guess around missing Dockerfiles.
3. Reconcile `ci.yml` with existing Sprint-specific workflows. Preserve stronger existing PostgreSQL race, security, observability, and frontend tests instead of replacing them.
4. Make all service test installs deterministic. Prefer lock/constraint files already present in the repository.
5. Ensure every Python service has one Alembic head and that existing clean-DB/round-trip/drift tests remain required.
6. Merge Sprint 18 security workflow with `supply-chain.yml` to avoid duplicate scans while retaining secret scan, Bandit, pip-audit, npm audit, Trivy, and container hardening checks.
7. Configure branch protection from `BRANCH_PROTECTION.md` after final check names stabilize.
8. Configure GitHub Environment `staging` with required reviewers and variables `STAGING_COMPOSE_FILES`, `STAGING_HEALTH_URL`, optional `STAGING_BACKUP_SCRIPT`, and secret environment files on the runner. Do not store `.env.staging` in Git.
9. Update real Compose service image fields to consume the rendered image variables such as `IDENTITY_SERVICE_IMAGE`, `FRONTEND_IMAGE`, and `API_GATEWAY_IMAGE`.
10. Keep infrastructure stateful services (PostgreSQL/Redis/RabbitMQ/MinIO/observability) out of the application release image manifest unless the architecture later intentionally versions them as application components.
11. Test `ci-plan.py` on service-only, shared-library, frontend-only, and Gateway-only diffs.
12. Test release tag validation. A release tag must be immutable and point to a commit contained in `main`.
13. Run one pre-release tag in a non-production registry/project if necessary and verify all 12 images build successfully.
14. Verify each release image has an SBOM, provenance attestation, keyless Cosign signature, OCI source/revision/version labels, and no HIGH/CRITICAL unaccepted vulnerabilities.
15. Verify `release-manifest.json` contains exactly 12 unique components and all refs are digest pinned.
16. Reconcile migration detection with actual Alembic directory layouts. The generated detector understands common `/migrations/` and `/alembic/versions/` layouts; extend only to real layouts found in the repository.
17. Test staging backup hook before any migration-bearing deployment. A backup failure must block deployment.
18. Test staging deploy for a no-migration release, then a safe additive migration release.
19. Validate migration execution uses each release image, not an arbitrary developer environment.
20. Validate health/readiness and Sprint 19 live smoke after staging deployment.
21. Run Student, Teacher, and Admin E2E after promotion.
22. Test rollback to a prior image manifest only with a schema-compatible release. Confirm no automatic database downgrade occurs.
23. Test a failed post-deploy health check and confirm operators receive enough evidence to choose forward-fix or safe image rollback; do not blindly auto-downgrade DB state.
24. Configure GHCR package retention so release-tagged/digest-referenced images are retained. Never garbage-collect an image still referenced by a supported release manifest.
25. Keep staging/production credentials on deployment runners/environments only. Build/PR jobs must not receive them.
26. Prevent untrusted PRs from running on self-hosted deployment runners.
27. Re-run Sprint 18 supply-chain security, Sprint 19 full QA, Sprint 20 performance baseline, and Sprint 21 observability config after workflow consolidation.
28. Archive release evidence: manifest/checksum, image digests, attestations/signatures, test summaries, migration result, staging smoke/E2E result, and known exceptions.

Sprint 22 is integrated when CI is mandatory on protected `main`, a tag produces a fully signed/attested immutable release, and an approved staging deployment can reproduce that exact release by digest without rebuilding it.
