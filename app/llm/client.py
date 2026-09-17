"""Session-independent OpenAI-compatible transports for the analysis tool loop."""
from dataclasses import dataclass, field
import os
import re
import requests
from dotenv import load_dotenv
from .service_errors import ExternalServiceError, check_response

load_dotenv()
PROVIDERS = {
    "Groq": "https://api.groq.com/openai/v1/chat/completions",
    "OpenRouter": "https://openrouter.ai/api/v1/chat/completions",
    "OpenAI": "https://api.openai.com/v1/chat/completions",
    "DeepSeek": "https://api.deepseek.com/chat/completions",
}
OPENROUTER_URL = PROVIDERS["OpenRouter"]
DEFAULT_MODELS = {"Groq": "openai/gpt-oss-120b", "OpenRouter": "openai/gpt-oss-120b"}


@dataclass(frozen=True)
class LLMSettings:
    provider: str
    api_key: str = field(repr=False)
    model: str
    personal: bool = False
    temperature: float = 0.2
    max_tokens: int = 8192
    reasoning_effort: str = "high"
    timeout: float = 180

    def __post_init__(self):
        if self.provider not in PROVIDERS or not self.api_key.strip() or any(c.isspace() for c in self.api_key):
            raise ExternalServiceError("Invalid credentials.", kind="configuration", provider=self.provider)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:/@+-]{0,199}", self.model):
            raise ExternalServiceError("Invalid model ID.", kind="configuration", provider=self.provider)
        if not 0 <= self.temperature <= 2 or not 1 <= self.max_tokens <= 32768 or self.timeout <= 0:
            raise ExternalServiceError("Invalid generation limits.", kind="configuration", provider=self.provider)
        if self.reasoning_effort not in {"low", "medium", "high"}:
            raise ExternalServiceError("Invalid reasoning effort.", kind="configuration", provider=self.provider)

    @classmethod
    def from_env(cls, provider: str | None = None):
        selected = provider or os.getenv("LLM_PROVIDER", "groq")
        selected = {"groq": "Groq", "openrouter": "OpenRouter"}.get(selected.lower(), selected)
        if selected not in DEFAULT_MODELS:
            raise ExternalServiceError("Unsupported default provider.", kind="configuration")
        configured = os.getenv("LLM_PROVIDER", "groq").lower()
        model = os.getenv(f"{selected.upper()}_MODEL") or (
            os.getenv("LLM_MODEL") if configured == selected.lower() else None
        ) or DEFAULT_MODELS[selected]
        try:
            return cls(selected, os.getenv(f"{selected.upper()}_API_KEY", "").strip(), model,
                       temperature=float(os.getenv("LLM_TEMPERATURE", "0.2")),
                       max_tokens=int(os.getenv("LLM_MAX_TOKENS", "8192")),
                       reasoning_effort=os.getenv("LLM_REASONING_EFFORT", "high"),
                       timeout=float(os.getenv("LLM_TIMEOUT", "180")))
        except ValueError:
            raise ExternalServiceError("Invalid environment settings.", kind="configuration", provider=selected) from None


def chat_completion(messages: list[dict], tools: list[dict] | None = None, *, settings: LLMSettings | None = None) -> dict:
    settings = settings or LLMSettings.from_env()
    payload = {"model": settings.model, "messages": messages}
    if settings.provider == "OpenAI":
        payload["max_completion_tokens"] = settings.max_tokens
        if settings.model.startswith(("o1", "o3", "o4", "gpt-5")):
            payload["reasoning_effort"] = settings.reasoning_effort
        else:
            payload["temperature"] = settings.temperature
    else:
        payload.update(temperature=settings.temperature, top_p=1)
        if settings.provider != "Groq":
            payload.update(frequency_penalty=0, presence_penalty=0)
        payload["max_completion_tokens" if settings.provider == "Groq" else "max_tokens"] = settings.max_tokens
        if settings.provider == "Groq" and settings.model.startswith("openai/gpt-oss-"):
            payload.update(reasoning_effort=settings.reasoning_effort, include_reasoning=False)
        elif settings.provider == "OpenRouter" and "gpt-oss" in settings.model:
            payload["reasoning"] = {"effort": settings.reasoning_effort, "exclude": True}
    if tools:
        payload.update(tools=tools, tool_choice="auto")
        if settings.provider in {"Groq", "OpenRouter"}:
            payload["parallel_tool_calls"] = True
    try:
        response = requests.post(PROVIDERS[settings.provider],
                                 headers={"Authorization": f"Bearer {settings.api_key}", "Content-Type": "application/json"},
                                 json=payload, timeout=settings.timeout, allow_redirects=False)
        if 300 <= response.status_code < 400:
            raise ExternalServiceError("Unexpected redirect.", kind="connection", provider=settings.provider)
        check_response(response)
        body = response.json()
        choice = body["choices"][0]
        message = choice["message"]
        content, calls = message.get("content"), message.get("tool_calls")
        if choice.get("finish_reason") == "length":
            raise ExternalServiceError("Completion was truncated.", kind="invalid_response", provider=settings.provider)
        if not (isinstance(content, str) and content.strip()) and not calls:
            raise ValueError("Empty message")
        if calls and (not isinstance(calls, list) or any(
            not isinstance(call, dict) or not isinstance(call.get("function"), dict) or not call.get("id")
            for call in calls
        )):
            raise ValueError("Invalid tool calls")
        normalized = {"role": "assistant", "content": content}
        if calls:
            normalized["tool_calls"] = calls
        return {"choices": [{"message": normalized}]}
    except requests.Timeout:
        raise ExternalServiceError("Request timed out.", kind="timeout", provider=settings.provider) from None
    except requests.RequestException:
        raise ExternalServiceError("Connection failed.", kind="connection", provider=settings.provider) from None
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        raise ExternalServiceError("Invalid provider response.", kind="invalid_response", provider=settings.provider) from None


def generate_answer(prompt: str) -> str:
    return chat_completion([{"role": "user", "content": prompt}])["choices"][0]["message"]["content"]
