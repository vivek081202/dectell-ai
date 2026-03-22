"""
DecTell AI — Report & Insights Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import datetime
import io

from utils.ui_utils import inject_global_css, page_header, section_label, divider, render_footer
from utils.data_utils import require_dataset
from utils.llm_utils import llm_generate_report, llm_business_insights

inject_global_css()
page_header("Outputs", "Report & Insights",
    "AI-generated analytics reports with business and technical recommendations, ready to export.")

df = require_dataset()
if df is None:
    render_footer()
    st.stop()

api_key      = st.session_state.get("groq_api_key", "")
model_result = st.session_state.get("model_result")
scenario_sum = st.session_state.get("scenario_summary")
causal_sum   = st.session_state.get("causal_summary")
filename     = st.session_state.get("uploaded_filename", "dataset")

# ── Configuration ──────────────────────────────────────────────────────────────
section_label("Report Configuration")
c1, c2 = st.columns(2)
with c1:
    report_type = st.radio("Report type", ["Full Report", "Business Report", "Technical Report"],
                           horizontal=True)
with c2:
    if not api_key:
        st.markdown('<p style="font-size:0.82rem;color:#F59E0B;margin-top:0.5rem;">'
                    'Add Groq API key for AI-generated reports. Basic report available without it.</p>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:0.82rem;color:#10B981;margin-top:0.5rem;">'
                    'AI will generate a comprehensive, data-specific report.</p>',
                    unsafe_allow_html=True)

gen_btn = st.button("Generate Report", type="primary")

if gen_btn:
    if api_key:
        with st.spinner("AI is writing your report…"):
            if report_type == "Full Report":
                report_text = llm_generate_report(df, model_result, scenario_sum, causal_sum, api_key)
            elif report_type == "Business Report":
                report_text = llm_business_insights(df, model_result, "business", api_key)
            else:
                report_text = llm_business_insights(df, model_result, "technical", api_key)
        st.session_state["generated_report"] = report_text
        st.toast("Report generated successfully.")
    else:
        # Fallback: rule-based report
        from modules.eda_analysis import generate_auto_insights
        from modules.report_generator import build_text_report
        insights = generate_auto_insights(df)
        report_text = build_text_report(filename, df, insights, model_result, scenario_sum, causal_sum)
        st.session_state["generated_report"] = report_text
        st.toast("Basic report generated. Add API key for AI-powered reports.")

report = st.session_state.get("generated_report")
if report:
    divider()
    section_label("Report Preview")
    st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:14px;
     padding:1.75rem 2rem;white-space:pre-wrap;font-size:0.875rem;
     color:#9BB5CF;line-height:1.8;max-height:600px;overflow-y:auto;">
{report}
</div>""", unsafe_allow_html=True)

    divider()
    section_label("Download")
    today = datetime.date.today()
    c1, c2 = st.columns(2)
    with c1:
        st.download_button(
            "Download as .txt",
            data=report.encode("utf-8"),
            file_name=f"DecTell_Report_{today}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with c2:
        # PDF generation
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import cm
            from reportlab.lib import colors
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

            buf = io.BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=A4,
                                    leftMargin=2.2*cm, rightMargin=2.2*cm,
                                    topMargin=2.2*cm, bottomMargin=2.2*cm)
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle("Title", parent=styles["Heading1"],
                                         fontSize=18, spaceAfter=12,
                                         textColor=colors.HexColor("#1A2540"))
            body_style  = ParagraphStyle("Body", parent=styles["Normal"],
                                         fontSize=10, leading=15, spaceAfter=6)
            head_style  = ParagraphStyle("Head", parent=styles["Heading2"],
                                         fontSize=13, spaceAfter=8, spaceBefore=14,
                                         textColor=colors.HexColor("#00A8CC"))

            story = [Paragraph("DecTell AI — Analytics Report", title_style),
                     Paragraph(f"Generated: {today} &nbsp;·&nbsp; Dataset: {filename}", body_style),
                     HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2C3F60")),
                     Spacer(1, 12)]

            for line in report.split("\n"):
                line = line.strip()
                if not line:
                    story.append(Spacer(1, 4))
                elif line.startswith("==") or line.startswith("--"):
                    continue
                elif line.isupper() and len(line) > 3:
                    story.append(Paragraph(line.title(), head_style))
                else:
                    safe = line.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                    story.append(Paragraph(safe, body_style))

            doc.build(story)
            pdf_bytes = buf.getvalue()
            st.download_button(
                "Download as .pdf",
                data=pdf_bytes,
                file_name=f"DecTell_Report_{today}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        except Exception as e:
            st.download_button(
                "Download as .txt (PDF unavailable)",
                data=report.encode("utf-8"),
                file_name=f"DecTell_Report_{today}.txt",
                mime="text/plain",
                use_container_width=True,
            )
            st.caption(f"PDF export requires reportlab: pip install reportlab ({e})")

render_footer()
