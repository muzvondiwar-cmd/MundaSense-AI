from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from mundasense.schemas import AssessmentRequest

Locale = Literal["en", "sn"]
Source = Literal["manual", "demo", "scenario"]
RiskBand = Literal["low", "moderate", "high"]
ConfidenceBand = Literal["high", "medium", "low", "insufficient"]
DataStatus = Literal["real", "synthetic_demo"]


class AssessmentCreate(BaseModel):
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

    def to_domain(self) -> AssessmentRequest:
        return AssessmentRequest(**self.model_dump())


class InputValue(BaseModel):
    value: float
    unit: str


class AssessmentInputs(BaseModel):
    rainfall: InputValue
    fertilizer: InputValue
    temperature: InputValue
    humidity: InputValue
    soil_ph: InputValue


class AssessmentContext(BaseModel):
    crop: Literal["maize"]
    season: str
    district: str
    farm_reference: str
    language: Locale
    source: Source


class Confidence(BaseModel):
    band: ConfidenceBand
    score: float | None = None
    method: str


class Prediction(BaseModel):
    yield_t_ha: float
    range_low_t_ha: float
    range_high_t_ha: float
    risk_band: RiskBand
    risk_score: float = Field(ge=0, le=100)
    risk_label: str
    risk_explanation: str
    confidence: Confidence


class Driver(BaseModel):
    feature: str
    label: str
    direction: Literal["raises_yield", "lowers_yield", "neutral"]
    importance: float
    signed_contribution: float
    value: float
    unit: str
    explanation: str
    approximate: bool


class WarningItem(BaseModel):
    code: str
    severity: Literal["info", "warning", "critical"]
    title: str
    message: str
    feature: str | None = None


class SupportingAction(BaseModel):
    title: str
    message: str
    rule_id: str


class AdvisoryResponse(BaseModel):
    priority_action: str
    message: str
    reason: str
    referral_required: bool
    referral_message: str | None
    supporting_actions: list[SupportingAction]


class Versions(BaseModel):
    model: str
    risk_policy: str
    rules: str
    app: str


class AssessmentResponse(BaseModel):
    assessment_id: str
    created_at: str
    inputs: AssessmentInputs
    context: AssessmentContext
    prediction: Prediction
    drivers: list[Driver]
    warnings: list[WarningItem]
    advisory: AdvisoryResponse
    versions: Versions
    data_status: DataStatus
    synthetic_model: bool
    explanation_method: str
    disclaimer: str
    technical_metadata: dict[str, Any]


class HistoryItem(BaseModel):
    assessment_id: str
    created_at: str
    district: str
    farm_reference: str
    predicted_yield_t_ha: float
    risk_band: RiskBand
    confidence: ConfidenceBand
    referral_required: bool
    data_status: DataStatus
    source: Source
    model_version: str
    top_warning: str | None
    sync_status: Literal["pending", "synchronized", "failed"] = "synchronized"
    archived: bool = False


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
    total: int
    districts: list[str]


class ScenarioSimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    baseline_assessment_id: str = Field(min_length=1, max_length=120)
    overrides: dict[str, float]
    language: Locale = "en"


class ScenarioDelta(BaseModel):
    yield_t_ha: float
    range_low_t_ha: float
    range_high_t_ha: float
    risk_changed: bool
    confidence_changed: bool


class ScenarioSimulationResponse(BaseModel):
    baseline: AssessmentResponse
    scenario: AssessmentResponse
    delta: ScenarioDelta
    persisted: Literal[False] = False


class DashboardKpis(BaseModel):
    total_assessments: int
    high_risk_assessments: int
    average_predicted_yield_t_ha: float | None
    low_confidence_assessments: int
    referrals_required: int
    assessments_this_season: int = 0
    awaiting_synchronization: int = 0


class CountPoint(BaseModel):
    label: str
    count: int


class YieldPoint(BaseModel):
    label: str
    average_yield_t_ha: float
    sample_size: int


class DashboardResponse(BaseModel):
    kpis: DashboardKpis
    assessments_over_time: list[CountPoint]
    yield_over_time: list[YieldPoint]
    risk_distribution: list[CountPoint]
    confidence_distribution: list[CountPoint]
    frequent_drivers: list[CountPoint]
    yield_by_district: list[YieldPoint]
    priority_cases: list[HistoryItem]
    contains_synthetic_demo: bool
    small_sample: bool
    active_filters: dict[str, str | bool | None]
    model_version: str = ""
    recent_assessments: list[HistoryItem] = Field(default_factory=list)
    data_quality_alerts: list[HistoryItem] = Field(default_factory=list)


class DemoScenario(BaseModel):
    id: str
    name: str
    description: str
    values: AssessmentCreate


class HealthCheck(BaseModel):
    ok: bool
    detail: str


class HealthResponse(BaseModel):
    ready: bool
    status: Literal["local_system_ready", "needs_attention"]
    checks: dict[str, HealthCheck]
    app_version: str
    model_version: str | None


class FeatureConfig(BaseModel):
    key: str
    label: str
    unit: str
    hard_min: float
    hard_max: float
    example: float


class AppConfigResponse(BaseModel):
    crop: Literal["maize"] = "maize"
    features: list[FeatureConfig]
    locales: list[Locale]
    default_locale: Locale
    model_version: str
    app_version: str
    extension_contact: str
    demo_model: bool


class ModelMetric(BaseModel):
    label: str
    value: float
    unit: str | None = None


class ModelCardResponse(BaseModel):
    model_version: str
    status: str
    champion: str
    created_at: str
    explanation_method: str
    interval_method: str
    metrics: list[ModelMetric]
    features: list[FeatureConfig]
    limitations: list[str]
    training_ranges: dict[str, dict[str, float]]
