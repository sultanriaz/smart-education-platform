# Production Kubernetes Manifests

This directory is the provider-neutral production application baseline.

It intentionally excludes real secrets and provider-specific stateful service
manifests.

## Source manifests

The checked-in Deployments contain bootstrap image placeholders:

```text
smartedu.local/<component>:bootstrap
```

Those placeholders must never be deployed to production.

Sprint 22's `release-manifest.json` is the source of immutable image identity.

Render:

```powershell
python .\scripts\render-k8s-release.py `
    .\release-manifest.json `
    --output .\deploy\kubernetes\rendered-production.yaml
```

Verify:

```powershell
python .\scripts\verify-k8s-bundle.py `
    .\deploy\kubernetes\rendered-production.yaml
```

The verifier requires digest-pinned images.

## Kustomize

The source manifest tree is also a valid Kustomize base:

```powershell
kubectl kustomize .\deploy\kubernetes\production
```

Kustomize output still contains bootstrap image placeholders until release
rendering/reconciliation is performed.

Do not apply source Kustomize output directly to production.

## Secrets

`secrets.example.yaml` is not referenced by `kustomization.yaml`.

Create real `<component>-secrets` objects from the approved secret manager before
deployment.

## Examples

The `examples` directory contains optional provider-specific starting points.

Nothing there is automatically applied.
