"""
InsightFlow AI — Automated EDA Module
Generates insight summaries and statistical findings from cleaned data.
"""

import pandas as pd
import numpy as np


def generate_auto_insights(df: pd.DataFrame) -> list[str]:
    """
    Return a list of plain-English insight strings derived from the data.
    """
    insights = []
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # ── Dataset shape ─────────────────────────────────────────────────────────
    insights.append(
        f"📐 The dataset contains **{df.shape[0]:,} rows** and **{df.shape[1]} features**."
    )

    # ── Missing values ────────────────────────────────────────────────────────
    null_pct = df.isna().mean().mean() * 100
    if null_pct == 0:
        insights.append("✅ No missing values remain after cleaning.")
    else:
        most_null = df.isna().mean().idxmax()
        insights.append(
            f"⚠️ Overall missing rate: **{null_pct:.1f}%**. "
            f"Column **{most_null}** has the most nulls ({df[most_null].isna().mean()*100:.1f}%)."
        )

    # ── Correlation insights ───────────────────────────────────────────────────
    if len(num_cols) >= 2:
        corr = df[num_cols].corr().abs()
        np.fill_diagonal(corr.values, 0)
        max_val = corr.max().max()
        if max_val > 0.7:
            col_a = corr.stack().idxmax()[0]
            col_b = corr.stack().idxmax()[1]
            raw_corr = df[col_a].corr(df[col_b])
            direction = "positive" if raw_corr > 0 else "negative"
            insights.append(
                f"🔗 **Strong {direction} correlation** ({raw_corr:.2f}) between **{col_a}** and **{col_b}**."
            )
        elif max_val > 0.4:
            col_a = corr.stack().idxmax()[0]
            col_b = corr.stack().idxmax()[1]
            insights.append(
                f"🔗 Moderate correlation ({df[col_a].corr(df[col_b]):.2f}) between **{col_a}** and **{col_b}**."
            )

    # ── High skew ─────────────────────────────────────────────────────────────
    for col in num_cols:
        skew = df[col].skew()
        if abs(skew) > 2:
            direction = "right (positively)" if skew > 0 else "left (negatively)"
            insights.append(
                f"📊 **{col}** is heavily skewed {direction} (skew={skew:.2f}), "
                "suggesting outliers or a non-normal distribution."
            )

    # ── High cardinality categoricals ─────────────────────────────────────────
    for col in df.select_dtypes(include=["object"]).columns:
        n_unique = df[col].nunique()
        if n_unique > 50:
            insights.append(
                f"🗂️ **{col}** has **{n_unique}** unique values — consider grouping or encoding."
            )

    # ── Numeric summary extremes ───────────────────────────────────────────────
    if num_cols:
        most_variable = df[num_cols].std().idxmax()
        cv = df[most_variable].std() / (df[most_variable].mean() + 1e-9)
        if cv > 1:
            insights.append(
                f"📈 **{most_variable}** shows high variability (CV={cv:.2f}), "
                "indicating large spread relative to the mean."
            )

    return insights


def trend_analysis(df: pd.DataFrame) -> list[dict]:
    """
    Identify potential date/time columns and compute basic trends.
    Returns list of {col, trend, pct_change}.
    """
    results = []
    for col in df.columns:
        if any(kw in col.lower() for kw in ["date", "time", "year", "month", "week"]):
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().mean() > 0.8:
                    num_cols = df.select_dtypes(include="number").columns.tolist()
                    for nc in num_cols[:3]:
                        tmp = df.assign(_date=parsed).dropna(subset=["_date", nc])
                        tmp = tmp.sort_values("_date")
                        first_half = tmp[nc].iloc[: len(tmp) // 2].mean()
                        second_half = tmp[nc].iloc[len(tmp) // 2:].mean()
                        pct = ((second_half - first_half) / (first_half + 1e-9)) * 100
                        results.append({
                            "date_col": col,
                            "metric":   nc,
                            "trend":    "📈 Increasing" if pct > 2 else ("📉 Decreasing" if pct < -2 else "➡️ Stable"),
                            "pct_change": round(pct, 1),
                        })
            except Exception:
                pass
    return results
