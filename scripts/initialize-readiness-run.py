from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from smartedu_readiness import ReadinessRun, save_run


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("release_manifest")
    parser.add_argument("--production-url", required=True)
    parser.add_argument("--run-id")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    release = json.loads(Path(args.release_manifest).read_text(encoding="utf-8"))
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_id = args.run_id or (
        f"readiness-{re.sub(r'[^A-Za-z0-9.-]+', '-', release['release_tag'])}-{stamp}"
    )

    run = ReadinessRun(
        run_id=run_id,
        release_tag=release["release_tag"],
        commit_sha=release["commit_sha"],
        production_url=args.production_url.rstrip("/"),
        started_at=datetime.now(timezone.utc),
    )
    save_run(run, args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
