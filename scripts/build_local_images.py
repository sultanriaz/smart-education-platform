"""Build local Linux service images from a checked dependency wheel cache.

The normal service Dockerfiles remain network-installable root-context recipes.
This optional path keeps package hash validation while moving unreliable Docker
downloads to the host and retaining verified wheels for repeatable local builds.
"""

import argparse
import hashlib
import json
import subprocess
import sys

from local_stack import NAMES, ROOT, RUNTIME

LIBRARIES = ("contracts", "infra", "observability", "perf", "security")
WHEELS = ROOT / ".integration/python-wheels"


def run(command):
    subprocess.run(command, cwd=ROOT, check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--service", choices=NAMES, nargs="+")
    args = parser.parse_args()
    WHEELS.mkdir(parents=True, exist_ok=True)
    manifest_path = RUNTIME / "wheel-cache-manifest.json"
    if manifest_path.exists():
        for recorded in json.loads(manifest_path.read_text(encoding="utf-8")):
            cached = WHEELS / recorded["filename"]
            if not cached.is_file() or hashlib.sha256(cached.read_bytes()).hexdigest() != recorded["sha256"]:
                raise SystemExit("Dependency cache integrity check failed; the recorded wheel was not accepted.")
    elif not args.prepare:
        raise SystemExit("Prepare the verified dependency cache with --prepare first.")
    if args.prepare:
        run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-c",
                "requirements.constraints.txt",
                "setuptools",
                "wheel",
            ]
        )
        run(
            [
                sys.executable,
                "-m",
                "pip",
                "wheel",
                "--no-deps",
                "--no-build-isolation",
                "--wheel-dir",
                str(WHEELS),
            ]
            + [f"libs/python/smartedu_{name}" for name in LIBRARIES]
        )
        command = [
            sys.executable,
            "-m",
            "pip",
            "download",
            "-c",
            "requirements.constraints.txt",
            "--only-binary=:all:",
            "--python-version",
            "312",
            "--implementation",
            "cp",
            "--timeout",
            "120",
            "--retries",
            "5",
            "--dest",
            str(WHEELS),
        ]
        for platform in (
            "manylinux_2_34_x86_64",
            "manylinux_2_28_x86_64",
            "manylinux_2_17_x86_64",
            "manylinux2014_x86_64",
            "manylinux1_x86_64",
        ):
            command += ["--platform", platform]
        for abi in ("cp312", "abi3", "none"):
            command += ["--abi", abi]
        for name in NAMES:
            command += ["-r", f"services/{name}-service/requirements.txt"]
        command += [
            str(WHEELS / f"smartedu_{name}-0.1.0-py3-none-any.whl")
            for name in LIBRARIES
        ]
        # Host marker evaluation on Windows excludes this Linux Uvicorn extra.
        command += ["uvloop"]
        run(command)
    metadata = [
        {"filename": file.name, "sha256": hashlib.sha256(file.read_bytes()).hexdigest()}
        for file in sorted(WHEELS.glob("*.whl"))
    ]
    manifest_path.write_text(json.dumps(metadata, indent=2))
    for name in args.service or NAMES:
        original = ROOT / f"services/{name}-service/Dockerfile"
        text = original.read_text()
        start = text.index("RUN pip install")
        end = text.index("    && useradd", start)
        text = (
            text[:start]
            + "COPY --from=dependency_wheels / /opt/verified-wheels/\nRUN pip install -c constraints.txt --no-index --find-links=/opt/verified-wheels -r requirements.txt "
            + " ".join(f"smartedu-{library}==0.1.0" for library in LIBRARIES)
            + " \\\n"
            + text[end:]
        )
        generated = RUNTIME / f"Dockerfile.{name}.verified-wheels"
        generated.write_text(text, encoding="utf-8")
        run(
            [
                "docker",
                "build",
                "--build-context",
                f"dependency_wheels={WHEELS}",
                "-f",
                str(generated),
                "-t",
                f"smartedu-local/{name}-service:integration",
                ".",
            ]
        )
        print(f"Built {name}-service from verified dependency cache", flush=True)


if __name__ == "__main__":
    main()
