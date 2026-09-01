from __future__ import annotations

from mundasense.advisory.policy import classify_risk, derive_confidence, referral_required
from mundasense.schemas import DataWarning


def test_risk_threshold_edges_are_transparent() -> None:
    assert classify_risk(1.999)[0] == "high"
    assert classify_risk(2.0)[0] == "moderate"
    assert classify_risk(3.499)[0] == "moderate"
    assert classify_risk(3.5)[0] == "low"


def test_confidence_uses_interval_width() -> None:
    assert derive_confidence(4.0, 3.2, 4.8, ()) == "high"
    assert derive_confidence(2.0, 0.7, 3.3, ()) == "low"
    assert derive_confidence(4.0, 3.5, 4.5, (), metrics_valid=False) == "insufficient"


def test_extreme_warning_requires_referral() -> None:
    warning = DataWarning("ood_extreme_rainfall", "severe", "warning.extreme")
    assert referral_required("low", "high", (warning,))
