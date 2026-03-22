"""
DecTell AI — Home Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import requests
import json
import time

from utils.ui_utils import (
    inject_global_css, hero_section, stat_strip,
    feature_card, image_card, section_label, divider,
    lottie_inline, render_footer, PEXELS
)

inject_global_css()

# ── Extra CSS for this page ────────────────────────────────────────────────────
st.markdown("""
<style>
/* Partner card */
.partner-card {
    background: #1A2540;
    border: 1px solid #2C3F60;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    display: flex;
    align-items: center;
    gap: 1.75rem;
    transition: all 0.2s;
}
.partner-card:hover {
    border-color: #3A5278;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
    transform: translateY(-2px);
}
.partner-logo-box {
    width: 80px; height: 80px;
    border-radius: 14px;
    background: #0F1829;
    border: 1px solid #2C3F60;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
    font-size: 1.6rem;
    color: #00D4FF;
    font-weight: 900;
    font-family: 'Space Grotesk', sans-serif;
}
.partner-badge {
    display: inline-block;
    background: rgba(0,212,255,0.08);
    border: 1px solid rgba(0,212,255,0.2);
    border-radius: 99px;
    padding: 0.18rem 0.65rem;
    font-size: 0.68rem;
    font-weight: 700;
    color: #00D4FF;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}

/* Review slider */
.review-card {
    background: #1A2540;
    border: 1px solid #2C3F60;
    border-radius: 16px;
    padding: 1.75rem 2rem;
    position: relative;
    min-height: 190px;
}
.review-quote-mark {
    font-size: 4.5rem;
    color: rgba(0,212,255,0.12);
    font-family: Georgia, serif;
    line-height: 1;
    position: absolute;
    top: 0.5rem;
    left: 1.25rem;
}
.review-text {
    font-size: 0.92rem;
    color: #9BB5CF;
    line-height: 1.75;
    font-style: italic;
    margin-top: 1.2rem;
    position: relative;
    z-index: 1;
}
.review-author {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1.25rem;
}
.review-avatar {
    width: 38px; height: 38px;
    border-radius: 50%;
    background: linear-gradient(135deg, #1A3050, #213060);
    border: 1px solid #2C3F60;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700; color: #00D4FF;
    flex-shrink: 0;
    font-family: 'Space Grotesk', sans-serif;
}
.review-name {
    font-size: 0.85rem;
    font-weight: 700;
    color: #DDE8F8;
}
.review-role {
    font-size: 0.74rem;
    color: #6A88A8;
}
.review-stars {
    color: #F59E0B;
    font-size: 0.82rem;
    margin-left: auto;
    letter-spacing: 0.05em;
}
.slider-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #2C3F60;
    display: inline-block;
    margin: 0 3px;
    cursor: pointer;
    transition: background 0.2s;
}
.slider-dot.active {
    background: #00D4FF;
    width: 20px;
    border-radius: 99px;
}
</style>
""", unsafe_allow_html=True)


# ── Logo + Title ───────────────────────────────────────────────────────────────
logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
c_logo, c_title = st.columns([1, 8])
with c_logo:
    if os.path.exists(logo_path):
        st.image(logo_path, width=52)
with c_title:
    st.markdown("""
<div style="padding-top:0.55rem;">
    <span style="font-family:'Space Grotesk',sans-serif;font-size:1.55rem;
          font-weight:800;color:#DDE8F8;letter-spacing:-0.02em;">DecTell AI</span>
    <span style="font-size:0.72rem;font-weight:600;color:#3A5278;
          text-transform:uppercase;letter-spacing:0.1em;margin-left:0.75rem;">
        Decision Intelligence Platform
    </span>
</div>""", unsafe_allow_html=True)

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

# ── Hero ───────────────────────────────────────────────────────────────────────
hero_section(
    bg_key   = "hero_bg",
    pill     = "AI-Powered Business Analytics",
    title    = "Transform Data\nInto Decisions",
    subtitle = "Upload any business dataset. DecTell AI automatically cleans it, generates insights, trains predictive models, and lets you simulate decisions and business growth."
)

st.markdown("""
<style>
/* Make st.page_link buttons look like styled CTAs */
[data-testid="stPageLink"] a {
    display: inline-flex !important;
    align-items: center !important;
    text-decoration: none !important;
}
</style>
""", unsafe_allow_html=True)
 
_b1, _b2, _gap = st.columns([1.7, 1.65, 5.4])
with _b1:
    st.markdown("""
<style>
div[data-testid="stPageLink"]:first-of-type a {
    background: #00D4FF !important;
    color: #06101C !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.875rem !important;
    padding: 0.65rem 1.5rem !important;
    border-radius: 10px !important;
    border: none !important;
}
</style>""", unsafe_allow_html=True)
    st.page_link("pages/Upload.py", label="Start Analyzing")
with _b2:
    st.markdown("""
<style>
div[data-testid="stPageLink"]:last-of-type a {
    background: rgba(0,212,255,0.08) !important;
    color: #00D4FF !important;
    border: 1px solid rgba(0,212,255,0.25) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 0.65rem 1.5rem !important;
    border-radius: 10px !important;
}
</style>""", unsafe_allow_html=True)
    st.page_link("pages/About.py", label="Read Research", use_container_width=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Stat strip ─────────────────────────────────────────────────────────────────
stat_strip([
    ("Groq LLM",   "AI Engine"),
    ("8",          "Core Modules"),
    ("3+",         "ML Algorithms"),
    ("7",          "Sample Datasets"),
    ("Real-time",  "AI Chat"),
    ("PDF + TXT",  "Report Export"),
])

st.markdown("<div style='height:2.5rem'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — PARTNERS
# ══════════════════════════════════════════════════════════════════════════════
section_label("Trusted Partner")
st.markdown("""
<p style="font-size:0.875rem;color:#6A88A8;max-width:620px;
   line-height:1.7;margin-bottom:1.5rem;">
    DecTell AI is validated and supported by real-world business operations,
    ensuring our platform meets the demands of professional data consulting environments.
</p>""", unsafe_allow_html=True)

col_partner, col_partner_info = st.columns([1.6, 2.4], gap="large")

with col_partner:
    logo_dd_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "assets", "datadisco_logo.png"
    )

    # ── Logo + name row ────────────────────────────────────────────────────
    logo_col, name_col = st.columns([2, 3])
    with logo_col:
        if os.path.exists(logo_dd_path):
            st.image(logo_dd_path, width=150)
        else:
            st.markdown("""
<div style="width:88px;height:88px;border-radius:14px;background:#0F1829;
     border:1px solid #2C3F60;display:flex;align-items:center;justify-content:center;
     font-size:1.3rem;font-weight:900;color:#00D4FF;
     font-family:'Space Grotesk',sans-serif;text-align:center;line-height:1.2;">
    D&amp;D<br><span style="font-size:0.5rem;letter-spacing:0.08em;color:#6A88A8;">STUDIO</span>
</div>""", unsafe_allow_html=True)

    with name_col:
        st.markdown("""
<div style="padding-top:0.3rem;">
    <div class="partner-badge">Official Partner</div>
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.05rem;
         font-weight:800;color:#DDE8F8;line-height:1.2;margin-bottom:0.2rem;">
        Data &amp; Disco<br>Dreams Studio
    </div>
    <div style="font-size:0.75rem;color:#6A88A8;">Atlanta, United States</div>
</div>""", unsafe_allow_html=True)

    # ── Tagline + pills ────────────────────────────────────────────────────
    st.markdown("""
<div style="font-size:0.82rem;color:#4A6080;line-height:1.6;width:100%;
     padding-top:0.5rem;">
    Data Consulting &amp; Design for Small Businesses
</div>
<div style="display:flex;gap:0.5rem;flex-wrap:wrap;margin-top:0.65rem;">
    <span style="background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.22);
          border-radius:99px;padding:0.2rem 0.65rem;font-size:0.72rem;
          font-weight:600;color:#A78BFA;">Data Consulting</span>
    <span style="background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);
          border-radius:99px;padding:0.2rem 0.65rem;font-size:0.72rem;
          font-weight:600;color:#34D399;">Design Studio</span>
    <span style="background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.2);
          border-radius:99px;padding:0.2rem 0.65rem;font-size:0.72rem;
          font-weight:600;color:#00D4FF;">Business Analytics</span>
    <span style="background:rgba(124,58,237,0.08);border:1px solid rgba(124,58,237,0.22);
          border-radius:99px;padding:0.2rem 0.65rem;font-size:0.72rem;
          font-weight:600;color:#A78BFA;">Business Consulting</span>
</div>
</div>
""", unsafe_allow_html=True)


with col_partner_info:
    st.markdown("""
<div style="padding-top:0.5rem;">
    <h3 style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:700;
         color:#DDE8F8;margin-bottom:0.75rem;">
        Real-World Validation Partner
    </h3>
    <p style="font-size:0.875rem;color:#7A9AB8;line-height:1.75;margin-bottom:1.25rem;">
        DecTell AI was developed and validated in collaboration with
        <strong style="color:#DDE8F8;">Data &amp; Disco Dreams Studio</strong> —
        a data consulting and design firm serving small businesses across the United States.
        Their real-world analytics challenges, client datasets, and feedback directly shaped
        the platform's features, dual-mode UX, and business insight generation.
    </p>
</div>""", unsafe_allow_html=True)

    metrics_cols = st.columns(3)
    for mc, (val, lbl) in zip(metrics_cols, [
        ("Real", "Business Data"),
        ("SMB",  "Focus Market"),
        ("US",   "Market Scope"),
    ]):
        with mc:
            st.markdown(f"""
<div style="background:#0F1829;border:1px solid #2C3F60;border-radius:10px;
     padding:0.9rem 0.75rem;text-align:center;">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.35rem;font-weight:800;
         color:#00D4FF;margin-bottom:0.2rem;">{val}</div>
    <div style="font-size:0.68rem;color:#6A88A8;text-transform:uppercase;
         letter-spacing:0.08em;font-weight:600;">{lbl}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    st.markdown("""
<a href="https://dataanddiscodreamsstudio.com/" target="_blank"
   style="display:inline-flex;align-items:center;gap:0.5rem;
   background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.22);
   border-radius:8px;padding:0.5rem 1.1rem;text-decoration:none;
   font-size:0.82rem;font-weight:600;color:#00D4FF;transition:all 0.18s;">
    Visit Data &amp; Disco Dreams Studio
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#00D4FF" stroke-width="2.5">
        <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>
        <polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>
    </svg>
