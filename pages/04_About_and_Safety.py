import streamlit as st

from mundasense.config import project_root
from mundasense.constants import APP_VERSION
from mundasense.ui.components import (
    brand_header,
    configure_page,
    demo_banner,
    locale_control,
    page_intro,
    section_heading,
)
from mundasense.ui.runtime import get_runtime

configure_page("About & safety", icon="🛡️")
runtime = get_runtime()
config = runtime["config"]
translator = runtime["translator"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)
demo_banner(translator, locale, config.demo_banner)

page_intro(
    "Purpose, limits, and care",
    "About MundaSense AI",
    "A local decision-support prototype for smallholder maize farmers and agricultural extension officers in Zimbabwe and similar low-connectivity settings.",
)

purpose, limits = st.columns(2)
purpose.markdown(
    '<div class="ms-bento ms-bento-accent"><span class="ms-card-label">Designed to support</span>'
    "<h3>Earlier, better-informed conversations</h3><p>Organise field inputs, estimate a "
    "plausible maize-yield range, flag unusual inputs, explain model associations, and support "
    "an earlier conversation with an extension officer.</p></div>",
    unsafe_allow_html=True,
)
limits.markdown(
    '<div class="ms-bento"><span class="ms-card-label">Never intended for</span>'
    "<h3>Autonomous or consequential decisions</h3><p>No dosage or chemical prescriptions, "
    "irrigation control, insurance, credit, legal decisions, or claims of improved harvest "
    "outcomes.</p></div>",
    unsafe_allow_html=True,
)

section_heading(
    "How to read a result", "Choose an element to see what it means—and what it does not mean."
)
result_part = st.pills(
    "Result element",
    ["Prediction", "Plausible range", "Risk", "Confidence", "Drivers"],
    default="Prediction",
    label_visibility="collapsed",
)
result_explanations = {
    "Prediction": (
        "Central estimate",
        "The model's central estimate in tonnes per hectare. It is not a harvest promise.",
    ),
    "Plausible range": (
        "Calibrated uncertainty",
        "A residual-calibrated demonstration interval. Coverage is empirical, not guaranteed.",
    ),
    "Risk": (
        "Provisional category",
        "A threshold-based interpretation of the point estimate, not a diagnosis.",
    ),
    "Confidence": (
        "Input familiarity and range width",
        "A deterministic summary of interval width and whether inputs resemble training ranges.",
    ),
    "Drivers": (
        "Approximate model associations",
        "Comparisons relative to median demonstration inputs—not agronomic or biological causes.",
    ),
}
part_title, part_body = result_explanations[result_part or "Prediction"]
st.markdown(
    f'<div class="ms-priority"><strong>{part_title}</strong><br>{part_body}</div>',
    unsafe_allow_html=True,
)

section_heading(
    "Safety by design", "The operating boundaries are visible across the whole workflow."
)
data_column, referral_column = st.columns(2)
data_column.markdown(
    '<div class="ms-panel"><div class="ms-card-icon">⌂</div><h3>Local data handling</h3>'
    "<p>Assessments stay in a local SQLite file by default. Use a field alias; do not enter "
    "exact GPS, national ID, phone number, or a farmer's legal name.</p></div>",
    unsafe_allow_html=True,
)
referral_column.markdown(
    '<div class="ms-panel"><div class="ms-card-icon">👤</div><h3>Human referral</h3>'
    "<p>Seek extension review for high risk, weak confidence, unusual inputs, conflicting "
    "field observations, or management changes with safety or cost consequences.</p></div>",
    unsafe_allow_html=True,
)
st.info(config.extension_contact)

section_heading(
    "Review and reporting", "Deployment partners should complete these checks before field use."
)
with st.expander("Language and agronomic review status", icon="🗣️"):
    st.write(
        "English is authoritative for this MVP. Shona priority strings and every advisory rule "
        "remain pending bilingual and local agronomic review before field deployment."
    )
with st.expander("How to report a concern", icon="🚩"):
    st.write(
        "Record the assessment ID and model/rule versions, then contact the project owner or "
        "deployment partner. Contact details remain a deployment placeholder rather than an "
        "invented public address."
    )
with st.expander("Device owner responsibilities", icon="🔐"):
    st.write(
        "The device owner is responsible for access control, backups, retention choices, and "
        "secure deletion of local assessment history."
    )
st.caption(f"MundaSense AI {APP_VERSION} · MIT License · Demonstration release")
