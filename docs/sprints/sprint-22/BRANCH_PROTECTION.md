# Sprint 22 Branch Protection

Configure the Git hosting platform so `main` cannot be pushed to directly. Require pull requests, at least one reviewer, dismissal of stale approvals after material changes, successful CI/security checks, conversation resolution, and an up-to-date branch before merge. Restrict force-push and deletion.

Recommended required checks after final workflow reconciliation:

```text
CI / cicd-self-tests
CI / python-services
CI / frontend (when changed)
CI / gateway (when changed)
CI / container-checks
Security
Observability
```

GitHub Environment `staging` should require an authorized reviewer. Production protections are finalized in later deployment/readiness sprints.
