import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
import requests
from streamlit.testing.v1 import AppTest

from app.llm.client import LLMSettings, chat_completion
from app.llm.personal_settings import completion_for_session
from app.llm.service_errors import ExternalServiceError, FREE_QUOTA_MESSAGE, friendly_error


def response(status=200, body=None, headers=None):
    result = requests.Response()
    result.status_code = status
    result.url = "https://api.groq.com/openai/v1/chat/completions"
    result._content = json.dumps(body or {"choices": [{"message": {"content": "نتیجه", "reasoning": "private"}}]}).encode()
    result.headers.update(headers or {})
    return result


def test_groq_high_reasoning_and_portable_history(monkeypatch):
    post = Mock(return_value=response())
    monkeypatch.setattr("app.llm.client.requests.post", post)
    settings = LLMSettings("Groq", "private-key", "openai/gpt-oss-120b")
    result = chat_completion([{"role": "user", "content": "Analyze"}], tools=[{"type": "function"}], settings=settings)
    payload = post.call_args.kwargs["json"]
    assert payload["reasoning_effort"] == "high"
    assert payload["max_completion_tokens"] == 8192
    assert payload["temperature"] == 0.2
    assert "frequency_penalty" not in payload and "presence_penalty" not in payload
    assert payload["include_reasoning"] is False
    assert payload["parallel_tool_calls"] is True
    assert post.call_args.kwargs["allow_redirects"] is False
    assert "reasoning" not in result["choices"][0]["message"]
    assert "private-key" not in repr(settings)


def test_openrouter_server_selection_keeps_its_model_and_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_MODEL", "openai/gpt-oss-120b")
    monkeypatch.setenv("OPENROUTER_API_KEY", "router-key")
    monkeypatch.setenv("OPENROUTER_MODEL", "original/model:free")
    settings = LLMSettings.from_env("OpenRouter")
    assert settings.model == "original/model:free"
    assert settings.api_key == "router-key"


@pytest.mark.parametrize("status,detail,kind", [
    (401, "bad key", "authentication"), (402, "credit", "billing"),
    (429, "daily quota", "quota_exhausted"), (429, "requests/minute", "rate_limited"),
    (429, "unknown", "limit_unknown"), (503, "overloaded", "provider_capacity"),
    (404, "missing model", "model_unavailable"), (400, "bad parameters", "invalid_request"),
])
def test_provider_errors_are_classified_without_leaking(monkeypatch, status, detail, kind):
    post = Mock(return_value=response(status, {"error": {"message": detail + " secret-key", "code": status}}, {"Retry-After": "20"}))
    monkeypatch.setattr("app.llm.client.requests.post", post)
    with pytest.raises(ExternalServiceError) as raised:
        chat_completion([], settings=LLMSettings("Groq", "secret-key", "openai/gpt-oss-120b"))
    assert raised.value.kind == kind
    assert raised.value.provider == "Groq"
    assert raised.value.retry_after == 20
    assert "secret-key" not in friendly_error(raised.value)
    if kind == "quota_exhausted":
        assert friendly_error(raised.value) == FREE_QUOTA_MESSAGE
        assert "حساب شخصی" in friendly_error(raised.value, personal=True)


@pytest.mark.parametrize("body", [{"choices": []}, {"choices": [{"message": {"content": ""}}]},
    {"choices": [{"finish_reason": "length", "message": {"content": "unfinished"}}]}])
def test_empty_and_truncated_outputs_are_not_success(monkeypatch, body):
    monkeypatch.setattr("app.llm.client.requests.post", Mock(return_value=response(body=body)))
    with pytest.raises(ExternalServiceError, match="Invalid|truncated"):
        chat_completion([], settings=LLMSettings("Groq", "key", "openai/gpt-oss-120b"))


def test_personal_settings_are_isolated_and_required():
    first = SimpleNamespace(session_state={"personal_enabled": True})
    with pytest.raises(ExternalServiceError) as raised:
        completion_for_session(first)
    assert raised.value.kind == "unregistered_settings"
    first.session_state["personal_saved"] = LLMSettings("Groq", "first-key", "first-model", personal=True)
    second = SimpleNamespace(session_state={"personal_enabled": True, "personal_saved": LLMSettings("OpenRouter", "second-key", "second-model", personal=True)})
    assert completion_for_session(first).keywords["settings"].api_key == "first-key"
    assert completion_for_session(second).keywords["settings"].api_key == "second-key"


def test_personal_form_registers_deletes_and_invalidates_on_provider_change():
    app = AppTest.from_file(Path(__file__).resolve().parents[1] / "streamlit_app.py", default_timeout=20).run()
    app.checkbox(key="personal_enabled").check().run()
    app.text_input(key="personal_api_key").set_value("test-key")
    app.text_input(key="personal_model").set_value("openai/gpt-oss-120b")
    next(b for b in app.button if b.label == "ثبت").click().run()
    assert not app.exception
    assert app.session_state["personal_saved"].model == "openai/gpt-oss-120b"
    app.selectbox(key="personal_provider").select("OpenRouter").run()
    assert "personal_saved" not in app.session_state
    next(b for b in app.button if b.label == "حذف").click().run()
    assert not app.exception
    assert app.session_state["personal_enabled"] is False
    assert "personal_saved" not in app.session_state


def test_api_uses_friendly_provider_error(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from app.main import app
    from app.api import analyze
    from app.services import file_service
    monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
    client = TestClient(app)
    file_id = client.post("/upload", files={"file": ("data.csv", "Age\n20\n30", "text/csv")}).json()["file_id"]
    def fail(*args):
        raise ExternalServiceError("secret provider body", kind="authentication", provider="Groq", status=401)
    monkeypatch.setattr(analyze, "run_agent", fail)
    result = client.post("/analyze/", json={"file_id": file_id, "question": "Describe"})
    assert result.status_code == 503
    assert result.json()["detail"] == "کلید API پذیرفته نشد. لطفاً کلید و دسترسی حساب خود را بررسی کنید."
