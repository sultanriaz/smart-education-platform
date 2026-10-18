"""Hashes supplied, REAL UAT artifacts. Never generates a fake approval."""
import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--release-id", required=True)
    parser.add_argument("--evidence-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if not args.release_id.strip() or not args.evidence_dir.is_dir():
        parser.error("Real release ID and existing evidence directory required")
    items = []
    for p in sorted(args.evidence_dir.rglob("*")):
        if p.is_file() and p.resolve() != args.output.resolve():
            items.append({"path": str(p.relative_to(args.evidence_dir)), "bytes": p.stat().st_size, "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
    if not items:
        parser.error("Evidence folder contains no files")
    result = {"release_id": args.release_id, "recorded_at": datetime.now(UTC).isoformat(), "evidence": items, "acceptance_status": "PENDING_HUMAN_REVIEW", "pilot_signoff": None, "accessibility_manual_review": None}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("Recorded real evidence hashes, without claiming UAT acceptance:", args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
