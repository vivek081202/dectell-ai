"""
DecTell AI — Chat Utilities
Translate natural-language queries into dataframe operations and insights.
"""

import re
import pandas as pd
import numpy as np


# ── Intent patterns ────────────────────────────────────────────────────────────

_PATTERNS = [
    # group-by aggregations
    (r"(highest|largest|most|maximum|max|top)\s+(\w+)\s+by\s+(\w+)",          "max_by"),
    (r"(lowest|smallest|least|minimum|min|bottom)\s+(\w+)\s+by\s+(\w+)",      "min_by"),
    (r"(average|mean|avg)\s+(\w+)\s+by\s+(\w+)",                              "avg_by"),
    (r"(total|sum)\s+(\w+)\s+by\s+(\w+)",                                     "sum_by"),
    # correlation
    (r"correlation\s+between\s+(\w+)\s+and\s+(\w+)",                         "correlation"),
    # top N
    (r"top\s+(\d+)\s+(\w+)",                                                  "top_n"),
    # describe / stats
    (r"(describe|statistics|summary|stats)\s+(?:of\s+|for\s+)?(\w+)?",        "describe"),
    # missing values
    (r"missing|null|na\s+values?",                                             "missing"),
    # distribution
    (r"distribution\s+of\s+(\w+)",                                            "distribution"),
    # count rows
    (r"how\s+many\s+rows|row\s+count|shape",                                  "shape"),
    # columns
    (r"columns?|features?|fields?",                                            "columns"),
    # value counts
    (r"unique\s+values?\s+(?:of\s+|in\s+)?(\w+)",                            "value_counts"),
    # filter
    (r"where\s+(\w+)\s*(==|>|<|>=|<=)\s*([^\s]+)",                           "filter"),
    # generic search
    (r"(\w+)",                                                                 "generic"),
]


def _find_col(df: pd.DataFrame, token: str) -> str | None:
    """Case-insensitive fuzzy column matcher."""
    token_l = token.lower()
    for col in df.columns:
        if token_l == col.lower():
            return col
    for col in df.columns:
        if token_l in col.lower():
            return col
    return None


# ── Query processor ────────────────────────────────────────────────────────────

