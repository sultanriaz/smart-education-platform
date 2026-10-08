# Installing `smartedu-contracts` in service images

Sprint 16 introduces one repository-local Python package:

```text
libs/python/smartedu_contracts
```

Do not copy/paste the package into ten services.

## Recommended monorepo build pattern

Use the repository root as Docker build context and make each service Dockerfile
accept both the service source and the shared library.

Conceptual pattern:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY libs/python/smartedu_contracts /tmp/smartedu_contracts
RUN pip install --no-cache-dir /tmp/smartedu_contracts

COPY services/<service>/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY services/<service>/app ./app
```

Compose build:

```yaml
build:
  context: .
  dockerfile: services/<service>/Dockerfile
```

Keep service databases/private dependencies off the edge network.

## Alternative wheel pattern

From repository root:

```powershell
.\scripts\build-contract-wheel.ps1
```

Then copy the generated wheel into the service build stage and install it.

## Production rule

Build the shared package into the immutable service image. Do not depend on a
host bind mount for production.
