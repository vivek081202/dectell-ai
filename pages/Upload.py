"""
DecTell AI — Upload & Prepare Page (merged Upload + Smart Cleaning)
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
from utils.ui_utils import inject_global_css, page_header, section_label, divider, render_footer
from utils.data_utils import (
    load_file, set_raw_df, set_clean_df, get_raw_df,
    column_summary, validate_dataframe, get_numeric_cols
)
from utils.llm_utils import llm_smart_clean_plan
from modules.data_cleaning import run_cleaning_pipeline, get_cleaning_summary

inject_global_css()
page_header("Data Pipeline", "Upload & Prepare",
    "Upload your dataset. AI analyzes it and applies only necessary cleaning — never over-processes.")

# ── Upload ─────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Drop CSV or Excel file here",
    type=["csv", "xlsx", "xls"],
    label_visibility="collapsed",
)
st.markdown('<p style="font-size:0.78rem;color:#3A5070;margin-top:0.4rem;">'
            'Supported: .csv &nbsp;·&nbsp; .xlsx &nbsp;·&nbsp; .xls</p>', unsafe_allow_html=True)

if uploaded:
    with st.spinner("Loading dataset…"):
        try:
            file_bytes = uploaded.read()
            df_raw = load_file(file_bytes, uploaded.name)
            warnings = validate_dataframe(df_raw)
            for w in warnings:
                st.warning(w)
            set_raw_df(df_raw)
            set_clean_df(None)
            st.session_state["uploaded_filename"] = uploaded.name
            st.session_state["cleaning_done"] = False
        except Exception as e:
            st.error(f"Failed to load file: {e}")
            st.stop()

df_raw = get_raw_df()
if df_raw is None:
    st.info("Upload a CSV or Excel file above to begin.")
    render_footer()
    st.stop()

# ── Overview metrics ───────────────────────────────────────────────────────────
divider()
section_label("Dataset Overview")
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Rows",          f"{df_raw.shape[0]:,}")
m2.metric("Columns",       df_raw.shape[1])
m3.metric("Numeric Cols",  df_raw.select_dtypes(include="number").shape[1])
m4.metric("Missing Values",int(df_raw.isna().sum().sum()))
m5.metric("Duplicate Rows",int(df_raw.duplicated().sum()))

tab1, tab2, tab3 = st.tabs(["Preview", "Column Schema", "Statistics"])
with tab1:
    st.dataframe(df_raw.head(20), use_container_width=True, height=350)
with tab2:
    st.dataframe(column_summary(df_raw), use_container_width=True)
with tab3:
    nd = df_raw.select_dtypes(include="number")
    if not nd.empty:
        st.dataframe(nd.describe().T.round(4), use_container_width=True)
    else:
        st.info("No numeric columns.")

divider()

# ── AI-Powered Smart Cleaning ─────────────────────────────────────────────────
section_label("AI-Powered Data Preparation")

api_key = st.session_state.get("groq_api_key", "")
has_ai  = bool(api_key)

col_btn, col_info = st.columns([2, 3])
with col_btn:
    prepare_btn = st.button("Analyze & Prepare Dataset", type="primary", use_container_width=True)
with col_info:
    if not has_ai:
        st.markdown('<p style="font-size:0.82rem;color:#F59E0B;margin-top:0.5rem;">'
                    'Add Groq API key in sidebar for AI-driven cleaning decisions. '
                    'Standard pipeline will run otherwise.</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:0.82rem;color:#10B981;margin-top:0.5rem;">'
                    'AI will analyze your data and decide what (if anything) needs cleaning.</p>',
                    unsafe_allow_html=True)

if prepare_btn or st.session_state.get("cleaning_done"):
    if not st.session_state.get("cleaning_done"):
        # ── AI cleaning plan ───────────────────────────────────────────────────
        if has_ai:
            with st.spinner("AI is analyzing your dataset…"):
                plan = llm_smart_clean_plan(df_raw, api_key)
            st.session_state["cleaning_plan"] = plan

            # Display AI reasoning
            st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-left:3px solid #00D4FF;
     border-radius:12px;padding:1rem 1.25rem;margin:1rem 0;">
    <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
         letter-spacing:0.12em;color:#00D4FF;margin-bottom:0.4rem;">AI Assessment</div>
    <div style="font-size:0.875rem;color:#9BB5CF;line-height:1.65;">
        {plan.get('reasoning', 'Analysis complete.')}
    </div>
</div>""", unsafe_allow_html=True)

            if plan.get("warnings"):
                for w in plan["warnings"]:
                    st.warning(w)

            if not plan.get("needs_cleaning", True):
                st.success("Dataset looks clean. Passing directly to analysis pipeline.")
                set_clean_df(df_raw.copy())
                st.session_state["cleaning_done"] = True
                st.session_state["cleaning_log"] = ["AI determined no cleaning required — data passed as-is."]
            else:
                # Apply recommended operations selectively
                with st.spinner("Applying AI-recommended transformations…"):
                    id_cols = set(plan.get("id_columns", []))
                    df_work = df_raw.copy()
                    log = []
                    ops = plan.get("operations", [])

                    for op in ops:
                        col   = op.get("column", "")
                        action = op.get("action", "keep")
                        if col not in df_work.columns or col in id_cols:
                            continue
                        try:
                            if action == "impute_median" and col in df_work.select_dtypes(include="number").columns:
                                med = df_work[col].median()
                                nulls = df_work[col].isna().sum()
                                df_work[col] = df_work[col].fillna(med)
                                log.append(f"Imputed {nulls} nulls in '{col}' with median ({med:.2f})")
                            elif action == "impute_mode":
                                mode = df_work[col].mode()
                                if not mode.empty:
                                    nulls = df_work[col].isna().sum()
                                    df_work[col] = df_work[col].fillna(mode[0])
                                    log.append(f"Imputed {nulls} nulls in '{col}' with mode ('{mode[0]}')")
                            elif action == "drop_column":
                                df_work = df_work.drop(columns=[col])
                                log.append(f"Dropped column '{col}' (AI recommended)")
                            elif action == "cap_outliers" and col in df_work.select_dtypes(include="number").columns:
                                q1, q3 = df_work[col].quantile(0.25), df_work[col].quantile(0.75)
                                iqr = q3 - q1
                                lo, hi = q1 - 1.5*iqr, q3 + 1.5*iqr
                                n_out = ((df_work[col] < lo) | (df_work[col] > hi)).sum()
                                df_work[col] = df_work[col].clip(lo, hi)
                                log.append(f"Capped {n_out} outliers in '{col}' to [{lo:.2f}, {hi:.2f}]")
                            elif action == "label_encode":
                                from sklearn.preprocessing import LabelEncoder
                                le = LabelEncoder()
                                df_work[col] = le.fit_transform(df_work[col].astype(str))
                                log.append(f"Label-encoded '{col}'")
                            elif action == "one_hot":
                                if df_work[col].nunique() <= 15:
                                    dummies = pd.get_dummies(df_work[col], prefix=col, drop_first=True, dtype=int)
                                    df_work = pd.concat([df_work.drop(columns=[col]), dummies], axis=1)
                                    log.append(f"One-hot encoded '{col}'")
                        except Exception as e:
                            log.append(f"Skipped '{col}' ({action}): {e}")

                    # Remove duplicates
                    n_dups = df_work.duplicated().sum()
                    if n_dups > 0:
                        df_work = df_work.drop_duplicates().reset_index(drop=True)
                        log.append(f"Removed {n_dups} duplicate rows")

                    if not log:
                        log.append("AI found no operations needed — dataset passed as-is.")

                    set_clean_df(df_work)
                    st.session_state["cleaning_log"] = log
                    st.session_state["cleaning_done"] = True
        else:
            # Standard pipeline fallback
            with st.spinner("Running standard cleaning pipeline…"):
                df_clean, log = run_cleaning_pipeline(df_raw)
                set_clean_df(df_clean)
                st.session_state["cleaning_log"] = log
                st.session_state["cleaning_done"] = True

    # ── Show results ───────────────────────────────────────────────────────────
    from utils.data_utils import get_clean_df
    df_clean = get_clean_df()
    log = st.session_state.get("cleaning_log", [])

    if log:
        section_label("Preparation Log")
        for entry in log:
            st.markdown(f"""
<div style="display:flex;gap:0.6rem;align-items:flex-start;padding:0.4rem 0;
     border-bottom:1px solid #1E2D45;">
    <div style="width:5px;height:5px;background:#10B981;border-radius:50%;
         margin-top:0.45rem;flex-shrink:0;"></div>
    <div style="font-size:0.855rem;color:#7A9AB8;">{entry}</div>
</div>""", unsafe_allow_html=True)

    if df_clean is not None:
        divider()
        section_label("Prepared Dataset")
        c1, c2, c3 = st.columns(3)
        c1.metric("Final Rows",    f"{df_clean.shape[0]:,}", delta=f"{df_clean.shape[0]-df_raw.shape[0]}")
        c2.metric("Final Columns", df_clean.shape[1],        delta=df_clean.shape[1]-df_raw.shape[1])
        c3.metric("Missing Values",int(df_clean.isna().sum().sum()))
        st.dataframe(df_clean.head(15), use_container_width=True)
        st.success("Dataset prepared and ready. Proceed to **Exploratory Analysis**.")

render_footer()
