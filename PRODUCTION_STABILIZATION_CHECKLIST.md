# Production Stabilization Human Checklist

Release tag: ____________________  
Launch ID: ____________________  
Production URL: ____________________  
Closure review date: ____________________

The structured stabilization run is the machine-readable source of truth.

## Change

- [ ] **STAB-CHG-001** — No uncontrolled production hotfix bypassed release controls _(owner: TechnicalLead)_
- [ ] **STAB-CHG-002** — Any stabilization hotfix has its own immutable release identity and regression evidence _(owner: TechnicalLead)_

## Closure

- [ ] **STAB-FIN-001** — Production stabilization evidence index is complete and secret-free _(owner: ProjectSupervisor)_
- [ ] **STAB-FIN-002** — Final stabilization report is generated and reviewed _(owner: ProjectSupervisor)_
- [ ] **STAB-FIN-003** — Five operational/project approvals are recorded _(owner: ProjectSupervisor)_
- [ ] **STAB-FIN-004** — Final disposition is STABLE or STABLE_WITH_FOLLOWUPS _(owner: ProjectSupervisor)_

## DataIntegrity

- [ ] **STAB-DATA-001** — No confirmed production data-loss/corruption incident remains _(owner: TechnicalLead)_
- [ ] **STAB-DATA-002** — Reporting projections remain acceptably consistent with source events _(owner: TechnicalLead)_

## Database

- [ ] **STAB-DB-001** — All ten service databases are reachable only by intended services _(owner: SecurityOwner)_
- [ ] **STAB-DB-002** — PostgreSQL connection usage stays within safe budget _(owner: OperationsOwner)_
- [ ] **STAB-DB-003** — No persistent lock/deadlock/regression trend remains _(owner: OperationsOwner)_
- [ ] **STAB-DB-004** — Production backup/PITR schedule remains healthy after launch _(owner: OperationsOwner)_

## Edge

- [ ] **STAB-EDGE-001** — Production DNS remains correct _(owner: OperationsOwner)_
- [ ] **STAB-EDGE-002** — Production TLS remains valid and renewal path is healthy _(owner: OperationsOwner)_
- [ ] **STAB-EDGE-003** — Only frontend and API Gateway remain publicly exposed _(owner: SecurityOwner)_

## Identity

- [ ] **STAB-AUTH-001** — Login/refresh/logout/JWKS behavior remains healthy under real traffic _(owner: TechnicalLead)_

## Launch

- [ ] **STAB-LAUNCH-001** — Sprint 27 production launch gate passed _(owner: TechnicalLead)_
- [ ] **STAB-LAUNCH-002** — Production release identity still matches launch record _(owner: TechnicalLead)_
- [ ] **STAB-LAUNCH-003** — No unresolved SEV-1 launch incident remains _(owner: OperationsOwner)_

## Messaging

- [ ] **STAB-MQ-001** — RabbitMQ queues do not show unbounded backlog growth _(owner: OperationsOwner)_
- [ ] **STAB-MQ-002** — Retry/DLQ volume is understood and within accepted bounds _(owner: OperationsOwner)_
- [ ] **STAB-MQ-003** — Transactional outbox backlog drains normally _(owner: TechnicalLead)_
- [ ] **STAB-MQ-004** — Consumer/inbox deduplication shows no duplicate side-effect incident _(owner: TechnicalLead)_

## Observability

- [ ] **STAB-OBS-001** — All expected service metric targets remain present _(owner: OperationsOwner)_
- [ ] **STAB-OBS-002** — Logs and traces remain available for incident correlation _(owner: OperationsOwner)_
- [ ] **STAB-OBS-003** — Critical alert routing is tested and acknowledged by owners _(owner: OperationsOwner)_
- [ ] **STAB-OBS-004** — No unresolved critical production alert remains _(owner: OperationsOwner)_

## Operations

- [ ] **STAB-OPS-001** — Primary and backup operational owners have accepted ongoing ownership _(owner: OperationsOwner)_
- [ ] **STAB-OPS-002** — Runbooks contain current production endpoints/owners without secrets _(owner: OperationsOwner)_
- [ ] **STAB-OPS-003** — Known MEDIUM/LOW follow-ups are assigned with target dates _(owner: ProjectSupervisor)_

## Performance

- [ ] **STAB-PERF-001** — General production p95 remains within <=3 second target _(owner: TechnicalLead)_
- [ ] **STAB-PERF-002** — Attendance production latency remains within <=2 second target _(owner: TechnicalLead)_
- [ ] **STAB-PERF-003** — Representative notification delivery remains within <=5 second target _(owner: TechnicalLead)_
- [ ] **STAB-PERF-004** — No production saturation trend invalidates the 500-user capacity evidence _(owner: OperationsOwner)_

## Recovery

- [ ] **STAB-DR-001** — Recovery documentation still matches the deployed production architecture _(owner: OperationsOwner)_
- [ ] **STAB-DR-002** — Backup ownership and restore escalation remain assigned _(owner: OperationsOwner)_

## Redis

- [ ] **STAB-REDIS-001** — Cache Redis remains healthy without critical eviction/connection errors _(owner: OperationsOwner)_
- [ ] **STAB-REDIS-002** — Durable Redis remains healthy and persistent as designed _(owner: OperationsOwner)_

## Roles

- [ ] **STAB-ROLE-001** — Student core production workflow remains usable _(owner: ProductOwner)_
- [ ] **STAB-ROLE-002** — Teacher core production workflow remains usable _(owner: ProductOwner)_
- [ ] **STAB-ROLE-003** — Admin core production workflow remains usable _(owner: ProductOwner)_

## Security

- [ ] **STAB-SEC-001** — No post-launch critical security alert or unauthorized access finding remains _(owner: SecurityOwner)_
- [ ] **STAB-SEC-002** — Production secrets remain absent from Git/logs/evidence _(owner: SecurityOwner)_
- [ ] **STAB-SEC-003** — Administrative/operator access remains least-privilege and attributable _(owner: SecurityOwner)_

## Services

- [ ] **STAB-SVC-001** — All 12 application workloads remain Available _(owner: OperationsOwner)_
- [ ] **STAB-SVC-002** — No sustained crash-loop or abnormal restart pattern remains _(owner: OperationsOwner)_
- [ ] **STAB-SVC-003** — Readiness removes unhealthy pods from service _(owner: OperationsOwner)_

## Support

- [ ] **STAB-SUP-001** — Production support intake is operating and owned _(owner: OperationsOwner)_
- [ ] **STAB-SUP-002** — All launch-period user reports are triaged and severity-classified _(owner: ProductOwner)_
