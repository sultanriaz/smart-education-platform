from __future__ import annotations

from functools import lru_cache

from smartedu_infra import (
    DatabaseSettings,
    MessagingSettings,
    ObjectStorage,
    ObjectStorageSettings,
    RabbitEventBus,
    RedisSettings,
    build_engine,
)

SERVICE_NAME = "notification-service"


@lru_cache
def database_settings() -> DatabaseSettings:
    settings = DatabaseSettings()
    settings.db_application_name = SERVICE_NAME
    return settings


@lru_cache
def database_engine():
    return build_engine(database_settings())


@lru_cache
def redis_settings() -> RedisSettings:
    return RedisSettings()


@lru_cache
def messaging_settings() -> MessagingSettings:
    return MessagingSettings()


@lru_cache
def event_bus() -> RabbitEventBus:
    return RabbitEventBus(
        service_name=SERVICE_NAME,
        settings=messaging_settings(),
    )


@lru_cache
def object_storage_settings() -> ObjectStorageSettings:
    return ObjectStorageSettings()


@lru_cache
def object_storage() -> ObjectStorage:
    return ObjectStorage.from_settings(object_storage_settings())
