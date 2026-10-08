from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from smartedu_uat import UATRun, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("--staging-url", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    release = json.loads(
        Path(args.release_manifest).read_text(encoding="utf-8")
    )
    tag = release["release_tag"]
    commit = release["commit_sha"]

    if len(commit) != 40:
        raise SystemExit("release manifest commit_sha must be full Git SHA")

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or f"uat-{re.sub(r'[^A-Za-z0-9.-]+', '-', tag)}-{stamp}"

    run = UATRun(
        run_id=run_id,
        release_tag=tag,
        commit_sha=commit,
        staging_url=args.staging_url.rstrip("/"),
        started_at=datetime.now(timezone.utc),
    )
    save_run(run, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
