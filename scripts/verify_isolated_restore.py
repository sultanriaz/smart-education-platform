"""Perform isolated disaster-recovery verification of all twelve database checkpoint archives."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path
from decimal import Decimal

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_DIR = ROOT / "artifacts/database_checkpoints/wave17_checkpoint"
MANIFEST_PATH = CHECKPOINT_DIR / "manifest_20261018T155818Z.json"
CONTAINER = "smartedu-local-infra-postgres-1"

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

def run_psql(cmd_str: str, db: str = "postgres") -> tuple[int, str, str]:
    proc = subprocess.run(
        ["docker", "exec", CONTAINER, "psql", "-U", "postgres", "-d", db, "-c", cmd_str],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc.returncode, proc.stdout, proc.stderr

def run_psql_file(sql_file_path: Path, db: str) -> tuple[int, str, str]:
    with open(sql_file_path, "rb") as f:
        content = f.read()
    proc = subprocess.run(
        ["docker", "exec", "-i", CONTAINER, "psql", "-U", "postgres", "-d", db, "-v", "ON_ERROR_STOP=1"],
        input=content,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return proc.returncode, proc.stdout.decode("utf-8", errors="replace"), proc.stderr.decode("utf-8", errors="replace")

def main():
    if not MANIFEST_PATH.exists():
        print(f"Error: Manifest {MANIFEST_PATH} does not exist", file=sys.stderr)
        sys.exit(1)

    with open(MANIFEST_PATH, "r") as f:
        manifest = json.load(f)

    results = []

    print("=" * 80)
    print("SMARTEDU TWELVE-DATABASE DISASTER RECOVERY RESTORATION & INTEGRITY AUDIT")
    print("=" * 80)

    for name in NAMES:
        db_name = f"{name}_db"
        iso_db = f"dr_isolated_{db_name}"
        role_name = f"{name}_svc"
        db_meta = manifest["databases"].get(db_name)
        if not db_meta:
            print(f"Error: Database {db_name} not found in manifest", file=sys.stderr)
            continue

        dump_filename = db_meta["dump_file"]
        dump_path = CHECKPOINT_DIR / dump_filename
        expected_sha256 = db_meta["sha256"]
        expected_alembic = db_meta["alembic_version"]
        expected_tables = db_meta["tables"]

        item_result = {
            "database": db_name,
            "archive_file": dump_filename,
            "archive_format": "PostgreSQL Plain SQL (pg_dump 16.15)",
            "archive_size": dump_path.stat().st_size if dump_path.exists() else 0,
            "sha256_verified": False,
            "restore_executed": False,
            "restore_exit_code": None,
            "restore_result": "FAIL",
            "alembic_verified": False,
            "alembic_version": None,
            "schema_validated": False,
            "table_count_matched": False,
            "row_counts_matched": False,
            "domain_integrity_verified": False,
            "details": [],
            "overall_status": "FAIL",
        }

        # 1. SHA-256 Checksum Validation
        if not dump_path.exists():
            item_result["details"].append(f"Archive file {dump_path} missing")
            results.append(item_result)
            continue

        file_bytes = dump_path.read_bytes()
        actual_sha256 = hashlib.sha256(file_bytes).hexdigest()
        if actual_sha256 == expected_sha256:
            item_result["sha256_verified"] = True
        else:
            item_result["details"].append(f"SHA-256 mismatch: expected {expected_sha256}, got {actual_sha256}")
            results.append(item_result)
            continue

        # 2. Isolated Disposable Database Creation
        run_psql(f"DROP DATABASE IF EXISTS {iso_db};")
        code, out, err = run_psql(f"CREATE DATABASE {iso_db} OWNER {role_name};")
        if code != 0:
            item_result["details"].append(f"CREATE DATABASE failed: {err}")
            results.append(item_result)
            continue

        # 3. Isolated Restoration Execution
        item_result["restore_executed"] = True
        code, out, err = run_psql_file(dump_path, iso_db)
        item_result["restore_exit_code"] = code
        if code != 0:
            item_result["details"].append(f"psql restore error: {err[:300]}")
            run_psql(f"DROP DATABASE IF EXISTS {iso_db};")
            results.append(item_result)
            continue
        item_result["restore_result"] = "PASS"

        # 4. Alembic Revision Validation
        code, out, err = run_psql("SELECT version_num FROM alembic_version;", db=iso_db)
        actual_alembic = out.strip().split("\n")[-2].strip() if code == 0 and "version_num" in out else "N/A"
        item_result["alembic_version"] = actual_alembic
        if actual_alembic == expected_alembic:
            item_result["alembic_verified"] = True
        else:
            item_result["details"].append(f"Alembic mismatch: expected {expected_alembic}, got {actual_alembic}")

        # 5. Table Inventory & Row Counts Validation
        code, out, err = run_psql(
            "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE' ORDER BY table_name;",
            db=iso_db,
        )
        lines = [line.strip() for line in out.strip().split("\n")[2:-1] if line.strip() and not line.startswith("(")]
        actual_tables = [t for t in lines if t and t != "alembic_version"]
        
        missing_tables = [t for t in expected_tables if t not in actual_tables]
        if not missing_tables and len(actual_tables) == len(expected_tables):
            item_result["table_count_matched"] = True
            item_result["schema_validated"] = True
        else:
            item_result["details"].append(f"Table discrepancy: expected {len(expected_tables)}, got {len(actual_tables)} (missing: {missing_tables})")

        row_mismatches = []
        for tbl, exp_count in expected_tables.items():
            c_code, c_out, c_err = run_psql(f'SELECT COUNT(*) FROM "{tbl}";', db=iso_db)
            if c_code == 0:
                cnt_str = c_out.strip().split("\n")[-2].strip()
                try:
                    cnt = int(cnt_str)
                    if cnt != exp_count:
                        row_mismatches.append(f"{tbl}: expected {exp_count}, got {cnt}")
                except ValueError:
                    row_mismatches.append(f"{tbl}: invalid count output {cnt_str}")
            else:
                row_mismatches.append(f"{tbl}: count query failed")

        if not row_mismatches:
            item_result["row_counts_matched"] = True
        else:
            item_result["details"].append(f"Row count mismatches: {', '.join(row_mismatches)}")

        # 6. Domain-Specific Integrity Checks
        domain_integrity_passed = True
        if db_name == "finance_db":
            # Check Double Entry debits == credits
            d_code, d_out, _ = run_psql("SELECT COALESCE(SUM(debit), 0), COALESCE(SUM(credit), 0) FROM journal_lines;", db=iso_db)
            if d_code == 0:
                parts = [p.strip() for p in d_out.strip().split("\n")[-2].split("|")]
                total_debit, total_credit = Decimal(parts[0]), Decimal(parts[1])
                if total_debit == total_credit and total_debit > 0:
                    item_result["details"].append(f"General Ledger Trial Balance verified: Debits (PKR {total_debit}) == Credits (PKR {total_credit})")
                else:
                    domain_integrity_passed = False
                    item_result["details"].append(f"Trial balance imbalance: Debit={total_debit}, Credit={total_credit}")
            else:
                domain_integrity_passed = False

            # Check invoice line items reference valid invoices
            i_code, i_out, _ = run_psql("SELECT COUNT(*) FROM invoice_line_items li LEFT JOIN invoices i ON li.invoice_id = i.id WHERE i.id IS NULL;", db=iso_db)
            if i_code == 0 and int(i_out.strip().split("\n")[-2].strip()) == 0:
                item_result["details"].append("All invoice line items reference valid invoices")
            else:
                domain_integrity_passed = False
                item_result["details"].append("Orphaned invoice line items detected")

        elif db_name == "payroll_db":
            # Check run items reference valid runs
            r_code, r_out, _ = run_psql("SELECT COUNT(*) FROM payroll_run_items pri LEFT JOIN payroll_runs pr ON pri.run_id = pr.id WHERE pr.id IS NULL;", db=iso_db)
            if r_code == 0 and int(r_out.strip().split("\n")[-2].strip()) == 0:
                item_result["details"].append("All payroll run items reference valid payroll runs")
            else:
                domain_integrity_passed = False
                item_result["details"].append("Orphaned payroll run items detected")

            # Check payslips reference valid profiles
            p_code, p_out, _ = run_psql("SELECT COUNT(*) FROM payslips ps LEFT JOIN employee_payroll_profiles ep ON ps.employee_profile_id = ep.id WHERE ep.id IS NULL;", db=iso_db)
            if p_code == 0 and int(p_out.strip().split("\n")[-2].strip()) == 0:
                item_result["details"].append("All payslips reference valid employee profiles")
            else:
                domain_integrity_passed = False
                item_result["details"].append("Orphaned payslips detected")

        item_result["domain_integrity_verified"] = domain_integrity_passed

        # 7. Overall Evaluation
        if (
            item_result["sha256_verified"]
            and item_result["restore_result"] == "PASS"
            and item_result["alembic_verified"]
            and item_result["table_count_matched"]
            and item_result["row_counts_matched"]
            and item_result["domain_integrity_verified"]
        ):
            item_result["overall_status"] = "PASS"

        # 8. Clean up isolated disposable database
        run_psql(f"DROP DATABASE IF EXISTS {iso_db};")

        results.append(item_result)
        status_sym = "[PASS]" if item_result["overall_status"] == "PASS" else "[FAIL]"
        print(f"{status_sym} {db_name:18} | Restored & Verified | Tables: {len(actual_tables):2} | Alembic: {actual_alembic}")

    print("=" * 80)
    all_passed = all(r["overall_status"] == "PASS" for r in results)
    print(f"DISASTER RECOVERY AUDIT RESULT: {'ALL 12 DATABASES PASS' if all_passed else 'FAILURES DETECTED'}")
    print("=" * 80)

    # Save detailed JSON report
    report_file = CHECKPOINT_DIR / "restore_verification_report.json"
    with open(report_file, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Detailed restore audit written to {report_file}")

if __name__ == "__main__":
    main()

