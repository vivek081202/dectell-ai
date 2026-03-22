"""
DecTell AI — Groq LLM Integration Engine
All AI-powered capabilities use Groq API with llama-3.3-70b-versatile.
"""

import streamlit as st
import pandas as pd
import json
import re
from openai import OpenAI

# ── Groq client (singleton via st.cache_resource) ─────────────────────────────

@st.cache_resource
def get_groq_client(api_key: str) -> OpenAI:
    return OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1",
    )


PRIMARY_MODEL  = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "mixtral-8x7b-32768"


def _call_groq(
    messages: list[dict],
    api_key: str,
    temperature: float = 0.3,
    max_tokens: int = 1500,
) -> str:
    """Core Groq call with fallback model. Returns text response."""
    client = get_groq_client(api_key)
    for model in [PRIMARY_MODEL, FALLBACK_MODEL]:
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            if model == FALLBACK_MODEL:
                raise RuntimeError(f"Groq API failed on both models: {e}") from e
            continue
    return ""


# ── Dataset context builder ────────────────────────────────────────────────────

def build_dataset_context(df: pd.DataFrame, max_rows: int = 5) -> str:
    """Build a compact dataset description for LLM context."""
    num_cols  = df.select_dtypes(include="number").columns.tolist()
    cat_cols  = df.select_dtypes(include=["object", "category"]).columns.tolist()
    date_cols = [c for c in df.columns if any(kw in c.lower() for kw in ["date","time","year","month","week","day"])]

    stats_lines = []
    for col in num_cols[:12]:
        s = df[col].describe()
        stats_lines.append(
            f"  {col}: mean={s['mean']:.2f}, std={s['std']:.2f}, "
            f"min={s['min']:.2f}, max={s['max']:.2f}, nulls={df[col].isna().sum()}"
        )

    cat_lines = []
    for col in cat_cols[:8]:
        top = df[col].value_counts().head(5).to_dict()
        cat_lines.append(f"  {col}: {top} (unique={df[col].nunique()})")

    sample_rows = df.head(max_rows).to_string(index=False, max_cols=12)

    context = f"""
DATASET SUMMARY
===============
Shape: {df.shape[0]:,} rows × {df.shape[1]} columns
Total nulls: {df.isna().sum().sum()}
Columns: {list(df.columns)}
Numeric columns ({len(num_cols)}): {num_cols}
Categorical columns ({len(cat_cols)}): {cat_cols}
Date-like columns: {date_cols}

NUMERIC STATS:
{chr(10).join(stats_lines) if stats_lines else '  None'}

CATEGORICAL TOP VALUES:
{chr(10).join(cat_lines) if cat_lines else '  None'}

SAMPLE ROWS:
{sample_rows}
""".strip()
    return context


# ── System prompts ─────────────────────────────────────────────────────────────

ANALYST_SYSTEM = """You are DecTell AI — an expert Principal Business Analyst, Data Analyst, Data Scientist and Data Engineer combined.

Your role is to analyze datasets and generate accurate, actionable, and business-relevant insights.

Guidelines:
- Always base insights on actual data statistics provided, never hallucinate numbers
- Distinguish between correlation and causation clearly
- Provide insights relevant to the user type (business owner vs technical analyst)
- Use plain language for business users, technical depth for analysts
- Recommendations must be specific and actionable, never generic
- Flag data quality issues honestly
- Reference specific column names and actual values from the dataset
- Never suggest actions that contradict the data
"""

CLEANING_SYSTEM = """You are an expert Data Engineer analyzing a dataset for cleaning decisions.

Your task: Decide what cleaning operations are needed (if any) based on the actual data.

Rules:
- If data looks clean, say so — do NOT fabricate cleaning steps
- Identify columns that are identifiers (ID, UUID, key columns) — never impute or transform these
- For numeric columns with nulls: recommend median imputation only if null% < 40%
- For categorical with nulls: recommend mode imputation only if null% < 40%
- Flag columns with >40% nulls as potentially droppable (ask user intent)
- Identify outliers using IQR logic only where statistically meaningful
- Flag leakage risks (e.g. columns derived from target)
- Return structured JSON only, no prose
"""

