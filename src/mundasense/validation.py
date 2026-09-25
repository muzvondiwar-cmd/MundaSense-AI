from __future__ import annotations

import math
import re
from collections.abc import Mapping
from typing import Any

from mundasense.constants import FEATURE_SPEC
from mundasense.schemas import AssessmentRequest, AssessmentValidationError

_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def sanitise_text(value: Any, *, field_name: str, max_length: int = 80) -> str:
    text = _CONTROL_CHARS.sub(" ", str(value or "")).strip()
    text = " ".join(text.split())
    if len(text) > max_length:
        raise AssessmentValidationError([f"{field_name} must be {max_length} characters or fewer."])
    return text


def _coerce_feature(name: str, value: Any, errors: list[str]) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        errors.append(f"{name} must be a number.")
        return math.nan
    if not math.isfinite(number):
        errors.append(f"{name} must be finite.")
        return number
    bounds = FEATURE_SPEC[name]
    if number < bounds["hard_min"] or number > bounds["hard_max"]:
        errors.append(
            f"{name} must be between {bounds['hard_min']:g} and {bounds['hard_max']:g} "
            f"{bounds['unit']}."
        )
    return number


def validate_assessment(payload: Mapping[str, Any] | AssessmentRequest) -> AssessmentRequest:
    if isinstance(payload, AssessmentRequest):
        values: Mapping[str, Any] = payload.to_dict()
    else:
        values = payload
    errors: list[str] = []
    features = {name: _coerce_feature(name, values.get(name), errors) for name in FEATURE_SPEC}
    crop = str(values.get("crop", "maize")).strip().lower()
    if crop != "maize":
        errors.append("crop must be maize for this MVP.")
    language = str(values.get("language", "en")).strip().lower()
    if language not in {"en", "sn"}:
        errors.append("language must be 'en' or 'sn'.")
    source = str(values.get("source", "manual")).strip().lower()
    if source not in {"manual", "demo", "scenario"}:
        errors.append("source must be manual, demo, or scenario.")

    try:
        season = sanitise_text(values.get("season", ""), field_name="season", max_length=30)
        district = sanitise_text(values.get("district", ""), field_name="district")
        farm_reference = sanitise_text(
            values.get("farm_reference", ""), field_name="farm_reference"
        )
    except AssessmentValidationError as exc:
        errors.extend(exc.errors)
        season = district = farm_reference = ""

    if errors:
        raise AssessmentValidationError(errors)
    return AssessmentRequest(
        **features,
        crop=crop,
        season=season,
        district=district,
        farm_reference=farm_reference,
        language=language,
        source=source,
    )
