from __future__ import annotations

from pathlib import Path

import streamlit as st

from mundasense.i18n.translator import Translator
from mundasense.schemas import AssessmentResult
from mundasense.ui.charts import driver_chart, interval_chart
from mundasense.ui.theme import THEME_CSS


def configure_page(title: str, *, icon: str = "🌱") -> None:
    st.set_page_config(page_title=f"{title} · MundaSense AI", page_icon=icon, layout="wide")
    st.markdown(THEME_CSS, unsafe_allow_html=True)


def locale_control(default: str = "en") -> str:
    current = st.session_state.get("locale", default)
    labels_by_locale = {
        "en": (
            "Home",
            "New assessment",
            "Assessment history",
            "Model evaluation",
            "About & safety",
        ),
        "sn": (
            "Kumba",
            "Ongororo itsva",
            "Nhoroondo yeongororo",
            "Kuongorora modhi",
            "Nezve nekuchengeteka",
        ),
    }
    nav_labels = labels_by_locale.get(current, labels_by_locale["en"])
    st.sidebar.page_link("app.py", label=nav_labels[0], icon="🏠")
    st.sidebar.page_link("pages/01_New_Assessment.py", label=nav_labels[1], icon="🌽")
    st.sidebar.page_link("pages/02_Assessment_History.py", label=nav_labels[2], icon="🗂️")
    st.sidebar.page_link("pages/03_Model_Evaluation.py", label=nav_labels[3], icon="📊")
    st.sidebar.page_link("pages/04_About_and_Safety.py", label=nav_labels[4], icon="🛡️")
    st.sidebar.divider()
    labels = {"English": "en", "Shona (demo)": "sn"}
    selected = st.sidebar.selectbox(
        "Language / Mutauro",
        list(labels),
        index=0 if current == "en" else 1,
        key="locale_select",
    )
    locale = labels[selected]
    st.session_state["locale"] = locale
    return locale


def brand_header(logo_path: Path, translator: Translator, locale: str) -> None:
    if logo_path.exists():
        st.image(str(logo_path), width=285)
    st.caption(translator.t("app.tagline", locale))


def demo_banner(translator: Translator, locale: str, enabled: bool = True) -> None:
    if enabled:
        st.markdown(
            f'<div class="ms-demo">⚠ {translator.t("demo.banner", locale)}</div>',
            unsafe_allow_html=True,
        )
    if locale == "sn":
        st.caption(translator.t("demo.shona_review", locale))


def _risk_label(result: AssessmentResult, translator: Translator, locale: str) -> str:
    icon = {"low": "✓", "moderate": "!", "high": "▲"}[result.risk_code]
    label = translator.t(f"risk.{result.risk_code}", locale)
    return f'<span class="ms-risk ms-risk-{result.risk_code}">{icon} {label}</span>'


def warning_text(warning, translator: Translator, locale: str) -> str:
    if warning.feature:
        feature = translator.t(
            {
                "rainfall_mm": "field.rainfall",
                "fertilizer_kg_ha": "field.fertilizer",
                "temperature_c": "field.temperature",
                "humidity_pct": "field.humidity",
                "soil_ph": "field.soil_ph",
            }.get(warning.feature, warning.feature),
            locale,
        )
    else:
        feature = ""
    return translator.t(warning.message_key, locale, feature=feature, **warning.details)


def render_result(result: AssessmentResult, translator: Translator, locale: str) -> None:
    st.markdown("## Assessment result")
    col_prediction, col_risk, col_confidence = st.columns([1.25, 1, 1])
    col_prediction.metric(
        translator.t("result.prediction", locale), f"{result.predicted_yield_t_ha:.2f} t/ha"
    )
    with col_risk:
        st.caption(translator.t("result.risk", locale))
        st.markdown(_risk_label(result, translator, locale), unsafe_allow_html=True)
    col_confidence.metric(
        translator.t("result.confidence", locale),
        translator.t(f"confidence.{result.confidence_code}", locale),
    )

    st.altair_chart(interval_chart(result), width="stretch")
    st.caption(
        f"{translator.t('result.range', locale)}: "
        f"{result.interval_lower_t_ha:.2f}-{result.interval_upper_t_ha:.2f} t/ha. "
        "This is a calibrated model range, not a guarantee."
    )
    st.info(translator.t(result.risk_explanation_key, locale))

    if result.advisories:
        primary = result.advisories[0]
        st.markdown(f"### {translator.t('result.next_action', locale)}")
        st.markdown(
            '<div class="ms-priority">'
            f"<strong>{translator.t(primary.title_key, locale)}</strong><br>"
            f"{translator.t(primary.message_key, locale)}"
            "</div>",
            unsafe_allow_html=True,
        )
        if len(result.advisories) > 1:
            with st.expander("Supporting safe actions"):
                for item in result.advisories[1:]:
                    st.markdown(
                        f"**{translator.t(item.title_key, locale)}**  \n"
                        f"{translator.t(item.message_key, locale)}"
                    )

    st.markdown(f"### {translator.t('result.drivers', locale)}")
    st.altair_chart(driver_chart(result, translator, locale), width="stretch")
    for index, driver in enumerate(result.top_drivers, start=1):
        name = translator.t(driver.display_key, locale)
        st.markdown(
            f"**{index}. {name}: {driver.value:g} {driver.unit}** — "
            f"{translator.t(driver.message_key, locale)}"
        )
    st.caption("Driver explanations are approximate model associations, not agronomic causes.")

    if result.data_warnings:
        st.markdown(f"### {translator.t('result.warnings', locale)}")
        for warning in result.data_warnings:
            st.markdown(
                f'<div class="ms-warning">⚠ {warning_text(warning, translator, locale)}</div>',
                unsafe_allow_html=True,
            )

    if result.referral_required:
        st.markdown(
            '<div class="ms-referral">'
            f"<strong>👤 {translator.t('result.referral', locale)}</strong><br>"
            f"{translator.t('result.referral_body', locale)}"
            "</div>",
            unsafe_allow_html=True,
        )

    st.warning(translator.t(result.disclaimer_key, locale))
    with st.expander("Technical trace"):
        st.json(
            {
                "assessment_id": result.assessment_id,
                "created_at": result.created_at,
                "model_version": result.model_version,
                "risk_policy_version": result.risk_policy_version,
                "rules_version": result.rules_version,
                "synthetic_model": result.is_synthetic_model,
                "explanation_method": result.explanation_method,
                "warning_codes": [item.code for item in result.data_warnings],
                "advisory_rule_ids": [item.rule_id for item in result.advisories],
                **result.technical_metadata,
            }
        )
