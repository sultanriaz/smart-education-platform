from smartedu_testkit import breaking_changes


def test_breaking_change_detects_removed_path_and_operation():
    old = {
        "paths": {
            "/api/v1/things": {
                "get": {"responses": {"200": {}, "404": {}}},
                "post": {"responses": {"201": {}}},
            }
        }
    }
    new = {
        "paths": {
            "/api/v1/things": {
                "get": {"responses": {"200": {}}},
            }
        }
    }

    kinds = {change.kind for change in breaking_changes(old, new)}
    assert "removed_operation" in kinds
    assert "removed_response" in kinds


def test_added_paths_are_non_breaking():
    old = {"paths": {"/a": {"get": {"responses": {"200": {}}}}}}
    new = {
        "paths": {
            "/a": {"get": {"responses": {"200": {}}}},
            "/b": {"get": {"responses": {"200": {}}}},
        }
    }
    assert breaking_changes(old, new) == []
