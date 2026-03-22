"""
DecTell AI — LLM-Powered Chat with Data
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
import plotly.express as px

from utils.ui_utils import inject_global_css, page_header, section_label, divider, render_footer
from utils.data_utils import require_dataset
from utils.llm_utils import llm_chat_response
from utils.visualization_utils import PLOTLY_TEMPLATE

inject_global_css()
page_header("Intelligence", "Chat with Data",
    "Ask any question about your data in plain language. AI understands context, computes results, and explains insights.")

df = require_dataset()
if df is None:
    render_footer()
    st.stop()

api_key = st.session_state.get("groq_api_key", "")

if not api_key:
    st.warning("Add your Groq API key in the sidebar to enable AI chat. "
               "Without it, only basic keyword queries are supported.")

# ── Session state ──────────────────────────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []   # LLM conversation history

# ── Dataset summary chip ───────────────────────────────────────────────────────
num_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()

st.markdown(f"""
<div style="display:flex;gap:0.6rem;flex-wrap:wrap;margin-bottom:1.25rem;">
    <span class="stat-badge">{df.shape[0]:,} rows</span>
    <span class="stat-badge">{df.shape[1]} columns</span>
    <span class="stat-badge">{len(num_cols)} numeric</span>
    <span class="stat-badge">{len(cat_cols)} categorical</span>
</div>""", unsafe_allow_html=True)

# ── Quick query suggestions ────────────────────────────────────────────────────
suggestions = ["What are the key insights from this dataset?", "Show missing values",
               "What is the data quality like?"]
if len(num_cols) >= 2:
    suggestions.append(f"What is the correlation between {num_cols[0]} and {num_cols[-1]}?")
if cat_cols:
    suggestions.append(f"What are the top values in {cat_cols[0]}?")
if num_cols and cat_cols:
    suggestions.append(f"Which {cat_cols[0]} has the highest average {num_cols[0]}?")

section_label("Quick Queries")
scols = st.columns(min(3, len(suggestions)))
for i, sug in enumerate(suggestions[:6]):
    if scols[i % 3].button(sug, use_container_width=True, key=f"sug_{i}"):
        st.session_state.chat_history.append({"role": "user", "display": sug})
        with st.spinner("Thinking…"):
            if api_key:
                resp = llm_chat_response(df, st.session_state.chat_messages, sug, api_key)
                st.session_state.chat_messages.append({"role": "user", "content": sug})
                st.session_state.chat_messages.append({"role": "assistant", "content": resp["text"]})
            else:
                from utils.chat_utils import process_query
                resp = process_query(df, sug)
                resp = {"text": resp.get("text",""), "chart_suggestion": None,
                        "pandas_result": resp.get("table")}
        st.session_state.chat_history.append({"role": "assistant", "response": resp})
        st.rerun()

divider()

# ── Chat history ───────────────────────────────────────────────────────────────
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["display"])
    else:
        resp = msg.get("response", {})
        with st.chat_message("assistant"):
            if resp.get("text"):
                st.markdown(resp["text"])

            # Show pandas computed result table
            pr = resp.get("pandas_result")
            if pr is not None and isinstance(pr, pd.DataFrame) and not pr.empty:
                st.dataframe(pr.head(20), use_container_width=True)

            # Render chart suggestion
            cs = resp.get("chart_suggestion")
            if cs and isinstance(cs, dict):
                try:
                    ctype = cs.get("type","bar")
                    cx    = cs.get("x","")
                    cy    = cs.get("y","")
                    ctitle = cs.get("title","")
                    if cx in df.columns:
                        if ctype == "histogram":
                            fig = px.histogram(df, x=cx, title=ctitle,
                                               template=PLOTLY_TEMPLATE,
                                               color_discrete_sequence=["#00D4FF"])
                            st.plotly_chart(fig, use_container_width=True)
                        elif ctype in ("bar","line") and cy and cy in df.columns:
                            fn = px.bar if ctype=="bar" else px.line
                            fig = fn(df, x=cx, y=cy, title=ctitle, template=PLOTLY_TEMPLATE)
                            st.plotly_chart(fig, use_container_width=True)
                        elif ctype == "scatter" and cy and cy in df.columns:
                            fig = px.scatter(df, x=cx, y=cy, title=ctitle,
                                             template=PLOTLY_TEMPLATE, opacity=0.65)
                            st.plotly_chart(fig, use_container_width=True)
                except Exception:
                    pass

# ── Chat input ─────────────────────────────────────────────────────────────────
user_input = st.chat_input("Ask anything about your data…")
if user_input:
    st.session_state.chat_history.append({"role": "user", "display": user_input})
    with st.spinner("Thinking…"):
        if api_key:
            resp = llm_chat_response(df, st.session_state.chat_messages, user_input, api_key)
            st.session_state.chat_messages.append({"role": "user", "content": user_input})
            st.session_state.chat_messages.append({"role": "assistant", "content": resp["text"]})
        else:
            from utils.chat_utils import process_query
            qr = process_query(df, user_input)
            resp = {"text": qr.get("text",""), "chart_suggestion": None,
                    "pandas_result": qr.get("table")}
    st.session_state.chat_history.append({"role": "assistant", "response": resp})
    st.rerun()

# Clear button
if st.session_state.chat_history:
    if st.button("Clear Conversation", key="clear_chat"):
        st.session_state.chat_history = []
        st.session_state.chat_messages = []
        st.rerun()

render_footer()