</a>""", unsafe_allow_html=True)

divider()


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — REVIEWS SLIDER
# ══════════════════════════════════════════════════════════════════════════════
section_label("What Users Say")
st.markdown("""
<p style="font-size:0.875rem;color:#6A88A8;max-width:580px;
   line-height:1.7;margin-bottom:1.5rem;">
    Real feedback from analysts, business owners, and developers
    who have used DecTell AI on their data.
</p>""", unsafe_allow_html=True)


def fetch_reviews_from_sheets() -> list[dict]:
    """
    Fetch reviews from Google Sheets Feedback tab.
    Returns list of dicts: {name, role, text, rating, category}
    Filters for high-rating entries (rating >= 4) only.
    Falls back to curated static reviews if unavailable.
    """
    try:
        webhook = st.secrets.get("SHEETS_WEBHOOK_URL", "")
        if not webhook:
            return []

        # Build a read URL — Apps Script must expose a doGet() handler
        # See setup instructions below
        read_url = webhook.replace("/exec", "/exec") + "?action=get_feedback"
        resp = requests.get(read_url, timeout=6)
        if resp.status_code != 200:
            return []

        data = resp.json()
        reviews = []
        for row in data:
            try:
                rating = int(float(row.get("rating", 0)))
                if rating >= 4:
                    reviews.append({
                        "name":     row.get("name", "Anonymous").strip() or "Anonymous",
                        "role":     row.get("category", "Platform User"),
                        "text":     row.get("feedback", "").strip(),
                        "rating":   rating,
                        "category": row.get("category", ""),
                    })
            except Exception:
                continue
        return reviews
    except Exception:
        return []


# Curated static reviews — shown when no Sheets data available
STATIC_REVIEWS = [
    {
        "name":   "Priya M.",
        "role":   "Business Owner",
        "text":   "I described my goal in plain English — 'I want to know which customers might leave' — and DecTell AI configured the model, trained it, and gave me a full business report. I didn't write a single line of code. Genuinely impressive.",
        "rating": 5,
    },
    {
        "name":   "Arjun R.",
        "role":   "Data Analyst",
        "text":   "The scenario simulation is what sets this apart. I can adjust marketing spend, discount rates, and region variables with sliders and see the predicted revenue shift instantly. Saved hours of manual modelling.",
        "rating": 5,
    },
    {
        "name":   "Sarah K.",
        "role":   "Strategy Manager",
        "text":   "Most BI tools tell you what happened. DecTell AI tells you what will happen if you change something. The causal impact analysis gave us actual confidence intervals for our campaign ROI. That's decision support.",
        "rating": 5,
    },
    {
        "name":   "Rahul D.",
        "role":   "Data Scientist",
        "text":   "The LLM-powered cleaning is smart — it actually reads the dataset and decides what to impute, what to encode, and what to leave. On our messy CRM export it made the right calls without any manual configuration.",
        "rating": 4,
    },
    {
        "name":   "Meera S.",
        "role":   "Operations Lead",
        "text":   "I asked the chat 'which region has the highest churn rate?' and got a table, a chart suggestion, and an explanation — all in one response. It actually understood my question rather than pattern-matching keywords.",
        "rating": 5,
    },
    {
        "name":   "Kevin L.",
        "role":   "SMB Founder",
        "text":   "As a small business owner with no data team, this is the tool I've been waiting for. Upload the spreadsheet, tell it what you want to know, and get a proper business intelligence report. Couldn't be simpler.",
        "rating": 5,
    },
]


@st.cache_data(ttl=300, show_spinner=False)
def get_reviews() -> list[dict]:
    """Cache review fetch for 5 minutes."""
    live = fetch_reviews_from_sheets()
    return live if len(live) >= 3 else STATIC_REVIEWS


reviews = get_reviews()

# ── Slider state ───────────────────────────────────────────────────────────────
if "review_idx" not in st.session_state:
    st.session_state.review_idx = 0

n_reviews  = len(reviews)
chunk_size = 3   # show 3 cards at a time
n_pages    = max(1, (n_reviews + chunk_size - 1) // chunk_size)
cur_page   = st.session_state.review_idx % n_pages
start      = cur_page * chunk_size
page_revs  = reviews[start : start + chunk_size]

# Pad to 3 if last page has fewer
while len(page_revs) < chunk_size:
    page_revs.append(None)

# ── Render 3 review cards ──────────────────────────────────────────────────────
rev_cols = st.columns(3, gap="medium")

for rc, rev in zip(rev_cols, page_revs):
    with rc:
        if rev is None:
            st.markdown("""
