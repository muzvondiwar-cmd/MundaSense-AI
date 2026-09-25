from __future__ import annotations

import math

from mundasense.constants import RISK_POLICY_VERSION
from mundasense.schemas import ConfidenceCode, DataWarning, RiskCode

HIGH_RISK_BELOW_T_HA = 2.0
MODERATE_RISK_BELOW_T_HA = 3.0


def classify_risk(predicted_yield_t_ha: float) -> tuple[RiskCode, str, str]:
    if predicted_yield_t_ha < HIGH_RISK_BELOW_T_HA:
        return "high", "risk.explanation.high", RISK_POLICY_VERSION
    if predicted_yield_t_ha < MODERATE_RISK_BELOW_T_HA:
        return "moderate", "risk.explanation.moderate", RISK_POLICY_VERSION
    return "low", "risk.explanation.low", RISK_POLICY_VERSION


def derive_confidence(
    prediction: float,
    lower: float,
    upper: float,
    warnings: tuple[DataWarning, ...],
    metrics_valid: bool = True,
) -> ConfidenceCode:
    if not metrics_valid or not all(math.isfinite(value) for value in (prediction, lower, upper)):
        return "insufficient"
    width_ratio = (upper - lower) / max(abs(prediction), 0.5)
    severe_count = sum(item.severity == "severe" for item in warnings)
    unusual_count = sum(item.code.startswith("ood_") for item in warnings)
    if severe_count or unusual_count >= 2 or width_ratio > 0.85:
        return "low"
    if unusual_count == 1 or width_ratio > 0.5:
        return "medium"
    return "high"


def referral_required(
    risk: RiskCode, confidence: ConfidenceCode, warnings: tuple[DataWarning, ...]
) -> bool:
    return (
        risk == "high"
        or confidence in {"low", "insufficient"}
        or any(item.severity == "severe" for item in warnings)
        or sum(item.code.startswith("ood_") for item in warnings) >= 2
    )
