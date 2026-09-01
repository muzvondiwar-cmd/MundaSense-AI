import streamlit as st

from mundasense.config import project_root
from mundasense.ui.components import (
    brand_header,
    configure_page,
    demo_banner,
    locale_control,
    section_heading,
)
from mundasense.ui.runtime import get_runtime

configure_page("Home")

try:
    runtime = get_runtime()
except Exception as exc:  # noqa: BLE001 - friendly startup recovery path
    st.error("MundaSense could not start because its local model or configuration is unavailable.")
    st.code("python scripts/train_model.py")
    with st.expander("Developer detail"):
        st.exception(exc)
    st.stop()

config = runtime["config"]
translator = runtime["translator"]
locale = locale_control(config.default_locale)
brand_header(project_root() / "assets" / "mundasense_logo.png", translator, locale)
demo_banner(translator, locale, config.demo_banner)

st.markdown(
    """
<section class="ms-hero">
  <div class="ms-eyebrow">Offline-first maize decision support</div>
  <h1>Know the risk.<br><span class="ms-kicker">See what shapes it.</span></h1>
  <p class="ms-lead">Turn five familiar field conditions into an explainable maize-yield range, a provisional risk category, and one guarded next step—without sending farm data to a cloud service.</p>
  <div class="ms-hero-badges">
    <span class="ms-badge"><span class="ms-badge-dot"></span>Core assessment runs locally</span>
    <span class="ms-badge">◫ Traceable history</span>
    <span class="ms-badge">◎ Explainable results</span>
  </div>
</section>
""",
    unsafe_allow_html=True,
)

primary_action, secondary_action, _ = st.columns([1.15, 1.25, 2.6])
if primary_action.button(
    translator.t("action.start", locale), type="primary", width="stretch", icon="🌽"
):
    st.switch_page("pages/01_New_Assessment.py")
if secondary_action.button("Explore model evidence", width="stretch", icon="📊"):
    st.switch_page("pages/03_Model_Evaluation.py")

section_heading(
    "A clear path from field notes to a safer decision",
    "Designed to be readable in the field and reviewable by an extension officer.",
)
steps = [
    ("1", "Enter conditions", "Record seasonal weather, soil pH, and fertiliser already applied."),
    (
        "2",
        "Understand risk",
        "See the predicted yield range, risk label, confidence, and unusual-input warnings.",
    ),
    (
        "3",
        "Choose a safe next step",
        "Review a deterministic action and know when extension support is needed.",
    ),
]
columns = st.columns(3)
for column, (number, title, body) in zip(columns, steps, strict=True):
    column.markdown(
        f'<div class="ms-step"><span class="ms-step-number">{number}</span>'
        f"<h3>{title}</h3><p>{body}</p></div>",
        unsafe_allow_html=True,
    )

section_heading(
    "One result, two useful views",
    "Switch from a concise field explanation to deeper evidence without losing the safety context.",
)
farmer_tab, officer_tab = st.tabs(["🌱 Farmer summary", "🧭 Extension detail"])
with farmer_tab:
    farmer_one, farmer_two = st.columns([1.15, 1])
    farmer_one.markdown(
        '<div class="ms-bento ms-bento-accent"><span class="ms-card-label">At a glance</span>'
        "<h3>A range you can read quickly</h3><p>See the central yield estimate, plausible range, "
        "risk label, confidence, and the most important guarded next action together.</p></div>",
        unsafe_allow_html=True,
    )
    farmer_two.markdown(
        '<div class="ms-bento"><div class="ms-card-icon">✓</div><h3>Clarity before detail</h3>'
        "<p>Plain-language drivers and unusual-input warnings remain close to the result.</p></div>",
        unsafe_allow_html=True,
    )
with officer_tab:
    officer_one, officer_two = st.columns(2)
    officer_one.markdown(
        '<div class="ms-bento"><div class="ms-card-icon">⌁</div><h3>Trace every decision</h3>'
        "<p>Review model, policy, rule, warning, and explanation versions for each saved snapshot.</p></div>",
        unsafe_allow_html=True,
    )
    officer_two.markdown(
        '<div class="ms-bento"><div class="ms-card-icon">◫</div><h3>Inspect the evidence</h3>'
        "<p>Open calibrated ranges, model associations, held-out metrics, and local readiness checks.</p></div>",
        unsafe_allow_html=True,
    )

section_heading(
    "Designed for honest use", "Clear boundaries are part of the interface—not fine print."
)
honest_one, honest_two, honest_three = st.columns([1, 1, 1])
honest_one.markdown(
    '<div class="ms-bento"><span class="ms-card-label">Private by default</span>'
    "<h3>Local assessment</h3><p>Core inputs, results, and history stay on this device by default.</p></div>",
    unsafe_allow_html=True,
)
honest_two.markdown(
    '<div class="ms-bento"><span class="ms-card-label">Bounded advice</span>'
    "<h3>No dose prescription</h3><p>The tool records applied fertiliser; it never calculates a treatment dose.</p></div>",
    unsafe_allow_html=True,
)
honest_three.markdown(
    '<div class="ms-bento"><span class="ms-card-label">Human support</span>'
    "<h3>Referral when needed</h3><p>High risk, weak confidence, or unusual inputs can trigger extension review.</p></div>",
    unsafe_allow_html=True,
)

st.caption("MundaSense AI MVP · Maize only · Zimbabwe demonstration context")
