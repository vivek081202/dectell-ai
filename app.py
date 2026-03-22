"""
DecTell AI — Decision Intelligence Platform
Entry point: streamlit run app.py
"""
import streamlit as st

st.set_page_config(
    page_title="DecTell AI - Transform Data Into Decisions",
    page_icon="assets/favicon.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.ui_utils import inject_global_css, dataset_status_badge

inject_global_css()

# ── Pages ──────────────────────────────────────────────────────────────────────
pages = {
    "Platform": [
        st.Page("pages/Home.py",       title="Home",                default=True),
        st.Page("pages/About.py",      title="About"),
        st.Page("pages/Contact.py",    title="Contact"),
        st.Page("pages/Developer.py",    title="Developer & Team")
    ],
    "Data": [
        st.Page("pages/Upload.py",     title="Upload & Prepare"),
    ],
    "Analysis": [
        st.Page("pages/EDA.py",        title="Exploratory Analysis"),
        st.Page("pages/AIAnalyze.py",  title="AI Analyze"),
    ],
    "Intelligence": [
        st.Page("pages/Simulation.py", title="Scenario Simulation"),
        st.Page("pages/Causal.py",     title="Causal Impact"),
        st.Page("pages/Chat.py",       title="Chat with Data"),
    ],
    "Outputs": [
        st.Page("pages/Report.py",     title="Report & Insights"),
        st.Page("pages/Dashboard.py",  title="Analytics Dashboard"),
    ],
}

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Logo + Brand (top)
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    if os.path.exists(logo_path):
        c1, c2 = st.columns([1, 3])
        with c1:
            st.image(logo_path, width=40)
        with c2:
            st.markdown("""
<div style="padding-top:0.1rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1rem;font-weight:700;
       color:#DDE8F8;line-height:1.1;">DecTell AI</div>
  <div style="font-size:0.58rem;color:#4A6080;letter-spacing:0.09em;
       text-transform:uppercase;font-weight:600;margin-top:2px;">Decision Intelligence</div>
</div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family:\'Space Grotesk\',sans-serif;font-size:1rem;'
                    'font-weight:700;color:#DDE8F8;padding-bottom:0.5rem;">DecTell AI</div>',
                    unsafe_allow_html=True)

    # ── Groq API Key ───────────────────────────────────────────────────────────
    if "groq_api_key" not in st.session_state:
        st.session_state["groq_api_key"] = st.secrets.get("GROQ_API_KEY", "")
        st.markdown('<div style="font-size:0.72rem;color:#10B981;margin-top:0.2rem;">AI features active</div>',unsafe_allow_html=True)

    dataset_status_badge()
    st.markdown("""<div style="font-size:0.6rem;font-weight:700;text-transform:uppercase;
     letter-spacing:0.14em;color:#2C3F60;padding:0.7rem 0.25rem 0.2rem;">Navigation</div>""",
        unsafe_allow_html=True)

pg = st.navigation(pages)
pg.run()
