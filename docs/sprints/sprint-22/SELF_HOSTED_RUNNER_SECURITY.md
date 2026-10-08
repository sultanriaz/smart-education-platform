# Self-Hosted Deployment Runner Security

Use dedicated runners for staging/production deployments. Never run untrusted pull-request jobs on deployment runners. Scope GitHub Environment secrets to the deployment job, patch the OS/Docker runtime regularly, restrict network access to only registry/staging dependencies, and run the GitHub runner under a non-admin account wherever practical.

The runner workspace can contain release manifests but must not persist plaintext secrets. Rotate credentials if a runner is suspected compromised. Production runner controls are finalized with deployment architecture in later sprints.
