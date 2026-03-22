"""
DecTell AI — AI Analyze Page
Two modes: Business Owners (non-technical) and Data Professionals (technical)
Both modes render LLM text report + rich contextual visualizations.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import collections

from utils.ui_utils import inject_global_css, page_header, section_label, divider, render_footer
from utils.data_utils import require_dataset, get_numeric_cols, set_model
from utils.model_utils import train_model, detect_task, get_model_options
from utils.visualization_utils import feature_importance_chart, actual_vs_predicted, PLOTLY_TEMPLATE
from utils.llm_utils import llm_detect_ml_task, llm_business_insights

inject_global_css()
page_header("Analysis", "AI Analyze",
    "Intelligent model training and insights — tailored for business owners and data professionals.")

df = require_dataset()
if df is None:
    render_footer()
    st.stop()

api_key  = st.session_state.get("groq_api_key", "")
num_cols = get_numeric_cols(df)
all_cols = df.columns.tolist()

if len(num_cols) < 2:
    st.error("Need at least 2 numeric columns to run analysis.")
    render_footer()
    st.stop()


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _is_id_col(series: pd.Series) -> bool:
    """Detect ID/key columns that should not be charted."""
    name = series.name.lower()
    if any(kw in name for kw in ["id", "uuid", "key", "index", "ref", "code"]):
        if series.nunique() / max(len(series), 1) > 0.85:
            return True
    return False

def _safe_float_list(arr) -> list:
    try:
        return [float(v) for v in arr]
    except Exception:
        return []

ACCENT   = "#00D4FF"
PURPLE   = "#7C3AED"
GREEN    = "#10B981"
AMBER    = "#F59E0B"
RED      = "#EF4444"
SURFACE  = "#1A2540"
MUTED    = "#6A88A8"
TEXT     = "#DDE8F8"
BORDER   = "#2C3F60"

PALETTE  = [ACCENT, PURPLE, GREEN, AMBER, RED, "#EC4899", "#14B8A6"]


# ══════════════════════════════════════════════════════════════════════════════
# BUSINESS VISUALS — plain-language charts for non-technical users
# ══════════════════════════════════════════════════════════════════════════════

def render_business_visuals(df: pd.DataFrame, result: dict, target: str):
    task       = result.get("task", "regression")
    importance = result.get("importance", {})
    y_test     = _safe_float_list(result.get("y_test", []))
    y_pred     = _safe_float_list(result.get("y_pred", []))
    metrics    = result.get("metrics", {})
    features   = result.get("feature_cols", [])

    clean_num = [c for c in num_cols
                 if c != target and c in df.columns and not _is_id_col(df[c])]

    section_label("Visual Intelligence")

    # ── 1. Top drivers + Target breakdown ──────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        if importance:
            top = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:8]
            labels = [k for k, _ in top]
            values = [round(v * 100, 1) for _, v in top]
            colors = [f"rgba(0,212,255,{0.4 + 0.6*(v/max(values))})" for v in values]

            fig = go.Figure(go.Bar(
                x=values, y=labels, orientation="h",
                marker=dict(color=colors, line=dict(color=ACCENT, width=0.5)),
                text=[f"{v}%" for v in values],
                textposition="outside",
                textfont=dict(color=TEXT, size=10),
            ))
            fig.update_layout(
                title=dict(text="What Drives the Outcome Most?",
                           font=dict(size=13, color=TEXT)),
                template=PLOTLY_TEMPLATE,
                height=320,
                margin=dict(l=10, r=55, t=48, b=10),
                xaxis=dict(showticklabels=False, showgrid=False, zeroline=False),
                yaxis=dict(tickfont=dict(size=10, color="#9BB5CF")),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Longer bar = stronger influence on the prediction.")

    with col_b:
        if target in df.columns:
            s = df[target].dropna()
            if task == "classification":
                vc = s.value_counts().reset_index()
                vc.columns = [target, "Count"]
                fig = px.pie(
                    vc, values="Count", names=target,
                    title=f"How '{target}' Is Distributed",
                    color_discrete_sequence=PALETTE,
                    hole=0.48,
                )
                fig.update_traces(
                    textinfo="percent+label",
                    textfont_size=11,
                    pull=[0.04] * len(vc),
                )
                fig.update_layout(
                    template=PLOTLY_TEMPLATE, height=320,
                    margin=dict(t=48, b=10, l=10, r=10),
                    showlegend=True,
                    legend=dict(font=dict(color="#9BB5CF", size=10)),
                    paper_bgcolor="rgba(0,0,0,0)",
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("Current split of outcomes in your dataset.")
            else:
                avg = s.mean()
                fig = px.histogram(
                    df, x=target, nbins=30,
                    title=f"Spread of '{target}'",
                    color_discrete_sequence=[ACCENT],
                )
                fig.add_vline(x=avg, line_dash="dash",
                              line_color=AMBER, line_width=1.5,
                              annotation_text=f"Avg: {avg:.2f}",
                              annotation_font_color=AMBER,
                              annotation_position="top right")
                fig.update_layout(
                    template=PLOTLY_TEMPLATE, height=320,
                    margin=dict(t=48, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis_title=target, yaxis_title="Count",
                )
                st.plotly_chart(fig, use_container_width=True)
                st.caption("How your outcome values are spread across records.")

    # ── 2. How top 3 drivers relate to the outcome ─────────────────────────
    if importance and target in df.columns:
        top3 = [k for k, _ in sorted(importance.items(),
                key=lambda x: x[1], reverse=True)
                if k in df.columns and not _is_id_col(df[k])][:3]

        if top3:
            st.markdown(f"""
