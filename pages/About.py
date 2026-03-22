"""
DecTell AI — About Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from utils.ui_utils import (
    inject_global_css, hero_section, section_label,
    divider, lottie_inline, image_card, render_footer, PEXELS
)

inject_global_css()

# ── Hero ── (fixed: no trailing div)
hero_section(
    bg_key   = "research",
    pill     = "Research & Methodology",
    title    = "Why DecTell AI\nExists",
    subtitle = "A research-backed platform addressing the gap between traditional BI tools and true decision intelligence — combining predictive analytics, causal reasoning, and simulation."
)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

# ── Problem ────────────────────────────────────────────────────────────────────
section_label("The Problem")
st.markdown("""
<h2 style="font-size:1.75rem;font-weight:700;margin-bottom:0.75rem;">
    Existing Tools Are Not Enough
</h2>
<p style="margin-bottom:1.25rem;">
    Tools like Power BI Copilot, Tableau GPT, and ChatGPT Data Analyst can generate charts,
    answer questions, and summarise insights — but they share a fundamental limitation:
    they are descriptive, not prescriptive. They tell you what happened, not what to do next.
</p>""", unsafe_allow_html=True)

c_text, c_img = st.columns([3, 2])
with c_text:
    limitations = [
        ("Correlation ≠ Causation",   "Most BI systems identify correlations but cannot prove causal relationships."),
        ("Historical Patterns Only",  "Constrained to what has happened — cannot simulate rare or extreme future scenarios."),
        ("No Decision Simulation",    "Cannot run what-if analyses to predict outcomes of proposed decisions before execution."),
        ("No Intervention Evaluation","Measuring actual campaign or policy impact requires causal inference — absent from standard BI."),
    ]
    for title, desc in limitations:
        st.markdown(f"""
<div style="display:flex;gap:0.85rem;padding:0.9rem 0;border-bottom:1px solid #2C3F60;">
    <div style="width:8px;height:8px;background:#EF4444;border-radius:50%;
         margin-top:0.45rem;flex-shrink:0;"></div>
    <div>
        <div style="font-size:0.9rem;font-weight:600;color:#DDE8F8;margin-bottom:0.2rem;">{title}</div>
        <div style="font-size:0.82rem;color:#6A88A8;line-height:1.55;">{desc}</div>
    </div>
</div>""", unsafe_allow_html=True)

with c_img:
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    image_card("meeting",   "Decision Gaps",   "Where traditional BI falls short")
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    image_card("analytics", "Data Intelligence","Bridging analytics and action")

divider()

# ── Three Core Innovations ─────────────────────────────────────────────────────
section_label("Three Core Innovations")
st.markdown("""
<h2 style="font-size:1.75rem;font-weight:700;margin-bottom:0.5rem;">
    What Makes DecTell AI Different
</h2>
<p style="margin-bottom:1.75rem;">
    Three capabilities absent from standard BI platforms, each grounded in
    academic research on decision intelligence.
</p>""", unsafe_allow_html=True)

innovations = [
    {
        "num":"01","color":"#00D4FF","title":"Scenario Simulation Engine","tag":"Main Innovation",
        "body":"""Traditional BI shows the past. DecTell AI lets you explore the future.
The Scenario Simulation Engine uses trained predictive models with interactive parameter sliders
to generate predicted outcomes across hundreds of possible business configurations.
<br><br>
Users adjust variables — price, marketing spend, discount, inventory — and the model
predicts the resulting outcome instantly. This is called <strong style="color:#00D4FF;">Decision Intelligence</strong>.""",
        "example":"Marketing budget +20% → Simulated revenue: ₹1.4M vs baseline ₹1.2M"
    },
    {
        "num":"02","color":"#7C3AED","title":"Causal Impact Analysis","tag":"Beyond Correlation",
        "body":"""Normal analytics: sales increased when ads increased. But that does not prove ads caused sales.
<br><br>
DecTell AI uses <strong style="color:#DDE8F8;">Difference-in-Differences (DiD)</strong> — a rigorous
econometric technique — to estimate the true causal effect of an intervention by comparing treatment
and control groups before and after the event. Bootstrapped confidence intervals are computed automatically.""",
        "example":"March campaign effect: +18% causal impact (95% CI: [+12%, +24%])"
    },
    {
        "num":"03","color":"#10B981","title":"Groq-Powered AI Intelligence","tag":"LLM Integration",
        "body":"""DecTell AI integrates Groq's ultra-fast LLM inference (llama-3.3-70b-versatile)
as the core intelligence engine. The AI acts as a principal business analyst — interpreting data,
generating narrative insights, detecting ML task types from natural language, and producing
targeted recommendations for both business owners and technical analysts.
<br><br>
The Chat with Data feature allows users to ask any question in plain language and receive
contextual, data-grounded answers with visualisations.""",
        "example":"User: Which customers are at risk? → AI analyzes churn indicators, trains model, delivers business report."
    },
]

for innov in innovations:
    st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-left:3px solid {innov['color']};
     border-radius:14px;padding:1.75rem 1.85rem;margin-bottom:1.25rem;">
    <div style="display:flex;align-items:center;gap:0.85rem;margin-bottom:1rem;">
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.4rem;font-weight:700;
             color:{innov['color']};opacity:0.45;">{innov['num']}</div>
        <div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:1.05rem;
                 font-weight:700;color:#DDE8F8;">{innov['title']}</div>
            <div style="font-size:0.68rem;font-weight:600;text-transform:uppercase;
                 letter-spacing:0.1em;color:{innov['color']};margin-top:2px;">{innov['tag']}</div>
        </div>
    </div>
    <div style="font-size:0.875rem;color:#7A9AB8;line-height:1.75;margin-bottom:1rem;">
        {innov['body']}
    </div>
    <div style="background:rgba(0,0,0,0.2);border-radius:8px;padding:0.75rem 1rem;
         font-size:0.8rem;font-family:'JetBrains Mono',monospace;color:#6A88A8;">
        <span style="color:{innov['color']};font-weight:600;">Example: </span>{innov['example']}
    </div>
</div>""", unsafe_allow_html=True)

