import streamlit as st

from mundasense.config import project_root
from mundasense.constants import APP_VERSION
from mundasense.ui.components import brand_header, configure_page, demo_banner, locale_control
from mundasense.ui.runtime import get_runtime

configure_page("About & safety", icon="🛡️")
runtime = get_runtime()
config = runtime["config"]
translator = runtime["translator"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)
demo_banner(translator, locale, config.demo_banner)

st.markdown("# About MundaSense AI")
st.write(
    "MundaSense AI is a local decision-support prototype for smallholder maize farmers and agricultural extension officers in Zimbabwe and similar low-connectivity settings."
)

purpose, limits = st.columns(2)
purpose.markdown(
    '<div class="ms-panel"><h3>Intended purpose</h3><p>Organise field inputs, estimate a plausible maize-yield range, flag unusual inputs, explain model associations, and support an earlier conversation with an extension officer.</p></div>',
    unsafe_allow_html=True,
)
limits.markdown(
    '<div class="ms-panel"><h3>Not intended for</h3><p>Autonomous agronomy, dosage or chemical prescriptions, irrigation control, insurance, credit, legal decisions, or claims of improved harvest outcomes.</p></div>',
    unsafe_allow_html=True,
)

st.markdown("## How to read a result")
st.markdown(
    "- **Prediction:** the model's central estimate in tonnes per hectare.\n"
    "- **Plausible range:** a residual-calibrated demonstration interval, not guaranteed coverage.\n"
    "- **Risk:** a provisional threshold-based interpretation of the point estimate.\n"
    "- **Confidence:** a deterministic summary of interval width and input familiarity.\n"
    "- **Drivers:** approximate associations relative to median demonstration inputs, not causes."
)

st.markdown("## Data handling")
st.write(
    "Assessments are stored only in a local SQLite file by default. The MVP asks for a farm alias rather than a legal name and does not request exact GPS, national ID, phone number, or cloud account. Users are responsible for device access, backups, retention, and secure deletion."
)

st.markdown("## When to consult an extension officer")
st.write(
    "Seek extension review when risk is high, confidence is low or insufficient, several inputs are unusual, field observations conflict with the result, or a management change could have safety or cost consequences."
)
st.info(config.extension_contact)

st.markdown("## Language and agronomic review status")
st.write(
    "English is authoritative for this MVP. Shona priority strings and every advisory rule remain pending bilingual and local agronomic review before field deployment."
)

st.markdown("## Report a concern")
st.write(
    "Record the assessment ID and model/rule versions, then contact the project owner or deployment partner. Project contact details are intentionally left as a deployment placeholder rather than inventing a public address."
)
st.caption(f"MundaSense AI {APP_VERSION} · MIT License · Demonstration release")
