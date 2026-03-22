"""
DecTell AI — Causal Impact Analysis Page
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from utils.ui_utils import inject_global_css, render_footer, page_header, lottie_inline, section_label, divider
from utils.data_utils import require_dataset, get_numeric_cols
from modules.causal_analysis import did_estimate, regression_adjustment
from utils.visualization_utils import causal_before_after

inject_global_css()

page_header("Intelligence — Step 6", "Causal Impact Analysis",
            "Estimate true causal effects of interventions using DiD and regression adjustment methods.")

df = require_dataset()
if df is None:
    st.stop()

num_cols = get_numeric_cols(df)
all_cols = df.columns.tolist()

c_meth, c_anim = st.columns([3,1])
with c_anim:
    lottie_inline("causal", height=100)
with c_meth:
    section_label("Analysis Method")
    method = st.radio("", ["Difference-in-Differences (DiD)", "Regression Adjustment"],
                      horizontal=True, label_visibility="collapsed")

divider()

if method == "Difference-in-Differences (DiD)":
    st.markdown("""
<div style="background:#111827;border:1px solid #1E2D45;border-radius:12px;
     padding:1rem 1.25rem;font-size:0.85rem;color:#64748B;line-height:1.7;margin-bottom:1.5rem;">
    <strong style="color:#00D4FF;">DiD</strong> compares outcome changes for a treatment group vs a control group
    before and after an intervention to isolate the causal effect.<br>
    <code style="color:#00D4FF;">ATT = (Post_treated − Pre_treated) − (Post_control − Pre_control)</code>
</div>""", unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1: outcome_col   = st.selectbox("Outcome metric",       num_cols, index=0)
    with c2: treatment_col = st.selectbox("Treatment col (0/1)",  all_cols, index=min(1,len(all_cols)-1))
    with c3: period_col    = st.selectbox("Period column",        all_cols, index=min(2,len(all_cols)-1))

    uniq = df[period_col].dropna().unique().tolist()
    c4, c5 = st.columns(2)
    with c4: pre_value  = st.selectbox("Pre-period value",  uniq, index=0)
    with c5: post_value = st.selectbox("Post-period value", uniq, index=min(1,len(uniq)-1))

    if st.button("Run DiD Analysis", type="primary"):
        try:
            res = did_estimate(df, outcome_col, treatment_col, period_col, pre_value, post_value)
            st.session_state["causal_did"] = res
            divider()
            section_label("DiD Estimates")
            m1, m2, m3 = st.columns(3)
            m1.metric("ATT Estimate", f"{res['did_estimate']:.4f}" if res['did_estimate'] is not None else "—")
            m2.metric("95% CI Lower", f"{res['ci_lo']:.4f}" if res['ci_lo'] is not None else "—")
            m3.metric("95% CI Upper", f"{res['ci_hi']:.4f}" if res['ci_hi'] is not None else "—")

            st.markdown(f"""
<div style="background:#111827;border:1px solid #1E2D45;border-radius:12px;
     padding:1rem 1.25rem;font-size:0.85rem;color:#64748B;line-height:1.8;margin-top:1rem;">
    Pre-period: Treated = <code>{res['pre_treated']}</code>, Control = <code>{res['pre_control']}</code><br>
    Post-period: Treated = <code>{res['post_treated']}</code>, Control = <code>{res['post_control']}</code><br>
    <strong style="color:#94A3B8;">DiD = {res['did_estimate']}</strong>
    &nbsp;·&nbsp; 95% CI: [{res['ci_lo']}, {res['ci_hi']}]<br>
    <span style="color:#475569;">If CI excludes 0, the intervention had a statistically significant causal effect.</span>
</div>""", unsafe_allow_html=True)

            divider()
            section_label("Before vs After Distribution")
            c_l, c_r = st.columns(2)
            if res["pre_vals_treated"] and res["post_vals_treated"]:
                with c_l:
                    st.plotly_chart(causal_before_after(
                        res["pre_vals_treated"], res["post_vals_treated"],
                        "Pre (Treated)", "Post (Treated)", "Treatment Group"), use_container_width=True)
            if res["pre_vals_control"] and res["post_vals_control"]:
                with c_r:
                    st.plotly_chart(causal_before_after(
                        res["pre_vals_control"], res["post_vals_control"],
                        "Pre (Control)", "Post (Control)", "Control Group"), use_container_width=True)

            st.session_state["causal_summary"] = (
                f"DiD ATT={res['did_estimate']:.4f}, 95% CI [{res['ci_lo']:.4f}, {res['ci_hi']:.4f}].")
        except Exception as e:
            st.error(f"DiD failed: {e}")

else:
    st.markdown("""
<div style="background:#111827;border:1px solid #1E2D45;border-radius:12px;
     padding:1rem 1.25rem;font-size:0.85rem;color:#64748B;line-height:1.7;margin-bottom:1.5rem;">
    Controls for observed covariates to isolate the treatment effect via OLS.
    Model: <code style="color:#00D4FF;">outcome ~ treatment + covariates</code>
</div>""", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        outcome_col   = st.selectbox("Outcome metric",     num_cols, index=0)
        treatment_col = st.selectbox("Treatment col (0/1)",all_cols, index=min(1,len(all_cols)-1))
    with c2:
        covariate_cols = st.multiselect("Covariate columns",
            [c for c in num_cols if c != outcome_col],
            default=[c for c in num_cols if c != outcome_col][:3])

    if st.button("Run Regression Adjustment", type="primary"):
        if not covariate_cols:
            st.error("Select at least one covariate.")
        else:
            try:
                res = regression_adjustment(df, outcome_col, treatment_col, covariate_cols)
                divider()
                section_label("Regression Adjustment Estimates")
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Treatment Effect", f"{res['treatment_effect']:.4f}")
                m2.metric("95% CI Lower",     f"{res['ci_lo']:.4f}")
                m3.metric("95% CI Upper",     f"{res['ci_hi']:.4f}")
                m4.metric("R²",               f"{res['r_squared']:.4f}")

                st.markdown(f"""
<div style="background:#111827;border:1px solid #1E2D45;border-radius:12px;
     padding:1rem 1.25rem;font-size:0.85rem;color:#64748B;line-height:1.8;margin-top:1rem;">
    <strong style="color:#94A3B8;">{treatment_col}</strong> has an estimated effect of
    <code style="color:#00D4FF;">{res['treatment_effect']:.4f}</code> on
    <strong style="color:#94A3B8;">{outcome_col}</strong> controlling for:
    {", ".join(covariate_cols)}<br>
    95% CI: [{res['ci_lo']:.4f}, {res['ci_hi']:.4f}] &nbsp;·&nbsp; R² = {res['r_squared']:.4f}
</div>""", unsafe_allow_html=True)

                st.session_state["causal_summary"] = (
                    f"Reg adjustment: effect={res['treatment_effect']:.4f}, "
                    f"CI=[{res['ci_lo']:.4f},{res['ci_hi']:.4f}], R²={res['r_squared']:.4f}.")
            except Exception as e:
                st.error(f"Regression adjustment failed: {e}")
render_footer()
