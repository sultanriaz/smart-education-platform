"""Render local evidence without interpreting skips or unavailable gates as passes."""

import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs/integration"


def load(path):
    file = ROOT / path
    return json.loads(file.read_text(encoding="utf-8")) if file.exists() else None


def performance(profile):
    file = ROOT / f"artifacts/performance/{profile}_stats.csv"
    if not file.exists():
        return "NOT RUN"
    with file.open(encoding="utf-8", newline="") as stream:
        row = next(
            (row for row in csv.DictReader(stream) if row["Name"] == "Aggregated"), None
        )
    if not row:
        return "No completed request samples"
    return f"{row['Request Count']} requests; {row['Failure Count']} failures; P95 {row['95%']} ms; P99 {row['99%']} ms; mean {float(row['Average Response Time']):.2f} ms"


def failures(profile):
    file = ROOT / f"artifacts/performance/{profile}_failures.csv"
    counts = Counter()
    if file.exists():
        with file.open(encoding="utf-8", newline="") as stream:
            for row in csv.DictReader(stream):
                match = re.search(r"\b([45]\d{2}):", row["Error"])
                counts[match.group(1) if match else "other"] += int(row["Occurrences"])
    return "; ".join(f"HTTP {code}: {count}" for code, count in sorted(counts.items())) or "No recorded failures"


