import json

import pandas as pd
import pytest

from app.agent.orchestrator import run_agent
from app.llm.client import LLMSettings
from app.llm.service_errors import ExternalServiceError, friendly_error


def test_agent_executes_every_tool_call(monkeypatch, tmp_path):
    frame = pd.DataFrame({"Age": [20, 30, 40], "BMI": [21.0, 25.0, 30.0]})
    calls = [
        {
            "id": "stats",
            "function": {"name": "analyze_data", "arguments": '{"method":"describe","columns":["سن"]}'},
        },
        {
            "id": "histogram",
            "function": {"name": "create_chart", "arguments": '{"chart_type":"histogram","x":"سن"}'},
        },
        {
            "id": "scatter",
            "function": {"name": "create_chart", "arguments": '{"chart_type":"scatter","x":"سن","y":"bmi"}'},
        },
    ]
    responses = iter(
        [
            {"choices": [{"message": {"role": "assistant", "content": None, "tool_calls": calls}}]},
            {"choices": [{"message": {"role": "assistant", "content": "## نتیجه\nمیانگین و دو نمودار آماده شد."}}]},
        ]
    )

    def complete(**_):
        return next(responses)

    monkeypatch.setattr("app.tools.visualization.CHART_DIR", tmp_path)
    result = run_agent(frame, "سن را تحلیل کن و دو نمودار بکش", completion=complete)

    assert result.type == "mixed"
    assert len(result.charts) == 2
    assert result.answer.startswith("## نتیجه")


def test_agent_retries_an_initial_answer_without_tools():
    frame = pd.DataFrame({"Age": [20, 30, 40]})
    responses = iter(
        [
            {"choices": [{"message": {"role": "assistant", "content": "Please clarify."}}]},
            {
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "stats",
                                    "function": {
                                        "name": "analyze_data",
                                        "arguments": '{"method":"describe","columns":["Age"]}',
                                    },
                                }
                            ],
                        }
                    }
                ]
            },
            {"choices": [{"message": {"role": "assistant", "content": "Done."}}]},
        ]
    )

    result = run_agent(frame, "Describe age", completion=lambda **_: next(responses))

    assert result.answer == "Done."


def test_default_groq_uses_two_models_and_computed_evidence(monkeypatch):
    frame = pd.DataFrame({"BMI": [20.0, 25.0, 30.0], "Insulin": [50, 75, 100]})
    plan = {
        "overview": False,
        "analyses": [
            {"method": "describe", "columns": ["BMI"], "group_by": "", "correlation_method": "pearson"},
            {"method": "correlation", "columns": ["BMI", "Insulin"], "group_by": "", "correlation_method": "pearson"},
        ],
        "charts": [],
    }
    calls = []

    def complete(messages, *, settings, response_format=None):
        calls.append((messages, settings, response_format))
        if response_format:
            return {"choices": [{"message": {"content": json.dumps(plan)}}]}
        evidence = json.loads(messages[1]["content"])["tool_results"]
        assert [item["arguments"]["method"] for item in evidence] == ["describe", "correlation"]
        assert evidence[1]["output"]["result"]["BMI"]["Insulin"] == 1.0
        return {"choices": [{"message": {"content": "BMI با انسولین همبستگی مثبت دارد."}}]}

    monkeypatch.setattr("app.agent.orchestrator.chat_completion", complete)
    result = run_agent(frame, "تحلیل کن bmi رو و رابطه اش رو با انسولین بنویس",
                       settings=LLMSettings("Groq", "private-key", "openai/gpt-oss-120b"))

    assert len(calls) == 2
    assert calls[0][1].model == "openai/gpt-oss-20b"
    assert calls[0][1].reasoning_effort == "low"
    assert calls[0][2]["type"] == "json_schema"
    assert calls[1][1].model == "openai/gpt-oss-120b"
    assert calls[1][1].reasoning_effort == "medium"
    assert calls[1][2] is None
    assert "BMI" in result.answer


def test_oversized_schema_is_rejected_before_provider_call(monkeypatch):
    frame = pd.DataFrame({f"column_{index:04d}_" + "x" * 45: [index] for index in range(400)})
    calls = []
    monkeypatch.setattr("app.agent.orchestrator.chat_completion", lambda *args, **kwargs: calls.append(1))

    with pytest.raises(ExternalServiceError) as raised:
        run_agent(frame, "همهٔ ستون‌ها را بررسی کن",
                  settings=LLMSettings("Groq", "private-key", "openai/gpt-oss-120b"))

    assert raised.value.kind == "request_too_large"
    assert "ستون" in friendly_error(raised.value)
    assert calls == []
