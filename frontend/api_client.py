# ==========================================================
# FastAPI Client
# ==========================================================

import requests


# ==========================================================
# Configuration
# ==========================================================

API_URL = (
    "http://127.0.0.1:8000"
)


# ==========================================================
# Upload Dataset
# ==========================================================

def upload_file(
    file,
):

    """
    Upload dataset to FastAPI.
    """

    files = {

        "file": (

            file.name,

            file.getvalue(),

            file.type,

        )

    }


    response = requests.post(

        f"{API_URL}/upload",

        files=files,

        timeout=60,

    )


    response.raise_for_status()


    return response.json()



# ==========================================================
# Analyze Dataset
# ==========================================================

def analyze_dataset(
    file_id: str,
    question: str,
):

    """
    Send analysis request.
    """

    payload = {

        "file_id": file_id,

        "question": question,

    }


    response = requests.post(

        f"{API_URL}/analyze/",

        json=payload,

        timeout=120,

)


    if response.status_code != 200:

        print(
            "API ERROR:",
            response.text
        )

        raise Exception(
            response.text
        )


    return response.json()