CHAT_SYSTEM = """You are DecTell AI Data Chat — an intelligent analytics assistant.

You have access to a business dataset and must answer user questions accurately.

Rules:
- Answer based ONLY on the dataset context provided
- When asked for numbers, reference actual statistics from the data
- When visualization would help, describe what chart type and which columns to use
- If a question is outside the dataset scope, say so clearly
- Maintain conversation context across turns
- Be concise but complete — no filler phrases
- For business questions, translate technical findings to business language
"""


# ── LLM Functions ──────────────────────────────────────────────────────────────

def llm_smart_clean_plan(df: pd.DataFrame, api_key: str) -> dict:
    """
    Ask the LLM to analyze the dataset and return a structured cleaning plan.
    Returns dict with keys: needs_cleaning, operations, reasoning, warnings
    """
    ctx = build_dataset_context(df)
    null_summary = {col: int(df[col].isna().sum()) for col in df.columns if df[col].isna().sum() > 0}
    dup_count = int(df.duplicated().sum())

    prompt = f"""
{ctx}

NULL COUNTS PER COLUMN: {json.dumps(null_summary)}
DUPLICATE ROWS: {dup_count}

Analyze this dataset and return a JSON cleaning plan. Return ONLY valid JSON, no markdown.

Schema:
{{
  "needs_cleaning": true/false,
  "reasoning": "brief explanation of overall state",
  "operations": [
    {{
      "column": "column_name",
      "action": "impute_median|impute_mode|drop_column|drop_rows|cap_outliers|label_encode|one_hot|keep",
      "reason": "why",
      "priority": "high|medium|low"
    }}
  ],
  "id_columns": ["list of identifier columns to skip"],
  "warnings": ["any data quality warnings"]
}}
"""
    try:
        raw = _call_groq(
            messages=[
                {"role": "system", "content": CLEANING_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            api_key=api_key,
            temperature=0.1,
            max_tokens=2000,
        )
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"needs_cleaning": True, "reasoning": raw, "operations": [], "id_columns": [], "warnings": []}
    except Exception as e:
        return {"needs_cleaning": True, "reasoning": f"LLM unavailable: {e}", "operations": [], "id_columns": [], "warnings": []}


def llm_eda_insights(df: pd.DataFrame, api_key: str, charts_summary: str = "") -> str:
    """Generate EDA narrative insights from dataset + chart summary."""
    ctx = build_dataset_context(df)
    prompt = f"""
{ctx}

CHARTS GENERATED: {charts_summary if charts_summary else 'distribution plots, correlation heatmap, box plots'}

Generate a structured EDA insight report. Cover:
1. Overall data quality assessment
2. Key distribution findings (skewness, outliers, notable ranges)
3. Strongest correlations and their business implications
4. Patterns or anomalies worth investigating
5. Suggested next steps for analysis

Be specific — reference column names and actual numbers. Format with clear sections.
"""
    return _call_groq(
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        api_key=api_key,
        temperature=0.4,
        max_tokens=1200,
    )


def llm_detect_ml_task(df: pd.DataFrame, user_query: str, api_key: str) -> dict:
    """
    Given user's natural language goal, detect:
    - target column
    - task type (regression/classification)
    - best feature columns
    - recommended model
    - reasoning
    """
    ctx = build_dataset_context(df)
    prompt = f"""
{ctx}

USER GOAL: "{user_query}"

Based on the dataset and user goal, return ONLY valid JSON (no markdown):
{{
  "target_column": "column name to predict",
  "task_type": "regression" or "classification",
  "feature_columns": ["list of best feature column names"],
  "recommended_model": "Linear Regression" or "Random Forest" or "XGBoost",
  "reasoning": "why these choices",
  "business_context": "what this prediction means for the business",
  "confidence": "high|medium|low"
}}

Rules:
- Never use ID columns as features or target
- For binary/categorical targets → classification
- For continuous numeric targets → regression
- Exclude columns that would cause data leakage
"""
    try:
        raw = _call_groq(
            messages=[
                {"role": "system", "content": ANALYST_SYSTEM},
                {"role": "user", "content": prompt},
            ],
            api_key=api_key,
            temperature=0.2,
            max_tokens=800,
        )
        json_match = re.search(r'\{.*\}', raw, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return {"error": raw}
    except Exception as e:
        return {"error": str(e)}


def llm_business_insights(
    df: pd.DataFrame,
    model_result: dict | None,
    user_type: str,  # "business" or "technical"
    api_key: str,
    extra_context: str = "",
) -> str:
    """Generate targeted insights and recommendations based on user type."""
    ctx = build_dataset_context(df)
    model_info = ""
    if model_result:
        metrics = {k: v for k, v in model_result.get("metrics", {}).items() if k != "Report"}
        importance = model_result.get("importance", {})
        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:5] if importance else []
        model_info = f"""
ML MODEL RESULTS:
  Model: {model_result.get('model_name', 'Unknown')}
  Task: {model_result.get('task', 'Unknown')}
  Target: {model_result.get('target_col', 'Unknown')}
  Metrics: {metrics}
  Top Features: {top_features}
"""

    if user_type == "business":
        prompt = f"""
{ctx}
{model_info}
{extra_context}

You are speaking to a BUSINESS OWNER or NON-TECHNICAL STAKEHOLDER.

Generate a business intelligence report with:
1. EXECUTIVE SUMMARY (2-3 sentences, plain English)
2. KEY BUSINESS FINDINGS (3-5 bullet points with specific numbers)
3. REVENUE / GROWTH OPPORTUNITIES (specific actionable opportunities)
4. RISK ALERTS (things to watch or fix)
5. RECOMMENDED ACTIONS (concrete next steps the business should take)
6. PRIORITY FOCUS AREAS (top 3 things to act on this week)

Language rules:
- NO technical jargon (no R², MAE, p-values, coefficients)
- Use business language: revenue, customers, growth, retention, cost, profit
- Every recommendation must reference actual data patterns
- Be specific: "customers in segment X churn 3x more" not "some customers churn"
"""
    else:
        prompt = f"""
{ctx}
{model_info}
{extra_context}

You are speaking to a DATA ANALYST or DATA SCIENTIST.

Generate a technical analytics report with:
1. DATA QUALITY ASSESSMENT (nulls, distributions, outliers summary)
2. STATISTICAL FINDINGS (correlations, distributions, key stats)
3. MODEL PERFORMANCE ANALYSIS (metrics interpretation, feature importance insights)
4. FEATURE ENGINEERING SUGGESTIONS (new features to create)
5. MODELING RECOMMENDATIONS (model improvements, hyperparameter tuning, alternative models)
6. TECHNICAL NEXT STEPS (validation, A/B testing, monitoring)

Be precise with numbers. Reference column names. Suggest specific pandas/sklearn operations where relevant.
"""

    return _call_groq(
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        api_key=api_key,
        temperature=0.35,
        max_tokens=1800,
    )


def llm_chat_response(
    df: pd.DataFrame,
    conversation_history: list[dict],
    user_message: str,
    api_key: str,
) -> dict:
    """
    Full LLM-powered chat with data.
    Returns: {text, chart_suggestion: {type, x, y, color}, pandas_result}
    """
    ctx = build_dataset_context(df)

    system = f"""{CHAT_SYSTEM}

CURRENT DATASET CONTEXT:
{ctx}

Available columns: {list(df.columns)}
Numeric columns: {df.select_dtypes(include='number').columns.tolist()}
Categorical columns: {df.select_dtypes(include='object').columns.tolist()}
"""

    messages = [{"role": "system", "content": system}]

    # Include recent history (last 8 turns)
    for turn in conversation_history[-8:]:
        messages.append({"role": turn["role"], "content": turn["content"]})

    # Append current question with instruction to suggest chart if helpful
    messages.append({
        "role": "user",
        "content": f"""{user_message}

If a chart would help answer this, end your response with a JSON block like:
```chart
{{"type": "bar|line|scatter|histogram|pie", "x": "column_name", "y": "column_name", "title": "chart title"}}
```
Otherwise omit the chart block."""
    })

    try:
        raw_response = _call_groq(
            messages=messages,
            api_key=api_key,
            temperature=0.4,
            max_tokens=1000,
        )

        # Parse out chart suggestion if present
        chart_suggestion = None
        chart_match = re.search(r'```chart\s*(\{.*?\})\s*```', raw_response, re.DOTALL)
        if chart_match:
            try:
                chart_suggestion = json.loads(chart_match.group(1))
            except Exception:
                pass
            text_response = raw_response[:chart_match.start()].strip()
        else:
            text_response = raw_response.strip()

        # Try to compute a pandas result for factual questions
        pandas_result = _try_pandas_compute(df, user_message)

        return {
            "text": text_response,
            "chart_suggestion": chart_suggestion,
            "pandas_result": pandas_result,
        }

    except Exception as e:
        return {
            "text": f"I encountered an error processing your question: {e}. Please rephrase or check your API key.",
            "chart_suggestion": None,
            "pandas_result": None,
        }


def _try_pandas_compute(df: pd.DataFrame, query: str) -> pd.DataFrame | None:
    """
    Lightweight rule-based pandas computation for factual queries.
    Supplements LLM responses with actual data results.
    """
    q = query.lower()
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include="object").columns.tolist()

    try:
        if "missing" in q or "null" in q:
            mv = df.isna().sum().reset_index()
            mv.columns = ["Column", "Missing"]
            return mv[mv["Missing"] > 0].sort_values("Missing", ascending=False)

        if "top" in q or "highest" in q or "most" in q:
            import re
            n_match = re.search(r'\d+', q)
            n = int(n_match.group()) if n_match else 5
            for col in num_cols:
                if col.lower() in q:
                    return df.nlargest(n, col)[[col] + cat_cols[:2]]
            for col in cat_cols:
                if col.lower() in q:
                    vc = df[col].value_counts().head(n).reset_index()
                    vc.columns = [col, "Count"]
                    return vc

        if "average" in q or "mean" in q:
            for nc in num_cols:
                if nc.lower() in q:
                    for cc in cat_cols:
                        if cc.lower() in q:
                            return df.groupby(cc)[nc].mean().reset_index().sort_values(nc, ascending=False)

        if "count" in q or "how many" in q:
            for col in cat_cols:
                if col.lower() in q:
                    vc = df[col].value_counts().reset_index()
                    vc.columns = [col, "Count"]
                    return vc

    except Exception:
        pass
    return None


