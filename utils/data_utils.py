"""
DecTell AI — Data Utilities
Shared helpers for data loading, validation, and session state management.

IMPORTANT: Never use Python `or` / `and` / `not` / `if df:` on a DataFrame —
this raises ValueError in pandas. Always use `df is None` / `df is not None`.
"""

import io
import pandas as pd
import numpy as np
import streamlit as st


# ── Session-state helpers ──────────────────────────────────────────────────────

def get_raw_df() -> pd.DataFrame | None:
    """Return the raw uploaded DataFrame, or None if not set."""
    val = st.session_state.get("df_raw", None)
    return val if isinstance(val, pd.DataFrame) else None


def get_clean_df() -> pd.DataFrame | None:
    """Return the cleaned DataFrame, or None if not set."""
    val = st.session_state.get("df_clean", None)
    return val if isinstance(val, pd.DataFrame) else None


def set_raw_df(df: pd.DataFrame) -> None:
    st.session_state["df_raw"] = df


def set_clean_df(df: pd.DataFrame | None) -> None:
    st.session_state["df_clean"] = df


def get_model():
    return st.session_state.get("trained_model", None)


def set_model(model, feature_cols: list, target_col: str, model_name: str) -> None:
    st.session_state["trained_model"]  = model
    st.session_state["model_features"] = feature_cols
    st.session_state["model_target"]   = target_col
    st.session_state["model_name"]     = model_name


def get_model_meta() -> tuple:
    return (
        st.session_state.get("trained_model"),
        st.session_state.get("model_features"),
        st.session_state.get("model_target"),
        st.session_state.get("model_name"),
    )


# ── File loading ───────────────────────────────────────────────────────────────

@st.cache_data(show_spinner=False)
def load_file(file_bytes: bytes, file_name: str) -> pd.DataFrame:
    """Load CSV or Excel from raw bytes. Cached by content hash."""
    buf = io.BytesIO(file_bytes)
    ext = file_name.rsplit(".", 1)[-1].lower()
    if ext == "csv":
        return pd.read_csv(buf)
    elif ext in ("xlsx", "xls"):
        return pd.read_excel(buf)
    else:
        raise ValueError(f"Unsupported file format: .{ext}. Please upload CSV or Excel.")


# ── Dataset introspection ──────────────────────────────────────────────────────

def column_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Return a per-column summary: dtype, non-null count, null count/%, unique count."""
    rows = []
    for col in df.columns:
        rows.append({
            "Column":   col,
            "Dtype":    str(df[col].dtype),
            "Non-Null": int(df[col].notna().sum()),
            "Null":     int(df[col].isna().sum()),
            "Null %":   round(df[col].isna().mean() * 100, 1),
            "Unique":   int(df[col].nunique()),
        })
    return pd.DataFrame(rows)


def get_numeric_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include="number").columns.tolist()


def get_categorical_cols(df: pd.DataFrame) -> list[str]:
    return df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()


def require_dataset(allow_raw: bool = False) -> pd.DataFrame | None:
    """
    Returns the active DataFrame, or None with a warning if not loaded.

    Uses explicit `is None` checks — NEVER uses `or` on a DataFrame,
    which would raise: ValueError: The truth value of a DataFrame is ambiguous.
    """
    df = get_clean_df()                          # try cleaned first
    if df is None and allow_raw:                 # fall back to raw if allowed
        df = get_raw_df()
    if df is None:                               # nothing loaded at all
        st.warning("Please upload a dataset first via **Upload Dataset** in the sidebar.")
    return df                                    # caller checks `if df is None`


def validate_dataframe(df: pd.DataFrame) -> list[str]:
    """Return a list of human-readable validation warnings."""
    warnings: list[str] = []
    if df.empty:
        warnings.append("The uploaded dataset is empty.")
    if df.shape[1] < 2:
        warnings.append("The dataset has fewer than 2 columns.")
    null_pct = df.isna().mean().mean() * 100
    if null_pct > 50:
        warnings.append(f"The dataset has {null_pct:.1f}% missing values overall.")
    return warnings
