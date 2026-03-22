"""
DecTell AI — Model Utilities
Train, evaluate, and cache ML models.

Key design: handles ANY dataset including those with categorical string columns,
date columns, high-cardinality text, ID columns — all safely encoded before training.
"""

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler, LabelEncoder, OrdinalEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    mean_absolute_error, mean_squared_error, r2_score,
    accuracy_score, classification_report,
)

try:
    from xgboost import XGBRegressor, XGBClassifier
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

# ── Task detection ─────────────────────────────────────────────────────────────

def detect_task(series: pd.Series) -> str:
    """Return 'regression' or 'classification' based on target column."""
    if series.dtype == "object" or series.nunique() <= 10:
        return "classification"
    return "regression"

# ── Model catalogue ────────────────────────────────────────────────────────────

def get_model_options(task: str) -> dict:
    opts = {}
    if task == "regression":
        opts["Linear Regression"] = LinearRegression()
        opts["Random Forest"]     = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        if XGBOOST_AVAILABLE:
            opts["XGBoost"] = XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    else:
        # class_weight='balanced' handles imbalanced datasets automatically —
        # prevents the model from always predicting the majority class.
        opts["Logistic Regression"] = LogisticRegression(
            max_iter=1000, random_state=42, class_weight="balanced"
        )
        opts["Random Forest"] = RandomForestClassifier(
            n_estimators=100, random_state=42, n_jobs=-1, class_weight="balanced"
        )
        if XGBOOST_AVAILABLE:
            # XGBoost uses scale_pos_weight instead of class_weight
            opts["XGBoost"] = XGBClassifier(
                n_estimators=100, random_state=42, verbosity=0,
                eval_metric="logloss", use_label_encoder=False
            )
    return opts

# ── Smart feature encoder ──────────────────────────────────────────────────────

def _is_id_column(series: pd.Series) -> bool:
    """Detect ID / key columns that should be dropped, not encoded."""
    name = series.name.lower()
    id_keywords = ["id", "uuid", "key", "index", "code", "no", "num", "ref", "pk"]
    if any(kw in name for kw in id_keywords):
        if series.nunique() / max(len(series), 1) > 0.85:
            return True
    return False

