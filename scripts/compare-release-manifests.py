from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def image_map(payload: dict) -> dict[str, str]:
    return {
        item["component"]: item["immutable_ref"]
        for item in payload.get("images", [])
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("accepted")
    parser.add_argument("candidate")
    args = parser.parse_args()

    accepted = load(args.accepted)
    candidate = load(args.candidate)
    failures: list[str] = []

    for key in ("release_tag", "commit_sha"):
        if accepted.get(key) != candidate.get(key):
            failures.append(
                f"{key} differs: accepted={accepted.get(key)!r} "
                f"candidate={candidate.get(key)!r}"
            )

    accepted_images = image_map(accepted)
    candidate_images = image_map(candidate)
    if accepted_images != candidate_images:
        missing = sorted(set(accepted_images) - set(candidate_images))
        extra = sorted(set(candidate_images) - set(accepted_images))
        changed = sorted(
            component
            for component in set(accepted_images) & set(candidate_images)
            if accepted_images[component] != candidate_images[component]
        )
        failures.append(
            f"image mismatch missing={missing} extra={extra} changed={changed}"
        )

    if failures:
        print("Release identity mismatch:")
        for failure in failures:
            print(" - " + failure)
        return 1

    print(
        f"PASS release={candidate.get('release_tag')} "
        f"images={len(candidate_images)} exact_identity_match=true"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
