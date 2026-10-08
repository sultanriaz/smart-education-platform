import pytest

from smartedu_cicd import image_tags, validate_release_tag


def test_tags():
    assert image_tags(commit_sha="a" * 40, release_tag="v1.2.3") == ["sha-aaaaaaaaaaaa", "v1.2.3"]


def test_bad():
    with pytest.raises(ValueError):
        validate_release_tag("latest")
