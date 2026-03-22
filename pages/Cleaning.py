"""
DecTell AI — Data Cleaning Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from utils.ui_utils import inject_global_css, page_header, lottie_inline, section_label, divider
from utils.data_utils import get_raw_df, set_clean_df, get_clean_df, column_summary
from modules.data_cleaning import run_cleaning_pipeline, get_cleaning_summary

inject_global_css()

page_header("Data Pipeline — Step 2", "Clean & Transform",
            "Automated preprocessing: imputation, outlier handling, encoding, and type correction.")

df_raw = get_raw_df()
if df_raw is None:
    st.warning("Upload a dataset first via **Upload Dataset**.")
    st.stop()

# ── Controls ──────────────────────────────────────────────────────────────────
c_btn, c_anim = st.columns([4, 1])
with c_anim:
    lottie_inline("cleaning", height=90)
with c_btn:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    run_btn = st.button("Run Cleaning Pipeline", type="primary")

df_clean = get_clean_df()
if run_btn or df_clean is None:
    with st.status("Running automated pipeline…", expanded=False) as s:
        df_clean, log = run_cleaning_pipeline(df_raw)
        set_clean_df(df_clean)
        st.session_state["cleaning_log"] = log
        s.update(label="Pipeline complete.", state="complete")

log = st.session_state.get("cleaning_log", [])
summary = get_cleaning_summary(df_raw, df_clean)

divider()
section_label("Transformation Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows",           summary["rows_after"],  delta=summary["rows_after"]  - summary["rows_before"])
c2.metric("Columns",        summary["cols_after"],  delta=summary["cols_after"]  - summary["cols_before"])
c3.metric("Missing Removed",summary["nulls_before"] - summary["nulls_after"],
          delta=f"{summary['nulls_before']} → {summary['nulls_after']}", delta_color="inverse")
c4.metric("Duplicates Removed", summary["dups_before"] - summary["dups_after"],
          delta=f"{summary['dups_before']} → {summary['dups_after']}", delta_color="inverse")

divider()
section_label("Transformation Log")
if log:
    log_md = "\n".join(f"- {entry}" for entry in log)
    st.markdown(f"""
<div style="background:#111827;border:1px solid #1E2D45;border-radius:12px;
     padding:1.25rem 1.5rem;font-size:0.875rem;line-height:1.9;color:#94A3B8;">
{log_md}
</div>""", unsafe_allow_html=True)
else:
    st.info("No transformations were applied.")

divider()
section_label("Before vs After")
tab1, tab2 = st.tabs(["Before Cleaning", "After Cleaning"])
with tab1:
    st.caption(f"{df_raw.shape[0]:,} rows × {df_raw.shape[1]} columns — raw")
    st.dataframe(df_raw.head(20), use_container_width=True)
    with st.expander("Column schema — before"):
        st.dataframe(column_summary(df_raw), use_container_width=True)

with tab2:
    st.caption(f"{df_clean.shape[0]:,} rows × {df_clean.shape[1]} columns — cleaned")
    st.dataframe(df_clean.head(20), use_container_width=True)
    with st.expander("Column schema — after"):
        st.dataframe(column_summary(df_clean), use_container_width=True)

st.success("Clean dataset saved. Proceed to **Exploratory Analysis**.")
