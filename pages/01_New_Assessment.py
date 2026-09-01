from __future__ import annotations

import streamlit as st

from mundasense.config import project_root
from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.schemas import AssessmentValidationError
from mundasense.ui.components import (
    brand_header,
    configure_page,
    demo_banner,
    locale_control,
    render_result,
)
from mundasense.ui.runtime import get_runtime

configure_page("New assessment", icon="🌽")
runtime = get_runtime()
config = runtime["config"]
translator = runtime["translator"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)
demo_banner(translator, locale, config.demo_banner)

st.markdown("# New field assessment")
st.write(
    "Use measurements from one defined assessment season. Required units are shown beside every field."
)


def apply_scenario(name: str) -> None:
    for key, value in DEMO_SCENARIOS[name].items():
        st.session_state[f"assessment_{key}"] = value


for key, value in DEMO_SCENARIOS["balanced"].items():
    st.session_state.setdefault(f"assessment_{key}", value)

st.markdown("### Try a demonstration scenario")
scenario_columns = st.columns(3)
scenario_columns[0].button(
    "A · Balanced conditions",
    on_click=apply_scenario,
    args=("balanced",),
    width="stretch",
)
scenario_columns[1].button(
    "B · Water stress",
    on_click=apply_scenario,
    args=("water_stress",),
    width="stretch",
)
scenario_columns[2].button(
    "C · Unusual data",
    on_click=apply_scenario,
    args=("unusual",),
    width="stretch",
)

with st.form("assessment_form", border=True):
    st.markdown("### 1 · Field information")
    field_left, field_right = st.columns(2)
    field_left.text_input(
        "Farm reference (use an alias, not a farmer's legal name)",
        max_chars=80,
        key="assessment_farm_reference",
    )
    field_right.text_input("District (optional)", max_chars=80, key="assessment_district")
    season_left, crop_right = st.columns(2)
    season_left.text_input("Season (optional)", max_chars=30, key="assessment_season")
    crop_right.text_input("Crop", disabled=True, key="assessment_crop")

    st.markdown("### 2 · Weather conditions")
    weather_one, weather_two, weather_three = st.columns(3)
    weather_one.number_input(
        "Seasonal rainfall (mm)",
        min_value=0.0,
        max_value=2000.0,
        step=10.0,
        key="assessment_rainfall_mm",
        help="Total rainfall for the defined assessment season; example: 650 mm.",
    )
    weather_two.number_input(
        "Mean temperature (°C)",
        min_value=-10.0,
        max_value=60.0,
        step=0.5,
        key="assessment_temperature_c",
        help="Mean temperature over the same assessment season; example: 24 °C.",
    )
    weather_three.number_input(
        "Mean humidity (%)",
        min_value=0.0,
        max_value=100.0,
        step=1.0,
        key="assessment_humidity_pct",
        help="Mean relative humidity over the assessment season; example: 62%.",
    )

    st.markdown("### 3 · Soil conditions")
    st.number_input(
        "Soil pH",
        min_value=0.0,
        max_value=14.0,
        step=0.1,
        key="assessment_soil_ph",
        help="A recent representative soil measurement; example: pH 6.2.",
    )

    st.markdown("### 4 · Farm-management input")
    st.number_input(
        "Recorded fertiliser already applied (kg/ha)",
        min_value=0.0,
        max_value=1000.0,
        step=5.0,
        key="assessment_fertilizer_kg_ha",
        help="Record only what was already applied. MundaSense does not calculate a dose.",
    )

    st.markdown("### 5 · Review and assess")
    st.caption("Submitting saves a local assessment snapshot with its model and policy versions.")
    submitted = st.form_submit_button(
        translator.t("action.assess", locale), type="primary", width="stretch"
    )

if submitted:
    payload = {
        key: st.session_state[f"assessment_{key}"]
        for key in (
            "rainfall_mm",
            "fertilizer_kg_ha",
            "temperature_c",
            "humidity_pct",
            "soil_ph",
            "crop",
            "season",
            "district",
            "farm_reference",
        )
    }
    try:
        st.session_state["latest_result"] = runtime["service"].assess(payload)
        st.success("Assessment completed and saved locally.")
    except AssessmentValidationError as exc:
        for error in exc.errors:
            st.error(error)
    except Exception as exc:  # noqa: BLE001
        st.error("The assessment could not be completed safely. Check the local model and inputs.")
        with st.expander("Developer detail"):
            st.exception(exc)

if "latest_result" in st.session_state:
    render_result(st.session_state["latest_result"], translator, locale)
