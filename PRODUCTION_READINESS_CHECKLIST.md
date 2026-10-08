# Production Readiness Human Checklist

Release tag: ____________________  
Commit SHA: ____________________  
Production URL: ____________________  
Review date: ____________________

The structured readiness run is the machine-readable source of truth. This checklist is a human review worksheet.

## Change

- [ ] **PR-CHG-001** — Change freeze window and release scope are declared _(owner: ProductOwner)_
- [ ] **PR-CHG-002** — Production migration plan has backup, ordering, ownership, and abort criteria _(owner: TechnicalLead)_
- [ ] **PR-CHG-003** — Rollback/forward-fix criteria are documented and tested where applicable _(owner: TechnicalLead)_
- [ ] **PR-CHG-004** — No automatic DB downgrade is required for rollback plan _(owner: TechnicalLead)_
- [ ] **PR-CHG-005** — Production deployment credentials/runner permissions are least privilege _(owner: SecurityOwner)_

## Communications

- [ ] **PR-COM-001** — Launch communication and stakeholder notification plan is prepared _(owner: ProductOwner)_
- [ ] **PR-COM-002** — Maintenance/deployment window and user impact are documented _(owner: ProductOwner)_
- [ ] **PR-COM-003** — Post-launch support coverage and escalation window are scheduled _(owner: OperationsOwner)_

## Data

- [ ] **PR-DATA-001** — Ten service databases exist with per-service least-privilege accounts _(owner: SecurityOwner)_
- [ ] **PR-DATA-002** — Production PostgreSQL HA/failover is configured _(owner: OperationsOwner)_
- [ ] **PR-DATA-003** — PostgreSQL PITR/backup and restore drill passed _(owner: OperationsOwner)_
- [ ] **PR-DATA-004** — Redis cache and durable tiers are isolated and authenticated _(owner: SecurityOwner)_
- [ ] **PR-DATA-005** — RabbitMQ production topology is HA/private with retry/DLQ controls _(owner: OperationsOwner)_
- [ ] **PR-DATA-006** — Object storage is private, versioned, encrypted, and recoverable _(owner: SecurityOwner)_
- [ ] **PR-DATA-007** — Production data seeding/bootstrap is defined and non-destructive _(owner: TechnicalLead)_

## DisasterRecovery

- [ ] **PR-DR-001** — Production backup retention and recovery responsibilities are assigned _(owner: OperationsOwner)_
- [ ] **PR-DR-002** — RTO/RPO assumptions are explicitly documented and supported by evidence _(owner: OperationsOwner)_
- [ ] **PR-DR-003** — Site/region disaster recovery gaps are documented with owners _(owner: OperationsOwner)_

## FinalGate

- [ ] **PR-FIN-001** — All required readiness evidence is archived without secrets _(owner: ProjectSupervisor)_
- [ ] **PR-FIN-002** — Production launch runbook has named step owners and checkpoints _(owner: ProjectSupervisor)_
- [ ] **PR-FIN-003** — Five production-readiness approvals are recorded _(owner: ProjectSupervisor)_

## Infrastructure

- [ ] **PR-INF-001** — Production Kubernetes cluster and namespace are provisioned _(owner: OperationsOwner)_
- [ ] **PR-INF-002** — Production Ingress/load balancer is configured _(owner: OperationsOwner)_
- [ ] **PR-INF-003** — Production DNS resolves to intended edge _(owner: OperationsOwner)_
- [ ] **PR-INF-004** — Production TLS certificate is valid and renewable _(owner: OperationsOwner)_
- [ ] **PR-INF-005** — Only frontend and API Gateway are publicly routed _(owner: SecurityOwner)_
- [ ] **PR-INF-006** — All 10 backend APIs remain private ClusterIP/internal services _(owner: SecurityOwner)_
- [ ] **PR-INF-007** — Pod Security baseline is enforced for application workloads _(owner: SecurityOwner)_
- [ ] **PR-INF-008** — HPA/PDB/probes/resource limits are reconciled and valid _(owner: OperationsOwner)_

