# Performance Run Record

## Build

```text
Git commit:
Environment:
Date/time UTC:
Gateway version:
Frontend version:
```

## Topology

```text
Gateway replicas:
Identity replicas:
Academic replicas:
Attendance replicas:
Scheduling replicas:
Notification API replicas:
Notification workers:
Facility replicas:
Learning replicas:
Assessment replicas:
Reporting replicas:
Platform replicas:
```

## Database / infrastructure

```text
PostgreSQL version:
max_connections:
Redis topology:
RabbitMQ topology:
Object storage:
```

## Workload

```text
Profile:
Users:
Spawn rate:
Duration:
Student/Teacher/Admin mix:
Cold or warm cache:
```

## Results

```text
Total requests:
Total failures:
Overall RPS:
Overall error rate:

General p95:
Attendance read p95:
Attendance write p95:
Notification visibility p95:
Reporting dashboard p95:
```

## Capacity observations

```text
Peak service CPU:
Peak service memory:
Peak DB connections:
DB lock waits:
Slowest SQL:
Redis latency:
RabbitMQ maximum queue age:
Object-storage p95:
```

## Changes since baseline

```text
Indexes:
Cache:
Replica counts:
Pool sizes:
Worker concurrency:
Code changes:
```

## Verdict

```text
SRS 500 concurrent users: PASS/FAIL
General 3-second p95: PASS/FAIL
Attendance 2-second p95: PASS/FAIL
Notifications 5-second p95: PASS/FAIL
Error rate <=1%: PASS/FAIL
```

## Follow-up

Document bottlenecks with evidence and the next experiment. Do not record
secrets/tokens in this report.
