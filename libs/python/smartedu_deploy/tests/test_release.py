import pytest

from smartedu_deploy import ReleaseImage


def test_release_image_requires_digest_pinned_reference():
    image = ReleaseImage(
        component="identity-service",
        repository="ghcr.io/example/identity-service",
        digest="sha256:" + "a" * 64,
        immutable_ref="ghcr.io/example/identity-service@sha256:" + "a" * 64,
    )
    assert image.component == "identity-service"


def test_release_image_rejects_tag_only_reference():
    with pytest.raises(ValueError):
        ReleaseImage(
            component="identity-service",
            repository="ghcr.io/example/identity-service",
            digest="sha256:" + "a" * 64,
            immutable_ref="ghcr.io/example/identity-service:v1.0.0",
        )
