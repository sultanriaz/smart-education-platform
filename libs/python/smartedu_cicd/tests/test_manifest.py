import pytest

from smartedu_cicd import ReleaseImage, ReleaseManifest


def test_manifest():
    i = ReleaseImage(
        component="x",
        repository="ghcr.io/o/x",
        digest="sha256:" + "b" * 64,
        immutable_ref="ghcr.io/o/x@sha256:" + "b" * 64,
    )
    m = ReleaseManifest(
        release_tag="v1.0.0",
        commit_sha="a" * 40,
        generated_at="2026-10-07T00:00:00Z",
        source_repository="o/r",
        images=[i],
    )
    assert m.images[0].component == "x"


def test_bad_digest():
    with pytest.raises(ValueError):
        ReleaseImage(component="x", repository="r", digest="latest", immutable_ref="r:latest")
