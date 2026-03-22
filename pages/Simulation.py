"""
DecTell AI — Scenario Simulation Page

Design principles:
- Works with ANY dataset type: numeric, categorical, boolean, date, mixed
- Regression → shows predicted value with delta
- Classification → shows CLASS PROBABILITY (0-100%) not just class label
  so sliders always produce visible continuous output, even with imbalanced data
- Sliders for numeric, dropdowns for categorical, toggles for boolean
- Never calls .mean() or arithmetic on string columns
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np

from utils.ui_utils import inject_global_css, render_footer, page_header, section_label, divider
from utils.data_utils import require_dataset, get_model_meta
from utils.model_utils import predict_single, predict_proba_single
from utils.visualization_utils import scenario_comparison

inject_global_css()
page_header("Intelligence", "Scenario Simulation",
            "Adjust variables and instantly forecast how outcomes change. "
            "Numeric features use sliders; categorical features use dropdowns.")

df = require_dataset()
if df is None:
    render_footer()
    st.stop()

model, feature_cols, target_col, model_name = get_model_meta()
if model is None:
    st.warning("Train a model first in **AI Analyze**.")
    render_footer()
    st.stop()

result = st.session_state.get("model_result")
if result is None:
    st.warning("No model result found. Please re-train the model in **AI Analyze**.")
    render_footer()
    st.stop()

task = result.get("task", "regression")
target_encoder = result.get("target_encoder")

# ── Model info strip ───────────────────────────────────────────────────────────
mode_label = "Probability Mode" if task == "classification" else "Value Prediction"
st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:12px;
     padding:1rem 1.25rem;font-size:0.85rem;color:#6A88A8;line-height:1.7;margin-bottom:1.5rem;">
    <strong style="color:#9BB5CF;">Model:</strong> {model_name} &nbsp;·&nbsp;
    <strong style="color:#9BB5CF;">Target:</strong> {target_col} &nbsp;·&nbsp;
    <strong style="color:#9BB5CF;">Task:</strong> {task.capitalize()} &nbsp;·&nbsp;
    <strong style="color:#00D4FF;">Output: {mode_label}</strong>
</div>""", unsafe_allow_html=True)

# ── Explain probability mode to users ─────────────────────────────────────────
if task == "classification":
    classes = target_encoder.classes_.tolist() if target_encoder is not None else ["Class 0", "Class 1"]
    st.markdown(f"""
<div style="background:rgba(0,212,255,0.05);border:1px solid rgba(0,212,255,0.15);
     border-radius:10px;padding:0.8rem 1rem;margin-bottom:1rem;font-size:0.82rem;color:#6A88A8;">
    This is a classification problem — target classes: 
    <strong style="color:#9BB5CF;">{", ".join(str(c) for c in classes)}</strong>.
    The simulation shows <strong style="color:#00D4FF;">probability %</strong> for each class,
    which responds continuously to every slider change.
</div>""", unsafe_allow_html=True)

# ── Classify columns for controls ─────────────────────────────────────────────
def _classify_cols(df, cols):
    numeric, categorical, boolean = [], [], []
    for col in cols:
        if col not in df.columns:
            continue
        s = df[col]
        if s.dtype == "object":
            lower_vals = s.dropna().str.lower().unique()
            if set(lower_vals).issubset({"yes","no","true","false","y","n","1","0"}):
                boolean.append(col); continue
        if pd.api.types.is_numeric_dtype(s):
            numeric.append(col)
        else:
            categorical.append(col)
    return numeric, categorical, boolean

numeric_cols, cat_cols, bool_cols = _classify_cols(df, feature_cols)

# ── Safe baseline computation — never .mean() on strings ──────────────────────
def _safe_baseline(df, col):
    s = df[col].dropna()
    if s.empty:
        return 0
    if pd.api.types.is_numeric_dtype(s):
        return float(s.mean())
    return s.mode()[0] if not s.mode().empty else s.iloc[0]

base_vals = {col: _safe_baseline(df, col) for col in feature_cols if col in df.columns}

# ── Controls ───────────────────────────────────────────────────────────────────
divider()
section_label("Adjust Variables")
st.markdown("""<p style="font-size:0.82rem;color:#4A6080;margin-bottom:1rem;">
Change any variable below. Click <strong>Run Simulation</strong> to see how the outcome shifts.</p>""",
unsafe_allow_html=True)

sim_vals = {}

# Numeric sliders
if numeric_cols:
    n_show = min(9, len(numeric_cols))
    grid = st.columns(min(3, n_show))
    for i, col in enumerate(numeric_cols[:n_show]):
        s = df[col].dropna()
        cmin, cmax, cmean = float(s.min()), float(s.max()), float(s.mean())
        if cmin == cmax:
            cmin -= abs(cmin * 0.1) + 1
            cmax += abs(cmax * 0.1) + 1
        step = max((cmax - cmin) / 100, 0.001)
        with grid[i % 3]:
            sim_vals[col] = st.slider(col, cmin, cmax, cmean,
                                      step=step, format="%.2f", key=f"sn_{col}")

# Categorical dropdowns
if cat_cols:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    section_label("Categorical Variables")
    grid2 = st.columns(min(3, len(cat_cols)))
    for i, col in enumerate(cat_cols[:9]):
        opts = df[col].dropna().unique().tolist()
        default = base_vals.get(col, opts[0])
        if default not in opts:
            default = opts[0]
        with grid2[i % 3]:
            sim_vals[col] = st.selectbox(col, opts,
                index=opts.index(default), key=f"sc_{col}")