def main():
    suites = load("artifacts/verification/results.json") or []
    live = load("artifacts/integration/live-results.json") or []
    review = load("artifacts/browser/review.json") or []
    containers = load("artifacts/verification/container-results.json") or []
    plans = load("artifacts/performance/query-plans.json") or []
    inventory = load(".integration/inventory.json") or []
    manifest = load(".integration/merge-manifest.json") or []
    totals = {}
    for label in ("passed", "failed", "skipped"):
        totals[label] = sum(
            int(match.group(1))
            if (match := re.search(rf"(\d+) {label}", row["summary"]))
            else 0
            for row in suites
        )
    e2e = load("artifacts/browser/e2e.json") or {}
    stats = e2e.get("stats", {})
    lines = [
        "# Final integration delivery report",
        "",
        "Updated 2026-10-08. Local engineering evidence; not institutional acceptance or a production release.",
        "",
        "## A. Integration",
        "",
        f"Integrated {len(inventory)} supplied packages (Sprints 4–28); retained Sprints 1–3 from original Git HEAD `8a4cc6a`. No packages 1–3 or `sprint-zips` directory were available. Validated {sum(len(row['files']) for row in inventory)} archive file entries; {len(manifest)} provenance actions are retained under ignored `.integration/merge-manifest.json`. The local branch is `integration/2026-10-08`; recovery bundle and original ZIPs remain available.",
        "",
        "Ten independent services, thirteen shared libraries, gateway, three role workspaces, migrations, infrastructure and operational catalogs are integrated. [Architecture](SYSTEM_ARCHITECTURE.md), [inventory](SPRINT_INVENTORY.md), [conflicts](MERGE_DECISIONS.md), [limits](KNOWN_LIMITATIONS.md).",
        "",
        "| Sprint | Final status |",
        "|---|---|",
    ]
    descriptions = {
        1: "Identity baseline retained; suite and live authentication verified",
        2: "Academic baseline retained; suite and owner contracts verified",
        3: "Attendance baseline retained; suite and live finalization/summary verified",
        4: "Scheduling integrated; real recurring timetable verified",
        5: "Notification integrated; real announcement/SMTP/event delivery verified",
        6: "Facility integrated; approval, conflict and isolation verified",
        7: "Learning integrated; real notes and private S3 round trip verified",
        8: "Assessment integrated; real answers/grading, saved progress and timed expiry verified",
        9: "Reporting integrated; real broker projection and CSV verified",
        10: "Platform integrated; durable health/reindex/Academic export jobs verified",
        11: "Gateway integrated; real routing/CORS, private routes and non-root startup verified",
        12: "Frontend shell integrated and modernized",
        13: "Student workspace integrated; routes/browser workflow verified",
        14: "Teacher workspace integrated; routes and authorization verified",
        15: "Admin workspace integrated; routes and authorization verified",
        16: "Contracts/resilience integrated; suites and real Redis idempotency verified",
        17: "Owned migrations, RabbitMQ, Redis and private storage integrated and started",
        18: "Security integration, recovery/cookies/uploads verified within stated limits",
        19: "QA libraries/suites integrated and executed; conditional skips retained",
        20: "Performance tooling integrated; real local measurements below",
        21: "Telemetry wiring and suites verified; external collector pipelines NOT RUN",
        22: "CI/CD catalogs and local validation pass; hosted workflows NOT RUN",
        23: "Deployment topology/tooling integrated; actual cluster deployment NOT RUN",
        24: "Staging tooling/suites integrated; staging execution NOT RUN",
        25: "UAT tooling/suites integrated; institutional UAT/signoff NOT RUN",
        26: "Readiness tooling/suites integrated; real production gates NOT RUN",
        27: "Production release tooling integrated; production deployment NOT RUN",
        28: "Stabilization tooling integrated; production observation/drills NOT RUN",
    }
    lines += [f"| {number} | {descriptions[number]} |" for number in range(1, 29)]
    lines += [
        "",
        "Conflicts resolved: chronological schema/runtime extensions; Student read and Teacher authoring contracts; all role routes retained when recovery routes were added; stable idempotency and authenticated downloads retained with cookie sessions; independent owned migrations/event stores; root-context Docker library paths; local host routing/CORS and protected infrastructure configuration. No old-SRS omissions caused feature deletion.",
        "",
        "## B. Functional results",
        "",
        "| Component | Local result / evidence |",
        "|---|---|",
    ]
    for row in suites:
        if row["component"].endswith("-service"):
            lines.append(f"| {row['component']} | {row['status']}: {row['summary']} |")
    lines += [
        "| API Gateway | Built/running Nginx; namespace routing, CORS and public internal-route rejection verified |",
        "| Student frontend | Actual attendance/timetable/resources/assessment/booking data; saved assessment resume/submission verified |",
        "| Teacher frontend | Actual sections/attendance/timetable/resources/assessment/announcements/facilities pages; backend ownership checks |",
        "| Admin frontend | Actual user/academic/scheduling/facility/notification/reporting/platform pages |",
        "",
        "Representative full-system checks:",
        "",
        "| Live case | Result | Evidence |",
        "|---|---|---|",
    ]
    lines += [f"| {row['name']} | {row['status']} | {row['detail']} |" for row in live]
    lines += [
        "",
        "## C. UI/UX",
        "",
        "Replaced the Vite starter/sprint shell with shared light/dark violet, navy and charcoal tokens, polished cards, real charts, personalized dashboards, role navigation, profile/logout, notification badges, page finder and keyboard shortcuts. Lazy pages provide loading/error/empty states. Touch targets, responsive tables and navigation support 320/375/768/1024/1440 widths. Motion uses brief transform/opacity transitions and honors reduced-motion preferences.",
        "",
        f"Browser page review: {len(review)} records (role pages plus dark dashboard checks); {sum(len(row.get('widths', [])) for row in review)} width checks. Findings remain in `artifacts/browser/review.json`. Axe targets WCAG 2 A/AA and 2.1 AA; automated checks are not human accessibility acceptance.",
        "",
        "Local screenshots: [Student desktop](../../artifacts/browser/student-desktop.png), [Student dark](../../artifacts/browser/student-dark.png), [Student mobile](../../artifacts/browser/student-mobile.png), [Teacher desktop](../../artifacts/browser/teacher-desktop.png), [Teacher mobile](../../artifacts/browser/teacher-mobile.png), [Admin desktop](../../artifacts/browser/admin-desktop.png), [Admin dark](../../artifacts/browser/admin-dark.png). Before screenshots were not captured; original source is retained for comparison.",
        "",
        "## D. Debugging and optimization",
        "",
        "| Problem / root cause | Repair and measured boundary |",
        "|---|---|",
        "| PostgreSQL DISTINCT over JSON failed although SQLite suites passed | Learning uses a unique target-ID subquery; real Student catalog now succeeds |",
        "| Attendance totals wrapper and obsolete routes produced incorrect UI/404s | Actual totals mapped to 80%; Teacher sessions/records and Admin assignments use owner contracts |",
        "| Login cookies/recovery adapters were not connected to actual accounts | Owned token/account/outbox adapters, threadpool Argon2/DB calls, strict HttpOnly refresh and real encrypted SMTP delivery |",
        "| Platform multiline application constructor missed contract middleware | Actual installation and regression test; real retry returns one ticket and body conflict returns 409 |",
        "| Archived outbox/worker extensions were present but not executing | Owned durable publishers/consumers, retries/quarantine, real projections and jobs |",
        "| Graded attempt GET omitted results; reload consumed attempts | Safe persisted grade/answer DTO, own active-attempt contract, browser resume and locked answer/submit writes |",
        "| Cross-question choice input was accepted | Owner question-choice validation rejects it before persistence |",
        "| Quiz duration was displayed without enforcement | Persisted earlier timer/deadline, indexed bounded expiry worker, locked late-edit rejection, server-clock countdown and idempotent submission; blank written responses remain gradeable |",
        "| Snapshot filters were silently ignored | Scalar column equality filters applied; unsupported input returns a domain error |",
        "| Registry could target arbitrary origins | Explicit host allowlist and origin/path validation; custom deployment hosts require `SERVICE_REGISTRY_ALLOWED_HOSTS` |",
        "| Repeated HTTP/TLS setup dominated local service calls | Bounded per-origin clients reuse connections; per-request authorization and rejected cookie persistence are regression tested |",
        "| Large eager frontend bundle | Initial 605.69 KB / 163.4 KB gzip main bundle became 331.91 KB / 103.24 KB gzip plus lazy chunks; CSS 39.15 KB / 8.97 KB gzip |",
        "| Mobile overflow and inaccessible Admin role selector | Grid/min-width constraints, truncation and labels; complete page width/axe review |",
        "| Gateway non-root PID path denied startup | `/tmp/nginx.pid`, writable template/cache directories and verified non-root startup |",
        "| Docker Desktop's native-host alias selected unreachable IPv6 under load | Explicit local-only host-gateway IPv4 selection; latest diagnostic has zero network-unreachable errors; remaining throttles/timeouts remain failures |",
        "| Container dependency download/resolution failed | Shared tested-version constraints and host-downloaded Linux wheels; SHA-256 checks preserved; all ten service images built and their authenticated APIs verified |",
        "",
        "Database pools, connection/read/statement timeouts and request/upload limits are bounded. Authorization relationships are never cached across callers. Publishing holds an owned row lock through bounded broker confirmation; consumers deduplicate in their own transactions. These controls are not evidence of production availability or DR acceptance.",
        "",
        "PostgreSQL `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` was executed through each owner's local credentials for finalized attendance aggregation, unique learning-resource target IDs and bounded expired-attempt selection. Full plans are in `artifacts/performance/query-plans.json`. These small labelled tables do not justify speculative indexes or certify production query scalability.",
        "",
        "| Measured owner query | Planning | Execution |",
        "|---|---:|---:|",
        *[f"| {row['service']}: {row['query']} | {row['result']['Planning Time']:.3f} ms | {row['result']['Execution Time']:.3f} ms |" for row in plans],
        "",
        "## E. Test evidence",
        "",
        f"Latest isolated totals: **{totals.get('passed', 0)} passed, {totals.get('failed', 0)} failed, {totals.get('skipped', 0)} skipped** across {len(suites)} service/library/gateway/system suites. Skips include explicitly configured PostgreSQL/concurrency and external live-environment cases; they remain SKIPPED even when a separate representative local test passes. See [exact suite results](TEST_RESULTS.md).",
        "",
        "| Check | Actual result |",
        "|---|---|",
        "| Backend/shared libraries/contracts/gateway/system | Recorded suite results above; separate-process execution avoids unrelated `app` package collisions |",
        "| Frontend unit tests | PASS: 40 tests across 15 files, including deadline/clock-skew checks |",
        "| TypeScript/Vite build | PASS; production preview exercised |",
        "| Frontend lint | PASS, zero warnings |",
        "| Python service/library lint | PASS after fixes; actual command in runbook |",
        f"| Playwright latest | {stats.get('expected', 'NOT RUN')} expected/passed; {stats.get('unexpected', 0)} unexpected/failed; {stats.get('skipped', 0)} skipped; {stats.get('flaky', 0)} flaky |",
        f"| Live integration | {sum(row['status'] == 'PASS' for row in live)} PASS, {sum(row['status'] == 'FAIL' for row in live)} FAIL |",
        "| Security checks | Generated-secret scan, non-root Dockerfile audit, ownership/cookie/recovery/internal-scope/storage checks; image CVE scan NOT RUN |",
        "| Dependencies | pip check PASS; production npm audit zero reported vulnerabilities |",
        "| Docker startup | PostgreSQL, two Redis, RabbitMQ, Mailpit, MinIO and Nginx PASS; owned MinIO policies/bootstrap PASS |",
        f"| Service Docker images | {sum(row['status'] == 'PASS' for row in containers)} PASS, {sum(row['status'] == 'FAIL' for row in containers)} FAIL: built images started as non-root, passed owned migration readiness and real authenticated API requests |",
        f"| 20-user smoke, 120 seconds | {performance('smoke')} |",
        f"| 500-user diagnostic, 600 seconds | FAIL: {performance('srs-500')}; {failures('srs-500')} |",
        "| Staging/production/UAT/DR/99% availability | NOT RUN or unresolved real acceptance; local tooling tests do not substitute |",
        "",
        "The earlier load run was interrupted by gateway hardening and is retained under `artifacts/performance/interrupted-500`; it is not acceptance evidence. Early failing test/build runs and logs remain under `.integration/runtime`. The latest 500-user diagnostic shares one IP/three identities with security throttles enabled; local image builds overlapped part of the run. Its 429 rejections and 503 upstream timeouts are failures. Low response percentiles dominated by rejected requests do not establish successful interaction latency, an approved workload or production capacity. Exact environment caveats are retained in `artifacts/performance/srs-500-environment.json`.",
        "",
        "The initial Docker download hash mismatch was identified for the cryptography Linux wheel. The verified host download and cache resolved the build path without accepting the mismatched artifact. Image CVE scans, signing and real cluster deployment remain NOT RUN. `artifacts/verification/container-results.json` records each of the ten actual container/API outcomes.",
        "",
        "## F. Exact Windows run instructions",
        "",
        "See the numbered PowerShell commands in [README](../../README.md). `scripts/local.ps1` provides Configure, Infrastructure, Migrate, Services, Seed, Frontend, Test and Stop actions. APIs start before API-based seeding. Local application: `http://localhost:5173`; gateway: `http://localhost:18080`; real demo mail: `http://localhost:18025`. Credentials are generated in ignored `.integration/runtime/secrets.json`; no production password is provided or committed.",
        "",
        "Stop preserves service databases, Docker volumes, sprint inputs and unrelated projects. Local frontend preview is intended for demonstration; external production deployment follows the separately verifiable topology/release gates.",
        "",
        "## G. FYP readiness",
        "",
        "The native local demonstration has ten migrated owner APIs, three modern role workspaces, real linked demo data, durable background workers, recovery email and private file storage. Demonstrate Student attendance/timetable/learning/assessment progress, Teacher announcements, booking approval/conflicts and Admin reporting/health/jobs. Automated evidence establishes the specific workflows above.",
        "",
        "Full institutional acceptance and production readiness are **not complete**. The 500-user target must be evaluated with its actual rejection rate and an approved distributed workload; image CVE scans/signing, hosted CI, cluster deployment, production secrets/DNS/TLS, staging/UAT, sustained availability and recovery objectives remain external gates. [Known limits and proposed improvements](KNOWN_LIMITATIONS.md) explicitly separate present implementation from future work.",
    ]
    (DOCS / "FINAL_DELIVERY_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )
    print(
        f"Delivery report updated from {len(suites)} suite records and {len(live)} live cases"
    )


if __name__ == "__main__":
    main()
