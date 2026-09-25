from __future__ import annotations

from backend.schemas import (
    AdvisoryResponse,
    AssessmentContext,
    AssessmentInputs,
    AssessmentResponse,
    Confidence,
    Driver,
    HistoryItem,
    InputValue,
    Prediction,
    SupportingAction,
    Versions,
    WarningItem,
)
from mundasense.constants import APP_VERSION
from mundasense.i18n.translator import Translator
from mundasense.schemas import AssessmentResult, DataWarning

FEATURE_KEYS = {
    "rainfall_mm": "field.rainfall",
    "fertilizer_kg_ha": "field.fertilizer",
    "temperature_c": "field.temperature",
    "humidity_pct": "field.humidity",
    "soil_ph": "field.soil_ph",
}


def derive_data_status(result: AssessmentResult) -> str:
    if result.data_status == "synthetic_demo":
        return "synthetic_demo"
    inputs = result.validated_inputs
    if inputs.source in {"demo", "scenario"} or inputs.farm_reference.lower().startswith("demo -"):
        return "synthetic_demo"
    return "real"


def translate_warning(warning: DataWarning, translator: Translator, locale: str) -> WarningItem:
    if warning.feature:
        feature = translator.t(FEATURE_KEYS.get(warning.feature, warning.feature), locale)
    else:
        feature = ""
    message = translator.t(warning.message_key, locale, feature=feature, **warning.details)
    severity = "critical" if warning.severity == "severe" else warning.severity
    title = {
        "critical": "Measurement needs verification",
        "warning": "Unusual model input",
        "info": "Assessment note",
    }[severity]
    return WarningItem(
        code=warning.code,
        severity=severity,
        title=title,
        message=message,
        feature=warning.feature,
    )


def serialize_result(
    result: AssessmentResult, translator: Translator, locale: str | None = None
) -> AssessmentResponse:
    inputs = result.validated_inputs
    selected_locale = locale if locale in {"en", "sn"} else inputs.language
    drivers = [
        Driver(
            feature=driver.feature,
            label=translator.t(driver.display_key, selected_locale),
            direction={
                "increased": "raises_yield",
                "decreased": "lowers_yield",
                "neutral": "neutral",
            }[driver.direction],
            importance=round(abs(driver.contribution), 4),
            signed_contribution=round(driver.contribution, 4),
            value=driver.value,
            unit=driver.unit,
            explanation=translator.t(driver.message_key, selected_locale),
            approximate=driver.approximate,
        )
        for driver in result.top_drivers
    ]
    warnings = [
        translate_warning(item, translator, selected_locale) for item in result.data_warnings
    ]
    primary = result.advisories[0] if result.advisories else None
    supporting = [
        SupportingAction(
            title=translator.t(item.title_key, selected_locale),
            message=translator.t(item.message_key, selected_locale),
            rule_id=item.rule_id,
        )
        for item in result.advisories[1:]
    ]
    advisory = AdvisoryResponse(
        priority_action=(
            translator.t(primary.title_key, selected_locale)
            if primary
            else "Seek qualified agronomic review"
        ),
        message=(
            translator.t(primary.message_key, selected_locale)
            if primary
            else "No deterministic advisory was available for this result."
        ),
        reason=primary.rationale if primary else "No matching rule was available.",
        referral_required=result.referral_required,
        referral_message=(
            translator.t("result.referral_body", selected_locale)
            if result.referral_required
            else None
        ),
        supporting_actions=supporting,
    )
    return AssessmentResponse(
        assessment_id=result.assessment_id,
        created_at=result.created_at,
        inputs=AssessmentInputs(
            rainfall=InputValue(value=inputs.rainfall_mm, unit="mm / assessment season"),
            fertilizer=InputValue(value=inputs.fertilizer_kg_ha, unit="kg/ha recorded application"),
            temperature=InputValue(value=inputs.temperature_c, unit="°C seasonal mean"),
            humidity=InputValue(value=inputs.humidity_pct, unit="% seasonal mean"),
            soil_ph=InputValue(value=inputs.soil_ph, unit="pH"),
        ),
        context=AssessmentContext(
            crop="maize",
            season=inputs.season,
            district=inputs.district,
            farm_reference=inputs.farm_reference,
            language=inputs.language,
            source=inputs.source,
        ),
        prediction=Prediction(
            yield_t_ha=result.predicted_yield_t_ha,
            range_low_t_ha=result.interval_lower_t_ha,
            range_high_t_ha=result.interval_upper_t_ha,
            risk_band=result.risk_code,
            risk_label=translator.t(f"risk.{result.risk_code}", selected_locale),
            risk_explanation=translator.t(result.risk_explanation_key, selected_locale),
            confidence=Confidence(
                band=result.confidence_code,
                score=None,
                method="Deterministic policy using interval width and input familiarity.",
            ),
        ),
        drivers=drivers,
        warnings=warnings,
        advisory=advisory,
        versions=Versions(
            model=result.model_version,
            risk_policy=result.risk_policy_version,
            rules=result.rules_version,
            app=APP_VERSION,
        ),
        data_status=derive_data_status(result),
        synthetic_model=result.is_synthetic_model,
        explanation_method=result.explanation_method,
        disclaimer=translator.t(result.disclaimer_key, selected_locale),
        technical_metadata=result.technical_metadata,
    )


def history_item(result: AssessmentResult, translator: Translator) -> HistoryItem:
    serialized = serialize_result(result, translator, "en")
    top_warning = serialized.warnings[0].message if serialized.warnings else None
    return HistoryItem(
        assessment_id=result.assessment_id,
        created_at=result.created_at,
        district=result.validated_inputs.district,
        farm_reference=result.validated_inputs.farm_reference,
        predicted_yield_t_ha=result.predicted_yield_t_ha,
        risk_band=result.risk_code,
        confidence=result.confidence_code,
        referral_required=result.referral_required,
        data_status=derive_data_status(result),
        source=result.validated_inputs.source,
        model_version=result.model_version,
        top_warning=top_warning,
    )
