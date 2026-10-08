from __future__ import annotations

import argparse
import json
import subprocess


DEFAULT_COMPONENTS = [
    "identity-service",
    "academic-service",
    "attendance-service",
    "scheduling-service",
    "notification-service",
    "facility-service",
    "learning-service",
    "assessment-service",
    "reporting-service",
    "platform-service",
    "frontend",
    "api-gateway",
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--namespace", default="smartedu")
    parser.add_argument("--context")
    args = parser.parse_args()

    command = ["kubectl"]
    if args.context:
        command += ["--context", args.context]
    command += [
        "-n",
        args.namespace,
        "get",
        "secret",
        "-o",
        "json",
    ]

    result = subprocess.run(
        command,
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)
    present = {item["metadata"]["name"] for item in payload["items"]}
    required = {f"{component}-secrets" for component in DEFAULT_COMPONENTS}
    missing = sorted(required - present)

    if missing:
        print("Missing required production Secrets:")
        for name in missing:
            print(" - " + name)
        return 1

    print(f"PASS required_secrets={len(required)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
