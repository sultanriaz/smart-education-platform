from __future__ import annotations

import re

SEMVER_TAG = re.compile(r"^v(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(-[0-9A-Za-z.-]+)?$")


def validate_release_tag(tag: str) -> str:
    if not SEMVER_TAG.fullmatch(tag):
        raise ValueError("release tag must be vMAJOR.MINOR.PATCH or a hyphenated prerelease")
    return tag


def short_sha(commit_sha: str, length: int = 12) -> str:
    if len(commit_sha) < length:
        raise ValueError("commit SHA is too short")
    int(commit_sha, 16)
    return commit_sha[:length].lower()


def image_tags(*, commit_sha: str, release_tag: str | None = None) -> list[str]:
    result = [f"sha-{short_sha(commit_sha)}"]
    if release_tag:
        result.append(validate_release_tag(release_tag))
    return result
