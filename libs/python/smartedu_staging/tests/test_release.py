import pytest

from smartedu_staging import ReleaseImage


def test_release_image_must_be_digest_pinned():
    image = ReleaseImage(
        component="identity-service",
        digest="sha256:" + "a" * 64,
        immutable_ref="ghcr.io/example/identity@sha256:" + "a" * 64,
    )
    assert image.component == "identity-service"


def test_tag_only_release_image_rejected():
    with pytest.raises(ValueError):
        ReleaseImage(
            component="identity-service",
            digest="sha256:" + "a" * 64,
            immutable_ref="ghcr.io/example/identity:v1.0.0",
        )
