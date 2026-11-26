from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    database_url: str = Field(alias="DATABASE_URL")
    db_pool_size: int = Field(default=10, ge=1, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, ge=0, alias="DB_MAX_OVERFLOW")
    db_pool_timeout_seconds: int = Field(default=30, ge=1, alias="DB_POOL_TIMEOUT_SECONDS")
    db_pool_recycle_seconds: int = Field(default=1800, ge=60, alias="DB_POOL_RECYCLE_SECONDS")
    db_statement_timeout_ms: int = Field(default=15000, ge=100, alias="DB_STATEMENT_TIMEOUT_MS")
    db_application_name: str = Field(default="smartedu-service", alias="DB_APPLICATION_NAME")


class RedisSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    redis_cache_url: str = Field(default="redis://redis-cache:6379/0", alias="REDIS_CACHE_URL")
    redis_durable_url: str = Field(
        default="redis://redis-durable:6379/0", alias="REDIS_DURABLE_URL"
    )
    redis_key_prefix: str = Field(default="smartedu", alias="REDIS_KEY_PREFIX")
    redis_socket_timeout_seconds: float = Field(
        default=2.0, gt=0, alias="REDIS_SOCKET_TIMEOUT_SECONDS"
    )


class MessagingSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    rabbitmq_url: str = Field(
        default="amqp://smartedu:smartedu@rabbitmq:5672/smartedu",
        alias="RABBITMQ_URL",
    )
    event_exchange: str = Field(default="smartedu.events", alias="EVENT_EXCHANGE")
    dead_letter_exchange: str = Field(default="smartedu.dlx", alias="DEAD_LETTER_EXCHANGE")
    retry_exchange: str = Field(default="smartedu.retry", alias="RETRY_EXCHANGE")
    queue_prefix: str = Field(default="smartedu", alias="EVENT_QUEUE_PREFIX")
    prefetch_count: int = Field(default=20, ge=1, le=500, alias="EVENT_PREFETCH_COUNT")
    publish_timeout_seconds: float = Field(default=5.0, gt=0, alias="EVENT_PUBLISH_TIMEOUT_SECONDS")
    retry_delay_ms: int = Field(default=5000, ge=100, le=300000, alias="EVENT_RETRY_DELAY_MS")
    max_delivery_attempts: int = Field(default=5, ge=1, le=20, alias="EVENT_MAX_DELIVERY_ATTEMPTS")


class ObjectStorageSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    s3_endpoint_url: str = Field(default="http://minio:9000", alias="S3_ENDPOINT_URL")
    s3_region: str = Field(default="us-east-1", alias="S3_REGION")
    s3_access_key_id: str = Field(alias="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = Field(alias="S3_SECRET_ACCESS_KEY")
    s3_use_ssl: bool = Field(default=False, alias="S3_USE_SSL")
    s3_addressing_style: str = Field(default="path", alias="S3_ADDRESSING_STYLE")
    s3_presign_ttl_seconds: int = Field(
        default=900, ge=60, le=86400, alias="S3_PRESIGN_TTL_SECONDS"
    )


class RetentionSettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    outbox_retention_days: int = Field(default=14, ge=1, alias="OUTBOX_RETENTION_DAYS")
    inbox_retention_days: int = Field(default=30, ge=1, alias="INBOX_RETENTION_DAYS")
    audit_retention_days: int = Field(default=365, ge=30, alias="AUDIT_RETENTION_DAYS")
    notification_delivery_retention_days: int = Field(
        default=90, ge=7, alias="NOTIFICATION_DELIVERY_RETENTION_DAYS"
    )
    job_retention_days: int = Field(default=30, ge=1, alias="JOB_RETENTION_DAYS")
