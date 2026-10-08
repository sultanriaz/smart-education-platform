from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path

import yaml


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=True,
        text=True,
        capture_output=capture,
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle")
    parser.add_argument("--context", required=True)
    parser.add_argument("--namespace", default="smartedu")
    parser.add_argument("--timeout-seconds", type=int, default=600)
    args = parser.parse_args()

    documents = [
        doc
        for doc in yaml.safe_load_all(
            Path(args.bundle).read_text(encoding="utf-8")
        )
        if isinstance(doc, dict)
    ]

    for doc in documents:
        if doc.get("kind") != "Job":
            raise SystemExit(f"unexpected migration resource kind: {doc.get('kind')}")

    if not documents:
        print("PASS migration_jobs=0")
        return 0

    completed = []
    for doc in documents:
        name = doc["metadata"]["name"]
        component = doc["metadata"].get("labels", {}).get("smartedu.io/component")
        print(f"=== migration {component} ({name}) ===")

        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".yaml",
            encoding="utf-8",
            delete=False,
        ) as handle:
            yaml.safe_dump(doc, handle, sort_keys=False)
            temp_path = handle.name

        try:
            # A release-tagged migration Job is immutable evidence. If a Job with
            # this exact name already exists, kubectl apply is idempotent and the
            # subsequent wait observes its existing completion/failure state.
            run([
                "kubectl",
                "--context", args.context,
                "apply",
                "-f", temp_path,
            ])
            run([
                "kubectl",
                "--context", args.context,
                "-n", args.namespace,
                "wait",
                "--for=condition=complete",
                f"job/{name}",
                f"--timeout={args.timeout_seconds}s",
            ])
            completed.append(name)
        except subprocess.CalledProcessError:
            print(f"Migration Job failed or timed out: {name}")
            try:
                logs = run([
                    "kubectl",
                    "--context", args.context,
                    "-n", args.namespace,
                    "logs",
                    f"job/{name}",
                    "--all-containers=true",
                    "--tail=200",
                ], capture=True)
                print(logs.stdout)
            except Exception as exc:
                print(f"Could not retrieve migration logs: {exc}")
            return 1
        finally:
            Path(temp_path).unlink(missing_ok=True)

    print(f"PASS migration_jobs={len(completed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
