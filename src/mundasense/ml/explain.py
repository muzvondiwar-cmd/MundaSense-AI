from __future__ import annotations

from typing import Any

from mundasense.constants import FEATURE_SPEC
from mundasense.ml.features import enforce_feature_order
from mundasense.schemas import PredictionDriver


def explain_prediction(
    pipeline: Any,
    inputs: dict[str, float],
    training_ranges: dict[str, dict[str, float]],
    *,
    top_n: int = 3,
) -> tuple[PredictionDriver, ...]:
    contributions: list[PredictionDriver] = []
    prediction = float(pipeline.predict(enforce_feature_order(inputs))[0])
    for feature, value in inputs.items():
        counterfactual = dict(inputs)
        counterfactual[feature] = float(training_ranges[feature]["median"])
        without_feature_value = float(pipeline.predict(enforce_feature_order(counterfactual))[0])
        contribution = prediction - without_feature_value
        if contribution > 0.015:
            direction = "increased"
        elif contribution < -0.015:
            direction = "decreased"
        else:
            direction = "neutral"
        contributions.append(
            PredictionDriver(
                feature=feature,
                display_key=FEATURE_SPEC[feature]["display_key"],
                unit=FEATURE_SPEC[feature]["unit"],
                value=float(value),
                direction=direction,
                contribution=round(float(contribution), 4),
                message_key=f"driver.{direction}",
                approximate=True,
            )
        )
    contributions.sort(key=lambda item: (-abs(item.contribution), item.feature))
    return tuple(contributions[:top_n])
