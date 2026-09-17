"""Single-process web demo, ready for Streamlit Community Cloud."""

import os

import streamlit as st

from app.agent.orchestrator import run_agent
from app.loaders.pandas_loader import load_data
from app.profiling.profiler import profile_dataset
from app.ui import page_css, render_markdown
from app.llm.personal_settings import render_personal_settings, completion_for_session
from app.llm.service_errors import friendly_error


st.set_page_config(page_title="AI Data Analyst", page_icon="📊", layout="wide")
st.markdown(page_css(), unsafe_allow_html=True)

# Cloud secrets override local .env values when the app is deployed.
try:
    for name in ("OPENROUTER_API_KEY", "GROQ_API_KEY", "LLM_MODEL", "LLM_PROVIDER", "GROQ_MODEL", "OPENROUTER_MODEL"):
        if value := st.secrets.get(name):
            os.environ[name] = value
except FileNotFoundError:
    pass

st.markdown('<div class="app-eyebrow">MULTILINGUAL DATA WORKSPACE</div>', unsafe_allow_html=True)
st.title("AI Data Analyst")
st.caption("Upload a dataset, ask a multi-part question in Persian or English, and receive evidence-based analysis.")

render_personal_settings(st)

with st.container(border=True):
    st.subheader("1. Upload a dataset")
    uploaded = st.file_uploader("Choose a CSV, Excel, or JSON file", type=["csv", "xlsx", "json"])

if uploaded:
    signature = (uploaded.name, uploaded.size)
    if st.session_state.get("file_signature") != signature:
        try:
            # A new upload invalidates the previous analysis result.
            st.session_state.dataset = load_data(uploaded)
            st.session_state.file_signature = signature
            st.session_state.result = None
        except Exception as exc:
            st.error(f"Could not read the file: {exc}")
elif st.session_state.get("file_signature"):
    for key in ("dataset", "file_signature", "result"):
        st.session_state.pop(key, None)

if "dataset" in st.session_state:
    frame = st.session_state.dataset
    profile = profile_dataset(frame)

    with st.container(border=True):
        st.subheader("Dataset overview")
        metrics = st.columns(4)
        metrics[0].metric("Rows", profile["rows"])
        metrics[1].metric("Columns", profile["columns"])
        metrics[2].metric("Missing cells", sum(profile["missing_values"].values()))
        metrics[3].metric("Duplicate rows", profile["duplicate_rows"])
        with st.expander("Preview the first 20 rows", expanded=True):
            st.dataframe(frame.head(20), width="stretch")

    with st.container(border=True):
        st.subheader("2. Ask for an analysis")
        st.caption("You can request several statistics and charts in the same message.")
        question = st.text_area(
            "Analysis request",
            placeholder="Example: Describe age, detect its outliers, and create both a histogram and a box plot.",
            height=110,
        )
        analyze = st.button("Run analysis", type="primary", disabled=not question.strip())

    if analyze:
        try:
            with st.spinner("Analyzing the dataset..."):
                st.session_state.result = None
                st.session_state.result = run_agent(frame, question, completion=completion_for_session(st))
        except Exception as exc:
            st.error(friendly_error(exc, personal=st.session_state.get("personal_enabled", False)))

    if result := st.session_state.get("result"):
        with st.container(border=True):
            st.subheader("3. Analysis result")
            # Each rendered Markdown block gets its own automatic text direction.
            st.markdown(render_markdown(result.answer), unsafe_allow_html=True)
            if result.charts:
                st.subheader("Visualizations")
                tabs = st.tabs([f"{index + 1}. {chart.type.title()}" for index, chart in enumerate(result.charts)])
                for tab, chart in zip(tabs, result.charts):
                    with tab:
                        st.image(chart.path, caption=chart.title, width="stretch")
else:
    st.info("Upload a dataset to unlock the analysis workspace.")
