from smartedu_testkit import cases


def test_default_admin_only_matrix():
    matrix = {case.role: case.expected_statuses for case in cases()}
    assert matrix["admin"] == (200, 201, 204)
    assert matrix["teacher"] == (403,)
    assert matrix["student"] == (403,)
    assert matrix["anonymous"] == (401,)
