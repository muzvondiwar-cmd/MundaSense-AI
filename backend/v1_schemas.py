from __future__ import annotations

from datetime import date
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field, model_validator

from backend.schemas import (
    AssessmentCreate,
    AssessmentResponse,
    ConfidenceBand,
    Driver,
    Locale,
    RiskBand,
    Source,
    WarningItem,
)

SyncStatus = Literal["pending", "synchronized", "failed"]


class FarmCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: str(uuid4()), min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=120)
    contact_name: str = Field(default="", max_length=120)
    province: str = Field(min_length=1, max_length=80)
    district: str = Field(min_length=1, max_length=80)
    ward: str = Field(default="", max_length=80)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    notes: str = Field(default="", max_length=2_000)
    sync_status: SyncStatus = "synchronized"
    is_demo: bool = False
    created_at: str | None = None
    updated_at: str | None = None


class FarmResponse(FarmCreate):
    created_at: str
    updated_at: str
    field_count: int = 0


class FieldCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    id: str = Field(default_factory=lambda: str(uuid4()), min_length=8, max_length=64)
    farm_id: str = Field(min_length=8, max_length=64)
    name: str = Field(min_length=1, max_length=120)
    size_hectares: float = Field(gt=0, le=10_000)
    maize_variety: str = Field(default="", max_length=100)
    planting_date: date | None = None
    season: str = Field(default="2025/26", max_length=30)
    target_yield_t_ha: float | None = Field(default=None, ge=0, le=30)
    notes: str = Field(default="", max_length=2_000)
    sync_status: SyncStatus = "synchronized"
    is_demo: bool = False
    created_at: str | None = None
    updated_at: str | None = None


class FieldResponse(FieldCreate):
    planting_date: str | None = None
    created_at: str
    updated_at: str


class AssessmentV1Create(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    crop: Literal["maize"] = "maize"
    rainfall_mm: float = Field(ge=0, le=2_000)
    fertilizer_kg_ha: float = Field(ge=0, le=1_000)
    temperature_c: float = Field(ge=-10, le=60)
    humidity_pct: float = Field(ge=0, le=100)
    soil_ph: float = Field(ge=0, le=14)
    season: str = Field(default="2025/26", max_length=30)
    district: str = Field(default="", max_length=80)
    farm_reference: str = Field(default="", max_length=80)
    language: Locale = "en"
    source: Source = "manual"
    field_id: str | None = Field(default=None, max_length=64)
    province: str = Field(default="", max_length=80)
    ward: str = Field(default="", max_length=80)
    planting_date: date | None = None
    maize_variety: str = Field(default="", max_length=100)
    growth_stage: str = Field(default="", max_length=80)
    field_size_hectares: float | None = Field(default=None, gt=0, le=10_000)
    fertilizer_type: str = Field(default="", max_length=100)
    irrigation_available: bool | None = None
    crop_stress_observations: str = Field(default="", max_length=1_000)
    idempotency_key: str | None = Field(default=None, min_length=8, max_length=120)

    def legacy(self) -> AssessmentCreate:
        keys = AssessmentCreate.model_fields
        return AssessmentCreate(
            **{key: value for key, value in self.model_dump().items() if key in keys}
        )


class YieldRange(BaseModel):
    lower: float
    upper: float


class PredictionContract(BaseModel):
    predicted_yield_t_ha: float
    yield_range_t_ha: YieldRange
    risk_score: float = Field(ge=0, le=100)
    risk_level: RiskBand
    confidence: ConfidenceBand
    confidence_explanation: str
    top_drivers: list[Driver]
    warnings: list[WarningItem]
    recommended_next_actions: list[str]
    model_version: str
    is_demo_model: bool
    full_result: AssessmentResponse


class ScenarioCompareRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baseline_assessment_id: str = Field(min_length=1, max_length=120)
    overrides: dict[str, float]
    language: Locale = "en"


class SyncBatchItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    entity_type: Literal["assessment", "farm", "field"]
    idempotency_key: str = Field(min_length=8, max_length=120)
    payload: dict[str, Any]


class SyncBatchRequest(BaseModel):
    items: list[SyncBatchItem] = Field(min_length=1, max_length=100)

    @model_validator(mode="after")
    def unique_keys(self) -> SyncBatchRequest:
        keys = [item.idempotency_key for item in self.items]
        if len(keys) != len(set(keys)):
            raise ValueError("Each sync item must have a unique idempotency key.")
        return self


class SyncItemResult(BaseModel):
    idempotency_key: str
    entity_type: str
    entity_id: str
    status: Literal["synchronized", "failed"]
    duplicate: bool = False
    error: str | None = None


class SyncBatchResponse(BaseModel):
    items: list[SyncItemResult]
    synchronized: int
    failed: int


class InsightPoint(BaseModel):
    label: str
    value: float
    sample_size: int | None = None


class InsightsResponse(BaseModel):
    yield_over_time: list[InsightPoint]
    risk_distribution: list[InsightPoint]
    risk_by_district: list[InsightPoint]
    average_inputs: dict[str, float]
    common_risk_drivers: list[InsightPoint]
    data_completeness_pct: float
    unusual_records: int
    model_versions: list[InsightPoint]
    total_records: int
    contains_demo_data: bool
