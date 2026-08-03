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
    "qwen/qwen3-8b"
)


# ==========================================================
# Basic LLM Call
# ==========================================================

def generate_answer(
    prompt: str,
) -> str:

    if not OPENROUTER_API_KEY:

        raise ValueError(
            "OPENROUTER_API_KEY "
            "is not configured."
        )

    messages = [

        {
            "role": "user",
            "content": prompt,
        }

    ]

    response = chat_completion(
        messages
    )

    return (
        response["choices"][0]
        ["message"]
        ["content"]
    )


# ==========================================================
# Chat Completion
# ==========================================================

def chat_completion(
    messages: list,
    tools: list | None = None,
) -> dict:

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

        "messages": messages,
    }

    if tools:

        payload["tools"] = tools

        payload["tool_choice"] = "auto"

    response = requests.post(

        OPENROUTER_URL,

        headers=headers,

        json=payload,

        timeout=60,
    )

    if response.status_code == 429:

        raise Exception(
            "LLM rate limit reached. "
            "Please wait and try again."
        )


    response.raise_for_status()

    return response.json()