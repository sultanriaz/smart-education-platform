"""Package clean client delivery archive for SmartEdu Platform (Wave 17).

Excludes:
- Version control metadata (.git)
- Python virtual environments (.venv, venv)
- Python bytecode (__pycache__, *.pyc, *.pyo, *.pyd)
- Node modules and frontend build caches (node_modules, dist, dist-ssr)
- Test caches and results (.pytest_cache, .ruff_cache, test-results, playwright-report, htmlcov)
- Patches, diffs, and backup snapshots (.integration, .wave-patch-backups, *.patch, *.diff, *.bak, *.backup-*)
- Temporary logs (*.log) and OS artifacts (.DS_Store, Thumbs.db)
"""
from __future__ import annotations

import hashlib
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_ZIP = ROOT.parent / "SmartEdu_Client_Delivery_Wave17.zip"

EXCLUDE_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    ".pytest_cache",
    ".ruff_cache",
    ".vscode",
    ".idea",
    ".integration",
    ".wave-patch-backups",
    "SmartEdu_Wave08_Staging_Test_Hotfix",
    "node_modules",
    "dist",
    "dist-ssr",
    "build",
    "test-results",
    "playwright-report",
    "htmlcov",
    "__pycache__",
    "patch-backups",
    "artifacts",
}

EXCLUDE_EXTS = {
    ".pyc",
    ".pyo",
    ".pyd",
    ".log",
    ".patch",
    ".diff",
    ".bak",
    ".zip",
    ".tsbuildinfo",
    ".eslintcache",
}

EXCLUDE_FILES = {
    "Thumbs.db",
    ".DS_Store",
    "ehthumbs.db",
}

def main():
    print("=" * 80)
    print("SMARTEDU CLIENT DELIVERY PACKAGING")
    print("=" * 80)
    print(f"Source Root Directory : {ROOT}")
    print(f"Destination Archive   : {OUTPUT_ZIP}")

    if OUTPUT_ZIP.exists():
        OUTPUT_ZIP.unlink()

    included_count = 0
    total_uncompressed_bytes = 0

    with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
        for root_str, dirs, files in os.walk(ROOT):
            root_path = Path(root_str)
            rel_root = root_path.relative_to(ROOT)

            # Filter out excluded directories in-place
            dirs[:] = [
                d for d in dirs
                if d not in EXCLUDE_DIRS
                and not d.startswith(".backup")
                and not d.startswith("SmartEdu_")
            ]

            for file_name in files:
                file_path = root_path / file_name
                rel_file = rel_root / file_name

                # Check file exclusion
                if any(file_name.endswith(ext) for ext in EXCLUDE_EXTS):
                    continue
                if file_name in EXCLUDE_FILES:
                    continue
                if file_name.startswith(".backup"):
                    continue

                # Add to ZIP under archive root 'smart-education-platform/'
                archive_name = Path("smart-education-platform") / rel_file
                zipf.write(file_path, arcname=str(archive_name))

                included_count += 1
                total_uncompressed_bytes += file_path.stat().st_size

    # Compute SHA-256 checksum of generated package
    zip_bytes = OUTPUT_ZIP.read_bytes()
    zip_sha256 = hashlib.sha256(zip_bytes).hexdigest()
    zip_size_mb = len(zip_bytes) / (1024 * 1024)
    uncomp_size_mb = total_uncompressed_bytes / (1024 * 1024)

    print("-" * 80)
    print(f"Total Files Packaged  : {included_count:,}")
    print(f"Uncompressed Size     : {uncomp_size_mb:.2f} MB")
    print(f"Compressed ZIP Size   : {zip_size_mb:.2f} MB")
    print(f"Compression Ratio     : {(1 - len(zip_bytes)/total_uncompressed_bytes)*100:.1f}% savings")
    print(f"SHA-256 Checksum      : {zip_sha256}")
    print("=" * 80)
    print("DELIVERY PACKAGE READY FOR CLIENT HANDOFF!")

if __name__ == "__main__":
    main()

