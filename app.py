import streamlit as st

from mundasense.config import project_root
from mundasense.ui.components import (
    brand_header,
    configure_page,
    demo_banner,
    locale_control,
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
  <h1>Know the risk.<br><span class="ms-kicker">Understand the cause.</span></h1>
  <p class="ms-lead">MundaSense turns five field conditions into an explainable maize-yield estimate, a provisional risk category, and one guarded next step—without sending farm data to a cloud service.</p>
  <span class="ms-offline">● Core assessment runs locally</span>
</section>
""",
    unsafe_allow_html=True,
)

if st.button(translator.t("action.start", locale), type="primary", width="content"):
    st.switch_page("pages/01_New_Assessment.py")

st.markdown("## A clear path from field notes to a safer decision")
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

st.markdown("## Designed for honest use")
left, right = st.columns(2)
left.markdown(
    '<div class="ms-panel"><h3>What it does</h3><p>Creates a traceable local assessment with prediction, range, top drivers, warnings, policy versions, and saved history.</p></div>',
    unsafe_allow_html=True,
)
right.markdown(
    '<div class="ms-panel"><h3>What it does not do</h3><p>It does not prescribe chemical or fertiliser doses, guarantee a harvest, or replace field inspection and qualified agronomic judgement.</p></div>',
    unsafe_allow_html=True,
)

st.caption("MundaSense AI MVP · Maize only · Zimbabwe demonstration context")
