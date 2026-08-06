"""Minimal OpenRouter chat-completions client."""

import os

import requests
from dotenv import load_dotenv


load_dotenv()
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def chat_completion(messages: list[dict], tools: list[dict] | None = None) -> dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not configured.")

    payload = {
        "model": os.getenv("LLM_MODEL", "qwen/qwen3-8b"),
        "messages": messages,
    }
    if tools:
        payload.update({"tools": tools, "tool_choice": "auto", "parallel_tool_calls": True})

    response = requests.post(
        OPENROUTER_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )
    if response.status_code == 429:
        raise RuntimeError("LLM rate limit reached. Please wait and try again.")
    response.raise_for_status()
    return response.json()


def generate_answer(prompt: str) -> str:
    return chat_completion([{"role": "user", "content": prompt}])["choices"][0]["message"]["content"]
