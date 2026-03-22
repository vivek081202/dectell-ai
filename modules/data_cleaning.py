"""
InsightFlow AI — Data Cleaning & Transformation Module
Full automated preprocessing pipeline with transparency log.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler


def run_cleaning_pipeline(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Run the full cleaning pipeline on df.
    Returns (cleaned_df, log_of_transformations).
    Non-destructive: works on a copy.
    """
    df   = df.copy()
    log  = []
    orig_shape = df.shape

    # ── 1. Remove duplicate rows ───────────────────────────────────────────────
    n_dups = df.duplicated().sum()
    if n_dups:
        df.drop_duplicates(inplace=True)
        df.reset_index(drop=True, inplace=True)
        log.append(f"🗑️ Removed **{n_dups}** duplicate rows.")

    # ── 2. Data type corrections ───────────────────────────────────────────────
    for col in df.columns:
        if df[col].dtype == "object":
            # Try numeric coercion
            converted = pd.to_numeric(df[col], errors="coerce")
            null_before = df[col].isna().sum()
            null_after  = converted.isna().sum()
            # Accept conversion only if it doesn't introduce >10% new nulls
            if (null_after - null_before) / len(df) < 0.10 and converted.notna().sum() > 0:
                non_numeric_orig = df[col].dropna()
                actually_numeric = pd.to_numeric(non_numeric_orig, errors="coerce").notna().mean()
                if actually_numeric > 0.8:
                    df[col] = converted
                    log.append(f"🔢 Converted **{col}** to numeric.")

    # ── 3. Missing value imputation ────────────────────────────────────────────
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    for col in num_cols:
        n_null = df[col].isna().sum()
        if n_null:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            log.append(f"📊 Imputed **{n_null}** nulls in **{col}** with median ({median_val:.2f}).")

    for col in cat_cols:
        n_null = df[col].isna().sum()
        if n_null:
            mode_val = df[col].mode()[0] if not df[col].mode().empty else "Unknown"
            df[col] = df[col].fillna(mode_val)
            log.append(f"🔤 Imputed **{n_null}** nulls in **{col}** with mode ('{mode_val}').")

    # ── 4. Outlier handling (IQR cap) ─────────────────────────────────────────
    for col in num_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        n_out = ((df[col] < lower) | (df[col] > upper)).sum()
        if n_out:
            df[col] = df[col].clip(lower, upper)
            log.append(f"📌 Capped **{n_out}** outliers in **{col}** to IQR bounds [{lower:.2f}, {upper:.2f}].")

    # ── 5. Feature encoding ────────────────────────────────────────────────────
    cat_cols_after = df.select_dtypes(include=["object", "category"]).columns.tolist()
    for col in cat_cols_after:
        n_unique = df[col].nunique()
        if n_unique == 2:
            # Label encode binary
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            log.append(f"🏷️ Label-encoded binary column **{col}**.")
        elif 2 < n_unique <= 10:
            # One-hot encode low-cardinality
            dummies = pd.get_dummies(df[col], prefix=col, drop_first=True, dtype=int)
            df = pd.concat([df.drop(columns=[col]), dummies], axis=1)
            log.append(f"🔀 One-hot encoded **{col}** ({n_unique} categories → {len(dummies.columns)} cols).")
        else:
            # Label encode high-cardinality
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col].astype(str))
            log.append(f"🏷️ Label-encoded high-cardinality column **{col}** ({n_unique} unique values).")

    log.insert(0, f"📐 Shape: {orig_shape[0]} × {orig_shape[1]}  →  {df.shape[0]} × {df.shape[1]}")
    return df, log


def get_cleaning_summary(df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict:
    """Return a dict of summary stats comparing before and after."""
    return {
        "rows_before":    df_before.shape[0],
        "rows_after":     df_after.shape[0],
        "cols_before":    df_before.shape[1],
        "cols_after":     df_after.shape[1],
        "nulls_before":   int(df_before.isna().sum().sum()),
        "nulls_after":    int(df_after.isna().sum().sum()),
        "dups_before":    int(df_before.duplicated().sum()),
        "dups_after":     int(df_after.duplicated().sum()),
    }
