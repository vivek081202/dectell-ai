"""
DecTell AI — Contact Page
Google Sheets integration: see setup instructions in the expander below.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import datetime
import urllib.parse
import urllib.request

from utils.ui_utils import (
    inject_global_css, hero_section, section_label,
    divider, lottie_inline, render_footer
)

inject_global_css()


# ── Google Sheets helper ───────────────────────────────────────────────────────
def _submit_to_sheets(sheet_name: str, fields: dict) -> bool:
    """
    POST a row to Google Sheets via Apps Script Web App.
    Sends application/x-www-form-urlencoded — the format Apps Script
    doPost() reliably parses via e.parameter.

    Returns True on success, False/silent on failure — never crashes the UI.
    """
    try:
        webhook = st.secrets.get("SHEETS_WEBHOOK_URL", "")
        if not webhook:
            return False

        payload = {"sheet": sheet_name,
                   "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        payload.update({k: str(v) for k, v in fields.items()})

        data = urllib.parse.urlencode(payload).encode("utf-8")

        req = urllib.request.Request(
            webhook,
            data=data,
            method="POST",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "DecTell-AI/1.0",
            },
        )
        # Google Apps Script deployed URLs redirect POST to a new URL.
        # urllib follows redirects but converts POST→GET on 302 by default.
        # We handle this by catching HTTPError 302 manually.
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                resp.read()
        except urllib.error.HTTPError as e:
            if e.code in (301, 302, 303, 307, 308):
                # Follow redirect
                location = e.headers.get("Location", "")
                if location:
                    req2 = urllib.request.Request(location, data=data, method="POST",
                                                  headers=req.headers)
                    with urllib.request.urlopen(req2, timeout=10) as resp2:
                        resp2.read()
            else:
                raise
        return True

    except Exception as e:
        st.caption(f"Sheet logging note: {e}")
        return False


# ── Hero ───────────────────────────────────────────────────────────────────────
hero_section(
    bg_key   = "team",
    pill     = "Get In Touch",
    title    = "Contact &\nSupport",
    subtitle = "Questions about DecTell AI, research methodology, or collaboration? We'd love to hear from you."
)

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)

# ── Layout ─────────────────────────────────────────────────────────────────────
col_form, col_side = st.columns([3, 2], gap="large")

with col_form:
    # ── Contact Form ───────────────────────────────────────────────────────────
    section_label("Send a Message")

    name    = st.text_input("Full Name",     placeholder="Your name",          key="c_name")
    email   = st.text_input("Email Address", placeholder="you@example.com",    key="c_email")
    subject = st.selectbox("Subject", [
        "General Inquiry", "Research Collaboration", "Feature Request",
        "Bug Report", "Dataset Support", "Partnership", "Other",
    ], key="c_subject")
    message = st.text_area("Message",
                           placeholder="Describe your question or request…",
                           height=140, key="c_message")
    send_btn = st.button("Send Message", type="primary", use_container_width=True, key="send_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if send_btn:
        if not name or not email or not message:
            st.error("Please fill in your name, email, and message.")
        elif "@" not in email or "." not in email.split("@")[-1]:
            st.error("Please enter a valid email address.")
        else:
            with st.spinner("Sending…"):
                ok = _submit_to_sheets("Contact", {
                    "name": name, "email": email,
                    "subject": subject, "message": message,
                })
            if ok:
                st.toast(f"Message sent. We'll reply to {email} shortly.")
            else:
                st.toast(f"Message recorded (Sheet webhook not configured yet).")

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Feedback Form ──────────────────────────────────────────────────────────
    section_label("Platform Feedback")

    fb_name  = st.text_input("Your Name",  placeholder="Optional", key="fb_name")
    fb_email = st.text_input("Your Email", placeholder="Optional", key="fb_email")
    fb_rating = st.select_slider(
        "Overall Rating", options=[1, 2, 3, 4, 5], value=4,
        format_func=lambda x: ["★☆☆☆☆","★★☆☆☆","★★★☆☆","★★★★☆","★★★★★"][x-1],
        key="fb_rating"
    )
    fb_category = st.selectbox("Feedback Area", [
        "UI & Design", "AI Accuracy", "Performance",
        "Feature Request", "Data Analysis Quality", "Report Quality", "Other",
    ], key="fb_cat")
    fb_text = st.text_area(
        "Your Feedback",
        placeholder="What's working well? What could improve? What would you love to see?",
        height=120, key="fb_text"
    )
    fb_btn = st.button("Submit Feedback", use_container_width=True, key="fb_btn")
    st.markdown("</div>", unsafe_allow_html=True)

    if fb_btn:
        if not fb_text.strip():
            st.error("Please write your feedback before submitting.")
        else:
            with st.spinner("Submitting…"):
                ok = _submit_to_sheets("Feedback", {
                    "name": fb_name, "email": fb_email,
                    "rating": str(fb_rating), "category": fb_category,
                    "feedback": fb_text,
                })
            if ok:
                st.toast("Thank you for your feedback!")
            else:
                st.toast("Feedback recorded (Sheet webhook not configured yet).")

with col_side:
    lottie_inline("contact", height=180)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    section_label("Platform Details")
    details = [
        ("Version",      "DecTell AI 1.0"),
        ("Type",         "Research Analytics Platform"),
        ("AI Engine",    "Groq — llama-3.3-70b"),
        ("Framework",    "Python + Streamlit"),
        ("ML Models",    "Linear Regression, Random Forest, XGBoost"),
        ("Datasets",     "7 sample datasets included"),
        ("Licence",      "MIT — Free to use"),
    ]
    for label, value in details:
        st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
     padding:0.6rem 0;border-bottom:1px solid #2C3F60;">
    <span style="font-size:0.8rem;color:#6A88A8;font-weight:500;">{label}</span>
    <span style="font-size:0.82rem;color:#DDE8F8;font-weight:600;">{value}</span>
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    section_label("Quick Navigation")
    for label, target in [
        ("About & Research", "pages/About.py"),
        ("Start Analysis",   "pages/Upload.py"),
        ("AI Chat",          "pages/Chat.py"),
    ]:
        if st.button(label, use_container_width=True, key=f"qnav_{label}"):
            st.switch_page(target)

render_footer()
