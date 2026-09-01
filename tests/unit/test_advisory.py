from __future__ import annotations

from mundasense.advisory.engine import AdvisoryEngine
from mundasense.config import project_root
from mundasense.schemas import DataWarning


def engine() -> AdvisoryEngine:
    return AdvisoryEngine(project_root() / "src" / "mundasense" / "advisory" / "rules.yml")


def test_severe_warning_has_highest_precedence() -> None:
    warning = DataWarning("ood_extreme_soil_ph", "severe", "warning.extreme")
    actions = engine().evaluate(
        inputs={
            "rainfall_mm": 200,
            "fertilizer_kg_ha": 90,
            "temperature_c": 32,
            "humidity_pct": 40,
            "soil_ph": 9,
        },
        risk="high",
        confidence="low",
        warnings=(warning,),
    )
    assert actions[0].rule_id == "ADV-DATA-001"
    assert actions[0].referral_required


def test_safe_monitoring_is_default() -> None:
    actions = engine().evaluate(
        inputs={
            "rainfall_mm": 700,
            "fertilizer_kg_ha": 120,
            "temperature_c": 24,
            "humidity_pct": 62,
            "soil_ph": 6.2,
        },
        risk="low",
        confidence="high",
        warnings=(),
    )
    assert [item.rule_id for item in actions] == ["ADV-MONITOR-001"]


def test_water_stress_rule_never_prescribes_a_dose() -> None:
    actions = engine().evaluate(
        inputs={
            "rainfall_mm": 250,
            "fertilizer_kg_ha": 70,
            "temperature_c": 31,
            "humidity_pct": 38,
            "soil_ph": 6,
        },
        risk="moderate",
        confidence="medium",
        warnings=(),
    )
    assert actions[0].rule_id == "ADV-WATER-001"
    assert "dose" not in actions[0].rationale.lower()