<div style="background:#131C2E;border:1px dashed #1E2D45;border-radius:16px;
     min-height:190px;"></div>""", unsafe_allow_html=True)
            continue

        stars     = "★" * rev["rating"] + "☆" * (5 - rev["rating"])
        initials  = "".join(w[0].upper() for w in rev["name"].split()[:2]) or "?"
        text      = rev["text"]
        # Truncate very long reviews for card display
        display   = text[:220] + "…" if len(text) > 220 else text

        st.markdown(f"""
<div class="review-card">
    <div class="review-quote-mark">"</div>
    <div class="review-text">{display}</div>
    <div class="review-author">
        <div class="review-avatar">{initials}</div>
        <div>
            <div class="review-name">{rev["name"]}</div>
            <div class="review-role">{rev["role"]}</div>
        </div>
        <div class="review-stars">{stars}</div>
    </div>
</div>""", unsafe_allow_html=True)

# ── Navigation controls ────────────────────────────────────────────────────────
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

nav_l, nav_dots, nav_r = st.columns([1, 3, 1])

with nav_l:
    if st.button("← Prev", key="rev_prev", use_container_width=True):
        st.session_state.review_idx = (cur_page - 1) % n_pages
        st.rerun()

with nav_dots:
    dots_html = "<div style='display:flex;justify-content:center;align-items:center;gap:4px;padding-top:0.55rem;'>"
    for i in range(n_pages):
        active = "active" if i == cur_page else ""
        dots_html += f'<div class="slider-dot {active}"></div>'
    dots_html += "</div>"
    st.markdown(dots_html, unsafe_allow_html=True)

