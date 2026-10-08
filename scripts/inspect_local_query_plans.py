"""Measure SELECT plans using only the generated local owner credentials."""

import json

from dotenv import dotenv_values
from local_stack import ROOT, RUNTIME
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url


def main():
    fixtures = json.loads((RUNTIME / "demo-fixtures.json").read_text(encoding="utf-8"))
    cases = (
        ("attendance", "finalized_student_summary", """
            SELECT r.status, count(*) FROM attendance_records r
            JOIN attendance_sessions s ON s.id = r.attendance_session_id
            WHERE r.student_user_id = :student AND s.status = 'FINALIZED'
            GROUP BY r.status
        """, {"student": fixtures["student"]["id"]}),
        ("learning", "unique_section_resource_ids", """
            SELECT DISTINCT resource_id FROM resource_targets
            WHERE target_type = 'SECTION' AND target_id = :section
        """, {"section": fixtures["section"]["id"]}),
        ("assessment", "bounded_expired_attempts", """
            SELECT id FROM attempts WHERE status = 'IN_PROGRESS'
            AND expires_at <= CURRENT_TIMESTAMP
            ORDER BY expires_at, id LIMIT 25
        """, {}),
    )
    records = []
    for service, name, query, parameters in cases:
        config = dotenv_values(RUNTIME / f"{service}-service.env")
        database_url = config["DATABASE_URL"]
        parsed = make_url(database_url)
        if config.get("ENVIRONMENT") != "development" or parsed.host not in ("localhost", "127.0.0.1") or parsed.port != 55432:
            raise SystemExit("Query-plan inspection is restricted to generated local databases.")
        engine = create_engine(database_url, connect_args={"connect_timeout": 3})
        try:
            with engine.connect() as connection:
                result = connection.execute(text("EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + query), parameters).scalar_one()[0]
                records.append({"service": service, "query": name, "result": result})
                print(f"{service}: planning {result['Planning Time']:.3f} ms; execution {result['Execution Time']:.3f} ms")
        finally:
            engine.dispose()
    output = ROOT / "artifacts/performance/query-plans.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, indent=2) + "\n", encoding="utf-8")
    print("Small labelled fixture tables do not establish production query scalability.")


if __name__ == "__main__":
    main()
