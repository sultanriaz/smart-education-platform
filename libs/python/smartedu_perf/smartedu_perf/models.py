from __future__ import annotations

from pydantic import BaseModel, Field


class MetricBudget(BaseModel):
    name: str
    p95_ms: int = Field(gt=0)
    max_error_rate: float = Field(default=0.01, ge=0, le=1)
    min_rps: float | None = Field(default=None, ge=0)


class LoadProfile(BaseModel):
    name: str
    users: int = Field(ge=1)
    spawn_rate: float = Field(gt=0)
    duration_seconds: int = Field(ge=1)
    description: str = ""


class EndpointResult(BaseModel):
    name: str
    requests: int = Field(ge=0)
    failures: int = Field(ge=0)
    p50_ms: float = Field(ge=0)
    p95_ms: float = Field(ge=0)
    p99_ms: float = Field(ge=0)
    avg_ms: float = Field(ge=0)
    rps: float = Field(ge=0)

    @property
    def error_rate(self) -> float:
        if self.requests == 0:
            return 0.0
        return self.failures / self.requests


class BudgetEvaluation(BaseModel):
    name: str
    passed: bool
    reasons: list[str] = Field(default_factory=list)
