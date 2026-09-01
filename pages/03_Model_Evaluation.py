from __future__ import annotations

import json

import pandas as pd
import streamlit as st

from mundasense.config import project_root
from mundasense.health import readiness
from mundasense.ui.components import brand_header, configure_page, demo_banner, locale_control
from mundasense.ui.runtime import get_runtime

configure_page("Model evaluation", icon="📊")
runtime = get_runtime()
config = runtime["config"]
translator = runtime["translator"]
bundle = runtime["bundle"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)
demo_banner(translator, locale, config.demo_banner)

st.markdown("# Technical model evaluation")
st.warning(
    "These metrics describe held-out synthetic demonstration records. They do not prove farmer impact, agronomic efficacy, or field accuracy."
)

metadata_one, metadata_two, metadata_three = st.columns(3)
metadata_one.metric("Model version", bundle["model_version"])
metadata_two.metric("Champion", bundle["training_config"]["champion"].replace("_", " ").title())
metadata_three.metric("Training status", "Synthetic demonstration")
st.caption(f"Trained: {bundle['created_at']} · Explanation: {bundle['explanation_method']}")

metrics = bundle["metrics"]
metric_columns = st.columns(4)
metric_columns[0].metric("Held-out MAE", f"{metrics['mae_t_ha']:.3f} t/ha")
metric_columns[1].metric("Held-out RMSE", f"{metrics['rmse_t_ha']:.3f} t/ha")
metric_columns[2].metric("Held-out R²", f"{metrics['r2']:.3f}")
metric_columns[3].metric("Interval coverage", f"{metrics['interval_empirical_coverage']:.1%}")
st.caption(
    f"Nominal range coverage: {metrics['interval_nominal_coverage']:.0%}; "
    f"mean interval width: {metrics['mean_interval_width_t_ha']:.3f} t/ha. "
    "Thresholds and calibration remain provisional until field data are available."
)

st.markdown("## Candidate comparison on the calibration location")
comparison = pd.DataFrame(bundle["candidate_comparison"])
st.dataframe(comparison, width="stretch", hide_index=True)
st.write(
    "The champion was selected by lowest calibration MAE after comparison with a median naive baseline. "
    f"Validation MAE improved by {metrics['validation_mae_improvement_over_baseline']:.1%}."
)

st.markdown("## Held-out diagnostic plots")
figure_one, figure_two = st.columns(2)
figure_one.image(
    str(project_root() / "reports" / "figures" / "actual_vs_predicted.png"),
    caption="Actual versus predicted; dashed line is perfect agreement.",
)
figure_two.image(
    str(project_root() / "reports" / "figures" / "residuals.png"),
    caption="Residuals should be interpreted with the synthetic-data limitation.",
)

st.markdown("## Split and subgroup evidence")
st.json(bundle["split_strategy"])
st.dataframe(pd.DataFrame(metrics["subgroups"]), width="stretch", hide_index=True)

st.markdown("## Feature contract and training ranges")
ranges = pd.DataFrame(bundle["training_ranges"]).T.reset_index(names="feature")
st.dataframe(ranges, width="stretch", hide_index=True)

st.markdown("## Local readiness")
health = readiness(config)
for name, check in health["checks"].items():
    icon = "✓" if check["ok"] else "▲"
    st.write(f"{icon} **{name.title()}** — {check['detail']}")

with st.expander("Full evaluation metadata"):
    evaluation_path = project_root() / "reports" / "metrics" / "evaluation.json"
    if evaluation_path.exists():
        st.json(json.loads(evaluation_path.read_text(encoding="utf-8")))

st.markdown("## Prohibited interpretations")
st.markdown(
    "- Do not describe synthetic held-out performance as field validation.\n"
    "- Do not infer that the displayed drivers are biological causes.\n"
    "- Do not use the risk bands for credit, insurance, or legal decisions.\n"
    "- Do not derive treatment or fertiliser dosages from this model."
)
