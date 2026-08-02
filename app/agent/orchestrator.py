# ==========================================================
# Data Analyst Agent
# ==========================================================

import json

import pandas as pd

from app.llm.client import (
    chat_completion,
)

from app.tools.statistics import (
    calculate_statistics,
)

from app.tools.missing_values import (
    analyze_missing_values,
)

from app.tools.correlation import (
    calculate_correlation,
)


# ==========================================================
# Tool Definitions
# ==========================================================

TOOLS = [

    {
        "type": "function",

        "function": {

            "name": (
                "calculate_statistics"
            ),

            "description": (
                "Calculate descriptive "
                "statistics for numeric "
                "columns."
            ),

            "parameters": {

                "type": "object",

                "properties": {},
            },
        },
    },

    {
        "type": "function",

        "function": {

            "name": (
                "analyze_missing_values"
            ),

            "description": (
                "Analyze missing values "
                "in all dataset columns."
            ),

            "parameters": {

                "type": "object",

                "properties": {},
            },
        },
    },

    {
        "type": "function",

        "function": {

            "name": (
                "calculate_correlation"
            ),

            "description": (
                "Calculate correlations "
                "between numeric columns."
            ),

            "parameters": {

                "type": "object",

                "properties": {},
            },
        },
    },
]


# ==========================================================
# Tool Dispatcher
# ==========================================================

def execute_tool(
    tool_name: str,
    df: pd.DataFrame,
) -> dict:

    if tool_name == (
        "calculate_statistics"
    ):

        return calculate_statistics(
            df
        )

    if tool_name == (
        "analyze_missing_values"
    ):

        return analyze_missing_values(
            df
        )

    if tool_name == (
        "calculate_correlation"
    ):

        return calculate_correlation(
            df
        )

    return {

        "error": (
            f"Unknown tool: "
            f"{tool_name}"
        )

    }


# ==========================================================
# Agent
# ==========================================================

def run_agent(
    df: pd.DataFrame,
    question: str,
) -> str:

    messages = [

        {
            "role": "system",

            "content": (
                "You are a data analyst "
                "assistant. "
                "Use the available tools "
                "to analyze the dataset. "
                "Do not invent data."
            ),
        },

        {
            "role": "user",

            "content": question,
        },

    ]

    # ------------------------------------------------------
    # First LLM Call
    # ------------------------------------------------------

    response = chat_completion(

        messages=messages,

        tools=TOOLS,
    )

    message = (
        response["choices"][0]
        ["message"]
    )

    # ------------------------------------------------------
    # Check Tool Call
    # ------------------------------------------------------

    tool_calls = (
        message.get(
            "tool_calls"
        )
    )

    if not tool_calls:

        return message.get(
            "content",
            "",
        )

    # ------------------------------------------------------
    # Execute First Tool
    # ------------------------------------------------------

    tool_call = tool_calls[0]

    tool_name = (
        tool_call["function"]
        ["name"]
    )

    tool_result = execute_tool(

        tool_name=tool_name,

        df=df,
    )

    # ------------------------------------------------------
    # Add Assistant Tool Call
    # ------------------------------------------------------

    messages.append(
        message
    )

    # ------------------------------------------------------
    # Add Tool Result
    # ------------------------------------------------------

    messages.append({

        "role": "tool",

        "tool_call_id": (
            tool_call["id"]
        ),

        "content": json.dumps(

            tool_result,

            ensure_ascii=False,

            default=str,
        ),

    })

    # ------------------------------------------------------
    # Final LLM Call
    # ------------------------------------------------------

    final_response = chat_completion(

        messages=messages,
    )

    return (

        final_response["choices"][0]

        ["message"]

        ["content"]

    )