with nav_r:
    if st.button("Next →", key="rev_next", use_container_width=True):
        st.session_state.review_idx = (cur_page + 1) % n_pages
        st.rerun()

# ── Source note ────────────────────────────────────────────────────────────────
source = "Live from user feedback" if len(get_reviews()) != len(STATIC_REVIEWS) else "Featured reviews"
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:center;gap:0.5rem;
     margin-top:0.9rem;">
    <div style="width:6px;height:6px;border-radius:50%;
         background:{'#10B981' if 'Live' in source else '#6A88A8'};"></div>
    <span style="font-size:0.72rem;color:#3A5070;">{source}</span>
</div>""", unsafe_allow_html=True)

divider()


# ══════════════════════════════════════════════════════════════════════════════
# Rest of Home page (unchanged)
# ══════════════════════════════════════════════════════════════════════════════
section_label("Research-Driven Uniqueness")
st.markdown("""
<p style="font-size:0.95rem;color:#6A88A8;max-width:760px;line-height:1.75;margin-bottom:1.5rem;">
    Unlike Power BI, Tableau, or ChatGPT Data Analyst — which are descriptive — DecTell AI
    introduces <strong style="color:#DDE8F8;">Decision Intelligence</strong>: the ability to simulate future
    scenarios, measure causal effects of interventions, and generate AI-authored recommendations
    tailored to your role — whether you're a business owner or a data scientist.
