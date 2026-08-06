"""LLM tool loop for a multilingual data-analysis agent."""

import json
from collections.abc import Callable

import pandas as pd

from app.llm.client import chat_completion
from app.schemas.agent_schema import AgentResponse, ChartResult
from app.tools.analysis import analyze_data, dataset_overview
from app.tools.visualization import create_chart


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "dataset_overview",
            "description": "Inspect dataset size, column types, missing values and duplicates.",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_data",
            "description": "Run one statistical analysis. Call it more than once when the request has multiple parts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "method": {
                        "type": "string",
                        "enum": ["describe", "missing", "correlation", "outliers", "frequency", "group", "trend"],
                    },
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "group_by": {"type": "string"},
                    "correlation_method": {"type": "string", "enum": ["pearson", "spearman", "kendall"]},
                },
                "required": ["method"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_chart",
            "description": "Create one chart. Call repeatedly when multiple visualizations are requested.",
            "parameters": {
                "type": "object",
                "properties": {
                    "chart_type": {
                        "type": "string",
                        "enum": ["histogram", "box", "scatter", "line", "bar", "pie", "correlation"],
                    },
                    "x": {"type": "string", "description": "Main column, using its actual dataset name."},
                    "y": {"type": "string", "description": "Optional numeric value column."},
                    "group_by": {"type": "string", "description": "Optional category used to split the chart."},
                },
                "required": ["chart_type"],
            },
        },
    },
]


def execute_tool(name: str, df: pd.DataFrame, arguments: dict | None = None) -> dict:
    arguments = arguments or {}
    try:
        if name == "dataset_overview":
            return dataset_overview(df)
        if name == "analyze_data":
            return analyze_data(df, **arguments)
        if name == "create_chart":
            return create_chart(df, **arguments)
        return {"error": f"Unknown tool: {name}"}
    except (TypeError, ValueError) as exc:
        return {"error": str(exc)}


def _arguments(tool_call: dict) -> dict:
    raw = tool_call.get("function", {}).get("arguments", "{}")
    if isinstance(raw, dict):
        return raw
    try:
        parsed = json.loads(raw)
        return parsed if isinstance(parsed, dict) else {}
    except (json.JSONDecodeError, TypeError):
        return {}


def _instructions(df: pd.DataFrame) -> str:
    schema = [{"name": str(name), "type": str(dtype)} for name, dtype in df.dtypes.items()]
    return f"""You are a careful multilingual data analyst.
Dataset: {len(df)} rows. Schema: {json.dumps(schema, ensure_ascii=False)}

Rules:
- Match the user's language and return clean Markdown.
- Understand informal wording, Persian/English equivalents, casing differences and minor typos. Map concepts to the most likely schema column; ask only when genuinely ambiguous.
- Complete every part of the request. Use multiple tools and multiple rounds when needed; never stop after only the first requested analysis or chart.
- Use tools for every claim about the data. Never invent values.
- Prefer concise conclusions, mention the resolved column names, and explain statistical limitations.
- A chart does not replace the requested numerical analysis; perform both when both are requested.
"""


def _response(answer: str | None, charts: list[ChartResult]) -> AgentResponse:
    text = (answer or "Analysis completed.").strip()
    response_type = "mixed" if charts and answer else "chart" if charts else "text"
    return AgentResponse(
        type=response_type,
        answer=text,
        charts=charts,
        chart_path=charts[0].path if charts else None,
    )


def run_agent(
    df: pd.DataFrame,
    question: str,
    *,
    completion: Callable | None = None,
    max_rounds: int = 6,
) -> AgentResponse:
    """Run all requested tools until the model returns a final Markdown answer."""
    if df.empty:
        raise ValueError("The dataset is empty.")
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    complete = completion or chat_completion
    messages = [
        {"role": "system", "content": _instructions(df)},
        {"role": "user", "content": question.strip()},
    ]
    charts: list[ChartResult] = []
    used_tool = False

    for _ in range(max_rounds):
        message = complete(messages=messages, tools=TOOLS)["choices"][0]["message"]
        tool_calls = message.get("tool_calls") or []
        if not tool_calls:
            # Retry an initial answer that ignored the dataset tools.
            if not used_tool:
                messages.extend(
                    [
                        message,
                        {
                            "role": "user",
                            "content": (
                                "My request above is a valid dataset-analysis task. "
                                "Call every tool needed for every requested analysis and chart now; "
                                "do not answer until the tool results are available."
                            ),
                        },
                    ]
                )
                continue
            return _response(message.get("content"), charts)

        used_tool = True
        messages.append(message)
        for call in tool_calls[:10]:
            name = call.get("function", {}).get("name", "")
            result = execute_tool(name, df, _arguments(call))
            if result.get("type") == "chart":
                charts.append(
                    ChartResult(
                        type=result["chart_type"],
                        title=result["title"],
                        path=result["path"],
                    )
                )
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": call.get("id", name),
                    "content": json.dumps(result, ensure_ascii=False, default=str),
                }
            )

    final = complete(messages=messages)["choices"][0]["message"].get("content")
    return _response(final, charts)
