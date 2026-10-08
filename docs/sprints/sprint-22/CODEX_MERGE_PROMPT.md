Integrate Sprint 22 CI/CD Engineering into the actual merged Smart Education Platform Sprints 1–21.

FIRST inventory the current GitHub workflows, Dockerfiles, Compose service names, dependency files, test commands, Alembic layouts, Sprint 18 security checks, Sprint 19 quality gates, Sprint 20 performance workflow, and Sprint 21 observability workflow. Preserve stronger existing checks.

1. Reconcile `config/cicd/components.yaml` with the real 10 service Dockerfiles plus frontend and Gateway. Keep exactly one release component per deployable application image.
2. Make `ci-plan.py` correctly select changed services and fan out all components when shared libraries/contracts/workflow policy change.
3. Consolidate CI so service pytest/Ruff, real PostgreSQL concurrency where configured, migrations, frontend typecheck/lint/test/build, Gateway tests, security, observability validation, and changed-container Trivy checks remain mandatory.
4. Do not silently remove existing Sprint-specific CI just because a reusable workflow exists; migrate strong tests into reusable/matrix jobs or keep them as required jobs.
5. Keep PR workflow permissions read-only unless a check genuinely requires another permission. PR jobs must never receive staging/production secrets.
6. Configure branch protection recommendations after final job names stabilize.
7. Validate release tags as immutable SemVer-style `vMAJOR.MINOR.PATCH` tags contained in `main`.
8. On release, rebuild all 12 application images from the exact tagged commit. Do not promote mutable CI tags as the release artifact unless their digest and source commit are cryptographically verified equivalent.
9. Push to GHCR, create SBOM/provenance, GitHub provenance attestation, and keyless Cosign signature for every immutable image digest.
10. Do not deploy `latest`; staging/prod must consume release manifest digest references.
11. Generate one `release-manifest.json` containing all 12 unique images, exact 40-char commit SHA, release tag, migration-bearing components, and forward-only migration policy. Attach it plus SHA256 checksum to GitHub Release.
12. Test `validate-release-manifest.py` against missing, duplicate, bad-digest, and valid manifests.
13. Reconcile migration detection with actual paths. Every migration-bearing service must be marked in the release manifest.
14. Preserve one Alembic history/database per service. Never run one global cross-service migration transaction.
15. Configure protected GitHub Environment `staging` and a dedicated self-hosted staging runner. Untrusted PR code must never execute on that runner.
16. Reconcile actual staging Compose topology with `STAGING_COMPOSE_FILES`; modify existing Compose image fields to consume rendered release-image variables instead of creating a parallel deployment stack.
17. Staging deployment order: verify checksum -> verify Cosign signatures -> registry login -> approved backup -> pull digests -> service migrations -> deploy -> health/readiness -> Sprint 19 live smoke -> role E2E.
18. Make backup failure or migration failure stop deployment immediately.
19. Do not run database downgrade automatically. Default rollback is application-image rollback only after explicit current-schema compatibility confirmation. Otherwise forward-fix.
20. Test rollback with a schema-compatible previous release and prove the old digest is deployed without rebuilding.
21. Preserve event-contract compatibility during rollback. Check pending RabbitMQ events, reporting projections, cache formats, and object metadata where a rollback crosses versions.
22. Consolidate Sprint 18 supply-chain checks with `supply-chain.yml`: secret scan, Bandit, pip-audit, npm audit, Trivy, dependency review, and container hardening. Do not weaken severity gates to make CI green.
23. Ensure image base dependencies and GitHub Actions are reviewed/upgraded normally; do not blindly pin stale vulnerable versions just for reproducibility.
24. Verify generated SBOM/provenance/signatures can be queried from registry tooling and signature verification fails for an unsigned/tampered ref.
25. Verify staging environment secrets do not appear in logs, artifacts, release assets, Docker image layers, or PR jobs.
26. Re-run Sprint 21 observability smoke after deploy and ensure release/version labels appear in telemetry.
27. Re-run Sprint 20 baseline against staging after significant release-pipeline/Docker changes to catch image/runtime performance regressions.
28. Run Student/Teacher/Admin E2E on the deployed staging release, not a locally rebuilt copy.
29. Do not implement final production topology here; Sprint 23 owns deployment architecture. Keep production promotion disabled/manual until that architecture and Sprint 26 readiness are complete.
30. Do not solve Sprint 22 by moving release tags, using latest, sharing admin registry/database credentials, disabling migrations/tests/scans, auto-downgrading schemas, or allowing PRs onto deployment runners.

At completion report exact workflow names/checks, component catalog, per-service test totals, migration gates, container scan results, release image digests, SBOM/provenance/signature verification, release-manifest validation, staging backup/migration/deploy result, live smoke/E2E result, rollback drill result, secrets/permissions review, and every remaining CI/CD exception.
