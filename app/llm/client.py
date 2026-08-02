# ==========================================================
# LLM Client
# ==========================================================

import os

import requests

from dotenv import load_dotenv


# ==========================================================
# Environment
# ==========================================================

load_dotenv()


# ==========================================================
# Configuration
# ==========================================================

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY"
)

OPENROUTER_URL = (
    "https://openrouter.ai/api/v1/chat/completions"
)

DEFAULT_MODEL = (
    "openai/gpt-oss-20b:free"
)


# ==========================================================
# LLM Function
# ==========================================================

def generate_answer(
    prompt: str,
) -> str:

    if not OPENROUTER_API_KEY:

        raise ValueError(
            "OPENROUTER_API_KEY "
            "is not configured."
        )

    headers = {

        "Authorization": (
            f"Bearer "
            f"{OPENROUTER_API_KEY}"
        ),

        "Content-Type": (
            "application/json"
        ),
    }

    payload = {

        "model": DEFAULT_MODEL,

        "messages": [

            {
                "role": "user",
                "content": prompt,
            }

        ],
    }

    response = requests.post(

        OPENROUTER_URL,

        headers=headers,

        json=payload,

        timeout=60,
    )

    response.raise_for_status()

    data = response.json()

    return (
        data["choices"][0]
        ["message"]
        ["content"]
    )