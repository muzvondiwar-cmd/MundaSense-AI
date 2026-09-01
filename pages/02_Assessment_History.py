from __future__ import annotations

import pandas as pd
import streamlit as st

from mundasense.config import project_root
from mundasense.ui.components import brand_header, configure_page, locale_control, render_result
from mundasense.ui.runtime import get_runtime

configure_page("Assessment history", icon="🗂️")
runtime = get_runtime()
config = runtime["config"]
translator = runtime["translator"]
repository = runtime["repository"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)

st.markdown("# Assessment history")
st.write(
    "Saved results are immutable snapshots. Opening a record does not re-run the current model."
)

all_rows = repository.list(limit=2_000)
if not all_rows:
    st.info("No saved assessments yet. Complete a new field assessment to create local history.")
    st.stop()

districts = sorted({row["district"] for row in all_rows if row["district"]})
filter_one, filter_two, filter_three = st.columns(3)
risk_filter = filter_one.selectbox("Risk", ["All", "low", "moderate", "high"])
confidence_filter = filter_two.selectbox(
    "Confidence", ["All", "high", "medium", "low", "insufficient"]
)
district_filter = filter_three.selectbox("District", ["All", *districts])
rows = repository.list(
    risk=None if risk_filter == "All" else risk_filter,
    confidence=None if confidence_filter == "All" else confidence_filter,
    district=None if district_filter == "All" else district_filter,
    limit=2_000,
)

display = pd.DataFrame(rows)
if not display.empty:
    display["referral_required"] = display["referral_required"].map({0: "No", 1: "Yes"})
    st.dataframe(
        display[
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
        ],
        width="stretch",
        hide_index=True,
    )

csv_ids = [row["id"] for row in rows]
st.download_button(
    translator.t("action.export", locale),
    repository.export_csv(csv_ids),
    file_name="mundasense_assessments.csv",
    mime="text/csv",
)

labels = {
    row["id"]: (
        f"{row['created_at']} · {row['farm_reference'] or 'Unnamed field'} · "
        f"{row['risk_code']} risk"
    )
    for row in rows
}
selected_id = st.selectbox("Open assessment", list(labels), format_func=labels.get)
selected = repository.get(selected_id)
if selected:
    render_result(selected, translator, locale)

    with st.expander("Delete this local record"):
        confirmed = st.checkbox("I understand this removes the saved assessment from this device.")
        if st.button("Delete selected record", disabled=not confirmed) and repository.delete(
            selected_id
        ):
            st.success("Assessment deleted from local history.")
            st.rerun()
