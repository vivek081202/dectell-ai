"""
DecTell AI — Predictive Modelling Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from utils.ui_utils import inject_global_css, page_header, lottie_inline, section_label, divider
from utils.data_utils import require_dataset, get_numeric_cols, set_model
from utils.model_utils import train_model, detect_task, get_model_options
from utils.visualization_utils import feature_importance_chart, actual_vs_predicted

inject_global_css()

page_header("Analysis — Step 4", "Predictive Modelling",
            "Configure, train, and evaluate machine learning models on your cleaned dataset.")

df = require_dataset()
if df is None:
    st.stop()

num_cols  = get_numeric_cols(df)
all_cols  = df.columns.tolist()

if len(num_cols) < 2:
    st.error("Need at least 2 numeric columns to train a model.")
    st.stop()

# ── Config ─────────────────────────────────────────────────────────────────────
c_cfg, c_anim = st.columns([3, 1])
with c_anim:
    lottie_inline("model", height=110)

with c_cfg:
    section_label("Model Configuration")
    c1, c2 = st.columns(2)
    with c1:
        target_col = st.selectbox("Target variable", all_cols, index=len(all_cols)-1)
    with c2:
        remaining   = [c for c in all_cols if c != target_col]
        feature_cols = st.multiselect(
            "Feature columns", remaining,
            default=[c for c in get_numeric_cols(df) if c != target_col][:8],
        )

    c3, c4, c5 = st.columns(3)
    with c3:
        task = detect_task(df[target_col])
        model_opts = list(get_model_options(task).keys())
        model_name = st.selectbox("Algorithm", model_opts)
    with c4:
        test_size  = st.slider("Test split", 0.1, 0.4, 0.2, 0.05)
    with c5:
        st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
        st.markdown(f"""
<div class="stat-badge" style="margin-top:0.3rem;">
    Task: {task.capitalize()}
</div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    train_btn = st.button("Train Model", type="primary")

if train_btn:
    if not feature_cols:
        st.error("Select at least one feature column.")
    else:
        with st.status("Training model…", expanded=False) as s:
            try:
                result = train_model(df, feature_cols, target_col, model_name, test_size)
                st.session_state["model_result"] = result
                set_model(result["model"], feature_cols, target_col, model_name)
                s.update(label="Training complete.", state="complete")
            except Exception as e:
                st.error(f"Training failed: {e}")
                st.stop()

result = st.session_state.get("model_result")
if result:
    divider()
    section_label("Model Performance")
    metrics = result["metrics"]
    task_r  = result["task"]

    if task_r == "regression":
        m1, m2, m3 = st.columns(3)
        m1.metric("MAE",  metrics.get("MAE",  "—"))
        m2.metric("RMSE", metrics.get("RMSE", "—"))
        m3.metric("R²",   metrics.get("R²",   "—"))
    else:
        st.metric("Accuracy", f"{metrics.get('Accuracy', 0)*100:.2f}%")
        if "Report" in metrics:
            with st.expander("Classification report"):
                rdf = pd.DataFrame(metrics["Report"]).T.round(3)
                st.dataframe(rdf, use_container_width=True)

    if task_r == "regression":
        divider()
        section_label("Actual vs Predicted")
        st.plotly_chart(actual_vs_predicted(result["y_test"], result["y_pred"]),
                        use_container_width=True)
        with st.expander("Sample predictions (first 50)"):
            pdf = pd.DataFrame({
                "Actual":    result["y_test"][:50],
                "Predicted": result["y_pred"][:50],
                "Error":     (result["y_test"][:50] - result["y_pred"][:50]).round(4),
            })
            st.dataframe(pdf, use_container_width=True)

    if result.get("importance"):
        divider()
        section_label("Feature Importance")
        feats = list(result["importance"].keys())
        imps  = list(result["importance"].values())
        st.plotly_chart(feature_importance_chart(feats, imps), use_container_width=True)

    st.success("Model saved. Use it in **Scenario Simulation**.")
