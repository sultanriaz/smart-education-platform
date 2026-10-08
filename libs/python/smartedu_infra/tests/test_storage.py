import pytest

from smartedu_infra.storage import ObjectStorage


def test_safe_object_key_is_posix_and_relative():
    assert (
        ObjectStorage.safe_key("courses", "course-1", "week-2", "notes.pdf")
        == "courses/course-1/week-2/notes.pdf"
    )


@pytest.mark.parametrize(
    "value",
    [
        "../secret.txt",
        "/absolute/path.txt",
        "safe/../../escape.txt",
    ],
)
def test_safe_object_key_rejects_path_traversal(value):
    with pytest.raises(ValueError):
        ObjectStorage.safe_key(value)
