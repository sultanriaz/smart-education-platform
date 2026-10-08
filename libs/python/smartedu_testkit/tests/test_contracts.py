import pytest

from smartedu_testkit import assert_no_internal_paths, collect_openapi_paths


def test_openapi_path_collection():
    document = {"paths": {"/health": {}, "/api/v1/users": {}}}
    assert collect_openapi_paths(document) == {"/health", "/api/v1/users"}


def test_internal_path_guard():
    document = {"paths": {"/api/v1/internal/events": {}}}
    with pytest.raises(AssertionError):
        assert_no_internal_paths(document)
