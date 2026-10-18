"""Establish a verified 12-database checkpoint with schemas, row counts, and SHA256 checksums."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from dotenv import dotenv_values
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = ROOT / ".integration/runtime"
CHECKPOINT_DIR = ROOT / "artifacts/database_checkpoints/wave17_checkpoint"
NAMES = [
    "identity",
    "academic",
    "attendance",
    "scheduling",
    "notification",
    "facility",
    "learning",
    "assessment",
    "reporting",
    "platform",
    "finance",
    "payroll",
]


def main():
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    manifest = {
        "timestamp": timestamp,
        "database_count": len(NAMES),
        "databases": {},
    }

    print(f"Creating verified checkpoint for all {len(NAMES)} databases at {CHECKPOINT_DIR}...", flush=True)

    for name in NAMES:
        env_file = RUNTIME / f"{name}-service.env"
        env = dotenv_values(env_file)
        db_url = env["DATABASE_URL"]
        db_name = f"{name}_db"
        dump_file = CHECKPOINT_DIR / f"{db_name}_{timestamp}.sql"

        # 1. Execute pg_dump via docker container
        cmd = [
            "docker",
            "exec",
            "smartedu-local-infra-postgres-1",
            "pg_dump",
            "-U",
            "postgres",
            "-d",
            db_name,
            "--clean",
            "--if-exists",
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        dump_file.write_bytes(res.stdout)

        # 2. Compute SHA256 checksum
        dump_sha256 = hashlib.sha256(res.stdout).hexdigest()

        # 3. Query PostgreSQL engine for table counts, alembic version, and row counts
        engine = create_engine(db_url)
        db_info = {
            "dump_file": dump_file.name,
            "dump_size_bytes": len(res.stdout),
            "sha256": dump_sha256,
            "tables": {},
            "alembic_version": None,
        }

        with engine.connect() as conn:
            # Alembic revision
            try:
                ver = conn.scalar(text("SELECT version_num FROM alembic_version"))
                db_info["alembic_version"] = ver
            except Exception:
                db_info["alembic_version"] = "N/A"

            # Table list and row counts
            tables = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema = 'public' AND table_type = 'BASE TABLE' "
                    "ORDER BY table_name"
                )
            ).fetchall()

            for (tbl,) in tables:
                if tbl == "alembic_version":
                    continue
                try:
                    count = conn.scalar(text(f'SELECT COUNT(*) FROM "{tbl}"'))
                    db_info["tables"][tbl] = count
                except Exception as e:
                    db_info["tables"][tbl] = f"error: {e}"

        engine.dispose()
        manifest["databases"][db_name] = db_info
        print(f"  [CHECKPOINT] {db_name}: version={db_info['alembic_version']}, tables={len(db_info['tables'])}, dump_size={len(res.stdout)} bytes, sha256={dump_sha256[:12]}...", flush=True)

    manifest_file = CHECKPOINT_DIR / f"manifest_{timestamp}.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Checkpoint manifest saved to {manifest_file}", flush=True)


if __name__ == "__main__":
    main()

