"""
InsightFlow AI — Report Generator
Builds text and PDF-ready reports from session state artifacts.
"""

import io
import datetime
import pandas as pd


def build_text_report(
    dataset_name: str,
    df: pd.DataFrame,
    insights: list[str],
    model_result: dict | None,
    scenario_summary: str | None,
    causal_summary: str | None,
) -> str:
    """
    Generate a structured plain-text business analytics report.
    """
    now   = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []

    def h1(text): lines.append(f"\n{'='*70}\n{text}\n{'='*70}")
    def h2(text): lines.append(f"\n{'-'*50}\n{text}\n{'-'*50}")
    def para(text): lines.append(text)

    h1("INSIGHTFLOW AI — BUSINESS ANALYTICS REPORT")
    para(f"Generated : {now}")
    para(f"Dataset   : {dataset_name}")
    para(f"Shape     : {df.shape[0]:,} rows × {df.shape[1]} columns")

    # ── EDA Insights ──────────────────────────────────────────────────────────
    h2("1. KEY AUTOMATED INSIGHTS")
    for ins in insights:
        clean = ins.replace("**", "").replace("📊", "").replace("🔗", "").replace(
            "📐", "").replace("✅", "").replace("⚠️", "").replace("📈", "").replace("📉", "")
        para(f"  • {clean.strip()}")

    # ── Descriptive Stats ─────────────────────────────────────────────────────
    h2("2. DESCRIPTIVE STATISTICS (Numeric Columns)")
    num_df = df.select_dtypes(include="number")
    if not num_df.empty:
        desc = num_df.describe().round(3)
        para(desc.to_string())

    # ── Missing Values ────────────────────────────────────────────────────────
    h2("3. DATA QUALITY")
    null_counts = df.isna().sum()
    null_pct    = (null_counts / len(df) * 100).round(2)
    dq = pd.DataFrame({"Missing": null_counts, "Missing %": null_pct})
    dq = dq[dq["Missing"] > 0]
    if dq.empty:
        para("  No missing values detected.")
    else:
        para(dq.to_string())

    # ── Correlations ──────────────────────────────────────────────────────────
    h2("4. TOP CORRELATIONS")
    if num_df.shape[1] >= 2:
        corr = num_df.corr().abs()
        import numpy as _np
        pairs = (
            corr.where(~_np.eye(len(corr), dtype=bool))
            .stack()
            .sort_values(ascending=False)
            .head(5)
        )
        for (c1, c2), val in pairs.items():
            raw = df[c1].corr(df[c2])
            para(f"  • {c1} ↔ {c2} : {raw:.3f}")
    else:
        para("  Insufficient numeric columns for correlation analysis.")

    # ── ML Model Results ──────────────────────────────────────────────────────
    if model_result:
        h2("5. PREDICTIVE MODEL RESULTS")
        para(f"  Model     : {model_result.get('model_name', 'N/A')}")
        para(f"  Target    : {model_result.get('target_col', 'N/A')}")
        para(f"  Task      : {model_result.get('task', 'N/A')}")
        para("  Metrics:")
        for k, v in model_result.get("metrics", {}).items():
            if k != "Report":
                para(f"    {k}: {v}")
        if model_result.get("importance"):
            para("\n  Feature Importances (top 5):")
            imp = sorted(model_result["importance"].items(), key=lambda x: x[1], reverse=True)[:5]
            for feat, score in imp:
                para(f"    {feat}: {score:.4f}")

    # ── Scenario Simulation ───────────────────────────────────────────────────
    if scenario_summary:
        h2("6. SCENARIO SIMULATION SUMMARY")
        para(scenario_summary)

    # ── Causal Analysis ───────────────────────────────────────────────────────
    if causal_summary:
        h2("7. CAUSAL IMPACT SUMMARY")
        para(causal_summary)

    # ── Recommendations ───────────────────────────────────────────────────────
    h2("8. BUSINESS RECOMMENDATIONS")
    para("  Based on the analysis above:")
    para("  1. Focus optimization efforts on the most correlated features.")
    para("  2. Monitor high-variance metrics for anomalies.")
    para("  3. Use the trained model for scenario planning before major decisions.")
    para("  4. Validate causal findings with domain experts.")
    para("  5. Re-run analysis periodically as new data arrives.")

    h1("END OF REPORT — InsightFlow AI")

    return "\n".join(lines)


def build_pdf_report(text_report: str) -> bytes:
    """
    Convert text report to a minimal PDF using reportlab (if available),
    else returns UTF-8 bytes of the text report.
    """
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.units import cm

        buf    = io.BytesIO()
        doc    = SimpleDocTemplate(buf, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm,
                                   topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        story  = []

        for line in text_report.split("\n"):
            if line.startswith("="):
                continue
            elif line.startswith("-"):
                story.append(Spacer(1, 6))
            elif line.strip() == "":
                story.append(Spacer(1, 4))
            else:
                safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                if line.isupper() and len(line.strip()) > 3:
                    story.append(Paragraph(f"<b>{safe_line}</b>", styles["Heading2"]))
                else:
                    story.append(Paragraph(safe_line, styles["Normal"]))

        doc.build(story)
        return buf.getvalue()

    except ImportError:
        # reportlab not available — return plain text as bytes
        return text_report.encode("utf-8")