## Operations

- [ ] **PR-OPS-001** — Prometheus/Grafana/logs/traces/alerts are production-ready or approved managed equivalents _(owner: OperationsOwner)_
- [ ] **PR-OPS-002** — 10/10 backend services expose expected production telemetry internally _(owner: OperationsOwner)_
- [ ] **PR-OPS-003** — Critical alerts route to approved operators and have runbooks _(owner: OperationsOwner)_
- [ ] **PR-OPS-004** — Operational ownership and escalation contacts are assigned _(owner: OperationsOwner)_
- [ ] **PR-OPS-005** — Go-live monitoring window and launch dashboard are prepared _(owner: OperationsOwner)_
- [ ] **PR-OPS-006** — Support/incident intake and severity/escalation process are ready _(owner: OperationsOwner)_

## Performance

- [ ] **PR-PERF-001** — General p95 target <=3 seconds is satisfied on accepted evidence _(owner: TechnicalLead)_
- [ ] **PR-PERF-002** — Attendance p95 target <=2 seconds is satisfied _(owner: TechnicalLead)_
- [ ] **PR-PERF-003** — Notification end-to-end p95 target <=5 seconds is satisfied _(owner: TechnicalLead)_
- [ ] **PR-PERF-004** — 500 concurrent-user acceptance result is recorded and acceptable _(owner: TechnicalLead)_
- [ ] **PR-PERF-005** — Database connection budget remains safe at HPA maximum replicas _(owner: OperationsOwner)_

## Release

- [ ] **PR-REL-001** — Exact Sprint 25 accepted release manifest identified _(owner: TechnicalLead)_
- [ ] **PR-REL-002** — All 12 images are digest-pinned and signature/attestation verified _(owner: SecurityOwner)_
- [ ] **PR-REL-003** — Production deployment uses the same accepted image digests _(owner: TechnicalLead)_
- [ ] **PR-REL-004** — Migration-bearing components are explicitly identified _(owner: TechnicalLead)_

## Reliability

- [ ] **PR-RELIA-001** — Availability SLO target >=99% is represented in monitoring and ownership _(owner: OperationsOwner)_
- [ ] **PR-RELIA-002** — Pod failure and rolling-update drills pass _(owner: OperationsOwner)_
- [ ] **PR-RELIA-003** — Node failure/drain behavior is validated or formally limited by topology _(owner: OperationsOwner)_
- [ ] **PR-RELIA-004** — Observability component failures do not break business APIs _(owner: OperationsOwner)_

## Security

- [ ] **PR-SEC-001** — Production secret manager integration is configured _(owner: SecurityOwner)_
- [ ] **PR-SEC-002** — No production secrets are stored in Git, images, or CI artifacts _(owner: SecurityOwner)_
- [ ] **PR-SEC-003** — Identity JWT/JWKS production keys and rotation procedure are ready _(owner: SecurityOwner)_
- [ ] **PR-SEC-004** — Internal service credentials/tokens have production rotation procedures _(owner: SecurityOwner)_
- [ ] **PR-SEC-005** — Network/firewall rules keep DB/Redis/RabbitMQ/admin/metrics private _(owner: SecurityOwner)_
- [ ] **PR-SEC-006** — Sprint 18 security regression passes for the release candidate _(owner: SecurityOwner)_
- [ ] **PR-SEC-007** — Container/dependency/supply-chain scans pass release policy _(owner: SecurityOwner)_
- [ ] **PR-SEC-008** — Production admin/operator access uses named identities and MFA where supported _(owner: SecurityOwner)_

## UAT

- [ ] **PR-UAT-001** — Sprint 25 UAT promotion gate passes _(owner: ProductOwner)_
- [ ] **PR-UAT-002** — All required stakeholder UAT sign-offs are present _(owner: ProductOwner)_
- [ ] **PR-UAT-003** — No open BLOCKER, CRITICAL, or MAJOR UAT defects remain _(owner: ProductOwner)_
