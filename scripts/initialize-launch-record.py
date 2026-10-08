from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from smartedu_launch import LaunchRecord, save_launch


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("--readiness-run", required=True)
    parser.add_argument("--production-url", required=True)
    parser.add_argument("--kube-context", required=True)
    parser.add_argument("--launch-id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    release = json.loads(Path(args.release_manifest).read_text(encoding="utf-8"))
    readiness = json.loads(Path(args.readiness_run).read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    launch_id = args.launch_id or (
        f"launch-{re.sub(r'[^A-Za-z0-9.-]+', '-', release['release_tag'])}-{stamp}"
    )

    record = LaunchRecord(
        launch_id=launch_id,
        release_tag=release["release_tag"],
        commit_sha=release["commit_sha"],
        production_url=args.production_url.rstrip("/"),
        kube_context=args.kube_context,
        started_at=datetime.now(timezone.utc),
        readiness_run_id=readiness["run_id"],
    )
    save_launch(record, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
