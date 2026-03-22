"""
InsightFlow AI — Causal Impact Analysis Module
Regression-based difference-in-difference estimation.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression


def did_estimate(
    df: pd.DataFrame,
    outcome_col: str,
    treatment_col: str,
    period_col: str,
    pre_value,
    post_value,
) -> dict:
    """
    Difference-in-Differences (DiD) estimator.
    Computes:
        ATT = (post_treated - pre_treated) - (post_control - pre_control)

    Parameters
    ----------
    df            : DataFrame
    outcome_col   : The metric being measured (e.g., 'sales')
    treatment_col : Binary column marking treatment group (1) vs control (0)
    period_col    : Column marking time period (pre/post split by pre_value → post_value)
    pre_value     : Value of period_col that indicates pre-period
    post_value    : Value of period_col that indicates post-period
    """
    pre  = df[df[period_col] == pre_value]
    post = df[df[period_col] == post_value]

    def mean_or_nan(sub, treat):
        vals = sub[sub[treatment_col] == treat][outcome_col].dropna()
        return vals.mean() if len(vals) else np.nan

    pre_treated   = mean_or_nan(pre,  1)
    pre_control   = mean_or_nan(pre,  0)
    post_treated  = mean_or_nan(post, 1)
    post_control  = mean_or_nan(post, 0)

    did = (post_treated - pre_treated) - (post_control - pre_control)

    # Bootstrap CI (1000 resamples)
    boot_dids = []
    rng = np.random.default_rng(42)
    for _ in range(1000):
        s = df.sample(len(df), replace=True, random_state=rng.integers(0, 1e6))
        pre_b  = s[s[period_col] == pre_value]
        post_b = s[s[period_col] == post_value]
        d = ((mean_or_nan(post_b, 1) - mean_or_nan(pre_b, 1)) -
             (mean_or_nan(post_b, 0) - mean_or_nan(pre_b, 0)))
        boot_dids.append(d)

    boot_dids = np.array([x for x in boot_dids if not np.isnan(x)])
    ci_lo = float(np.percentile(boot_dids, 2.5))  if len(boot_dids) else np.nan
    ci_hi = float(np.percentile(boot_dids, 97.5)) if len(boot_dids) else np.nan

    return {
        "pre_treated":   round(pre_treated,  4) if not np.isnan(pre_treated)  else None,
        "post_treated":  round(post_treated, 4) if not np.isnan(post_treated) else None,
        "pre_control":   round(pre_control,  4) if not np.isnan(pre_control)  else None,
        "post_control":  round(post_control, 4) if not np.isnan(post_control) else None,
        "did_estimate":  round(did,  4) if not np.isnan(did)  else None,
        "ci_lo":         round(ci_lo, 4) if not np.isnan(ci_lo) else None,
        "ci_hi":         round(ci_hi, 4) if not np.isnan(ci_hi) else None,
        "pre_vals_treated":  df[(df[period_col] == pre_value)  & (df[treatment_col] == 1)][outcome_col].dropna().tolist(),
        "post_vals_treated": df[(df[period_col] == post_value) & (df[treatment_col] == 1)][outcome_col].dropna().tolist(),
        "pre_vals_control":  df[(df[period_col] == pre_value)  & (df[treatment_col] == 0)][outcome_col].dropna().tolist(),
        "post_vals_control": df[(df[period_col] == post_value) & (df[treatment_col] == 0)][outcome_col].dropna().tolist(),
    }


def regression_adjustment(
    df: pd.DataFrame,
    outcome_col: str,
    treatment_col: str,
    covariate_cols: list[str],
) -> dict:
    """
    OLS regression adjustment: outcome ~ treatment + covariates
    Returns treatment coefficient and 95% CI (via analytic SE).
    """
    from numpy.linalg import pinv

    cols = [treatment_col] + covariate_cols
    df_sub = df[cols + [outcome_col]].dropna()

    X = df_sub[cols].values
    y = df_sub[outcome_col].values
    X = np.column_stack([np.ones(len(X)), X])   # add intercept

    beta    = pinv(X.T @ X) @ X.T @ y
    y_hat   = X @ beta
    resid   = y - y_hat
    n, p    = X.shape
    sigma2  = (resid ** 2).sum() / (n - p)
    var_beta = sigma2 * np.diag(pinv(X.T @ X))

    idx = 1  # treatment column is index 1
    coef  = beta[idx]
    se    = var_beta[idx] ** 0.5
    ci_lo = coef - 1.96 * se
    ci_hi = coef + 1.96 * se

    return {
        "treatment_effect": round(coef,  4),
        "ci_lo":            round(ci_lo, 4),
        "ci_hi":            round(ci_hi, 4),
        "std_error":        round(se,    4),
        "r_squared":        round(1 - (resid**2).sum() / ((y - y.mean())**2).sum(), 4),
    }
