from __future__ import annotations

import math
from typing import Any


def prediction_interval(
    prediction: float, residual_calibration: dict[str, Any]
) -> tuple[float, float, dict[str, float]]:
    width = float(residual_calibration["absolute_error_quantile"])
    raw_lower = prediction - width
    raw_upper = prediction + width
    lower = max(0.0, raw_lower)
    upper = max(lower, raw_upper)
    if not all(math.isfinite(value) for value in (prediction, lower, upper)):
        raise ValueError("Prediction interval contains a non-finite value.")
    return lower, upper, {"raw_lower": raw_lower, "raw_upper": raw_upper}
