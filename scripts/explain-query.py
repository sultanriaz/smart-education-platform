from __future__ import annotations

import argparse
import json
from pathlib import Path

import psycopg


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--database-url", required=True)
    parser.add_argument("--sql-file", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Use ANALYZE and actually execute the query. Use only on safe test SQL.",
    )
    args = parser.parse_args()

    sql = Path(args.sql_file).read_text(encoding="utf-8").strip().rstrip(";")
    if not sql:
        raise SystemExit("SQL file is empty")

    prefix = "EXPLAIN (FORMAT JSON, BUFFERS"
    if args.execute:
        prefix += ", ANALYZE"
    statement = prefix + ") " + sql

    with psycopg.connect(args.database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(statement)
            row = cursor.fetchone()

    plan = row[0] if row else None
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(plan, indent=2, default=str) + "\n", encoding="utf-8")
    print(f"query_plan={output}")


if __name__ == "__main__":
    main()
