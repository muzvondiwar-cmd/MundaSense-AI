THEME_CSS = """
<style>
:root {
  --ms-green: #1B5E20;
  --ms-green-2: #2E7D32;
  --ms-teal: #00796B;
  --ms-gold: #D99A00;
  --ms-ink: #163A24;
  --ms-pale: #F4FAF4;
  --ms-muted: #5F7064;
  --ms-line: #DCE9DD;
}

.stApp { background: linear-gradient(180deg, #FBFDFB 0%, #F5FAF5 100%); }
[data-testid="stHeader"] { background: rgba(251, 253, 251, 0.88); }
[data-testid="stSidebar"] { background: #F0F7F1; border-right: 1px solid var(--ms-line); }
[data-testid="stSidebarNav"] { display: none; }
.block-container { max-width: 1160px; padding-top: 2.2rem; padding-bottom: 5rem; }
h1, h2, h3 { color: var(--ms-ink); letter-spacing: -0.02em; }
h1 { font-size: clamp(2.1rem, 5vw, 4rem) !important; line-height: 1.02 !important; }
p, li, label { color: #294A32; }

.ms-hero {
  padding: clamp(1.8rem, 5vw, 4.2rem);
  border: 1px solid var(--ms-line);
  border-radius: 28px;
  background: radial-gradient(circle at 90% 10%, rgba(0,121,107,.16), transparent 36%),
              linear-gradient(135deg, #FFFFFF 0%, #F1FAF2 100%);
  box-shadow: 0 22px 60px rgba(22,58,36,.08);
  margin-bottom: 1.5rem;
}
.ms-eyebrow { color: var(--ms-teal); font-weight: 800; text-transform: uppercase; letter-spacing: .12em; font-size: .76rem; }
.ms-lead { max-width: 720px; font-size: 1.16rem; line-height: 1.65; color: #42614A; }
.ms-kicker { color: var(--ms-gold); font-weight: 750; }
.ms-panel, .ms-step, .ms-result-card {
  border: 1px solid var(--ms-line);
  background: rgba(255,255,255,.9);
  border-radius: 18px;
  padding: 1.25rem 1.35rem;
  height: 100%;
  box-shadow: 0 10px 24px rgba(22,58,36,.05);
}
.ms-step-number {
  width: 2rem; height: 2rem; border-radius: 50%; display: inline-grid; place-items: center;
  color: white; background: var(--ms-green); font-weight: 800; margin-bottom: .75rem;
}
.ms-demo {
  border-left: 5px solid var(--ms-gold); background: #FFF8E3; color: #5D4700;
  border-radius: 10px; padding: .9rem 1rem; margin: .6rem 0 1.2rem; font-weight: 650;
}
.ms-offline {
  display: inline-flex; align-items: center; gap: .45rem; color: var(--ms-green);
  background: #E8F5E9; padding: .45rem .75rem; border-radius: 999px; font-weight: 750;
}
.ms-risk { display: inline-flex; gap: .55rem; align-items: center; padding: .55rem .85rem; border-radius: 999px; font-weight: 800; }
.ms-risk-low { color: #155B2A; background: #E6F4E8; border: 1px solid #B9DEBF; }
.ms-risk-moderate { color: #765A00; background: #FFF4D2; border: 1px solid #E8D18A; }
.ms-risk-high { color: #8A1C16; background: #FCE8E6; border: 1px solid #F0B6B1; }
.ms-meta { color: var(--ms-muted); font-size: .88rem; }
.ms-priority { border-left: 5px solid var(--ms-teal); background: #EAF7F5; padding: 1rem 1.1rem; border-radius: 10px; }
.ms-warning { border-left: 5px solid var(--ms-gold); background: #FFF8E3; padding: .85rem 1rem; border-radius: 10px; margin: .55rem 0; }
.ms-referral { border: 1px solid #EDAAA4; background: #FFF1F0; padding: 1rem 1.1rem; border-radius: 12px; }
.stButton > button, .stDownloadButton > button { border-radius: 12px; font-weight: 750; min-height: 2.7rem; }
.stButton > button[kind="primary"] { background: var(--ms-green); border-color: var(--ms-green); }
.stButton > button[kind="primary"], .stButton > button[kind="primary"] p {
  color: #FFFFFF !important;
}
button[kind="primaryFormSubmit"], button[kind="primaryFormSubmit"] p {
  color: #FFFFFF !important;
}
[data-testid="stMetric"] { background: white; border: 1px solid var(--ms-line); padding: 1rem; border-radius: 16px; }
@media (max-width: 700px) {
  .block-container { padding: 1.1rem .9rem 3rem; }
  .ms-hero { padding: 1.4rem; border-radius: 20px; }
}
</style>
"""
