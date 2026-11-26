from __future__ import annotations

SERVICE_DATABASES = {
    "identity-service": "identity_db",
    "academic-service": "academic_db",
    "attendance-service": "attendance_db",
    "scheduling-service": "scheduling_db",
    "notification-service": "notification_db",
    "facility-service": "facility_db",
    "learning-service": "learning_db",
    "assessment-service": "assessment_db",
    "reporting-service": "reporting_db",
    "platform-service": "platform_db",
}

SERVICE_DB_USERS = {
    service: service.removesuffix("-service").replace("-", "_") + "_svc"
    for service in SERVICE_DATABASES
}

DEFAULT_BUCKETS = (
    "learning-resources",
    "platform-imports",
    "platform-exports",
    "report-exports",
)


def database_name(service_name: str) -> str:
    try:
        return SERVICE_DATABASES[service_name]
    except KeyError as exc:
        raise ValueError(f"Unknown service: {service_name}") from exc


def database_user(service_name: str) -> str:
    try:
        return SERVICE_DB_USERS[service_name]
    except KeyError as exc:
        raise ValueError(f"Unknown service: {service_name}") from exc
