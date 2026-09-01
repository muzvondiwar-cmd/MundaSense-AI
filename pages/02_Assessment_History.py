from __future__ import annotations

import pandas as pd
import streamlit as st

from mundasense.config import project_root
from mundasense.ui.components import (
    brand_header,
    configure_page,
    locale_control,
    page_intro,
    render_result,
    section_heading,
)
from mundasense.ui.runtime import get_runtime

configure_page("Assessment history", icon="🗂️")
runtime = get_runtime()
config = runtime["config"]
translator = runtime["translator"]
repository = runtime["repository"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)

page_intro(
    "Local records",
    "Assessment history",
    "Explore immutable snapshots saved on this device. Opening a record preserves its original model, policy, and rule versions—it never re-runs the current model.",
)

all_rows = repository.list(limit=2_000)
if not all_rows:
    st.markdown(
        '<div class="ms-panel ms-empty-state"><div class="ms-empty-icon">🗂️</div>'
        "<h3>No saved assessments yet</h3><p>Complete a field assessment to create your first "
        "local, versioned snapshot.</p></div>",
        unsafe_allow_html=True,
    )
    if st.button("Create the first assessment", type="primary", icon="🌽"):
        st.switch_page("pages/01_New_Assessment.py")
    st.stop()

summary_one, summary_two, summary_three, summary_four = st.columns(4)
summary_one.metric("Saved assessments", len(all_rows))
summary_two.metric("High risk", sum(row["risk_code"] == "high" for row in all_rows))
summary_three.metric("Referrals", sum(bool(row["referral_required"]) for row in all_rows))
summary_four.metric("Districts", len({row["district"] for row in all_rows if row["district"]}))

section_heading(
    "Find a saved result", "Filter the local record set, then select any table row to open it."
)
districts = sorted({row["district"] for row in all_rows if row["district"]})
filter_main, filter_two, filter_three = st.columns([1.7, 1, 1])
with filter_main:
    risk_filter = st.segmented_control(
        "Risk",
        ["All", "low", "moderate", "high"],
        default="All",
        key="history_risk",
        width="stretch",
    )
confidence_filter = filter_two.selectbox(
    "Confidence", ["All", "high", "medium", "low", "insufficient"], key="history_confidence"
)
district_filter = filter_three.selectbox("District", ["All", *districts], key="history_district")
rows = repository.list(
    risk=None if risk_filter == "All" else risk_filter,
    confidence=None if confidence_filter == "All" else confidence_filter,
    district=None if district_filter == "All" else district_filter,
    limit=2_000,
)

display = pd.DataFrame(rows)
selected_id = None
if display.empty:
    st.info("No records match these filters. Adjust one or more filters to widen the view.")
else:
    display["referral_required"] = display["referral_required"].map({0: "No", 1: "Yes"})
    table = display[
        [
            "created_at",
            "district",
            "farm_reference",
            "predicted_yield_t_ha",
            "risk_code",
            "confidence_code",
            "referral_required",
            "model_version",
        ]
    ].rename(
        columns={
            "created_at": "Created",
            "district": "District",
            "farm_reference": "Field alias",
            "predicted_yield_t_ha": "Yield (t/ha)",
            "risk_code": "Risk",
            "confidence_code": "Confidence",
            "referral_required": "Referral",
            "model_version": "Model",
        }
    )
    table_event = st.dataframe(
        table,
        width="stretch",
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        key="history_table",
        column_config={"Yield (t/ha)": st.column_config.NumberColumn(format="%.2f")},
    )
    st.caption("Select a row to inspect the saved result. Filtering never changes stored records.")
    if table_event.selection.rows:
        selected_id = rows[table_event.selection.rows[0]]["id"]

csv_ids = [row["id"] for row in rows]
st.download_button(
    translator.t("action.export", locale),
    repository.export_csv(csv_ids),
    file_name="mundasense_assessments.csv",
    mime="text/csv",
    icon="⬇️",
    disabled=not rows,
)

selected = repository.get(selected_id) if selected_id else None
if selected:
    section_heading("Saved assessment", "This is the exact snapshot created at assessment time.")
    render_result(selected, translator, locale)

    with st.expander("Delete this local record"):
        confirmed = st.checkbox("I understand this removes the saved assessment from this device.")
        if st.button("Delete selected record", disabled=not confirmed) and repository.delete(
            selected_id
        ):
            st.success("Assessment deleted from local history.")
            st.rerun()
