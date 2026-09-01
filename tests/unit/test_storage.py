from __future__ import annotations

from datetime import UTC, datetime

from mundasense.schemas import AssessmentRequest, AssessmentResult


def sample_result() -> AssessmentResult:
    return AssessmentResult(
        assessment_id="test-1",
        created_at=datetime(2026, 8, 31, tzinfo=UTC).isoformat(),
        validated_inputs=AssessmentRequest(650, 100, 24, 60, 6.1, farm_reference="=2+2"),
        predicted_yield_t_ha=3.2,
        interval_lower_t_ha=2.5,
        interval_upper_t_ha=3.9,
        risk_code="moderate",
        risk_explanation_key="risk.explanation.moderate",
        risk_policy_version="risk-demo-v1",
        confidence_code="high",
        top_drivers=(),
        data_warnings=(),
        advisories=(),
        referral_required=False,
        model_version="test-model",
        rules_version="test-rules",
        is_synthetic_model=True,
        disclaimer_key="result.disclaimer",
        explanation_method="test",
    )


def test_save_and_reopen_snapshot(repository) -> None:
    expected = sample_result()
    repository.save(expected)
    actual = repository.get(expected.assessment_id)
    assert actual == expected


def test_schema_initialisation_is_idempotent(repository) -> None:
    repository.database.initialise()
    repository.database.initialise()
    assert repository.list() == []


def test_csv_export_neutralises_formula_injection(repository) -> None:
    repository.save(sample_result())
    exported = repository.export_csv()
    assert "'=2+2" in exported
