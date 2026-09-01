from __future__ import annotations

from mundasense.data.demo_data import DEMO_SCENARIOS


def test_full_service_persists_and_reopens(service, repository) -> None:
    result = service.assess(DEMO_SCENARIOS["balanced"])
    reopened = repository.get(result.assessment_id)
    assert reopened == result
    assert len(result.top_drivers) == 3
    assert result.interval_lower_t_ha <= result.predicted_yield_t_ha <= result.interval_upper_t_ha


def test_unusual_scenario_warns_and_refers(service) -> None:
    result = service.assess(DEMO_SCENARIOS["unusual"], persist=False)
    assert result.data_warnings
    assert result.confidence_code in {"low", "insufficient"}
    assert result.referral_required
