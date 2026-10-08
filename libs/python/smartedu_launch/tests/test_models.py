import pytest

from smartedu_launch import ReleaseImage, ReleaseManifest


def test_release_manifest_requires_digest_pinned_images():
    image = ReleaseImage(
        component="identity-service",
        digest="sha256:" + "a" * 64,
        immutable_ref="ghcr.io/example/identity@sha256:" + "a" * 64,
    )
    manifest = ReleaseManifest(
        release_tag="v1.0.0",
        commit_sha="b" * 40,
        images=[image],
    )
    assert manifest.images[0].component == "identity-service"


def test_tag_only_image_rejected():
    with pytest.raises(ValueError):
        ReleaseImage(
            component="identity-service",
            digest="sha256:" + "a" * 64,
            immutable_ref="ghcr.io/example/identity:v1.0.0",
        )


def test_short_commit_rejected():
    with pytest.raises(ValueError):
        ReleaseManifest(
            release_tag="v1.0.0",
            commit_sha="abc123",
            images=[],
        )
