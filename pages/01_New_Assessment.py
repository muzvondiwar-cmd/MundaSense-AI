from __future__ import annotations

import streamlit as st

from mundasense.config import project_root
from mundasense.data.demo_data import DEMO_SCENARIOS
from mundasense.schemas import AssessmentValidationError
from mundasense.ui.components import (
    assessment_progress,
    brand_header,
    configure_page,
    demo_banner,
    locale_control,
    page_intro,
    render_result,
    section_heading,
)
from mundasense.ui.runtime import get_runtime

configure_page("New assessment", icon="🌽")
runtime = get_runtime()
config = runtime["config"]
translator = runtime["translator"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)
demo_banner(translator, locale, config.demo_banner)

page_intro(
    "Guided field workflow",
    "Build a new assessment",
    "Use measurements from one defined season. Every required unit is visible, and the result is saved locally with its model and policy versions.",
)
assessment_progress()


def apply_scenario(name: str) -> None:
    for key, value in DEMO_SCENARIOS[name].items():
        st.session_state[f"assessment_{key}"] = value
    st.session_state["assessment_scenario"] = name


for key, value in DEMO_SCENARIOS["balanced"].items():
    st.session_state.setdefault(f"assessment_{key}", value)
st.session_state.setdefault("assessment_scenario", "balanced")

section_heading(
    "Start with a demonstration scenario",
    "Load a complete example, then adjust any measurement before assessment.",
)
scenario_details = (
    (
        "balanced",
        "A · Balanced conditions",
        "A familiar mid-range profile for learning the workflow.",
        "Good starting point",
    ),
    (
        "water_stress",
        "B · Water stress",
        "Lower rainfall to explore how risk and drivers change.",
        "Stress signal",
    ),
    (
        "unusual",
        "C · Unusual data",
        "Outlying measurements that exercise warnings and referral logic.",
        "Safety check",
    ),
)
scenario_columns = st.columns(3)
active_scenario = st.session_state["assessment_scenario"]
for column, (name, title, body, tag) in zip(scenario_columns, scenario_details, strict=True):
    column.markdown(
        f'<div class="ms-scenario"><h4>{title}</h4><p>{body}</p>'
        f'<span class="ms-scenario-tag">{tag}</span></div>',
        unsafe_allow_html=True,
    )
    column.button(
        "Loaded ✓" if active_scenario == name else "Load scenario",
        key=f"load_{name}",
        type="primary" if active_scenario == name else "secondary",
        on_click=apply_scenario,
        args=(name,),
        width="stretch",
    )

active_title = next(title for name, title, _, _ in scenario_details if name == active_scenario)
st.markdown(
    '<div class="ms-active-scenario">'
    f"<span>● Active example: {active_title}</span>"
    '<span class="ms-meta">Editable below</span></div>',
    unsafe_allow_html=True,
)

with st.form("assessment_form", border=True):
    field_tab, conditions_tab, review_tab = st.tabs(
        ["1 · Field & season", "2 · Conditions", "3 · Review & assess"]
    )
    with field_tab:
        st.markdown("### Identify this field safely")
        st.caption("Use an alias. Avoid legal names, phone numbers, national IDs, or exact GPS.")
        field_left, field_right = st.columns(2)
        field_left.text_input(
            "Farm reference (alias)",
            max_chars=80,
            key="assessment_farm_reference",
            placeholder="Example: North field",
        )
        field_right.text_input(
            "District (optional)",
            max_chars=80,
            key="assessment_district",
            placeholder="Example: Mutoko",
        )
        season_left, crop_right = st.columns(2)
        season_left.text_input(
            "Season (optional)",
            max_chars=30,
            key="assessment_season",
            placeholder="Example: 2025/26",
        )
        crop_right.text_input("Crop", disabled=True, key="assessment_crop")

    with conditions_tab:
        st.markdown("### Weather, soil, and recorded management")
        st.caption("Keep every value within the same assessment season.")
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
        soil_column, management_column = st.columns(2)
        soil_column.number_input(
            "Soil pH",
            min_value=0.0,
            max_value=14.0,
            step=0.1,
            key="assessment_soil_ph",
            help="A recent representative soil measurement; example: pH 6.2.",
        )
        management_column.number_input(
            "Recorded fertiliser already applied (kg/ha)",
            min_value=0.0,
            max_value=1000.0,
            step=5.0,
            key="assessment_fertilizer_kg_ha",
            help="Record only what was already applied. MundaSense does not calculate a dose.",
        )

    with review_tab:
        st.markdown("### Ready for local assessment")
        readiness_one, readiness_two, readiness_three = st.columns(3)
        readiness_one.metric("Required measurements", "5 / 5")
        readiness_two.metric("Processing", "On device")
        readiness_three.metric("Saved record", "Versioned")
        st.info(
            "Submitting checks input ranges, runs the local model, applies deterministic safety "
            "rules, and saves an immutable snapshot."
        )
        submitted = st.form_submit_button(
            translator.t("action.assess", locale),
            type="primary",
            width="stretch",
            icon="🌱",
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
    assessment_status = st.status("Running the local assessment…", expanded=True)
    try:
        assessment_status.write("Checking the input contract and familiar ranges")
        st.session_state["latest_result"] = runtime["service"].assess(payload)
        assessment_status.write("Applying risk, warning, and advisory rules")
        assessment_status.write("Saving the versioned result to local history")
        assessment_status.update(
            label="Assessment completed and saved locally",
            state="complete",
            expanded=False,
        )
        st.toast("Assessment ready", icon="🌽")
    except AssessmentValidationError as exc:
        assessment_status.update(label="Input review needed", state="error", expanded=False)
        for error in exc.errors:
            st.error(error)
    except Exception as exc:  # noqa: BLE001
        assessment_status.update(label="Assessment stopped safely", state="error", expanded=False)
        st.error("The assessment could not be completed safely. Check the local model and inputs.")
        with st.expander("Developer detail"):
            st.exception(exc)

if "latest_result" in st.session_state:
    render_result(st.session_state["latest_result"], translator, locale)
    history_action, reset_action, _ = st.columns([1.1, 1.1, 2.8])
    if history_action.button("Open saved history", icon="🗂️", width="stretch"):
        st.switch_page("pages/02_Assessment_History.py")
    if reset_action.button("Hide this result", icon="🔄", width="stretch"):
        del st.session_state["latest_result"]
        st.rerun()