def llm_generate_report(
    df: pd.DataFrame,
    model_result: dict | None,
    scenario_summary: str | None,
    causal_summary: str | None,
    api_key: str,
) -> str:
    """Generate a comprehensive analytics report using LLM."""
    ctx = build_dataset_context(df)
    model_info = ""
    if model_result:
        metrics = {k: v for k, v in model_result.get("metrics", {}).items() if k != "Report"}
        model_info = f"Model: {model_result.get('model_name')}, Task: {model_result.get('task')}, Metrics: {metrics}"

    prompt = f"""
{ctx}

MODEL INFO: {model_info if model_info else 'No model trained yet'}
SCENARIO: {scenario_summary if scenario_summary else 'No scenario run'}
CAUSAL: {causal_summary if causal_summary else 'No causal analysis run'}

Generate a complete, professional business analytics report with these sections:

EXECUTIVE SUMMARY
KEY DATA INSIGHTS (with actual numbers)
PREDICTIVE ANALYTICS FINDINGS
SCENARIO SIMULATION RESULTS
CAUSAL IMPACT FINDINGS
BUSINESS RECOMMENDATIONS (for owners/decision-makers)
TECHNICAL RECOMMENDATIONS (for analysts)
PRIORITY ACTION PLAN (top 5 actions ranked by impact)

Make every insight specific and reference actual column names and values.
Total length: 600-900 words.
"""
    return _call_groq(
        messages=[
            {"role": "system", "content": ANALYST_SYSTEM},
            {"role": "user", "content": prompt},
        ],
        api_key=api_key,
        temperature=0.35,
        max_tokens=2000,
    )
