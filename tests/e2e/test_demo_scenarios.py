from __future__ import annotations

import pytest

from mundasense.data.demo_data import DEMO_SCENARIOS


@pytest.mark.parametrize("scenario_name", ["balanced", "water_stress", "unusual"])
def test_each_demo_scenario_completes_end_to_end(service, scenario_name: str) -> None:
    result = service.assess(DEMO_SCENARIOS[scenario_name], persist=False)
    assert result.assessment_id
    assert result.risk_code in {"low", "moderate", "high"}
    assert result.confidence_code in {"high", "medium", "low", "insufficient"}
    assert len(result.top_drivers) == 3
    assert result.advisories


def test_demo_scenarios_exercise_distinct_safety_paths(service) -> None:
    balanced = service.assess(DEMO_SCENARIOS["balanced"], persist=False)
    water_stress = service.assess(DEMO_SCENARIOS["water_stress"], persist=False)
    unusual = service.assess(DEMO_SCENARIOS["unusual"], persist=False)

    assert balanced.risk_code == "low"
    assert water_stress.risk_code == "high"
    assert water_stress.predicted_yield_t_ha < balanced.predicted_yield_t_ha
    assert unusual.data_warnings
    assert unusual.confidence_code in {"low", "insufficient"}
    assert unusual.referral_required is True
