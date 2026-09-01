THEME_CSS = """
<style>
:root {
  --ms-green-950: #0D321D;
  --ms-green-800: #15592D;
  --ms-green: #1F7A3D;
  --ms-green-500: #38A45A;
  --ms-teal: #087E73;
  --ms-gold: #D99A00;
  --ms-ink: #12301E;
  --ms-copy: #345340;
  --ms-muted: #65766A;
  --ms-pale: #F3F8F3;
  --ms-line: #DCE8DD;
  --ms-white: #FFFFFF;
  --ms-shadow: 0 18px 50px rgba(18, 48, 30, .08);
}

html { scroll-behavior: smooth; }
.stApp {
  background:
    radial-gradient(circle at 7% 3%, rgba(56, 164, 90, .10), transparent 22rem),
    radial-gradient(circle at 94% 20%, rgba(8, 126, 115, .08), transparent 25rem),
    linear-gradient(180deg, #FCFEFC 0%, #F5F9F5 100%);
}
[data-testid="stHeader"] {
  background: rgba(252, 254, 252, .82);
  backdrop-filter: blur(14px);
  border-bottom: 1px solid rgba(220, 232, 221, .72);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #EEF6EF 0%, #F7FAF7 100%);
  border-right: 1px solid var(--ms-line);
}
[data-testid="stSidebarNav"] { display: none; }
[data-testid="stSidebar"] [data-testid="stPageLink"] {
  border-radius: 12px;
  margin: .12rem 0;
  transition: background .18s ease, transform .18s ease;
}
[data-testid="stSidebar"] [data-testid="stPageLink"]:hover {
  background: rgba(31, 122, 61, .08);
  transform: translateX(2px);
}
.block-container { max-width: 1180px; padding-top: 1.8rem; padding-bottom: 5rem; }
h1, h2, h3 { color: var(--ms-ink); letter-spacing: -.025em; }
h1 { font-size: clamp(2.15rem, 5vw, 4.15rem) !important; line-height: 1.02 !important; }
h2 { margin-top: 2rem !important; }
p, li, label { color: var(--ms-copy); }

.ms-brand-row {
  display: flex; align-items: center; justify-content: space-between; gap: 1rem;
  margin-bottom: .85rem;
}
.ms-page-intro { max-width: 790px; margin: .25rem 0 1.5rem; }
.ms-page-intro h1 { margin: .28rem 0 .65rem; }
.ms-page-intro p { font-size: 1.08rem; line-height: 1.65; margin: 0; color: #4A6552; }
.ms-eyebrow {
  color: var(--ms-teal); font-weight: 800; text-transform: uppercase;
  letter-spacing: .13em; font-size: .74rem;
}
.ms-kicker { color: var(--ms-gold); font-weight: 780; }
.ms-lead { max-width: 700px; font-size: 1.15rem; line-height: 1.65; color: #42614A; }

.ms-hero {
  position: relative; overflow: hidden;
  padding: clamp(1.8rem, 5vw, 4.3rem);
  border: 1px solid rgba(189, 219, 194, .82);
  border-radius: 30px;
  background:
    radial-gradient(circle at 90% 4%, rgba(8, 126, 115, .19), transparent 34%),
    radial-gradient(circle at 70% 115%, rgba(217, 154, 0, .11), transparent 28%),
    linear-gradient(135deg, rgba(255,255,255,.98) 0%, #EEF8EF 100%);
  box-shadow: 0 28px 70px rgba(18, 48, 30, .10);
  margin-bottom: 1.1rem;
  isolation: isolate;
}
.ms-hero::after {
  content: ""; position: absolute; width: 17rem; height: 17rem; border-radius: 50%;
  right: -6rem; bottom: -8rem; border: 1px solid rgba(31, 122, 61, .16);
  box-shadow: 0 0 0 2.5rem rgba(31,122,61,.035), 0 0 0 5rem rgba(31,122,61,.025);
  z-index: -1;
}
.ms-hero h1 { max-width: 760px; margin: .5rem 0 1rem; }
.ms-hero-badges, .ms-trust-strip {
  display: flex; flex-wrap: wrap; align-items: center; gap: .55rem; margin-top: 1.2rem;
}
.ms-badge, .ms-offline {
  display: inline-flex; align-items: center; gap: .42rem;
  color: var(--ms-green-800); background: rgba(255,255,255,.76);
  border: 1px solid #CFE2D1; padding: .48rem .72rem; border-radius: 999px;
  font-size: .84rem; font-weight: 760; backdrop-filter: blur(8px);
}
.ms-badge-dot { width: .48rem; height: .48rem; border-radius: 50%; background: var(--ms-green-500); }

.ms-panel, .ms-step, .ms-result-card, .ms-bento, .ms-scenario {
  border: 1px solid var(--ms-line);
  background: rgba(255,255,255,.90);
  border-radius: 20px;
  padding: 1.3rem 1.4rem;
  height: 100%;
  box-shadow: 0 10px 28px rgba(18,48,30,.055);
  transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
}
.ms-panel:hover, .ms-step:hover, .ms-bento:hover, .ms-scenario:hover {
  transform: translateY(-3px); border-color: #B9D9BF;
  box-shadow: var(--ms-shadow);
}
.ms-bento-accent {
  background: linear-gradient(145deg, #153F25 0%, #1F6937 100%);
  color: white; border-color: transparent;
}
.ms-bento-accent h3, .ms-bento-accent p, .ms-bento-accent .ms-card-label { color: white; }
.ms-card-label {
  display: block; color: var(--ms-teal); font-size: .72rem; font-weight: 850;
  text-transform: uppercase; letter-spacing: .1em; margin-bottom: .55rem;
}
.ms-card-icon {
  width: 2.35rem; height: 2.35rem; display: grid; place-items: center;
  border-radius: 12px; background: #EAF5EB; margin-bottom: .85rem; font-size: 1.15rem;
}
.ms-step { position: relative; }
.ms-step-number {
  width: 2.1rem; height: 2.1rem; border-radius: 50%; display: inline-grid; place-items: center;
  color: white; background: linear-gradient(145deg, var(--ms-green), var(--ms-teal));
  font-weight: 850; margin-bottom: .8rem; box-shadow: 0 7px 18px rgba(31,122,61,.22);
}
.ms-step h3, .ms-bento h3, .ms-panel h3 { margin: 0 0 .45rem; }
.ms-step p, .ms-bento p, .ms-panel p { margin-bottom: 0; line-height: 1.55; }

.ms-demo {
  border: 1px solid #E7CF89; border-left: 5px solid var(--ms-gold);
  background: linear-gradient(90deg, #FFF8E3, #FFFCF2); color: #5D4700;
  border-radius: 12px; padding: .88rem 1rem; margin: .5rem 0 1.2rem; font-weight: 650;
}
.ms-section-heading { display: flex; align-items: flex-end; justify-content: space-between; gap: 1rem; margin: 2rem 0 .9rem; }
.ms-section-heading h2 { margin: 0 !important; }
.ms-section-heading p { margin: 0; color: var(--ms-muted); max-width: 520px; }
.ms-progress-rail {
  display: grid; grid-template-columns: repeat(5, 1fr); gap: .45rem;
  margin: .8rem 0 1.15rem;
}
.ms-progress-step {
  padding: .65rem .7rem; border-radius: 12px; background: #F3F7F3;
  border: 1px solid var(--ms-line); font-size: .78rem; font-weight: 750; color: var(--ms-copy);
}
.ms-progress-step strong { color: var(--ms-green); margin-right: .28rem; }

.ms-scenario { padding: 1rem 1.05rem; min-height: 8.4rem; }
.ms-scenario h4 { color: var(--ms-ink); margin: 0 0 .35rem; font-size: 1rem; }
.ms-scenario p { margin: 0; font-size: .88rem; line-height: 1.45; color: var(--ms-muted); }
.ms-scenario-tag {
  display: inline-block; margin-top: .7rem; padding: .25rem .48rem; border-radius: 7px;
  background: #EDF5EE; color: var(--ms-green-800); font-size: .72rem; font-weight: 800;
}
.ms-active-scenario {
  display: flex; justify-content: space-between; gap: .8rem; align-items: center;
  border: 1px solid #B9D9BF; background: #F0F8F1; padding: .72rem .9rem;
  border-radius: 12px; margin: .65rem 0 1rem; color: var(--ms-green-800); font-weight: 740;
}

.ms-result-hero {
  position: relative; overflow: hidden; padding: clamp(1.45rem, 3vw, 2.1rem);
  border-radius: 24px; border: 1px solid #C8DFC9;
  background: linear-gradient(135deg, #FFFFFF 0%, #EDF7EE 100%);
  box-shadow: var(--ms-shadow); margin: 1rem 0 1.25rem;
}
.ms-result-grid { display: grid; grid-template-columns: 1.5fr 1fr 1fr; gap: .8rem; margin-top: 1rem; }
.ms-result-stat {
  background: rgba(255,255,255,.82); border: 1px solid rgba(207,226,209,.9);
  border-radius: 16px; padding: 1rem;
}
.ms-result-stat .label { color: var(--ms-muted); font-size: .77rem; font-weight: 780; text-transform: uppercase; letter-spacing: .06em; }
.ms-result-stat .value { color: var(--ms-ink); font-size: clamp(1.3rem, 3vw, 2rem); font-weight: 850; line-height: 1.15; margin-top: .35rem; }
.ms-result-stat .detail { color: var(--ms-muted); font-size: .8rem; margin-top: .28rem; }
.ms-risk { display: inline-flex; gap: .5rem; align-items: center; padding: .5rem .72rem; border-radius: 999px; font-weight: 850; }
.ms-risk-low { color: #155B2A; background: #E6F4E8; border: 1px solid #B9DEBF; }
.ms-risk-moderate { color: #765A00; background: #FFF4D2; border: 1px solid #E8D18A; }
.ms-risk-high { color: #8A1C16; background: #FCE8E6; border: 1px solid #F0B6B1; }
.ms-meta { color: var(--ms-muted); font-size: .86rem; }
.ms-priority {
  border: 1px solid #B8DDD7; border-left: 5px solid var(--ms-teal);
  background: linear-gradient(90deg, #EAF7F5, #F5FBFA); padding: 1rem 1.1rem; border-radius: 12px;
}
.ms-warning {
  border: 1px solid #E8D38F; border-left: 5px solid var(--ms-gold);
  background: #FFF9E8; padding: .85rem 1rem; border-radius: 11px; margin: .55rem 0;
}
.ms-referral {
  border: 1px solid #EDAAA4; background: linear-gradient(90deg, #FFF1F0, #FFF8F7);
  padding: 1rem 1.1rem; border-radius: 12px; margin: .8rem 0;
}
.ms-empty-state { text-align: center; padding: 3.2rem 1.5rem; }
.ms-empty-icon {
  width: 3.4rem; height: 3.4rem; display: grid; place-items: center; margin: 0 auto .8rem;
  border-radius: 18px; background: #EAF5EB; font-size: 1.55rem;
}

.stButton > button, .stDownloadButton > button, [data-testid="stFormSubmitButton"] button {
  border-radius: 12px; font-weight: 760; min-height: 2.75rem;
  transition: transform .16s ease, box-shadow .16s ease, border-color .16s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover, [data-testid="stFormSubmitButton"] button:hover {
  transform: translateY(-1px); box-shadow: 0 8px 20px rgba(18,48,30,.10);
}
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible,
input:focus-visible, textarea:focus-visible, [role="tab"]:focus-visible {
  outline: 3px solid rgba(8,126,115,.25) !important; outline-offset: 2px;
}
.stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] button[kind="primary"] {
  background: linear-gradient(135deg, var(--ms-green-800), var(--ms-green));
  border-color: var(--ms-green-800); box-shadow: 0 8px 20px rgba(31,122,61,.18);
}
.stButton > button[kind="primary"], .stButton > button[kind="primary"] p,
button[kind="primaryFormSubmit"], button[kind="primaryFormSubmit"] p { color: #FFFFFF !important; }
[data-testid="stMetric"] {
  background: rgba(255,255,255,.92); border: 1px solid var(--ms-line);
  padding: 1rem; border-radius: 17px; box-shadow: 0 8px 22px rgba(18,48,30,.045);
}
[data-testid="stForm"] { background: rgba(255,255,255,.66); border-color: var(--ms-line) !important; border-radius: 22px; }
[data-baseweb="tab-list"] { gap: .35rem; background: #EFF5F0; padding: .32rem; border-radius: 13px; }
[data-baseweb="tab"] { border-radius: 9px; padding-left: 1rem; padding-right: 1rem; }
[aria-selected="true"][data-baseweb="tab"] { background: #FFFFFF; box-shadow: 0 3px 10px rgba(18,48,30,.08); }
[data-testid="stSegmentedControl"] { margin-bottom: .65rem; }

@keyframes ms-rise { from { opacity: 0; transform: translateY(8px); } to { opacity: 1; transform: translateY(0); } }
.ms-hero, .ms-page-intro, .ms-result-hero { animation: ms-rise .45s ease both; }

@media (max-width: 800px) {
  .block-container { padding: 1.05rem .9rem 3rem; }
  .ms-hero { padding: 1.45rem; border-radius: 22px; }
  .ms-result-grid { grid-template-columns: 1fr; }
  .ms-progress-rail { grid-template-columns: 1fr 1fr; }
  .ms-section-heading { display: block; }
  .ms-section-heading p { margin-top: .35rem; }
}
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: .01ms !important; transition-duration: .01ms !important; scroll-behavior: auto !important; }
}
</style>
"""