<div style="font-size:0.72rem;font-weight:700;text-transform:uppercase;
     letter-spacing:0.12em;color:{MUTED};margin:1rem 0 0.5rem 0;">
    How the Top Drivers Relate to '{target}'
</div>""", unsafe_allow_html=True)
            rel_cols = st.columns(min(3, len(top3)))
            for rcol, feat in zip(rel_cols, top3):
                with rcol:
                    try:
                        if task == "classification":
                            fig = px.box(
                                df, x=target, y=feat,
                                color=target,
                                color_discrete_sequence=PALETTE,
                                title=feat,
                            )
                            fig.update_layout(
                                template=PLOTLY_TEMPLATE, height=260,
                                showlegend=False,
                                margin=dict(t=40, b=10, l=5, r=5),
                                paper_bgcolor="rgba(0,0,0,0)",
                                xaxis_title="", yaxis_title=feat,
                            )
                        else:
                            if pd.api.types.is_numeric_dtype(df[feat]):
                                fig = px.scatter(
                                    df.sample(min(400, len(df))),
                                    x=feat, y=target,
                                    trendline="ols",
                                    color_discrete_sequence=[ACCENT],
                                    trendline_color_override=AMBER,
                                    title=feat,
                                    opacity=0.55,
                                )
                                fig.update_layout(
                                    template=PLOTLY_TEMPLATE, height=260,
                                    margin=dict(t=40, b=10, l=5, r=5),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                )
                            else:
                                grp = df.groupby(feat)[target].mean().reset_index()
                                grp.columns = [feat, f"Avg {target}"]
                                fig = px.bar(
                                    grp, x=feat, y=f"Avg {target}",
                                    title=feat,
                                    color_discrete_sequence=[PURPLE],
                                )
                                fig.update_layout(
                                    template=PLOTLY_TEMPLATE, height=260,
                                    margin=dict(t=40, b=10, l=5, r=5),
                                    paper_bgcolor="rgba(0,0,0,0)",
                                )
                        st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        pass

    # ── 3. Model accuracy visual ───────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        if task == "regression" and y_test and y_pred:
            n = min(300, len(y_test))
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=y_test[:n], y=y_pred[:n], mode="markers",
                marker=dict(color=ACCENT, size=5, opacity=0.55),
                name="Predictions",
            ))
            mn, mx = min(y_test+y_pred), max(y_test+y_pred)
            fig.add_trace(go.Scatter(
                x=[mn, mx], y=[mn, mx], mode="lines",
                line=dict(color=AMBER, dash="dash", width=1.5),
                name="Perfect",
            ))
            r2 = metrics.get("R²", 0)
            fig.update_layout(
                title=dict(text=f"Predicted vs Actual  ({r2*100:.1f}% Accuracy)",
                           font=dict(size=12, color=TEXT)),
                template=PLOTLY_TEMPLATE, height=300,
                margin=dict(t=48, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Actual Value",
                yaxis_title="Predicted Value",
                legend=dict(font=dict(color="#9BB5CF", size=9)),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Points close to the yellow line = accurate predictions.")

        elif task == "classification":
            acc = metrics.get("Accuracy", 0)
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=round(acc * 100, 1),
                number=dict(suffix="%", font=dict(color=ACCENT, size=40)),
                title=dict(text="Model Accuracy", font=dict(color=TEXT, size=13)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor=MUTED,
                              tickfont=dict(color=MUTED)),
                    bar=dict(color=ACCENT),
                    bgcolor=SURFACE,
                    bordercolor=BORDER,
                    steps=[
                        dict(range=[0,  50], color="#131C2E"),
                        dict(range=[50, 75], color="#1A2540"),
                        dict(range=[75,100], color="#213050"),
                    ],
                    threshold=dict(
                        line=dict(color=AMBER, width=2),
                        thickness=0.8, value=75,
                    ),
                ),
            ))
            fig.update_layout(
                template=PLOTLY_TEMPLATE, height=300,
                margin=dict(t=30, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("75%+ is considered good. Yellow line = benchmark.")

    with col_d:
        if task == "regression" and y_test and y_pred:
            errors = [abs(p - a) for a, p in zip(y_test, y_pred)]
            fig = px.histogram(
                x=errors, nbins=25,
                color_discrete_sequence=[PURPLE],
                title="How Far Off Were Predictions?",
                labels={"x": "Prediction Error", "y": "Count"},
            )
            avg_err = np.mean(errors)
            fig.add_vline(x=avg_err, line_dash="dash",
                          line_color=AMBER, line_width=1.5,
                          annotation_text=f"Avg error: {avg_err:.2f}",
                          annotation_font_color=AMBER)
            fig.update_layout(
                template=PLOTLY_TEMPLATE, height=300,
                margin=dict(t=48, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Most errors should cluster near zero for a good model.")

        elif task == "classification" and y_test and y_pred:
            actual_c = dict(collections.Counter([str(v) for v in y_test]))
            pred_c   = dict(collections.Counter([str(v) for v in y_pred]))
            classes  = sorted(set(list(actual_c) + list(pred_c)))
            fig = go.Figure(data=[
                go.Bar(name="Actual",    x=classes,
                       y=[actual_c.get(c, 0) for c in classes],
                       marker_color=BORDER),
                go.Bar(name="Predicted", x=classes,
                       y=[pred_c.get(c, 0) for c in classes],
                       marker_color=ACCENT),
            ])
            fig.update_layout(
                barmode="group",
                title=dict(text="Actual vs Predicted Classes",
                           font=dict(size=12, color=TEXT)),
                template=PLOTLY_TEMPLATE, height=300,
                margin=dict(t=48, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                legend=dict(font=dict(color="#9BB5CF")),
            )
            st.plotly_chart(fig, use_container_width=True)
            st.caption("Predicted bars should closely match the actual bars.")

    # ── 4. Numeric trends explorer ─────────────────────────────────────────
    if clean_num:
        with st.expander("Explore Key Metric Trends", expanded=False):
            sel = st.multiselect(
                "Pick metrics to explore",
                clean_num,
                default=clean_num[:min(3, len(clean_num))],
                key="biz_trend",
            )
            if sel:
                t_cols = st.columns(min(3, len(sel)))
                for tc, col in zip(t_cols, sel):
                    with tc:
                        s = df[col].dropna()
                        fig = px.histogram(df, x=col, nbins=25,
                                           color_discrete_sequence=[GREEN],
                                           title=col)
                        fig.update_layout(
                            template=PLOTLY_TEMPLATE, height=200,
                            margin=dict(t=35, b=5, l=5, r=5),
                            paper_bgcolor="rgba(0,0,0,0)",
                            showlegend=False,
                            xaxis_title="", yaxis_title="",
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown(f"""
<div style="font-size:0.74rem;color:{MUTED};text-align:center;margin-top:-0.5rem;">
    Avg <strong style="color:{TEXT};">{s.mean():.2f}</strong> &nbsp;·&nbsp;
    Range <strong style="color:{TEXT};">{s.min():.2f}–{s.max():.2f}</strong>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TECHNICAL VISUALS — full analytical charts for data professionals
