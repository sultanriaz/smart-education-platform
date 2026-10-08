from __future__ import annotations

import argparse
import json
import time
import uuid
from pathlib import Path

import httpx


def inject_marker(payload: dict, field: str, marker: str) -> dict:
    cloned = json.loads(json.dumps(payload))
    target = cloned
    parts = field.split(".")
    for part in parts[:-1]:
        value = target.get(part)
        if not isinstance(value, dict):
            value = {}
            target[part] = value
        target = value
    target[parts[-1]] = marker
    return cloned


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--send-path", required=True)
    parser.add_argument("--inbox-path", required=True)
    parser.add_argument("--sender-token", required=True)
    parser.add_argument("--recipient-token", required=True)
    parser.add_argument("--payload-file", required=True)
    parser.add_argument("--marker-field", default="title")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--poll-interval", type=float, default=0.2)
    args = parser.parse_args()

    marker = f"perf-{uuid.uuid4()}"
    payload = json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
    payload = inject_marker(payload, args.marker_field, marker)

    sender_headers = {
        "Authorization": f"Bearer {args.sender_token}",
        "Idempotency-Key": str(uuid.uuid4()),
        "X-Correlation-ID": marker,
    }
    recipient_headers = {
        "Authorization": f"Bearer {args.recipient_token}",
    }

    base = args.base_url.rstrip("/")
    with httpx.Client(timeout=5.0) as client:
        started = time.perf_counter()
        response = client.post(
            base + args.send_path,
            headers=sender_headers,
            json=payload,
        )
        response.raise_for_status()

        deadline = started + args.timeout_seconds
        while time.perf_counter() < deadline:
            inbox = client.get(
                base + args.inbox_path,
                headers=recipient_headers,
            )
            inbox.raise_for_status()
            if marker in inbox.text:
                elapsed = time.perf_counter() - started
                print(f"marker={marker}")
                print(f"notification_visible_seconds={elapsed:.3f}")
                return 0
            time.sleep(args.poll_interval)

    print(
        f"FAIL: marker was not visible within "
        f"{args.timeout_seconds:.1f} seconds"
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
