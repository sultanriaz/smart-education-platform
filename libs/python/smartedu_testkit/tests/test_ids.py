from smartedu_testkit import stable_uuid


def test_stable_uuid_is_deterministic_and_distinct():
    assert stable_uuid("student") == stable_uuid("student")
    assert stable_uuid("student") != stable_uuid("teacher")
