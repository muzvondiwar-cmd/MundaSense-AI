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
