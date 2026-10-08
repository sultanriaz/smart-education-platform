# Kubernetes Security Baseline

Every application Deployment uses:

```text
runAsNonRoot: true
seccompProfile: RuntimeDefault
allowPrivilegeEscalation: false
readOnlyRootFilesystem: true
capabilities.drop: ALL
automountServiceAccountToken: false
```

Writable temporary paths use bounded `emptyDir` volumes.

## Images

Production images come only from the Sprint 22 release manifest and are
digest-pinned.

Release CI is responsible for:

```text
build
SBOM
provenance
Trivy scanning
Cosign signing
attestation
```

The cluster deployment identity should verify/allow only approved registry
sources. Admission-policy enforcement can be added when the production cluster
technology is finalized.

## Namespace isolation

Application workloads live in:

```text
smartedu
```

Default ingress denial is enabled.

Ingress is then opened only for:

```text
same-namespace application communication
Ingress controller -> frontend/API Gateway
```

Provider-specific egress lockdown must be completed before production.

## Kubernetes RBAC

Application pods do not receive Kubernetes API tokens by default.

Deployment automation receives only the namespace/cluster permissions required
for its deployment action.

Human production cluster access should use named identities, MFA, and audit
logging.

Do not use shared cluster-admin kubeconfig files in CI.

## Pod Security Admission

The production cluster should enforce Kubernetes Pod Security Admission at
least at the `restricted` profile where compatible.

Any exception must be explicit, documented, and narrowly scoped.

## Secrets

Kubernetes Secrets are transport/runtime objects, not the long-term source of
truth.

Use the approved external secret store and rotation process.
