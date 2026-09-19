"""LLM tool loop for a multilingual data-analysis agent."""

import json
from collections.abc import Callable
from dataclasses import replace
from functools import partial

import pandas as pd

from app.llm.client import LLMSettings, chat_completion
from app.llm.service_errors import ExternalServiceError
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


_ANALYSIS_PLAN_ITEM = {
    "type": "object",
    "properties": {
        "method": {"type": "string", "enum": ["describe", "missing", "correlation", "outliers", "frequency", "group", "trend"]},
        "columns": {"type": "array", "items": {"type": "string"}},
        "group_by": {"type": "string"},
        "correlation_method": {"type": "string", "enum": ["pearson", "spearman", "kendall"]},
    },
    "required": ["method", "columns", "group_by", "correlation_method"],
    "additionalProperties": False,
}
_CHART_PLAN_ITEM = {
    "type": "object",
    "properties": {
        "chart_type": {"type": "string", "enum": ["histogram", "box", "scatter", "line", "bar", "pie", "correlation"]},
        "x": {"type": "string"},
        "y": {"type": "string"},
        "group_by": {"type": "string"},
    },
    "required": ["chart_type", "x", "y", "group_by"],
    "additionalProperties": False,
}
PLAN_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "analysis_plan",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "overview": {"type": "boolean"},
                "analyses": {"type": "array", "items": _ANALYSIS_PLAN_ITEM},
                "charts": {"type": "array", "items": _CHART_PLAN_ITEM},
            },
            "required": ["overview", "analyses", "charts"],
            "additionalProperties": False,
        },
    },
}
MAX_QUESTION_CHARS = 3000
MAX_SCHEMA_CHARS = 12000
MAX_WRITER_INPUT_CHARS = 12000
MAX_PLAN_ANALYSES = 10
MAX_PLAN_CHARTS = 6


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


def _run_planned_groq_agent(df: pd.DataFrame, question: str, settings: LLMSettings) -> AgentResponse:
    """Use a small structured planner and one larger evidence-grounded answer call."""
    if len(question) > MAX_QUESTION_CHARS:
        raise ExternalServiceError("Question exceeds the analysis input budget.", kind="request_too_large", provider=settings.provider)
    schema = [{"name": str(name), "type": str(dtype)} for name, dtype in df.dtypes.items()]
    schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    if len(schema_text) > MAX_SCHEMA_CHARS:
        schema = [f"{name}:{dtype.kind}" for name, dtype in df.dtypes.items()]
        schema_text = json.dumps(schema, ensure_ascii=False, separators=(",", ":"))
    if len(schema_text) > MAX_SCHEMA_CHARS:
        raise ExternalServiceError("Dataset has too many columns for one analysis.", kind="request_too_large", provider=settings.provider)
    planner_settings = replace(settings, model="openai/gpt-oss-20b", temperature=0,
                               max_tokens=min(settings.max_tokens, 1200), reasoning_effort="low")
    plan_content = chat_completion(
        [
            {"role": "system", "content": (
                "Plan only the computations needed to answer the user's dataset question. "
                "Use exact column names from the schema. A request to analyze one numeric column "
                "needs describe for that column. A relationship between numeric columns needs "
                "correlation for those columns. Select overview only for an explicit dataset-wide "
                "overview. Select charts only when explicitly requested. Cover every requested part "
                "without unrelated analyses. Use empty strings for unused fields, empty columns "
                "for all relevant columns, and pearson unless another correlation is requested."
            )},
            {"role": "user", "content": json.dumps({"rows": len(df), "schema": schema, "question": question},
                                                  ensure_ascii=False, separators=(",", ":"))},
        ],
        settings=planner_settings,
        response_format=PLAN_RESPONSE_FORMAT,
    )["choices"][0]["message"]["content"]
    try:
        plan = json.loads(plan_content)
        if not isinstance(plan, dict) or not isinstance(plan.get("analyses"), list) or not isinstance(plan.get("charts"), list):
            raise ValueError("Invalid plan shape")
    except (TypeError, ValueError):
        raise ExternalServiceError("Invalid analysis plan.", kind="invalid_response", provider=settings.provider) from None
    if len(plan["analyses"]) > MAX_PLAN_ANALYSES or len(plan["charts"]) > MAX_PLAN_CHARTS:
        raise ExternalServiceError("Analysis plan exceeds the response budget.", kind="request_too_large", provider=settings.provider)

    evidence: list[dict] = []
    charts: list[ChartResult] = []
    if plan.get("overview") or (not plan["analyses"] and not plan["charts"]):
        evidence.append({"tool": "dataset_overview", "output": execute_tool("dataset_overview", df)})
    seen: set[str] = set()
    for item in plan["analyses"]:
        if not isinstance(item, dict):
            continue
        arguments = {
            "method": item.get("method"),
            "columns": item.get("columns") or None,
            "group_by": item.get("group_by") or None,
            "correlation_method": item.get("correlation_method") or "pearson",
        }
        signature = json.dumps(arguments, sort_keys=True, ensure_ascii=False)
        if signature in seen:
            continue
        seen.add(signature)
        evidence.append({"tool": "analyze_data", "arguments": arguments,
                         "output": execute_tool("analyze_data", df, arguments)})
    for item in plan["charts"]:
        if not isinstance(item, dict):
            continue
        arguments = {"chart_type": item.get("chart_type"), "x": item.get("x") or None,
                     "y": item.get("y") or None, "group_by": item.get("group_by") or None}
        signature = json.dumps(arguments, sort_keys=True, ensure_ascii=False)
        if signature in seen:
            continue
        seen.add(signature)
        result = execute_tool("create_chart", df, arguments)
        if result.get("type") == "chart":
            charts.append(ChartResult(type=result["chart_type"], title=result["title"], path=result["path"]))
        evidence.append({"tool": "create_chart", "arguments": arguments, "output": result})

    answer_settings = replace(settings, temperature=0.2, max_tokens=min(settings.max_tokens, 3000),
                              reasoning_effort="medium")
    writer_input = json.dumps({"question": question, "rows": len(df), "tool_results": evidence},
                              ensure_ascii=False, default=str, separators=(",", ":"))
    if len(writer_input) > MAX_WRITER_INPUT_CHARS:
        raise ExternalServiceError("Computed results exceed the response budget.", kind="request_too_large", provider=settings.provider)
    final = chat_completion(
        [
            {"role": "system", "content": (
                "Answer in the user's language using only the computed tool results. "
                "Address every requested part, cite the exact column names and relevant numbers, "
                "and explain uncertainty and statistical limitations. Correlation does not establish "
                "causation. If a computation failed, say what could not be computed. Never invent data. "
                "Keep the answer concise and clear."
            )},
            {"role": "user", "content": writer_input},
        ],
        settings=answer_settings,
    )["choices"][0]["message"]["content"]
    return _response(final, charts)


def run_agent(
    df: pd.DataFrame,
    question: str,
    *,
    completion: Callable | None = None,
    settings: LLMSettings | None = None,
    max_rounds: int = 6,
) -> AgentResponse:
    """Run all requested tools until the model returns a final Markdown answer."""
    if df.empty:
        raise ValueError("The dataset is empty.")
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    if completion is None:
        settings = settings or LLMSettings.from_env()
        if settings.provider == "Groq" and settings.model == "openai/gpt-oss-120b" and not settings.personal:
            return _run_planned_groq_agent(df, question, settings)
    complete = completion or partial(chat_completion, settings=settings)
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
