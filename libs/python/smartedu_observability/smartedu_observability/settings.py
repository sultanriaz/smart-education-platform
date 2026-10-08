from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ObservabilitySettings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    enabled: bool = Field(default=True, alias="OBSERVABILITY_ENABLED")
    service_name: str = Field(default="smartedu-service", alias="SERVICE_NAME")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    service_version: str = Field(default="unknown", alias="SERVICE_VERSION")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    json_logs: bool = Field(default=True, alias="JSON_LOGS")

    metrics_enabled: bool = Field(default=True, alias="METRICS_ENABLED")
    metrics_path: str = Field(default="/metrics", alias="METRICS_PATH")

    tracing_enabled: bool = Field(default=True, alias="TRACING_ENABLED")
    otlp_endpoint: str = Field(
        default="http://otel-collector:4317",
        alias="OTEL_EXPORTER_OTLP_ENDPOINT",
    )
    trace_sample_ratio: float = Field(
        default=1.0,
        ge=0,
        le=1,
        alias="TRACE_SAMPLE_RATIO",
    )

    request_id_header: str = Field(
        default="X-Request-ID",
        alias="REQUEST_ID_HEADER",
    )
    correlation_id_header: str = Field(
        default="X-Correlation-ID",
        alias="CORRELATION_ID_HEADER",
    )
