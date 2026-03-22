"""
DecTell AI — Developer Page
Vivek Singh | AI Developer & Business Data Analytics Professional
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from utils.ui_utils import inject_global_css, section_label, divider, render_footer

inject_global_css()

st.markdown("""
<style>
.dev-avatar-ring {
    width:155px;height:155px;border-radius:50%;
    border:3px solid #00D4FF;
    box-shadow:0 0 0 6px rgba(0,212,255,0.10),0 0 36px rgba(0,212,255,0.18);
    overflow:hidden;margin:0 auto 1.1rem auto;
    background:#1A2540;display:flex;align-items:center;justify-content:center;
}
.dev-avatar-ring img{width:100%;height:100%;object-fit:cover;}
.dev-avatar-placeholder{
    width:155px;height:155px;border-radius:50%;
    background:linear-gradient(135deg,#1A2540 0%,#213050 100%);
    display:flex;align-items:center;justify-content:center;
    font-size:2.5rem;font-weight:900;color:#00D4FF;
    font-family:"Space Grotesk",sans-serif;
}
.social-row{display:flex;flex-direction:column;gap:0.45rem;align-items:center;}
.social-badge{
    display:inline-flex;align-items:center;gap:0.5rem;
    background:#1A2540;border:1px solid #2C3F60;border-radius:8px;
    padding:0.42rem 0.9rem;text-decoration:none;
    font-size:0.81rem;font-weight:500;color:#9BB5CF;
    transition:all 0.18s;width:100%;max-width:200px;
}
.social-badge:hover{border-color:#00D4FF;color:#00D4FF;transform:translateY(-2px);}
.social-badge svg{width:15px;height:15px;flex-shrink:0;}
.skill-pill{
    display:inline-flex;align-items:center;
    background:rgba(0,212,255,0.07);border:1px solid rgba(0,212,255,0.2);
    border-radius:99px;padding:0.25rem 0.7rem;
    font-size:0.76rem;font-weight:600;color:#00D4FF;
    margin:0.2rem;letter-spacing:0.02em;
}
.sp-purple{background:rgba(124,58,237,0.08);border-color:rgba(124,58,237,0.25);color:#A78BFA;}
.sp-green{background:rgba(16,185,129,0.07);border-color:rgba(16,185,129,0.22);color:#34D399;}
.sp-amber{background:rgba(245,158,11,0.07);border-color:rgba(245,158,11,0.22);color:#FCD34D;}
.tech-card{
    background:#1A2540;border:1px solid #2C3F60;border-radius:14px;
    padding:1.1rem 0.85rem;text-align:center;transition:all 0.2s;height:100%;
}
.tech-card:hover{border-color:#3A5278;transform:translateY(-3px);box-shadow:0 8px 24px rgba(0,0,0,0.3);}
.tc-icon{font-size:1.75rem;margin-bottom:0.45rem;display:block;}
.tc-name{font-family:"Space Grotesk",sans-serif;font-size:0.86rem;font-weight:700;color:#DDE8F8;}
.tc-role{font-size:0.68rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.45rem;}
.tc-desc{font-size:0.73rem;color:#6A88A8;line-height:1.45;}
.info-card{background:#1A2540;border:1px solid #2C3F60;border-radius:12px;padding:1.2rem 1.35rem;}
.cert-badge{
    display:inline-flex;align-items:center;gap:0.4rem;
    background:#1A2540;border:1px solid #2C3F60;border-radius:8px;
    padding:0.4rem 0.8rem;font-size:0.77rem;font-weight:500;color:#9BB5CF;margin:0.22rem;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────────────
st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)
col_left, col_right = st.columns([1, 2.5], gap="large")

with col_left:
    photo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "vivek_photo.png")
    if os.path.exists(photo_path):
        import base64
        with open(photo_path, "rb") as f:
            img_b64 = base64.b64encode(f.read()).decode()
        avatar_html = f'''<div class="dev-avatar-ring"><img src="data:image/jpeg;base64,{img_b64}" alt="Vivek Singh"></div>'''
    else:
        avatar_html = '''<div class="dev-avatar-ring"><div class="dev-avatar-placeholder">VS</div></div>'''

    st.markdown(f"""
<div style="text-align:center;">
    {avatar_html}
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:800;
         color:#DDE8F8;margin-bottom:0.15rem;">Vivek Singh</div>
    <div style="font-size:0.8rem;color:#00D4FF;font-weight:600;letter-spacing:0.04em;
         margin-bottom:0.3rem;">Business Data Analyst</div>
    <div style="font-size:0.74rem;color:#6A88A8;margin-bottom:0.15rem;">Delhi NCR, India</div>
    <div style="font-size:0.74rem;color:#4A6080;">MCA · Big Data &amp; Analytics · JIIT Noida</div>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.9rem'></div>", unsafe_allow_html=True)
    st.markdown("""
<div class="social-row">
  <a class="social-badge" href="https://www.linkedin.com/in/vivek-singh-858941201/" target="_blank">
    <svg viewBox="0 0 24 24" fill="#0A66C2"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
    LinkedIn
  </a>
  <a class="social-badge" href="https://github.com/vivek081202" target="_blank">
    <svg viewBox="0 0 24 24" fill="#DDE8F8"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
    github.com/vivek081202
  </a>
  <a class="social-badge" href="mailto:vivekkrsingh082003@gmail.com">
    <svg viewBox="0 0 24 24" fill="#00D4FF"><path d="M24 5.457v13.909c0 .904-.732 1.636-1.636 1.636h-3.819V11.73L12 16.64l-6.545-4.91v9.273H1.636A1.636 1.636 0 010 19.366V5.457c0-.9.732-1.636 1.636-1.636h.009L12 11.63l10.355-7.81h.009A1.636 1.636 0 0124 5.457z"/></svg>
    vivekkrsingh082003
  </a>
</div>""", unsafe_allow_html=True)

with col_right:
    roles_html = "".join([
        f'''<span style="background:{bg};border:1px solid {bd};border-radius:99px;padding:0.26rem 0.78rem;font-size:0.78rem;font-weight:600;color:{col};margin:0.2rem;display:inline-block;">{label}</span>'''
        for label,col,bg,bd in [
            ("Lead Development","#00D4FF","rgba(0,212,255,0.09)","rgba(0,212,255,0.22)"),
            ("AI & ML Engineering","#A78BFA","rgba(124,58,237,0.08)","rgba(124,58,237,0.25)"),
            ("Data Analytics","#34D399","rgba(16,185,129,0.08)","rgba(16,185,129,0.22)"),
            ("Business Analytics","#FCD34D","rgba(245,158,11,0.08)","rgba(245,158,11,0.22)"),
            ("Research Author","#FCA5A5","rgba(239,68,68,0.08)","rgba(239,68,68,0.22)"),
        ]
    ])
    st.markdown(f"""
<div style="padding-top:0.25rem;">
    <div style="font-size:0.67rem;font-weight:700;text-transform:uppercase;
         letter-spacing:0.14em;color:#00D4FF;margin-bottom:0.5rem;">About the Developer</div>
    <h1 style="font-size:1.85rem;font-weight:800;margin:0 0 0.7rem 0;color:#DDE8F8;line-height:1.2;">
        Turning Business Data<br>Into Intelligence
    </h1>
    <p style="font-size:0.9rem;color:#7A9AB8;line-height:1.75;margin-bottom:1rem;">
        Business Data Analytics professional with hands-on experience in Python, SQL, and ML
        skilled at translating complex datasets into actionable insights that drive real decisions.
        MCA Grduate in Big Data &amp; Analytics at JIIT Noida, India, with internship
        experience at US-based firms across CRM, Revenue, financial, sustainability, and operational analytics.
    </p>
    <p style="font-size:0.9rem;color:#7A9AB8;line-height:1.75;margin-bottom:1.25rem;">
        <strong style="color:#9BB5CF;">DecTell AI</strong> is my major research project
        a production-grade Decision Intelligence platform that integrates LLM, causal impact
        analysis (DiD), scenario simulation, and natural language data chat into a single Streamlit application.
        Validated across 8+ real-world datasets with up to 90% R² and 92%+ classification accuracy.
    </p>
    <div style="background:#1A2540;border:1px solid #2C3F60;border-left:3px solid #00D4FF;
         border-radius:12px;padding:0.9rem 1.1rem;">
        <div style="font-size:0.67rem;font-weight:700;text-transform:uppercase;
             letter-spacing:0.12em;color:#00D4FF;margin-bottom:0.55rem;">Role on DecTell AI</div>
        {roles_html}
    </div>
</div>""", unsafe_allow_html=True)

divider()

# ── EXPERIENCE ────────────────────────────────────────────────────────────────
section_label("Work Experience")

for exp in [
    {
        "year":"Jan 2026 — Present","color":"#00D4FF",
        "title":"Business Data Analyst Intern",
        "org":"Data & Disco Dreams Studio · Remote, Atlanta, United States",
        "bullets":[
            "Hypothesis-driven analysis of customer lifecycle data to identify revenue drivers and high-value segments.",
            "Designed performance dashboards in MS Excel improving visibility into revenue trends.",
            "Contributed to a reusable performance tracking framework enabling data-driven stakeholder decisions.",
        ]
    },
    {
        "year":"Jun 2025 — Aug 2025","color":"#A78BFA",
        "title":"Data Analyst & Engineering Intern",
        "org":"ECGO · Atlanta, Georgia, United States",
        "bullets":[
            "Analyzed 47K+ structured records using Python and SQL for consumption trends and revenue analysis.",
            "Built data ingestion pipelines for 13.5K+ records ensuring data quality and reporting accuracy.",
            "Architected ETL pipelines integrating MySQL and AWS, reducing report generation time by 80%.",
        ]
    },
]:
    bullet_rows = "".join([
        f'''<div style="display:flex;gap:0.55rem;margin-bottom:0.35rem;">
        <div style="width:5px;height:5px;background:{exp["color"]};border-radius:50%;margin-top:0.42rem;flex-shrink:0;"></div>
        <div style="font-size:0.8rem;color:#7A9AB8;line-height:1.55;">{b}</div></div>'''
        for b in exp["bullets"]
    ])
    st.markdown(f"""
<div class="info-card" style="margin-bottom:0.75rem;border-left:3px solid {exp["color"]};">
    <div style="display:flex;align-items:flex-start;justify-content:space-between;
         flex-wrap:wrap;gap:0.5rem;margin-bottom:0.5rem;">
        <div>
            <div style="font-size:0.9rem;font-weight:700;color:#DDE8F8;">{exp["title"]}</div>
            <div style="font-size:0.8rem;color:#6A88A8;margin-top:0.1rem;">{exp["org"]}</div>
        </div>
        <span style="background:rgba(0,0,0,0.2);border:1px solid #2C3F60;border-radius:99px;
              padding:0.2rem 0.65rem;font-size:0.7rem;font-weight:600;
              color:{exp["color"]};white-space:nowrap;">{exp["year"]}</span>
    </div>
    {bullet_rows}
</div>""", unsafe_allow_html=True)

divider()

# ── SKILLS ────────────────────────────────────────────────────────────────────
section_label("Skills & Expertise")
skill_groups = [
    ("AI & Analytics","#00D4FF","",
     ["Groq LLM","Machine Learning","Causal Inference","EDA","Statistical Analysis","Hypothesis Testing","Predictive Modeling","NLP"]),
    ("Programming & Data","#A78BFA","sp-purple",
     ["Python","SQL","MySQL","Pandas","NumPy","Scikit-learn","XGBoost","ETL Pipelines"]),
    ("Tools & Platforms","#34D399","sp-green",
     ["Streamlit","Power BI","MS Excel","AWS","Plotly","JIRA","Git / GitHub","Jupyter"]),
    ("Business & Domain","#FCD34D","sp-amber",
     ["Business Intelligence","Financial Analysis","Stakeholder Mgmt","Agile / SDLC","BRD & FRD","Data Quality","Reporting","Decision Making"]),
]
sk_cols = st.columns(4)
for col, (label, color, cls, skills) in zip(sk_cols, skill_groups):
    with col:
        pills = " ".join([f'<span class="skill-pill {cls}">{s}</span>' for s in skills])
        st.markdown(f"""
<div class="info-card">
    <div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;
         color:{color};margin-bottom:0.7rem;">{label}</div>
    {pills}
</div>""", unsafe_allow_html=True)

divider()

# ── EDUCATION + CERTS ─────────────────────────────────────────────────────────
col_edu, col_cert = st.columns(2, gap="large")
with col_edu:
    section_label("Education")
    st.markdown("""
<div class="info-card">
    <div style="display:flex;gap:1rem;padding:0.85rem 0;border-bottom:1px solid #1E2D45;">
        <div style="width:10px;height:10px;border-radius:50%;background:#00D4FF;margin-top:0.42rem;flex-shrink:0;"></div>
        <div>
            <div style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#00D4FF;margin-bottom:0.15rem;">Jul 2024 — May 2026</div>
            <div style="font-size:0.9rem;font-weight:700;color:#DDE8F8;margin-bottom:0.15rem;">Master of Computer Applications (MCA)</div>
            <div style="font-size:0.8rem;color:#6A88A8;">Big Data and Analytics &nbsp;·&nbsp; CGPA: 8.2</div>
            <div style="font-size:0.78rem;color:#4A6080;">Jaypee Institute of Information Technology (JIIT), Noida</div>
        </div>
    </div>
    <div style="display:flex;gap:1rem;padding:0.85rem 0;">
        <div style="width:10px;height:10px;border-radius:50%;background:#A78BFA;margin-top:0.42rem;flex-shrink:0;"></div>
        <div>
            <div style="font-size:0.67rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;color:#A78BFA;margin-bottom:0.15rem;">Aug 2020 — Jun 2023</div>
            <div style="font-size:0.9rem;font-weight:700;color:#DDE8F8;margin-bottom:0.15rem;">Bachelor of Computer Applications (BCA)</div>
            <div style="font-size:0.8rem;color:#6A88A8;">Software Development &amp; AI &nbsp;·&nbsp; CGPA: 8.9</div>
            <div style="font-size:0.78rem;color:#4A6080;">Guru Gobind Singh Indraprastha University (GGSIPU), New Delhi</div>
        </div>
    </div>
</div>""", unsafe_allow_html=True)

with col_cert:
    section_label("Certifications")
    certs = [("🎓","Stanford — Statistics"),("📊","Microsoft PL-300 Power BI"),
             ("💻","LeetCode — SQL"),("⚡","LinkedIn — Agile Development"),("🤖","Anthropic — Claude AI Tools")]
    cert_html = "".join([f'<div class="cert-badge"><span>{i}</span>{n}</div>' for i,n in certs])
    st.markdown(f'''<div class="info-card" style="min-height:200px;"><div style="display:flex;flex-wrap:wrap;gap:0.1rem;">{cert_html}</div></div>''', unsafe_allow_html=True)

divider()

# ── TECH STACK ────────────────────────────────────────────────────────────────
section_label("DecTell AI — Technology Stack")
st.markdown('''<p style="font-size:0.875rem;color:#6A88A8;margin-bottom:1.4rem;">Every technology was chosen for a specific purpose — fast LLM inference, production-grade ML, interactive visualisation, and zero-friction deployment.</p>''', unsafe_allow_html=True)

techs = [
    ("🐍","Python 3.12","Core Language","#3B82F6","Primary language for all modules — data processing, ML, API integration, and UI logic."),
    ("🔴","Streamlit","Web Framework","#EF4444","Multi-page app with dual-mode UX, sidebar navigation, and all interactive widgets."),
    ("⚡","Groq API","LLM Engine","#F59E0B","Ultra-fast inference powering smart cleaning, NL task detection, insights, and chat."),
    ("🧠","llama-3.3-70b","Primary AI Model","#8B5CF6","Groq-hosted open-source LLM acting as Principal Business Analyst across all AI features."),
    ("🐼","Pandas","Data Processing","#10B981","DataFrame engine for ingestion, encoding, imputation, outlier capping, and transforms."),
    ("🔢","NumPy","Numerical Compute","#EC4899","Array ops, bootstrap resampling for causal CI, and numerical stability throughout."),
    ("🤖","Scikit-learn","Machine Learning","#F97316","Linear Regression, Logistic Regression, Random Forest with balanced class weights."),
    ("🚀","XGBoost","Gradient Boosting","#06B6D4","High-performance gradient boosted trees for both regression and classification tasks."),
    ("📊","Plotly","Visualisation","#64748B","All interactive charts — histograms, heatmaps, scatter, probability bars, comparisons."),
    ("📄","ReportLab","PDF Generation","#84CC16","Styled PDF export for AI-authored business and technical analytics reports."),
    ("🔗","Google Sheets","Integration","#22C55E","Webhook-based logging for contact and feedback form submissions via Apps Script."),
    ("✨","Streamlit-Lottie","UI Animations","#A855F7","Lottie JSON animations for hero sections and visual polish across all pages."),
]
for row in [techs[:4], techs[4:8], techs[8:12]]:
    cols = st.columns(4)
    for col, (icon,name,role,color,desc) in zip(cols, row):
        with col:
            st.markdown(f'''
<div class="tech-card" style="border-top:2px solid {color};">
    <span class="tc-icon">{icon}</span>
    <div class="tc-name">{name}</div>
    <div class="tc-role" style="color:{color};">{role}</div>
    <div class="tc-desc">{desc}</div>
</div>''', unsafe_allow_html=True)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

divider()

# ── STATS STRIP ───────────────────────────────────────────────────────────────
section_label("DecTell AI — At a Glance")
stats = [("8+","Datasets Validated"),("90%","Best R² Score"),("92%+","Classification Acc."),
         ("7","Core Modules"),("llama-Groq-3.3-70b","AI Engine"),("MIT","Open Source")]
cols = st.columns(6)
for col,(val,lbl) in zip(cols, stats):
    with col:
        st.markdown(f'''
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:12px;padding:1rem 0.6rem;text-align:center;">
    <div style="font-family:'Space Grotesk',sans-serif;font-size:1.25rem;font-weight:800;
         color:#00D4FF;line-height:1.1;margin-bottom:0.3rem;">{val}</div>
    <div style="font-size:0.67rem;color:#6A88A8;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">{lbl}</div>
</div>''', unsafe_allow_html=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
st.markdown('''
<div style="background:linear-gradient(135deg,rgba(0,212,255,0.06) 0%,rgba(124,58,237,0.06) 100%);
     border:1px solid #2C3F60;border-radius:16px;padding:1.75rem 2.5rem;text-align:center;">
    <div style="font-size:1.2rem;color:#DDE8F8;font-family:'Space Grotesk',sans-serif;
         font-weight:600;line-height:1.55;margin-bottom:0.65rem;">
        "The goal was never to build another dashboard.<br>
        It was to build a system that
        <span style="color:#00D4FF;">thinks like a business analyst.</span>"
    </div>
    <div style="font-size:0.8rem;color:#6A88A8;">— Vivek Singh &nbsp;·&nbsp; Lead Developer, DecTell AI</div>
</div>''', unsafe_allow_html=True)

render_footer()
