from __future__ import annotations

from mundasense.schemas import DataWarning


def detect_unusual_inputs(
    inputs: dict[str, float], training_ranges: dict[str, dict[str, float]]
) -> tuple[DataWarning, ...]:
    warnings: list[DataWarning] = []
    for feature, value in inputs.items():
        bounds = training_ranges[feature]
        if value < bounds["min"] or value > bounds["max"]:
            warnings.append(
                DataWarning(
                    code=f"ood_extreme_{feature}",
                    severity="severe",
                    message_key="warning.extreme",
                    feature=feature,
                    details={
                        "lower": round(bounds["min"], 2),
                        "upper": round(bounds["max"], 2),
                        "value": value,
                    },
                )
            )
        elif value < bounds["q01"] or value > bounds["q99"]:
            warnings.append(
                DataWarning(
                    code=f"ood_unusual_{feature}",
                    severity="warning",
                    message_key="warning.unusual",
                    feature=feature,
                    details={
                        "lower": round(bounds["q01"], 2),
                        "upper": round(bounds["q99"], 2),
                        "value": value,
                    },
                )
            )
    if len(warnings) >= 2:
        warnings.append(
            DataWarning(
                code="ood_multiple_features",
                severity="severe",
                message_key="warning.multiple",
                details={"feature_count": len(warnings)},
            )
        )
    return tuple(warnings)
