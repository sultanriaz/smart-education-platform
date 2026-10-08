from smartedu_infra.naming import (
    DEFAULT_BUCKETS,
    SERVICE_DATABASES,
    SERVICE_DB_USERS,
    database_name,
    database_user,
)


def test_all_ten_services_have_independent_database_names_and_users():
    assert len(SERVICE_DATABASES) == 10
    assert len(set(SERVICE_DATABASES.values())) == 10
    assert len(set(SERVICE_DB_USERS.values())) == 10

    assert database_name("academic-service") == "academic_db"
    assert database_user("academic-service") == "academic_svc"


def test_required_object_buckets_are_private_domain_names():
    assert "learning-resources" in DEFAULT_BUCKETS
    assert "platform-imports" in DEFAULT_BUCKETS
    assert "platform-exports" in DEFAULT_BUCKETS
    assert "report-exports" in DEFAULT_BUCKETS
