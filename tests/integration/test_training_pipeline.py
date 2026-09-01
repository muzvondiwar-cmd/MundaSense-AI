from __future__ import annotations

import numpy as np

from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.ml.features import enforce_feature_order


def test_training_produces_finite_prediction_and_metadata(trained_bundle) -> None:
    prediction = trained_bundle["pipeline"].predict(
        enforce_feature_order(
            {
                key: DEMO_SCENARIOS["balanced"][key]
                for key in (
                    "rainfall_mm",
                    "fertilizer_kg_ha",
                    "temperature_c",
                    "humidity_pct",
                    "soil_ph",
                )
            }
        )
    )
    assert np.isfinite(prediction).all()
    assert trained_bundle["training_config"]["target"] == "yield_t_ha"
    assert "yield_t_ha" not in trained_bundle["training_config"]["features"]
    assert trained_bundle["metrics"]["validation_mae_improvement_over_baseline"] > 0.05


def test_bundle_has_calibration_and_three_candidate_families(trained_bundle) -> None:
    assert trained_bundle["residual_calibration"]["absolute_error_quantile"] > 0
    names = {item["model"] for item in trained_bundle["candidate_comparison"]}
    assert {"naive_median", "ridge", "random_forest", "gradient_boosting"} <= names
