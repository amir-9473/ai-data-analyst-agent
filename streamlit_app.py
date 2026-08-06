"""Single-process web demo, ready for Streamlit Community Cloud."""

import os

import streamlit as st

from app.agent.orchestrator import run_agent
from app.loaders.pandas_loader import load_data
from app.profiling.profiler import profile_dataset


st.set_page_config(page_title="AI Data Analyst", page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    [data-testid="stMarkdownContainer"] h1,
    [data-testid="stMarkdownContainer"] h2,
    [data-testid="stMarkdownContainer"] h3,
    [data-testid="stMarkdownContainer"] td,
    [data-testid="stMarkdownContainer"] th,
    input, textarea {
        unicode-bidi: plaintext;
        text-align: start;
    }
    [data-testid="stFileUploader"] {direction: auto;}
    .stApp {font-family: Tahoma, "Segoe UI", sans-serif;}
    </style>
    """,
    unsafe_allow_html=True,
)

try:
    if key := st.secrets.get("OPENROUTER_API_KEY"):
        os.environ["OPENROUTER_API_KEY"] = key
    if model := st.secrets.get("LLM_MODEL"):
        os.environ["LLM_MODEL"] = model
except FileNotFoundError:
    pass

st.title("📊 دستیار هوشمند تحلیل داده | AI Data Analyst")
st.caption("فایل را بارگذاری کنید و سؤال‌های چندبخشی را به فارسی یا انگلیسی بپرسید.")

uploaded = st.file_uploader("CSV، Excel یا JSON", type=["csv", "xlsx", "json"])
if uploaded:
    signature = (uploaded.name, uploaded.size)
    if st.session_state.get("file_signature") != signature:
        try:
            st.session_state.dataset = load_data(uploaded)
            st.session_state.file_signature = signature
            st.session_state.result = None
        except Exception as exc:
            st.error(f"خطا در خواندن فایل / Could not read file: {exc}")

if "dataset" in st.session_state:
    frame = st.session_state.dataset
    profile = profile_dataset(frame)
    left, right = st.columns([2, 1])
    with left:
        st.subheader("پیش‌نمایش داده | Data preview")
        st.dataframe(frame.head(20), width="stretch")
    with right:
        st.subheader("خلاصه | Overview")
        st.metric("Rows", profile["rows"])
        st.metric("Columns", profile["columns"])
        st.metric("Missing cells", sum(profile["missing_values"].values()))

    question = st.text_area(
        "درخواست تحلیل | Analysis request",
        placeholder="مثال: توزیع سن را تحلیل کن، نقاط پرت را بگو و هیستوگرام و نمودار جعبه‌ای بکش.",
        height=100,
    )
    if st.button("تحلیل کن | Analyze", type="primary", disabled=not question.strip()):
        try:
            with st.spinner("در حال تحلیل... | Analyzing..."):
                st.session_state.result = run_agent(frame, question)
        except Exception as exc:
            st.error(f"تحلیل انجام نشد / Analysis failed: {exc}")

    if result := st.session_state.get("result"):
        st.divider()
        st.subheader("نتیجه | Result")
        st.markdown(result.answer)
        if result.charts:
            columns = st.columns(min(2, len(result.charts)))
            for index, chart in enumerate(result.charts):
                with columns[index % len(columns)]:
                    st.image(chart.path, caption=chart.title, width="stretch")
else:
    st.info("برای شروع یک فایل انتخاب کنید. | Upload a dataset to begin.")
