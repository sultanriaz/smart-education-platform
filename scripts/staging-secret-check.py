from __future__ import annotations

import argparse
import json
import subprocess

from smartedu_staging import load_topology


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--topology",
        default="config/staging/staging-topology.yaml",
    )
    args = parser.parse_args()

    topology = load_topology(args.topology)
    result = subprocess.run(
        [
            "kubectl",
            "-n",
            topology.namespace,
            "get",
            "secret",
            "-o",
            "json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    present = {
        item["metadata"]["name"]
        for item in json.loads(result.stdout)["items"]
    }
    missing = sorted(set(topology.required_secrets) - present)

    if missing:
        print("Missing staging Secrets:")
        for name in missing:
            print(" - " + name)
        return 1

    print(f"PASS required_secrets={len(topology.required_secrets)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
