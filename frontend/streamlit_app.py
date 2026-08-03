# ==========================================================
# AI Data Analyst Agent - Streamlit UI
# ==========================================================

import streamlit as st

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
    layout="centered",
)


# ==========================================================
# Session State
# ==========================================================

if "file_id" not in st.session_state:
    st.session_state.file_id = None


if "filename" not in st.session_state:
    st.session_state.filename = None



# ==========================================================
# Header
# ==========================================================

st.title(
    "📊 AI Data Analyst Agent"
)

st.write(
    "Upload your dataset and ask analytical questions using AI."
)


# ==========================================================
# Reset
# ==========================================================

if st.session_state.file_id:

    if st.button(
        "Reset Dataset"
    ):

        st.session_state.file_id = None
        st.session_state.filename = None

        st.rerun()



# ==========================================================
# Upload
# ==========================================================

uploaded_file = st.file_uploader(

    "Upload CSV / Excel dataset",

    type=[
        "csv",
        "xlsx",
    ],

)


if uploaded_file and not st.session_state.file_id:

    try:

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


        st.success(
            "Dataset uploaded successfully."
        )


    except Exception as e:

        st.error(
            str(e)
        )



# ==========================================================
# Dataset Information
# ==========================================================

if st.session_state.file_id:


    st.info(
        f"""
        Dataset:
        {st.session_state.filename}

        File ID:
        {st.session_state.file_id}
        """
    )


    st.divider()


    # ======================================================
    # Question
    # ======================================================

    question = st.text_input(

        "Ask your analysis question",

        placeholder=(

            "Example: "
            "Create histogram for age column"

        ),

    )


    if st.button(
        "Analyze"
    ):


        if not question:

            st.warning(
                "Please enter a question."
            )


        else:


            try:

                with st.spinner(
                    "AI is analyzing..."
                ):


                    response = analyze_dataset(

                        file_id=(

                            st.session_state.file_id

                        ),

                        question=question,

                    )


                st.success(
                    "Analysis completed."
                )


                # ------------------------------------------
                # Response Type
                # ------------------------------------------

                st.subheader(
                    "Result Type"
                )

                st.write(
                    response.get(
                        "type",
                        "unknown"
                    )
                )


                # ------------------------------------------
                # Answer
                # ------------------------------------------

                st.subheader(
                    "Answer"
                )

                st.write(
                    response.get(
                        "answer"
                    )
                )


                # ------------------------------------------
                # Chart
                # ------------------------------------------

                chart_path = response.get(
                    "chart_path"
                )


                if chart_path:


                    st.subheader(
                        "Visualization"
                    )


                    st.image(
                        chart_path
                    )


            except Exception as e:

                st.error(
                    str(e)
                )