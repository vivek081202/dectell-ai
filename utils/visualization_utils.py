"""
DecTell AI — Visualization Utilities
Reusable Plotly chart builders.
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


PLOTLY_TEMPLATE = "plotly_dark"


def histogram(df: pd.DataFrame, col: str) -> go.Figure:
    fig = px.histogram(
        df, x=col, nbins=40,
        title=f"Distribution of {col}",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#4FC3F7"],
    )
    fig.update_layout(bargap=0.05)
    return fig


def boxplot(df: pd.DataFrame, col: str) -> go.Figure:
    fig = px.box(
        df, y=col,
        title=f"Box Plot — {col}",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#81C784"],
    )
    return fig


def scatter(df: pd.DataFrame, x: str, y: str, color: str | None = None) -> go.Figure:
    fig = px.scatter(
        df, x=x, y=y, color=color,
        title=f"{y} vs {x}",
        template=PLOTLY_TEMPLATE,
        opacity=0.65,
    )
    return fig


def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    num_df = df.select_dtypes(include="number")
    corr   = num_df.corr()
    fig = px.imshow(
        corr,
        text_auto=".2f",
        title="Correlation Matrix",
        template=PLOTLY_TEMPLATE,
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
    )
    fig.update_layout(height=500)
    return fig


def bar_chart(df: pd.DataFrame, x: str, y: str, title: str = "") -> go.Figure:
    fig = px.bar(
        df, x=x, y=y,
        title=title or f"{y} by {x}",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#CE93D8"],
    )
    return fig


def line_chart(df: pd.DataFrame, x: str, y: str | list[str], title: str = "") -> go.Figure:
    fig = px.line(
        df, x=x, y=y,
        title=title or f"{y} over {x}",
        template=PLOTLY_TEMPLATE,
        markers=True,
    )
    return fig


def feature_importance_chart(features: list[str], importances: list[float]) -> go.Figure:
    sorted_pairs = sorted(zip(features, importances), key=lambda x: x[1])
    fig = go.Figure(go.Bar(
        x=[p[1] for p in sorted_pairs],
        y=[p[0] for p in sorted_pairs],
        orientation="h",
        marker_color="#FFB74D",
    ))
    fig.update_layout(
        title="Feature Importance",
        template=PLOTLY_TEMPLATE,
        height=max(300, len(features) * 28),
    )
    return fig


def actual_vs_predicted(y_actual, y_pred) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(range(len(y_actual))), y=y_actual,
        mode="lines", name="Actual", line=dict(color="#4FC3F7"),
    ))
    fig.add_trace(go.Scatter(
        x=list(range(len(y_pred))), y=y_pred,
        mode="lines", name="Predicted", line=dict(color="#FF8A65", dash="dash"),
    ))
    fig.update_layout(
        title="Actual vs Predicted",
        template=PLOTLY_TEMPLATE,
        xaxis_title="Sample Index",
        yaxis_title="Value",
    )
    return fig


def causal_before_after(
    before_vals, after_vals,
    before_label="Before", after_label="After",
    title="Before vs After Intervention",
) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Box(y=before_vals, name=before_label, marker_color="#EF9A9A"))
    fig.add_trace(go.Box(y=after_vals,  name=after_label,  marker_color="#A5D6A7"))
    fig.update_layout(title=title, template=PLOTLY_TEMPLATE)
    return fig


def value_counts_bar(series: pd.Series, top_n: int = 15) -> go.Figure:
    vc = series.value_counts().head(top_n).reset_index()
    vc.columns = ["Category", "Count"]
    fig = px.bar(
        vc, x="Category", y="Count",
        title=f"Value Distribution — {series.name}",
        template=PLOTLY_TEMPLATE,
        color_discrete_sequence=["#80CBC4"],
    )
    return fig


def scenario_comparison(labels: list[str], base_vals: list[float], sim_vals: list[float]) -> go.Figure:
    fig = go.Figure(data=[
        go.Bar(name="Baseline", x=labels, y=base_vals, marker_color="#78909C"),
        go.Bar(name="Simulated", x=labels, y=sim_vals, marker_color="#26C6DA"),
    ])
    fig.update_layout(
        barmode="group",
        title="Baseline vs Simulated Outcome",
        template=PLOTLY_TEMPLATE,
    )
    return fig
