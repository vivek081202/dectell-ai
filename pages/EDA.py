"""
DecTell AI — Exploratory Data Analysis Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from utils.ui_utils import inject_global_css, page_header, section_label, divider, render_footer
from utils.data_utils import require_dataset, get_numeric_cols, get_categorical_cols
from utils.visualization_utils import histogram, boxplot, scatter, correlation_heatmap, value_counts_bar
from utils.llm_utils import llm_eda_insights
from modules.eda_analysis import generate_auto_insights, trend_analysis

inject_global_css()
page_header("Analysis", "Exploratory Analysis",
    "Automated statistical analysis, visual patterns, and AI-generated business insights.")

df = require_dataset()
if df is None:
    render_footer()
    st.stop()

num_cols = get_numeric_cols(df)
cat_cols = get_categorical_cols(df)
api_key  = st.session_state.get("groq_api_key", "")

# Filter out ID-like columns from analysis (avoid useless charts)
def is_id_col(series: pd.Series) -> bool:
    name = series.name.lower()
    if any(kw in name for kw in ["id","uuid","key","index","code","no","num"]):
        if series.nunique() / max(len(series), 1) > 0.9:
            return True
    return False

clean_num = [c for c in num_cols if not is_id_col(df[c])]
clean_cat = [c for c in cat_cols if not is_id_col(df[c]) and df[c].nunique() <= 30]

# ── AI Insights ────────────────────────────────────────────────────────────────
section_label("AI-Generated Insights")
col_ai, col_btn = st.columns([4, 1])
with col_btn:
    gen_btn = st.button("Generate AI Insights", type="primary", use_container_width=True)

if gen_btn:
    if not api_key:
        st.warning("Add your Groq API key in the sidebar to generate AI insights.")
    else:
        with st.spinner("AI is analyzing your dataset…"):
            ai_text = llm_eda_insights(df, api_key)
            st.session_state["eda_ai_insights"] = ai_text

ai_insights = st.session_state.get("eda_ai_insights")
if ai_insights:
    st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-left:3px solid #00D4FF;
     border-radius:12px;padding:1.25rem 1.5rem;white-space:pre-wrap;
     font-size:0.875rem;color:#9BB5CF;line-height:1.75;">
{ai_insights}
</div>""", unsafe_allow_html=True)
else:
    # Rule-based fallback
    auto_insights = generate_auto_insights(df)
    for ins in auto_insights:
        clean = ins.replace("**","").strip()
        st.markdown(f"""
<div style="display:flex;gap:0.7rem;align-items:flex-start;padding:0.55rem 0;border-bottom:1px solid #1E2D45;">
    <div style="width:5px;height:5px;background:#00D4FF;border-radius:50%;margin-top:0.45rem;flex-shrink:0;"></div>
    <div style="font-size:0.875rem;color:#9BB5CF;">{clean}</div>
</div>""", unsafe_allow_html=True)

# ── Trend indicators ───────────────────────────────────────────────────────────
trends = trend_analysis(df)
if trends:
    divider()
    section_label("Trend Indicators")
    t_cols = st.columns(min(4, len(trends)))
    for i, t in enumerate(trends[:4]):
        t_cols[i].metric(f"{t['metric']}", t["trend"], f"{t['pct_change']:+.1f}%")

divider()

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Distributions", "Box Plots", "Correlation", "Relationships", "Categoricals"
])

with tab1:
    if not clean_num:
        st.info("No meaningful numeric columns to plot.")
    else:
        sel = st.multiselect("Select columns", clean_num,
                             default=clean_num[:min(3, len(clean_num))], key="dist_sel")
        for col in sel:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.plotly_chart(histogram(df, col), use_container_width=True)
            with c2:
                st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
                d = df[col].describe()
                st.metric("Mean",   f"{d['mean']:.2f}")
                st.metric("Median", f"{df[col].median():.2f}")
                st.metric("Std Dev",f"{d['std']:.2f}")
                skew = df[col].skew()
                st.metric("Skewness", f"{skew:.2f}",
                          delta="Right skewed" if skew > 1 else ("Left skewed" if skew < -1 else "Normal"))

with tab2:
    if not clean_num:
        st.info("No numeric columns.")
    else:
        sel = st.multiselect("Select columns", clean_num,
                             default=clean_num[:min(4, len(clean_num))], key="box_sel")
        if sel:
            grid = st.columns(min(2, len(sel)))
            for i, col in enumerate(sel):
                with grid[i % 2]:
                    st.plotly_chart(boxplot(df, col), use_container_width=True)
                    q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
                    iqr = q3 - q1
                    n_out = ((df[col] < q1-1.5*iqr) | (df[col] > q3+1.5*iqr)).sum()
                    if n_out > 0:
                        st.caption(f"{n_out} potential outliers detected in {col}")

with tab3:
    if len(clean_num) < 2:
        st.info("Need at least 2 numeric columns for correlation analysis.")
    else:
        st.plotly_chart(correlation_heatmap(df), use_container_width=True)
        corr = df[clean_num].corr()
        pairs = []
        for i in range(len(clean_num)):
            for j in range(i+1, len(clean_num)):
                val = corr.iloc[i, j]
                pairs.append({
                    "Column A": clean_num[i],
                    "Column B": clean_num[j],
                    "Correlation": round(val, 4),
                    "Strength": "Strong" if abs(val) > 0.6 else ("Moderate" if abs(val) > 0.3 else "Weak"),
                    "Direction": "Positive" if val > 0 else "Negative",
                })
        pdf = pd.DataFrame(pairs).sort_values("Correlation", key=abs, ascending=False)
        with st.expander("Full correlation table"):
            st.dataframe(pdf, use_container_width=True)

with tab4:
    if len(clean_num) < 2:
        st.info("Need at least 2 numeric columns.")
    else:
        c1, c2, c3 = st.columns(3)
        x = c1.selectbox("X axis", clean_num, index=0)
        y = c2.selectbox("Y axis", clean_num, index=min(1, len(clean_num)-1))
        color_opts = ["None"] + clean_cat
        color_by = c3.selectbox("Color by", color_opts)
        color = None if color_by == "None" else color_by
        st.plotly_chart(scatter(df, x, y, color), use_container_width=True)

with tab5:
    show_cols = clean_cat if clean_cat else []
    if not show_cols:
        st.info("No suitable categorical columns (all may be high-cardinality or encoded).")
    else:
        sel = st.multiselect("Select columns", show_cols,
                             default=show_cols[:min(3, len(show_cols))], key="cat_sel")
        for col in sel:
            st.plotly_chart(value_counts_bar(df[col]), use_container_width=True)

render_footer()
