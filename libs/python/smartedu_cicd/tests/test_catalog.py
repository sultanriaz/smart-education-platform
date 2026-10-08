from smartedu_cicd import ComponentCatalog, affected_components


def c():
    return ComponentCatalog.model_validate(
        {
            "global_watched_paths": ["libs/python/**"],
            "components": [
                {
                    "name": "a",
                    "kind": "python-service",
                    "path": "services/a",
                    "dockerfile": "services/a/Dockerfile",
                    "image_suffix": "a",
                },
                {
                    "name": "frontend",
                    "kind": "frontend",
                    "path": "apps/frontend",
                    "dockerfile": "apps/frontend/Dockerfile",
                    "image_suffix": "frontend",
                },
            ],
        }
    )


def test_local_change():
    assert [x.name for x in affected_components(c(), ["services/a/app/main.py"])] == ["a"]


def test_global_change():
    assert {x.name for x in affected_components(c(), ["libs/python/x/a.py"])} == {"a", "frontend"}
