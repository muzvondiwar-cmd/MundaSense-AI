from __future__ import annotations

import pytest

from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.schemas import AssessmentValidationError
from mundasense.validation import sanitise_text, validate_assessment


def test_valid_assessment_is_coerced() -> None:
    payload = {**DEMO_SCENARIOS["balanced"], "rainfall_mm": "690"}
    request = validate_assessment(payload)
    assert request.crop == "maize"
    assert request.rainfall_mm == 690.0
    assert request.model_features()["soil_ph"] == 6.2


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("rainfall_mm", -1),
        ("fertilizer_kg_ha", 1001),
        ("temperature_c", 61),
        ("humidity_pct", 101),
        ("soil_ph", 14.1),
    ],
)
def test_hard_boundaries_are_rejected(field: str, value: float) -> None:
    payload = {**DEMO_SCENARIOS["balanced"], field: value}
    with pytest.raises(AssessmentValidationError):
        validate_assessment(payload)


def test_non_maize_crop_is_rejected() -> None:
    with pytest.raises(AssessmentValidationError, match="maize"):
        validate_assessment({**DEMO_SCENARIOS["balanced"], "crop": "sorghum"})


def test_text_is_bounded_and_control_characters_are_removed() -> None:
    assert sanitise_text(" Farm\x00 A ", field_name="farm") == "Farm A"
    with pytest.raises(AssessmentValidationError):
        sanitise_text("x" * 81, field_name="farm")