def process_query(df: pd.DataFrame, query: str) -> dict:
    """
    Parse a natural-language query and return:
        {
            "text":    str explanation,
            "table":   pd.DataFrame | None,
            "chart":   str | None,   # column name for auto-chart
            "chart_x": str | None,
            "chart_y": str | None,
            "chart_type": "bar"|"line"|"histogram"|"scatter" | None,
        }
    """
    q = query.lower().strip()
    result = {"text": "", "table": None, "chart_x": None, "chart_y": None, "chart_type": None}

    # ── missing values ─────────────────────────────────────────────────────────
    if re.search(r"missing|null|na\s*value", q):
        mv = df.isna().sum().reset_index()
        mv.columns = ["Column", "Missing"]
        mv = mv[mv["Missing"] > 0].sort_values("Missing", ascending=False)
        if mv.empty:
            result["text"] = "✅ No missing values found in the dataset."
        else:
            result["text"]  = f"Found **{mv['Missing'].sum()}** missing values across {len(mv)} columns."
            result["table"] = mv
        return result

    # ── shape ─────────────────────────────────────────────────────────────────
    if re.search(r"how\s+many\s+rows|row\s+count|shape", q):
        result["text"] = f"The dataset has **{df.shape[0]:,} rows** and **{df.shape[1]} columns**."
        return result

    # ── columns ───────────────────────────────────────────────────────────────
    if re.search(r"\bcolumns?\b|\bfeatures?\b|\bfields?\b", q):
        result["text"]  = f"The dataset has **{df.shape[1]} columns**:\n\n" + ", ".join(f"`{c}`" for c in df.columns)
        return result

    # ── correlation ───────────────────────────────────────────────────────────
    m = re.search(r"correlation\s+between\s+(\w+)\s+and\s+(\w+)", q)
    if m:
        c1 = _find_col(df, m.group(1))
        c2 = _find_col(df, m.group(2))
        if c1 and c2:
            corr = df[c1].corr(df[c2])
            strength = (
                "strong positive" if corr > 0.6 else
                "moderate positive" if corr > 0.3 else
                "strong negative" if corr < -0.6 else
                "moderate negative" if corr < -0.3 else "weak"
            )
            result["text"]      = f"Correlation between **{c1}** and **{c2}**: **{corr:.3f}** ({strength} correlation)."
            result["chart_x"]   = c1
            result["chart_y"]   = c2
            result["chart_type"] = "scatter"
        else:
            result["text"] = f"⚠️ Could not match columns from query: '{m.group(1)}', '{m.group(2)}'."
        return result

    # ── top N ─────────────────────────────────────────────────────────────────
    m = re.search(r"top\s+(\d+)\s+(\w+)", q)
    if m:
        n   = int(m.group(1))
        col = _find_col(df, m.group(2))
        if col and col in df.select_dtypes(include="number").columns:
            top = df.nlargest(n, col)[[col] + [c for c in df.columns if c != col][:3]]
            result["text"]  = f"Top **{n}** rows by **{col}**:"
            result["table"] = top
            result["chart_x"]   = df.columns[0]
            result["chart_y"]   = col
            result["chart_type"] = "bar"
        elif col:
            vc = df[col].value_counts().head(n).reset_index()
            vc.columns = [col, "Count"]
            result["text"]  = f"Top **{n}** values in **{col}**:"
            result["table"] = vc
            result["chart_x"]   = col
            result["chart_y"]   = "Count"
            result["chart_type"] = "bar"
        else:
            result["text"] = f"⚠️ Column '{m.group(2)}' not found."
        return result

    # ── aggregation by group ───────────────────────────────────────────────────
    for pat, intent in [
        (r"(highest|largest|most|max|top)\s+(\w+)\s+by\s+(\w+)",     "max"),
        (r"(lowest|smallest|least|min|bottom)\s+(\w+)\s+by\s+(\w+)", "min"),
        (r"(average|mean|avg)\s+(\w+)\s+by\s+(\w+)",                 "mean"),
        (r"(total|sum)\s+(\w+)\s+by\s+(\w+)",                        "sum"),
    ]:
        m = re.search(pat, q)
        if m:
            val_col  = _find_col(df, m.group(2))
            grp_col  = _find_col(df, m.group(3))
            if val_col and grp_col and val_col in df.select_dtypes(include="number").columns:
                grp = df.groupby(grp_col)[val_col].agg(intent).reset_index().sort_values(val_col, ascending=(intent=="min"))
                result["text"]      = f"**{intent.capitalize()} of {val_col}** grouped by **{grp_col}**:"
                result["table"]     = grp
                result["chart_x"]   = grp_col
                result["chart_y"]   = val_col
                result["chart_type"] = "bar"
            else:
                result["text"] = f"⚠️ Could not resolve columns in query."
            return result

    # ── distribution ──────────────────────────────────────────────────────────
    m = re.search(r"distribution\s+of\s+(\w+)", q)
    if m:
        col = _find_col(df, m.group(1))
        if col:
            result["text"]      = f"Distribution of **{col}**:"
            result["chart_x"]   = col
            result["chart_type"] = "histogram"
        else:
            result["text"] = f"⚠️ Column '{m.group(1)}' not found."
        return result

    # ── value counts ──────────────────────────────────────────────────────────
    m = re.search(r"unique\s+values?\s+(?:of\s+|in\s+)?(\w+)", q)
    if m:
        col = _find_col(df, m.group(1))
        if col:
            vc = df[col].value_counts().reset_index()
            vc.columns = [col, "Count"]
            result["text"]  = f"**{df[col].nunique()}** unique values in **{col}**:"
            result["table"] = vc
        else:
            result["text"] = f"⚠️ Column '{m.group(1)}' not found."
        return result

    # ── describe ──────────────────────────────────────────────────────────────
    if re.search(r"\bdescribe\b|\bstatistics\b|\bsummary\b|\bstats\b", q):
        # Check if a column is mentioned
        for col in df.columns:
            if col.lower() in q:
                result["text"]  = f"Statistics for **{col}**:"
                result["table"] = df[col].describe().reset_index().rename(columns={"index": "Stat", col: "Value"})
                return result
        result["text"]  = "Dataset summary statistics:"
        result["table"] = df.describe().T.reset_index().rename(columns={"index": "Column"})
        return result

    # ── generic column mention ─────────────────────────────────────────────────
    for col in df.columns:
        if col.lower() in q:
            if col in df.select_dtypes(include="number").columns:
                desc = df[col].describe()
                result["text"] = (
                    f"**{col}** — mean: `{desc['mean']:.2f}`, "
                    f"std: `{desc['std']:.2f}`, "
                    f"min: `{desc['min']:.2f}`, max: `{desc['max']:.2f}`."
                )
                result["chart_x"]   = col
                result["chart_type"] = "histogram"
            else:
                vc = df[col].value_counts().head(10).reset_index()
                vc.columns = [col, "Count"]
                result["text"]  = f"Top values in **{col}**:"
                result["table"] = vc
                result["chart_x"]   = col
                result["chart_y"]   = "Count"
                result["chart_type"] = "bar"
            return result

    # ── fallback ───────────────────────────────────────────────────────────────
    result["text"] = (
        "I couldn't understand that query precisely. Try asking:\n\n"
        "- *Which region has the highest sales?*\n"
        "- *Show distribution of price*\n"
        "- *Correlation between age and income*\n"
        "- *Top 5 products by revenue*\n"
        "- *Describe churn*\n"
        "- *Missing values*"
    )
    return result
