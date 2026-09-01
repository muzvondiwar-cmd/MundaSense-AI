from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RiskCode = Literal["low", "moderate", "high"]
ConfidenceCode = Literal["high", "medium", "low", "insufficient"]


@dataclass(frozen=True, slots=True)
class AssessmentRequest:
    rainfall_mm: float
    fertilizer_kg_ha: float
    temperature_c: float
    humidity_pct: float
    soil_ph: float
    crop: str = "maize"
    season: str = "2025/26"
    district: str = ""
    farm_reference: str = ""

    def model_features(self) -> dict[str, float]:
        return {
            "rainfall_mm": self.rainfall_mm,
            "fertilizer_kg_ha": self.fertilizer_kg_ha,
            "temperature_c": self.temperature_c,
            "humidity_pct": self.humidity_pct,
            "soil_ph": self.soil_ph,
        }

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class DataWarning:
    code: str
    severity: Literal["info", "warning", "severe"]
    message_key: str
    feature: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class PredictionDriver:
    feature: str
    display_key: str
    unit: str
    value: float
    direction: Literal["increased", "decreased", "neutral"]
    contribution: float
    message_key: str
    approximate: bool = True


@dataclass(frozen=True, slots=True)
class Advisory:
    rule_id: str
    priority: int
    title_key: str
    message_key: str
    rationale: str
    referral_required: bool
    review_status: str


@dataclass(frozen=True, slots=True)
class AssessmentResult:
    assessment_id: str
    created_at: str
    validated_inputs: AssessmentRequest
    predicted_yield_t_ha: float
    interval_lower_t_ha: float
    interval_upper_t_ha: float
    risk_code: RiskCode
    risk_explanation_key: str
    risk_policy_version: str
    confidence_code: ConfidenceCode
    top_drivers: tuple[PredictionDriver, ...]
    data_warnings: tuple[DataWarning, ...]
    advisories: tuple[Advisory, ...]
    referral_required: bool
    model_version: str
    rules_version: str
    is_synthetic_model: bool
    disclaimer_key: str
    explanation_method: str
    technical_metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["validated_inputs"] = self.validated_inputs.to_dict()
        return payload


class AssessmentValidationError(ValueError):
    def __init__(self, errors: list[str]):
        super().__init__("; ".join(errors))
        self.errors = errors


class ModelBundleError(RuntimeError):
    """Raised when a local model bundle is missing, tampered, or incompatible."""


class RuleCatalogueError(RuntimeError):
    """Raised when the deterministic advisory catalogue is invalid."""
