"""
DecTell AI — Analytics Dashboard Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.ui_utils import inject_global_css, render_footer, page_header, lottie_inline, section_label, divider
from utils.data_utils import require_dataset, get_numeric_cols, get_model_meta
from utils.visualization_utils import PLOTLY_TEMPLATE, correlation_heatmap

inject_global_css()

page_header("Outputs — Step 9", "Analytics Dashboard",
            "Live KPIs, model performance, feature importance, and distribution overview.")

df = require_dataset()
if df is None:
    st.stop()

num_cols     = get_numeric_cols(df)
model, fcols, tcol, mname = get_model_meta()
model_result = st.session_state.get("model_result")

# ── Dataset KPIs ───────────────────────────────────────────────────────────────
c_kpi, c_anim = st.columns([4,1])
with c_anim:
    lottie_inline("dashboard", height=100)
with c_kpi:
    section_label("Dataset Health")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Rows",          f"{df.shape[0]:,}")
    k2.metric("Columns",       df.shape[1])
    k3.metric("Numeric Cols",  len(num_cols))
    k4.metric("Missing Values",int(df.isna().sum().sum()))
    k5.metric("Memory (KB)",   f"{df.memory_usage(deep=True).sum() // 1024:,}")

# ── Column KPIs ────────────────────────────────────────────────────────────────
if num_cols:
    divider()
    section_label("Column Summaries")
    kpi_cols_show = num_cols[:6]
    kpi_row = st.columns(len(kpi_cols_show))
    for i, col in enumerate(kpi_cols_show):
        kpi_row[i].metric(col, f"{df[col].mean():,.2f}", delta=f"± {df[col].std():.2f}")

# ── Model Performance ──────────────────────────────────────────────────────────
if model_result:
    divider()
    section_label("Model Performance")
    metrics = model_result["metrics"]
    mc = st.columns(len([k for k in metrics if k != "Report"]))
    for i, (k, v) in enumerate([(k,v) for k,v in metrics.items() if k != "Report"]):
        mc[i].metric(k, v)

    if model_result.get("importance"):
        imp = sorted(model_result["importance"].items(), key=lambda x: x[1], reverse=True)[:8]
        imp_df = pd.DataFrame(imp, columns=["Feature", "Importance"])
        fig = px.bar(imp_df, x="Importance", y="Feature", orientation="h",
                     title="Feature Importance", template=PLOTLY_TEMPLATE,
                     color="Importance", color_continuous_scale=["#1E2D45","#00D4FF"])
        fig.update_layout(height=300, showlegend=False,
                          margin=dict(l=10,r=10,t=40,b=10))
        st.plotly_chart(fig, use_container_width=True)

# ── Distributions ──────────────────────────────────────────────────────────────
if num_cols:
    divider()
    section_label("Distribution Overview")
    sel = st.multiselect("Select columns", num_cols,
                         default=num_cols[:min(4, len(num_cols))], key="dash_dist")
    if sel:
        grid = st.columns(min(2, len(sel)))
        for i, col in enumerate(sel):
            with grid[i % 2]:
                fig = px.histogram(df, x=col, nbins=30, title=col,
                                   template=PLOTLY_TEMPLATE,
                                   color_discrete_sequence=["#00D4FF"], height=230)
                fig.update_layout(showlegend=False,
                                  margin=dict(l=10,r=10,t=36,b=10))
                st.plotly_chart(fig, use_container_width=True)

# ── Correlation ────────────────────────────────────────────────────────────────
if len(num_cols) >= 2:
    divider()
    section_label("Correlation Matrix")
    st.plotly_chart(correlation_heatmap(df), use_container_width=True)

# ── Top / bottom ───────────────────────────────────────────────────────────────
if num_cols:
    divider()
    section_label("Top & Bottom Records")
    sort_col = st.selectbox("Sort by", num_cols, index=0, key="dash_sort")
    c1, c2 = st.columns(2)
    with c1:
        st.caption("Top 5")
        st.dataframe(df.nlargest(5, sort_col), use_container_width=True)
    with c2:
        st.caption("Bottom 5")
        st.dataframe(df.nsmallest(5, sort_col), use_container_width=True)

st.markdown("""
<div style="text-align:center;padding:2rem 0 0;font-size:0.75rem;color:#334155;">
    DecTell AI — Analytics Dashboard
</div>""", unsafe_allow_html=True)
render_footer()