# ══════════════════════════════════════════════════════════════════════════════

def render_technical_visuals(df: pd.DataFrame, result: dict,
                              target: str, feature_cols: list):
    task       = result.get("task", "regression")
    importance = result.get("importance", {})
    y_test     = _safe_float_list(result.get("y_test", []))
    y_pred     = _safe_float_list(result.get("y_pred", []))
    metrics    = result.get("metrics", {})

    clean_num = [c for c in num_cols
                 if c != target and c in df.columns and not _is_id_col(df[c])]

    section_label("Model Visualizations")

    # ── Feature importance ─────────────────────────────────────────────────
    if importance:
        feats = list(importance.keys())
        imps  = list(importance.values())
        st.plotly_chart(feature_importance_chart(feats, imps),
                        use_container_width=True)

    # ── REGRESSION charts ──────────────────────────────────────────────────
    if task == "regression" and y_test and y_pred:
        r2   = metrics.get("R²",   0)
        mae  = metrics.get("MAE",  0)
        rmse = metrics.get("RMSE", 0)
        residuals = [p - a for a, p in zip(y_test, y_pred)]

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(actual_vs_predicted(y_test, y_pred),
                            use_container_width=True)
        with c2:
            # Residuals vs Fitted
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=y_pred, y=residuals, mode="markers",
                marker=dict(color=PURPLE, size=4, opacity=0.55),
                name="Residual",
            ))
            fig.add_hline(y=0, line_dash="dash",
                          line_color=AMBER, line_width=1.5)
            fig.update_layout(
                title=dict(text="Residuals vs Fitted Values",
                           font=dict(size=12, color=TEXT)),
                template=PLOTLY_TEMPLATE, height=320,
                margin=dict(t=48, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis_title="Fitted Values", yaxis_title="Residual",
            )
            st.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            # Residual distribution
            fig = px.histogram(x=residuals, nbins=30,
                               color_discrete_sequence=[GREEN],
                               title="Residual Distribution",
                               labels={"x": "Residual", "y": "Count"})
            fig.add_vline(x=0, line_dash="dash",
                          line_color=AMBER, line_width=1.5)
            fig.update_layout(
                template=PLOTLY_TEMPLATE, height=280,
                margin=dict(t=48, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with c4:
            # Metrics bar
            fig = go.Figure(go.Bar(
                x=["R²", "MAE", "RMSE"],
                y=[r2, mae, rmse],
                marker_color=[ACCENT, PURPLE, AMBER],
                text=[f"{r2:.4f}", f"{mae:.4f}", f"{rmse:.4f}"],
                textposition="outside",
                textfont=dict(color=TEXT, size=11),
            ))
            fig.update_layout(
                title=dict(text="Model Metrics Summary",
                           font=dict(size=12, color=TEXT)),
                template=PLOTLY_TEMPLATE, height=280,
                margin=dict(t=48, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
                yaxis=dict(showticklabels=False, showgrid=False),
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── CLASSIFICATION charts ──────────────────────────────────────────────
    elif task == "classification":
        acc = metrics.get("Accuracy", 0)

        c1, c2 = st.columns(2)
        with c1:
            # Accuracy gauge with delta vs 75% benchmark
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=round(acc * 100, 1),
                delta=dict(reference=75, valueformat=".1f",
                           increasing=dict(color=GREEN),
                           decreasing=dict(color=RED)),
                number=dict(suffix="%", font=dict(color=ACCENT, size=40)),
                title=dict(text="Classification Accuracy",
                           font=dict(color=TEXT, size=13)),
                gauge=dict(
                    axis=dict(range=[0, 100], tickcolor=MUTED,
                              tickfont=dict(color=MUTED)),
                    bar=dict(color=ACCENT),
                    bgcolor=SURFACE, bordercolor=BORDER,
                    steps=[
                        dict(range=[0,  50], color="#131C2E"),
                        dict(range=[50, 75], color="#1A2540"),
                        dict(range=[75,100], color="#213050"),
                    ],
                    threshold=dict(
                        line=dict(color=AMBER, width=2),
                        thickness=0.8, value=75),
                ),
            ))
            fig.update_layout(
                template=PLOTLY_TEMPLATE, height=300,
                margin=dict(t=30, b=10, l=10, r=10),
                paper_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig, use_container_width=True)

        with c2:
            if y_test and y_pred:
                actual_c = dict(collections.Counter([str(v) for v in y_test]))
                pred_c   = dict(collections.Counter([str(v) for v in y_pred]))
                classes  = sorted(set(list(actual_c) + list(pred_c)))
                fig = go.Figure(data=[
                    go.Bar(name="Actual",    x=classes,
                           y=[actual_c.get(c, 0) for c in classes],
                           marker_color=BORDER),
                    go.Bar(name="Predicted", x=classes,
                           y=[pred_c.get(c, 0) for c in classes],
                           marker_color=ACCENT),
                ])
                fig.update_layout(
                    barmode="group",
                    title=dict(text="Actual vs Predicted Class Distribution",
                               font=dict(size=12, color=TEXT)),
                    template=PLOTLY_TEMPLATE, height=300,
                    margin=dict(t=48, b=10, l=10, r=10),
                    paper_bgcolor="rgba(0,0,0,0)",
                    legend=dict(font=dict(color="#9BB5CF")),
                )
                st.plotly_chart(fig, use_container_width=True)

        # Per-class Precision / Recall / F1
        if "Report" in metrics:
            try:
                report  = metrics["Report"]
                rows    = {k: v for k, v in report.items()
                           if k not in ["accuracy","macro avg","weighted avg"]}
                if rows:
                    cls_names = list(rows.keys())
                    precision = [round(rows[c].get("precision", 0)*100, 1) for c in cls_names]
                    recall    = [round(rows[c].get("recall",    0)*100, 1) for c in cls_names]
                    f1        = [round(rows[c].get("f1-score",  0)*100, 1) for c in cls_names]

                    fig = go.Figure(data=[
                        go.Bar(name="Precision", x=cls_names, y=precision,
                               marker_color=ACCENT),
                        go.Bar(name="Recall",    x=cls_names, y=recall,
                               marker_color=PURPLE),
                        go.Bar(name="F1-Score",  x=cls_names, y=f1,
                               marker_color=GREEN),
                    ])
                    fig.update_layout(
                        barmode="group",
                        title=dict(text="Per-Class Precision / Recall / F1 (%)",
                                   font=dict(size=12, color=TEXT)),
                        template=PLOTLY_TEMPLATE, height=300,
                        margin=dict(t=48, b=10, l=10, r=10),
                        paper_bgcolor="rgba(0,0,0,0)",
                        yaxis_title="Score (%)",
                        legend=dict(font=dict(color="#9BB5CF")),
                    )
                    st.plotly_chart(fig, use_container_width=True)
            except Exception:
                pass

    # ── Feature correlation with target ───────────────────────────────────
    if (clean_num and target in df.columns
            and pd.api.types.is_numeric_dtype(df[target])):
        with st.expander("Feature Correlation with Target", expanded=False):
            corrs = []
            for col in clean_num:
                try:
                    c_val = df[col].corr(df[target])
                    if not np.isnan(c_val):
                        corrs.append((col, round(c_val, 4)))
                except Exception:
                    pass
            if corrs:
                corrs.sort(key=lambda x: abs(x[1]), reverse=True)
                corr_df = pd.DataFrame(corrs, columns=["Feature", "Correlation"])
                bar_colors = [ACCENT if v >= 0 else RED
                              for v in corr_df["Correlation"]]
                fig = go.Figure(go.Bar(
                    x=corr_df["Correlation"],
                    y=corr_df["Feature"],
                    orientation="h",
                    marker_color=bar_colors,
                    text=[f"{v:+.3f}" for v in corr_df["Correlation"]],
                    textposition="outside",
                    textfont=dict(color=TEXT, size=10),
                ))
                fig.add_vline(x=0, line_color=MUTED, line_width=1)
                fig.update_layout(
                    title=dict(text=f"Pearson Correlation with '{target}'",
                               font=dict(size=12, color=TEXT)),
                    template=PLOTLY_TEMPLATE,
                    height=max(260, len(corrs) * 30),
                    margin=dict(t=48, b=10, l=10, r=80),
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showticklabels=False, showgrid=False),
                )
                st.plotly_chart(fig, use_container_width=True)

    # ── Feature distributions (selected) ──────────────────────────────────
    if clean_num:
        with st.expander("Feature Distributions", expanded=False):
            sel = st.multiselect(
                "Select features",
                clean_num,
                default=clean_num[:min(4, len(clean_num))],
                key="tech_feat_dist",
            )
            if sel:
                cols_g = st.columns(min(4, len(sel)))
                for gc, feat in zip(cols_g, sel):
                    with gc:
                        s = df[feat].dropna()
                        skew = s.skew()
                        fig = px.histogram(df, x=feat, nbins=25,
                                           color_discrete_sequence=[PURPLE],
                                           title=feat)
                        fig.update_layout(
                            template=PLOTLY_TEMPLATE, height=220,
                            margin=dict(t=35, b=5, l=5, r=5),
                            paper_bgcolor="rgba(0,0,0,0)",
                            showlegend=False, xaxis_title="", yaxis_title="",
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        st.markdown(f"""
<div style="font-size:0.72rem;color:{MUTED};text-align:center;margin-top:-0.5rem;">
    Mean <b style="color:{TEXT};">{s.mean():.2f}</b> &nbsp;·&nbsp;
    Std <b style="color:{TEXT};">{s.std():.2f}</b> &nbsp;·&nbsp;
    Skew <b style="color:{AMBER if abs(skew)>1 else TEXT};">{skew:.2f}</b>
</div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# USER TYPE SELECTOR
# ══════════════════════════════════════════════════════════════════════════════
section_label("Select Your Profile")
user_type = st.radio(
    "",
    ["Business Owner / Decision Maker", "Data Analyst / Data Scientist"],
    horizontal=True,
    label_visibility="collapsed",
)
is_business = "Business" in user_type
divider()


# ══════════════════════════════════════════════════════════════════════════════
# BUSINESS OWNER MODE
# ══════════════════════════════════════════════════════════════════════════════
if is_business:
    section_label("Tell Us Your Business Goal")
    st.markdown("""
<p style="font-size:0.875rem;color:#6A88A8;margin-bottom:1rem;">
Describe what you want to understand or predict about your business in plain language.
Our AI will handle the technical analysis automatically.
</p>""", unsafe_allow_html=True)

    goal = st.text_area(
        "Your business goal",
        placeholder=(
            "Examples:\n"
            "• I want to understand which customers are likely to stop buying from us\n"
            "• I want to predict next month's revenue based on marketing spend\n"
            "• I want to know which products drive the most profit"
        ),
        height=120,
        label_visibility="collapsed",
    )

    run_btn = st.button("Analyze My Business Data", type="primary")

    if run_btn:
        if not goal.strip():
            st.error("Please describe your business goal above.")
        elif not api_key:
            st.warning("Add your Groq API key in the sidebar to enable AI analysis.")
        else:
            with st.spinner("AI is understanding your business goal…"):
                ml_config = llm_detect_ml_task(df, goal, api_key)

            if "error" in ml_config:
                st.error(f"AI could not parse your goal: {ml_config['error']}")
            else:
                target     = ml_config.get("target_column", "")
                features   = [c for c in ml_config.get("feature_columns", [])
                              if c in df.columns]
                model_name = ml_config.get("recommended_model", "Random Forest")
                task       = ml_config.get("task_type", "regression")
                reasoning  = ml_config.get("reasoning", "")
                biz_context= ml_config.get("business_context", "")

                st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-left:3px solid #10B981;
     border-radius:12px;padding:1rem 1.25rem;margin:1rem 0;">
    <div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;
         letter-spacing:0.12em;color:#10B981;margin-bottom:0.4rem;">AI Understanding</div>
    <div style="font-size:0.875rem;color:#9BB5CF;margin-bottom:0.5rem;">{reasoning}</div>
    <div style="font-size:0.82rem;color:#6A88A8;">Business context: {biz_context}</div>
</div>""", unsafe_allow_html=True)

                if not target or target not in df.columns:
                    st.error(f"AI suggested target '{target}' not found. Please rephrase.")
                elif not features:
                    st.error("AI could not identify feature columns. Please rephrase.")
                else:
                    with st.spinner(f"Training {model_name} model…"):
                        try:
                            result = train_model(df, features, target, model_name)
                            st.session_state["model_result"]   = result
                            st.session_state["model_target"]   = target
                            st.session_state["model_features"] = features
                            set_model(result["model"], features, target, model_name)
                        except Exception as e:
                            st.error(f"Model training failed: {e}")
                            render_footer()
                            st.stop()

                    with st.spinner("Generating business insights and recommendations…"):
                        biz_report = llm_business_insights(
                            df, result, "business", api_key,
                            extra_context=f"User goal: {goal}"
                        )
                        st.session_state["business_insights"] = biz_report

                    # ── Text report ────────────────────────────────────────
                    divider()
                    section_label("Business Intelligence Report")
                    st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:14px;
     padding:1.5rem 1.75rem;white-space:pre-wrap;font-size:0.9rem;
     color:#9BB5CF;line-height:1.8;">
{biz_report}
</div>""", unsafe_allow_html=True)

                    # ── Plain-English confidence metrics ───────────────────
                    divider()
                    section_label("Model Confidence")
                    metrics = result["metrics"]
                    if result["task"] == "regression":
                        r2 = metrics.get("R²", 0)
                        confidence = ("High" if r2 > 0.75
                                      else "Moderate" if r2 > 0.5 else "Low")
                        col1, col2 = st.columns(2)
                        col1.metric("Prediction Accuracy", f"{r2*100:.1f}%",
                                    delta=confidence + " confidence")
                        col2.metric("Average Prediction Error",
                                    f"±{metrics.get('MAE', 0):.2f} units")
                    else:
                        acc = metrics.get("Accuracy", 0)
                        col1, col2 = st.columns(2)
                        col1.metric("Classification Accuracy", f"{acc*100:.1f}%")
                        col2.metric("Records Analysed", f"{df.shape[0]:,}")

                    # ── Visualizations ─────────────────────────────────────
                    divider()
                    render_business_visuals(df, result, target)

    # Restore from session
    elif ("business_insights" in st.session_state
          and st.session_state.get("model_result")):
        result  = st.session_state["model_result"]
        target  = st.session_state.get("model_target", "")
        metrics = result["metrics"]

        divider()
        section_label("Business Intelligence Report")
        st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:14px;
     padding:1.5rem 1.75rem;white-space:pre-wrap;font-size:0.9rem;
     color:#9BB5CF;line-height:1.8;">
{st.session_state['business_insights']}
</div>""", unsafe_allow_html=True)

        divider()
        section_label("Model Confidence")
        if result["task"] == "regression":
            r2 = metrics.get("R²", 0)
            col1, col2 = st.columns(2)
            col1.metric("Prediction Accuracy", f"{r2*100:.1f}%")
            col2.metric("Average Error", f"±{metrics.get('MAE', 0):.2f} units")
        else:
            acc = metrics.get("Accuracy", 0)
            col1, col2 = st.columns(2)
            col1.metric("Classification Accuracy", f"{acc*100:.1f}%")
            col2.metric("Records Analysed", f"{df.shape[0]:,}")

        if target:
            divider()
            render_business_visuals(df, result, target)


# ══════════════════════════════════════════════════════════════════════════════
# TECHNICAL MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    section_label("Model Configuration")
    c1, c2 = st.columns(2)
    with c1:
        target_col = st.selectbox("Target Variable", all_cols, index=len(all_cols)-1)
    with c2:
        remaining    = [c for c in all_cols if c != target_col]
        feature_cols = st.multiselect(
            "Feature Columns", remaining,
            default=[c for c in num_cols if c != target_col][:8],
        )

    c3, c4, c5 = st.columns(3)
    with c3:
        task       = detect_task(df[target_col])
        model_opts = list(get_model_options(task).keys())
        model_name = st.selectbox("Algorithm", model_opts)
    with c4:
        test_size = st.slider("Test Split", 0.1, 0.4, 0.2, 0.05)
    with c5:
        st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
        st.markdown(f'<span class="stat-badge">Task: {task.capitalize()}</span>',
                    unsafe_allow_html=True)

    nl_goal = st.text_input(
        "Describe your goal (optional — AI will validate your config)",
        placeholder="e.g. Predict customer churn to improve retention"
    )

    train_btn = st.button("Train Model", type="primary")

    if train_btn:
        if not feature_cols:
            st.error("Select at least one feature column.")
        else:
            if nl_goal and api_key:
                with st.spinner("AI validating your configuration…"):
                    ml_config = llm_detect_ml_task(df, nl_goal, api_key)
                ai_target = ml_config.get("target_column", "")
                if ai_target and ai_target != target_col and ai_target in df.columns:
                    st.info(
                        f"AI suggests target: **{ai_target}** | "
                        f"You selected: **{target_col}** — proceeding with your selection."
                    )

            with st.spinner(f"Training {model_name}…"):
                try:
                    result = train_model(df, feature_cols, target_col,
                                         model_name, test_size)
                    st.session_state["model_result"]   = result
                    st.session_state["model_target"]   = target_col
                    st.session_state["model_features"] = feature_cols
                    set_model(result["model"], feature_cols, target_col, model_name)
                except Exception as e:
                    st.error(f"Training failed: {e}")
                    render_footer()
                    st.stop()

    result = st.session_state.get("model_result")
    if result:
        divider()
        section_label("Model Performance")
        metrics = result["metrics"]

        if result["task"] == "regression":
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

        # ── All technical visualizations ───────────────────────────────────
        divider()
        render_technical_visuals(
            df, result,
            target=st.session_state.get("model_target", target_col),
            feature_cols=st.session_state.get("model_features", feature_cols),
        )

        # ── LLM technical insights ─────────────────────────────────────────
        if api_key:
            if st.button("Generate Technical Insights", key="tech_insights_btn"):
                with st.spinner("Generating technical analysis…"):
                    tech_report = llm_business_insights(
                        df, result, "technical", api_key
                    )
                    st.session_state["technical_insights"] = tech_report

        if "technical_insights" in st.session_state:
            divider()
            section_label("Technical Analysis Report")
            st.markdown(f"""
<div style="background:#1A2540;border:1px solid #2C3F60;border-radius:14px;
     padding:1.5rem 1.75rem;white-space:pre-wrap;font-size:0.875rem;
     color:#9BB5CF;line-height:1.75;">
{st.session_state['technical_insights']}
</div>""", unsafe_allow_html=True)

render_footer()
