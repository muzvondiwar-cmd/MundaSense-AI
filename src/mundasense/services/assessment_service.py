from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from mundasense.advisory.engine import AdvisoryEngine
from mundasense.advisory.policy import classify_risk, derive_confidence, referral_required
from mundasense.constants import RULES_VERSION
from mundasense.ml.drift import detect_unusual_inputs
from mundasense.ml.explain import explain_prediction
from mundasense.ml.features import enforce_feature_order
from mundasense.ml.uncertainty import prediction_interval
from mundasense.schemas import AssessmentRequest, AssessmentResult
from mundasense.storage.assessment_repository import AssessmentRepository
from mundasense.validation import validate_assessment

LOGGER = logging.getLogger("mundasense")


class AssessmentService:
    def __init__(
        self,
        *,
        bundle: dict[str, Any],
        advisory_engine: AdvisoryEngine,
        repository: AssessmentRepository | None = None,
        clock: Any | None = None,
        id_factory: Any | None = None,
    ):
        self.bundle = bundle
        self.advisory_engine = advisory_engine
        self.repository = repository
        self.clock = clock or (lambda: datetime.now(UTC))
        self.id_factory = id_factory or (lambda: str(uuid4()))

    def assess(
        self, request: AssessmentRequest | dict[str, Any], *, persist: bool = True
    ) -> AssessmentResult:
        """Validate, predict, explain, guard, and optionally persist an assessment."""
        validated = validate_assessment(request)
        inputs = validated.model_features()
        pipeline = self.bundle["pipeline"]
        prediction = max(0.0, float(pipeline.predict(enforce_feature_order(inputs))[0]))
        lower, upper, raw_bounds = prediction_interval(
            prediction, self.bundle["residual_calibration"]
        )
        warnings = detect_unusual_inputs(inputs, self.bundle["training_ranges"])
        risk, risk_explanation, risk_version = classify_risk(prediction)
        confidence = derive_confidence(
            prediction,
            lower,
            upper,
            warnings,
            metrics_valid=bool(self.bundle.get("metrics")),
        )
        drivers = explain_prediction(
            pipeline,
            inputs,
            self.bundle["training_ranges"],
            top_n=3,
        )
        advisories = self.advisory_engine.evaluate(
            inputs=inputs,
            risk=risk,
            confidence=confidence,
            warnings=warnings,
        )
        must_refer = referral_required(risk, confidence, warnings) or any(
            item.referral_required for item in advisories
        )
        created_at = self.clock().replace(microsecond=0).isoformat()
        result = AssessmentResult(
            assessment_id=self.id_factory(),
            created_at=created_at,
            validated_inputs=validated,
            predicted_yield_t_ha=round(prediction, 3),
            interval_lower_t_ha=round(lower, 3),
            interval_upper_t_ha=round(upper, 3),
            risk_code=risk,
            risk_explanation_key=risk_explanation,
            risk_policy_version=risk_version,
            confidence_code=confidence,
            top_drivers=drivers,
            data_warnings=warnings,
            advisories=advisories,
            referral_required=must_refer,
            model_version=self.bundle["model_version"],
            rules_version=RULES_VERSION,
            is_synthetic_model=bool(self.bundle["is_synthetic"]),
            disclaimer_key="result.disclaimer",
            explanation_method=self.bundle["explanation_method"],
            technical_metadata={
                "raw_interval_bounds": raw_bounds,
                "dataset_fingerprint": self.bundle["dataset_fingerprint"],
                "bundle_schema_version": self.bundle["bundle_schema_version"],
                "interval_method": self.bundle["residual_calibration"]["method"],
            },
        )
        if persist and self.repository is not None:
            self.repository.save(result)
        LOGGER.info(
            "assessment_completed",
            extra={"model_version": result.model_version, "rules_version": result.rules_version},
        )
        return result