def _safe_encode_features(X: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """
    Encode a feature DataFrame so it contains only numeric values.
    Handles: string categoricals, booleans, dates, mixed types, nulls.

    Returns:
        X_encoded  — fully numeric DataFrame
        encoders   — dict of {col: encoder} for later inverse transform / predict
    """
    X = X.copy()
    encoders = {}

    for col in list(X.columns):
        series = X[col]

        # ── Drop ID-like columns ───────────────────────────────────────────────
        if _is_id_column(series):
            X = X.drop(columns=[col])
            encoders[col] = "__dropped_id__"
            continue

        # ── Parse date columns → numeric features ─────────────────────────────
        if series.dtype == "object":
            parsed = pd.to_datetime(series, errors="coerce")
            if parsed.notna().mean() > 0.7:
                X[col] = (parsed - pd.Timestamp("2000-01-01")).dt.days
                X[col] = X[col].fillna(X[col].median())
                encoders[col] = "__date_numeric__"
                continue

        # ── Numeric columns — just fill nulls ─────────────────────────────────
        if pd.api.types.is_numeric_dtype(series):
            X[col] = series.fillna(series.median())
            continue

        # ── Boolean / Yes-No → 0/1 ────────────────────────────────────────────
        if series.dtype == "object":
            lower_vals = series.dropna().str.lower().unique()
            if set(lower_vals).issubset({"yes", "no", "true", "false", "1", "0", "y", "n"}):
                mapping = {"yes": 1, "no": 0, "true": 1, "false": 0,
                           "y": 1, "n": 0, "1": 1, "0": 0}
                X[col] = series.str.lower().map(mapping).fillna(0).astype(int)
                encoders[col] = "__bool__"
                continue

        # ── Categorical string columns ─────────────────────────────────────────
        if series.dtype == "object" or str(series.dtype) == "category":
            n_unique = series.nunique()

            # Fill nulls with a placeholder before encoding
            X[col] = series.fillna("__missing__")

            if n_unique <= 15:
                # One-hot encode low-cardinality (≤15 unique values)
                dummies = pd.get_dummies(X[col], prefix=col, drop_first=False, dtype=int)
                X = X.drop(columns=[col])
                X = pd.concat([X, dummies], axis=1)
                encoders[col] = "__onehot__"
            else:
                # Label encode high-cardinality
                le = LabelEncoder()
                X[col] = le.fit_transform(X[col].astype(str))
                encoders[col] = le

    # Final safety: ensure all columns are numeric, coerce anything remaining
    for col in X.columns:
        if not pd.api.types.is_numeric_dtype(X[col]):
            X[col] = pd.to_numeric(X[col], errors="coerce").fillna(0)

    # Fill any remaining NaNs
    X = X.fillna(0)

    return X, encoders

def _encode_target(y: pd.Series, task: str) -> tuple[np.ndarray, LabelEncoder | None]:
    """Encode target column. For classification with string labels → LabelEncoder."""
    if task == "classification" and y.dtype == "object":
        le = LabelEncoder()
        y_enc = le.fit_transform(y.astype(str))
        return y_enc, le
    elif task == "regression":
        return y.values.astype(float), None
    else:
        return y.values, None

# ── Training pipeline ──────────────────────────────────────────────────────────

def train_model(
    df: pd.DataFrame,
    feature_cols: list[str],
    target_col: str,
    model_name: str,
    test_size: float = 0.2,
) -> dict:
    """
    Full train/test pipeline. Automatically encodes ANY column type:
    - String categoricals → one-hot (≤15 unique) or label encoded (>15)
    - Boolean Yes/No → 0/1
    - Date strings → days since epoch
    - ID columns → dropped automatically
    - Nulls → filled (median for numeric, '__missing__' for categorical)

    Returns dict with model, metrics, predictions, feature importance, encoders.
    """
    # Only keep columns that actually exist
    valid_features = [c for c in feature_cols if c in df.columns]
    if not valid_features:
        raise ValueError("None of the selected feature columns exist in the dataset.")

    X_raw = df[valid_features].copy()
    y_raw = df[target_col].copy()

    # Drop rows where target is null
    valid_mask = y_raw.notna()
    X_raw = X_raw[valid_mask].reset_index(drop=True)
    y_raw = y_raw[valid_mask].reset_index(drop=True)

    if len(X_raw) < 20:
        raise ValueError(f"Too few valid rows ({len(X_raw)}) after removing nulls in target.")

    # Detect task type from raw target (before encoding)
    task = detect_task(y_raw)

    # Encode features
    X_encoded, encoders = _safe_encode_features(X_raw)
    encoded_feature_names = list(X_encoded.columns)

    # Encode target
    y_encoded, target_encoder = _encode_target(y_raw, task)

    # Get model
    models = get_model_options(task)
    if model_name not in models:
        # Fallback to Random Forest if requested model isn't available
        model_name = "Random Forest"
    model = models[model_name]

    # Scale for linear models
    scaler = None
    if "Linear" in model_name or "Logistic" in model_name:
        scaler = StandardScaler()
        X_final = scaler.fit_transform(X_encoded)
    else:
        X_final = X_encoded.values

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_final, y_encoded, test_size=test_size, random_state=42
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    # Metrics
    if task == "regression":
        metrics = {
            "MAE":  round(float(mean_absolute_error(y_test, y_pred)), 4),
            "RMSE": round(float(mean_squared_error(y_test, y_pred) ** 0.5), 4),
            "R²":   round(float(r2_score(y_test, y_pred)), 4),
        }
        y_proba_test = None
    else:
        metrics = {
            "Accuracy": round(float(accuracy_score(y_test, y_pred)), 4),
            "Report":   classification_report(y_test, y_pred, output_dict=True,
                                              zero_division=0),
        }
        # Store probabilities for simulation — gives continuous output per slider change
        try:
            y_proba_test = model.predict_proba(X_test)
        except Exception:
            y_proba_test = None

    # Feature importance — map back to original column names where possible
    importance = None
    if hasattr(model, "feature_importances_"):
        raw_imp = dict(zip(encoded_feature_names, model.feature_importances_.tolist()))
        # Aggregate one-hot columns back to original column name
        aggregated = {}
        for enc_col, imp_val in raw_imp.items():
            # One-hot cols look like "Original_Value" — find original col
            original = None
            for orig in valid_features:
                if enc_col.startswith(orig + "_") or enc_col == orig:
                    original = orig
                    break
            key = original if original else enc_col
            aggregated[key] = aggregated.get(key, 0) + imp_val
        importance = {k: round(v, 6) for k, v in
                      sorted(aggregated.items(), key=lambda x: x[1], reverse=True)}

    elif hasattr(model, "coef_"):
        coefs = model.coef_.flatten() if model.coef_.ndim > 1 else model.coef_
        importance = dict(zip(encoded_feature_names, np.abs(coefs).tolist()))

    # Decode y_test labels for display if target was encoded
    y_test_display = y_test
    y_pred_display = y_pred
    if target_encoder is not None:
        try:
            y_test_display = target_encoder.inverse_transform(y_test.astype(int))
            y_pred_display = target_encoder.inverse_transform(
                np.clip(y_pred.astype(int), 0, len(target_encoder.classes_) - 1)
            )
        except Exception:
            pass

    return {
        "model":          model,
        "scaler":         scaler,
        "encoders":       encoders,
        "target_encoder": target_encoder,
        "task":           task,
        "model_name":     model_name,
        "metrics":        metrics,
        "y_test":         y_test_display,
        "y_pred":         y_pred_display,
        "y_proba":        y_proba_test,
        "importance":     importance,
        "feature_cols":   valid_features,
        "encoded_feature_names": encoded_feature_names,
        "target_col":     target_col,
        "n_samples":      len(X_raw),
        "encoding_summary": {k: ("dropped" if v == "__dropped_id__"
                                 else "one-hot" if v == "__onehot__"
                                 else "bool" if v == "__bool__"
                                 else "date→numeric" if v == "__date_numeric__"
                                 else "label-encoded")
                             for k, v in encoders.items()},
    }

# ── Prediction helper ──────────────────────────────────────────────────────────

def predict_single(result: dict, input_values: dict) -> float:
    """
    Predict for a single dict of {feature: value}.
    Handles the same encoding that was applied during training.
    """
    model   = result["model"]
    scaler  = result["scaler"]
    cols    = result["encoded_feature_names"]

    # Build a single-row DataFrame matching original features, then re-encode
    orig_cols = result["feature_cols"]
    row_df = pd.DataFrame([{c: input_values.get(c, None) for c in orig_cols}])

    # Apply the same encoding
    X_enc, _ = _safe_encode_features(row_df)

    # Align columns to training schema — add missing cols as 0, drop extra
    for c in cols:
        if c not in X_enc.columns:
            X_enc[c] = 0
    X_enc = X_enc[[c for c in cols if c in X_enc.columns]]

    # Pad if any columns still missing
    if X_enc.shape[1] < len(cols):
        for c in cols:
            if c not in X_enc.columns:
                X_enc[c] = 0
        X_enc = X_enc[cols]

    if scaler:
        X_final = scaler.transform(X_enc)
    else:
        X_final = X_enc.values

    pred = model.predict(X_final)
    return float(pred[0])


def predict_proba_single(result: dict, input_values: dict) -> list[float] | None:
    """
    Return class probabilities [p_class0, p_class1, ...] for classification models.
    Returns None for regression models or if model doesn't support predict_proba.
    This gives CONTINUOUS output for sliders — unlike predict() which only flips
    at decision boundaries, making sliders appear to do nothing.
    """
    model = result["model"]
    if not hasattr(model, "predict_proba"):
        return None
    if result.get("task") != "classification":
        return None

    scaler = result["scaler"]
    cols   = result["encoded_feature_names"]
    orig_cols = result["feature_cols"]

    row_df = pd.DataFrame([{c: input_values.get(c, None) for c in orig_cols}])
    X_enc, _ = _safe_encode_features(row_df)

    for c in cols:
        if c not in X_enc.columns:
            X_enc[c] = 0
    X_enc = X_enc[[c for c in cols if c in X_enc.columns]]
    if X_enc.shape[1] < len(cols):
        for c in cols:
            if c not in X_enc.columns:
                X_enc[c] = 0
        X_enc = X_enc[cols]

    if scaler:
        X_final = scaler.transform(X_enc)
    else:
        X_final = X_enc.values

    try:
        proba = model.predict_proba(X_final)
        return proba[0].tolist()
    except Exception:
        return None
