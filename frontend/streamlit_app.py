# ==========================================================
# AI Data Analyst Agent - Streamlit UI
# ==========================================================

import streamlit as st

'''from frontend.api_client import (
    upload_file,
    analyze_dataset,
)'''

from api_client import (
    upload_file,
    analyze_dataset,
)


# ==========================================================
# Page Config
# ==========================================================

st.set_page_config(
    page_title="AI Data Analyst Agent",
    page_icon="📊",
)


# ==========================================================
# Title
# ==========================================================

st.title(
    "📊 AI Data Analyst Agent"
)

st.write(
    "Upload your dataset and ask analytical questions."
)


# ==========================================================
# Upload Section
# ==========================================================

uploaded_file = st.file_uploader(
    "Upload CSV file",
    type=[
        "csv",
        "xlsx",
    ],
)


if uploaded_file:

    st.success(
        "File uploaded."
    )


    # ------------------------------------------------------
    # Upload to Backend
    # ------------------------------------------------------

    if "file_id" not in st.session_state:

        with st.spinner(
            "Uploading dataset..."
        ):

            result = upload_file(
                uploaded_file
            )


            st.session_state.file_id = (
                result["file_id"]
            )


            st.session_state.filename = (
                result["filename"]
            )


    st.info(
        f"Dataset: {st.session_state.filename}"
    )


# ==========================================================
# Question Section
# ==========================================================

if "file_id" in st.session_state:


    question = st.text_input(
        "Ask your question:",
        placeholder=(
            "Example: "
            "Create histogram for age column"
        ),
    )


    if st.button(
        "Analyze"
    ):


        if question:


            with st.spinner(
                "Analyzing..."
            ):


                try:

                    response = analyze_dataset(

                        file_id=(
                            st.session_state.file_id
                        ),

                        question=question,

                    )


                    st.write(
                        response["answer"]
                    )


                except Exception as e:

                    st.error(
                        str(e)
                    )


            st.subheader(
                "Answer"
            )


            st.write(
                response["answer"]
            )


            # --------------------------------------------------
            # Chart Display
            # --------------------------------------------------

            if response.get(
                "chart_path"
            ):

                st.subheader(
                    "Chart"
                )

                st.image(
                    response["chart_path"]
                )