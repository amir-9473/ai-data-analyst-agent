import pandas as pd

from app.agent.orchestrator import run_agent


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