# Boolean toggles
if bool_cols:
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    section_label("Yes / No Variables")
    grid3 = st.columns(min(3, len(bool_cols)))
    for i, col in enumerate(bool_cols):
        default = base_vals.get(col, "No")
        default_idx = 0 if str(default).lower() in ("yes","true","1","y") else 1
        with grid3[i % 3]:
            sim_vals[col] = st.selectbox(col, ["Yes","No"],
                index=default_idx, key=f"sb_{col}")

# Fill any un-shown features with baseline
for col in feature_cols:
    if col not in sim_vals and col in df.columns:
        sim_vals[col] = base_vals.get(col, 0)

# ── Run Simulation ─────────────────────────────────────────────────────────────
divider()
run_btn = st.button("Run Simulation", type="primary")

if run_btn or st.session_state.get("sim_ran"):
    st.session_state["sim_ran"] = True

    try:
        # ── CLASSIFICATION: show probabilities ────────────────────────────────
        if task == "classification":
            base_proba = predict_proba_single(result, base_vals)
            sim_proba  = predict_proba_single(result, sim_vals)

            if base_proba is None or sim_proba is None:
                # Fallback to class labels if proba not available
                base_pred = predict_single(result, base_vals)
                sim_pred  = predict_single(result, sim_vals)
                section_label("Prediction Outcome")
                c1, c2 = st.columns(2)
                c1.metric("Baseline", str(base_pred))
                c2.metric("Simulated", str(sim_pred),
                          delta="Changed" if str(base_pred) != str(sim_pred) else "No change",
                          delta_color="normal" if str(base_pred) != str(sim_pred) else "off")
            else:
                classes = (target_encoder.classes_.tolist()
                           if target_encoder is not None
                           else [f"Class {i}" for i in range(len(base_proba))])

                section_label("Prediction Outcome — Class Probabilities")

                # Show a metric card per class
                n_classes = len(classes)
                prob_cols = st.columns(min(n_classes, 4))
                for i, cls in enumerate(classes[:4]):
                    b_pct  = round(base_proba[i] * 100, 2)
                    s_pct  = round(sim_proba[i]  * 100, 2)
                    delta  = round(s_pct - b_pct, 2)
                    with prob_cols[i % 4]:
                        st.metric(
                            label    = f"P({cls})",
                            value    = f"{s_pct:.1f}%",
                            delta    = f"{delta:+.2f}% vs baseline ({b_pct:.1f}%)",
                            delta_color = "normal" if delta >= 0 else "inverse",
                        )

                # Probability bar chart
                divider()
                section_label("Baseline vs Simulated Probabilities")
                import plotly.graph_objects as go
                fig = go.Figure(data=[
                    go.Bar(name="Baseline",  x=[str(c) for c in classes],
                           y=[round(p*100,2) for p in base_proba],
                           marker_color="#3A5278"),
                    go.Bar(name="Simulated", x=[str(c) for c in classes],
                           y=[round(p*100,2) for p in sim_proba],
                           marker_color="#00D4FF"),
                ])
                fig.update_layout(
                    barmode="group",
                    title="Class Probability Comparison (%)",
                    template="plotly_dark",
                    yaxis_title="Probability (%)",
                    height=350,
                    margin=dict(t=40, b=20, l=20, r=20),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Most likely class
                most_likely_base = classes[int(np.argmax(base_proba))]
                most_likely_sim  = classes[int(np.argmax(sim_proba))]
                if most_likely_base != most_likely_sim:
                    st.success(f"Prediction shifted: **{most_likely_base}** → **{most_likely_sim}**")
                else:
                    st.info(f"Most likely outcome remains **{most_likely_sim}** — probability distribution shifted.")

                st.session_state["scenario_summary"] = (
                    f"Classification probabilities: baseline={dict(zip(classes,[round(p*100,1) for p in base_proba]))}, "
                    f"simulated={dict(zip(classes,[round(p*100,1) for p in sim_proba]))}"
                )

        # ── REGRESSION: show predicted value ─────────────────────────────────
        else:
            baseline_pred  = predict_single(result, base_vals)
            simulated_pred = predict_single(result, sim_vals)
            delta     = simulated_pred - baseline_pred
            delta_pct = (delta / (abs(baseline_pred) + 1e-9)) * 100

            section_label("Prediction Outcome")
            c1, c2, c3 = st.columns(3)
            c1.metric("Baseline Prediction",  f"{baseline_pred:,.4f}")
            c2.metric("Simulated Prediction", f"{simulated_pred:,.4f}",
                      delta=f"{delta:+.4f}")
            c3.metric("Change", f"{delta_pct:+.2f}%")

            divider()
            section_label("Comparison Chart")
            st.plotly_chart(
                scenario_comparison(["Prediction"], [baseline_pred], [simulated_pred]),
                use_container_width=True,
            )

            st.session_state["scenario_summary"] = (
                f"Baseline={baseline_pred:.4f}, Simulated={simulated_pred:.4f}, "
                f"Change={delta:+.4f} ({delta_pct:+.2f}%)"
            )

        # ── Feature change summary (works for all types) ──────────────────────
        with st.expander("Feature Change Summary"):
            rows = []
            for col in feature_cols:
                bv = base_vals.get(col, "—")
                sv = sim_vals.get(col, "—")
                if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                    try:
                        dv = round(float(sv) - float(bv), 4)
                        pv = round((float(sv) - float(bv)) / (abs(float(bv)) + 1e-9) * 100, 2)
                    except Exception:
                        dv, pv = "—", "—"
                else:
                    dv = "changed" if str(bv) != str(sv) else "same"
                    pv = "—"
                rows.append({"Feature": col, "Baseline": bv,
                             "Simulated": sv, "Change": dv, "% Change": pv})
            st.dataframe(pd.DataFrame(rows), use_container_width=True)

    except Exception as e:
        st.error(f"Simulation error: {e}")
        st.caption("Try re-training the model in **AI Analyze** first.")

render_footer()
