from __future__ import annotations

import pytest

from mundasense.ml.drift import detect_unusual_inputs
from mundasense.ml.features import enforce_feature_order
from mundasense.ml.uncertainty import prediction_interval


def test_feature_order_rejects_missing_or_unexpected_values() -> None:
    with pytest.raises(ValueError, match="missing features"):
        enforce_feature_order({"rainfall_mm": 500})


def test_interval_clips_negative_lower_bound() -> None:
    lower, upper, raw = prediction_interval(0.3, {"absolute_error_quantile": 0.8})
    assert lower == 0
    assert lower <= 0.3 <= upper
    assert raw["raw_lower"] < 0


def test_out_of_distribution_severity() -> None:
    ranges = {
        name: {"min": 0, "q01": 10, "q99": 90, "max": 100, "median": 50}
        for name in (
            "rainfall_mm",
            "fertilizer_kg_ha",
            "temperature_c",
            "humidity_pct",
            "soil_ph",
        )
    }
    inputs = {name: 50.0 for name in ranges}
    inputs["rainfall_mm"] = 5
    assert detect_unusual_inputs(inputs, ranges)[0].severity == "warning"
    inputs["rainfall_mm"] = -1
    assert detect_unusual_inputs(inputs, ranges)[0].severity == "severe"
