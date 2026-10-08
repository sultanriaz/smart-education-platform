from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import httpx

SERVICES = {
    "identity": "IDENTITY_SERVICE_URL",
    "academic": "ACADEMIC_SERVICE_URL",
    "attendance": "ATTENDANCE_SERVICE_URL",
    "scheduling": "SCHEDULING_SERVICE_URL",
    "notification": "NOTIFICATION_SERVICE_URL",
    "facility": "FACILITY_SERVICE_URL",
    "learning": "LEARNING_SERVICE_URL",
    "assessment": "ASSESSMENT_SERVICE_URL",
    "reporting": "REPORTING_SERVICE_URL",
    "platform": "PLATFORM_SERVICE_URL",
}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="tests/contracts/snapshots",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.mkdir(parents=True, exist_ok=True)

    missing = []
    for service, variable in SERVICES.items():
        base = os.getenv(variable, "").rstrip("/")
        if not base:
            missing.append(variable)
            continue
        response = httpx.get(base + "/openapi.json", timeout=10.0)
        response.raise_for_status()
        document = response.json()
        (output / f"{service}.openapi.json").write_text(
            json.dumps(document, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"captured {service}")

    if missing:
        print("Skipped services without URL variables: " + ", ".join(missing))


if __name__ == "__main__":
    main()
