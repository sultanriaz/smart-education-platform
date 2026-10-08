Integrate Sprint 23 Deployment Architecture into the actual merged Smart
Education Platform from Sprints 1–22.

FIRST inspect the real repository. Do not blindly apply the generated manifests.

1. Inspect actual runtime contracts

   Confirm for all 12 deployable components:
   - Dockerfile path
   - internal port
   - health route
   - readiness route
   - required environment variables
   - required secret variables
   - writable filesystem paths
   - shutdown behavior

2. Reconcile production topology

   Read:
   `config/deployment/production-topology.yaml`

   Keep at least two replicas per public/critical stateless workload unless there
   is a documented technical reason not to.

   Treat replica/resource values as Sprint 20 candidate values, not guarantees.

3. Kubernetes manifests

   Reconcile every Deployment/Service/HPA/PDB against the real images.

   Preserve:
   - RollingUpdate
   - maxUnavailable 0
   - probes
   - resources
   - HPA
   - PDB
   - topology spread
   - anti-affinity
   - runAsNonRoot
   - readOnlyRootFilesystem
   - drop ALL
   - no privilege escalation
   - no unnecessary service-account tokens

   If an image requires a writable directory, mount a bounded writable volume.
   Do not disable readOnlyRootFilesystem globally.

4. Public network boundary

   Only frontend and API Gateway may be reachable through public Ingress.

   Domain services remain ClusterIP.

   Do not add LoadBalancer/NodePort services for internal APIs.

5. Gateway

   Reconcile Ingress `/api` routing with the actual Sprint 11 Gateway.

   Preserve Sprint 16 request/correlation logic and Sprint 18 edge security.

6. Frontend

   Reconcile frontend runtime API origin and Nginx port with Sprint 12/18.

7. DNS/TLS

   Replace `smartedu.example.edu` with the approved real staging/production
   domain configuration.

   Choose the actual TLS mechanism:
   - provider-managed certificate
   - or cert-manager

   Do not enable HSTS before HTTPS is validated.

8. Secrets

   Inspect every real Pydantic settings class and frontend/Gateway runtime config.

   Replace generated secret examples with exact per-service secret contracts.

   Store real values only in the approved secret manager/Kubernetes integration.

   Do not commit Secret values.

9. Stateful services

   Select the real provider/implementation for:
   - PostgreSQL
   - Redis cache
   - Redis durable
   - RabbitMQ
   - object storage
   - email
   - observability

   Production must be HA/private or an explicitly approved equivalent.

10. Database ownership

    Preserve ten service databases and least-privilege service DB accounts.

    No service may gain read access to another service DB.

11. PostgreSQL recovery

    Configure HA and PITR/continuous recovery appropriate to the provider.

    Test restore in staging.

12. Redis

    Keep cache vs durable reliability classes separate.

    Do not move permanent business truth into Redis.

13. RabbitMQ

    Preserve Sprint 17 outbox/inbox reliability.

    Use HA durable broker topology.

14. Object storage

    Keep buckets private and versioned/encrypted.

    Preserve Sprint 18 least-privilege credentials.

15. Sprint 22 release manifest

    Production images must come from the exact digest refs in
    `release-manifest.json`.

    Run:
    `scripts/render-k8s-release.py`

    Then:
    `scripts/verify-k8s-bundle.py`

    There must be zero bootstrap/tag-only images.

16. Supply-chain verification

    Verify Sprint 22:
    - Cosign signature
    - provenance/attestation
    - SBOM
    - vulnerability gates

    before cluster deployment.

17. HPA and resource budget

    Reconcile HPA maximum replicas with Sprint 20 load results.

    Re-run the DB connection budget against maximum pods.

    Do not configure HPA so it can exhaust PostgreSQL connections.

18. Networking

    Preserve default-deny ingress.

    Reconcile ingress-controller namespace labels.

    Implement provider-specific egress rules before production:
    - DNS
    - DB
    - Redis
    - RabbitMQ
    - object storage
    - email provider
    - OTel/observability

    Only enable global default-deny egress after those rules are tested.

19. Pod Security

    Configure cluster/namespace Pod Security Admission to restricted where
    compatible.

    Narrowly document any exception.

20. Kubernetes identities

    App pods should not need Kubernetes API access.

    Keep `automountServiceAccountToken: false`.

    Deployment automation should use short-lived/federated cluster credentials
    where the environment supports them.

21. Observability

    Connect to Sprint 21:
    - metrics
    - logs
    - traces
    - alerts

    Do not make observability a readiness dependency.

22. Backup/restore

    Implement and test:
    - PostgreSQL PITR
    - object version restore
    - release-manifest redeploy
    - secret recovery

    Record recovery time and data integrity verification.

23. Disaster recovery

    Read `DISASTER_RECOVERY.md`.

    Close provider-specific gaps for:
    - zone loss
    - site/region loss
    - DNS failover
    - secret recovery
    - data restore

24. CI validation

    Reconcile `.github/workflows/deployment-architecture.yml` with Sprint 22 CI.

    PR jobs may validate manifests but must not get production cluster
    credentials.

25. Staging handoff

    Prepare Sprint 24 so staging can use the same architecture with:
    - separate domain/DNS
    - separate secrets
    - non-production data
    - production-like network/security
    - smaller but representative stateful infrastructure

26. Run:
    - smartedu-deploy tests
    - tests/deployment
    - kubectl kustomize
    - production preflight
    - synthetic release render/verify

27. Full regressions

    Run Sprint 18–22 quality/security/performance/observability/release checks.

Do not solve Sprint 23 by:
- putting databases inside app pods
- using one public port per microservice
- using `latest`
- committing Kubernetes Secret values
- disabling probes
- running one replica for critical production APIs
- removing transaction/outbox behavior
- sharing one DB superuser
- exposing observability/admin ports publicly
- disabling pod security because an image needs one writable directory
- blindly enabling default-deny egress without dependency rules
- calling a single-node local cluster production-ready

At completion report:
- final workload/port table
- final replica/HPA/resource values
- real public domain and TLS approach
- stateful service products/topology
- secret-management mechanism
- per-service DB ownership check
- network/egress policy status
- rendered release image digests
- Cosign/attestation verification
- Pod Security results
- HPA/PDB/probe validation
- DB connection budget at HPA max
- backup/restore staging drill results
- node/pod failure test
- rolling update result
- Sprint 18–22 regression totals
- any deployment gap remaining for Sprint 24/26