divider()

# ── End Users ──────────────────────────────────────────────────────────────────
section_label("Who This Platform Serves")
st.markdown("""
<h2 style="font-size:1.75rem;font-weight:700;margin-bottom:1.25rem;">
    Built for Real Business Users
</h2>""", unsafe_allow_html=True)

users = [
    ("Business Decision Makers", "#00D4FF",
     "Use scenario simulation and what-if analysis to evaluate strategic decisions — pricing, marketing, operations — before implementation."),
    ("Business Analysts", "#7C3AED",
     "Leverage AI-assisted analytics that automatically cleans data, performs EDA, and generates insights while enabling deeper decision intelligence."),
    ("Data Analysts & Scientists", "#10B981",
     "Accelerate analytics through an integrated platform combining preprocessing, predictive modelling, causal analysis, and LLM-powered interpretation."),
    ("Strategy & Operations Teams", "#F59E0B",
     "Understand the impact of business interventions using causal analysis — not just correlations or descriptive dashboards."),
    ("Non-Technical Business Users", "#EF4444",
     "Interact with datasets via natural language chat. Ask questions, get answers and charts — no technical expertise required."),
]

c1, c2 = st.columns(2)
for i, (name, color, desc) in enumerate(users):
    with (c1 if i % 2 == 0 else c2):
        st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-top:2px solid {color};
     border-radius:12px;padding:1.1rem 1.25rem;margin-bottom:0.9rem;">
    <div style="font-size:0.88rem;font-weight:700;color:#DDE8F8;margin-bottom:0.35rem;">{name}</div>
    <div style="font-size:0.82rem;color:#6A88A8;line-height:1.55;">{desc}</div>
</div>""", unsafe_allow_html=True)

divider()

# ── Platform Architecture ──────────────────────────────────────────────────────
section_label("Platform Architecture")
st.markdown("""
<h2 style="font-size:1.75rem;font-weight:700;margin-bottom:1.25rem;">
    Five Core Intelligence Modules
</h2>""", unsafe_allow_html=True)

modules = [
    ("M1", "AI-Powered Data Preparation",
     "Groq LLM analyzes the dataset and decides exactly what cleaning is needed — imputation, encoding, outlier handling — without over-processing clean data."),
    ("M2", "Automated Exploratory Analysis",
     "Distribution analysis, correlation matrices, trend detection, and AI-generated narrative interpretations of every key finding."),
    ("M3", "Dual-Mode Predictive Intelligence",
     "Business owners describe goals in plain language; the AI configures and trains the right model. Analysts get full technical control. Both get targeted insights."),
    ("M4", "Decision Simulation & Causal Analysis",
     "What-if scenario sliders powered by trained models. DiD and regression adjustment for causal effect estimation with confidence intervals."),
    ("M5", "Groq LLM Chat & Reporting",
     "Natural language chat backed by actual dataframe computations. AI-generated full reports with business and technical recommendation tracks."),
]

for code, name, desc in modules:
    st.markdown(f"""
<div style="display:flex;gap:0.9rem;padding:0.95rem 0;border-bottom:1px solid #2C3F60;">
    <div style="font-family:'JetBrains Mono',sans-serif;font-size:0.72rem;font-weight:600;
         color:#00D4FF;background:rgba(0,212,255,0.08);border-radius:6px;
         padding:0.2rem 0.55rem;height:fit-content;white-space:nowrap;margin-top:0.1rem;">{code}</div>
    <div>
        <div style="font-size:0.9rem;font-weight:700;color:#DDE8F8;margin-bottom:0.25rem;">{name}</div>
        <div style="font-size:0.82rem;color:#6A88A8;line-height:1.55;">{desc}</div>
    </div>
</div>""", unsafe_allow_html=True)

divider()

# ── Research context ───────────────────────────────────────────────────────────
section_label("Research Context")
c_l, c_r = st.columns([2, 3])
with c_l:
    lottie_inline("about", height=200)
with c_r:
    st.markdown("""
<h2 style="font-size:1.6rem;font-weight:700;margin-bottom:0.75rem;">
    Decision Intelligence as a Research Domain
</h2>
<p>Research shows that simulation and synthetic scenario generation allow organisations to
explore rare and extreme events that never appear in historical data. This is critical for:</p>""",
    unsafe_allow_html=True)
    for point in [
        "Supply chain stress testing under demand shocks",
        "Marketing mix optimisation before campaign launch",
        "Pricing strategy evaluation without A/B test cost",
        "HR retention policy impact estimation pre-implementation",
        "Financial scenario planning under market volatility",
    ]:
        st.markdown(f"""
<div style="display:flex;gap:0.65rem;padding:0.45rem 0;">
    <div style="width:6px;height:6px;background:#00D4FF;border-radius:50%;
         margin-top:0.45rem;flex-shrink:0;"></div>
    <div style="font-size:0.875rem;color:#7A9AB8;">{point}</div>
</div>""", unsafe_allow_html=True)

render_footer()