</p>""", unsafe_allow_html=True)

pillars = [
    ("Scenario\nSimulation", "Explore future outcomes before committing to a decision."),
    ("Causal\nAnalysis",     "Measure true impact of interventions — not just correlations."),
    ("LLM\nIntelligence",    "Groq-powered AI that thinks like a senior business analyst."),
    ("Natural Language\nChat","Ask any data question in plain English — get answers instantly."),
]
p_cols = st.columns(4)
for col, (title, desc) in zip(p_cols, pillars):
    with col:
        st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:12px;
     padding:1.2rem 1rem;text-align:center;height:100%;">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:0.88rem;font-weight:700;
         color:#00D4FF;margin-bottom:0.4rem;white-space:pre-line;">{title}</div>
    <div style="font-size:0.78rem;color:#4A6080;line-height:1.5;">{desc}</div>
</div>""", unsafe_allow_html=True)

divider()

section_label("Platform Capabilities")
features = [
    ("↑",  "Smart Data Upload",       "Upload CSV or Excel. AI determines and applies only necessary cleaning."),
    ("⊛",  "Intelligent EDA",         "Automated distributions, correlations, and AI-generated narrative insights."),
    ("◉",  "Dual-Mode AI Analyze",    "Business owners describe goals; analysts get full technical control."),
    ("⊕",  "Scenario Simulation",     "What-if sliders drive trained models to forecast business outcomes."),
    ("⊘",  "Causal Impact",           "DiD and regression adjustment estimate true intervention effects."),
    ("◎",  "LLM Data Chat",           "Natural language Q&A with full conversation memory and chart responses."),
    ("▤",  "Smart Report Export",     "AI-written reports in two tracks — business and technical — as PDF or text."),
    ("≡",  "Analytics Dashboard",     "Live KPIs, model metrics, feature importances, and distribution overview."),
]
for row_feats in [features[:4], features[4:]]:
    cols = st.columns(4)
    for col, (icon, title, desc) in zip(cols, row_feats):
        with col:
            feature_card(icon, title, desc)
    st.markdown("<div style='height:0.65rem'></div>", unsafe_allow_html=True)

divider()

section_label("Built for Real Business Problems")
ic1, ic2, ic3 = st.columns(3)
with ic1:
    image_card("analytics",   "Business Analytics",    "Automated chart generation & trend detection")
with ic2:
    image_card("code",        "Predictive Modelling",  "ML-powered forecasting on any dataset")
with ic3:
    image_card("strategy",    "Decision Intelligence", "Scenario simulation & causal reasoning")

divider()

section_label("How It Works")
steps = [
    ("01", "Upload",     "Load your CSV or Excel dataset"),
    ("02", "AI Prepares","Smart cleaning — only what's needed"),
    ("03", "Explore",    "EDA with AI-generated insights"),
    ("04", "Analyze",    "Describe your goal or configure a model"),
    ("05", "Simulate",   "Run what-if scenario analysis"),
    ("06", "Report",     "Export AI-written business report"),
]
cols = st.columns(6)
for col, (num, step, desc) in zip(cols, steps):
    with col:
        st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:10px;
     padding:1rem 0.65rem;text-align:center;">
    <div style="font-size:0.6rem;font-weight:700;letter-spacing:0.1em;
         color:#00D4FF;margin-bottom:0.4rem;">{num}</div>
    <div style="font-size:0.82rem;font-weight:600;color:#DDE8F8;margin-bottom:0.3rem;">{step}</div>
    <div style="font-size:0.72rem;color:#3A5070;line-height:1.4;">{desc}</div>
</div>""", unsafe_allow_html=True)

render_footer()
