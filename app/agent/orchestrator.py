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

from app.tools.visualization import (
    create_histogram,
)

from app.tools.dataset_info import (
    list_columns,
    dataset_overview,
    column_information,
)

from app.schemas.agent_schema import (
    AgentResponse,
)

# ==========================================================
# Tool Definitions
# ==========================================================

TOOLS = [


{
    "type": "function",

    "function": {

        "name": "list_columns",

        "description": (
            "Return all column names "
            "available in the dataset."
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

        "name": "dataset_overview",

        "description": (
            "Return basic information "
            "about dataset size "
            "including rows and columns."
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

        "name": "column_information",

        "description": (
            "Return detailed information "
            "about a specific column."
        ),

        "parameters": {

            "type": "object",

            "properties": {

                "column_name": {

                    "type": "string",

                    "description": (
                        "Column name "
                        "to inspect."
                    ),
                },

            },

            "required": [
                "column_name"
            ],
        },
    },
},
    # ------------------------------------------------------
    # Statistics Tool
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Missing Values Tool
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Correlation Tool
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Visualization Tool
    # ------------------------------------------------------

    {
        "type": "function",

        "function": {

            "name": (
                "create_histogram"
            ),

            "description": (
                "Create a histogram "
                "for a numeric dataset "
                "column."
            ),

            "parameters": {

                "type": "object",

                "properties": {

                    "column_name": {

                        "type": "string",

                        "description": (
                            "The numeric "
                            "column to "
                            "visualize."
                        ),
                    },
                },

                "required": [
                    "column_name"
                ],
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
    arguments: dict | None = None,
) -> dict:

    """
    Execute the selected analysis tool.

    Parameters
    ----------
    tool_name:
        Name of the tool selected by the LLM.

    df:
        Dataset to analyze.

    arguments:
        Arguments provided by the LLM
        for the selected tool.

    Returns
    -------
    dict
        Tool execution result.
    """

    # ------------------------------------------------------
    # Default Arguments
    # ------------------------------------------------------

    if arguments is None:

        arguments = {}


    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    if tool_name == (
        "calculate_statistics"
    ):

        return calculate_statistics(
            df
        )


    # ------------------------------------------------------
    # Missing Values
    # ------------------------------------------------------

    if tool_name == (
        "analyze_missing_values"
    ):

        return analyze_missing_values(
            df
        )


    # ------------------------------------------------------
    # Correlation
    # ------------------------------------------------------

    if tool_name == (
        "calculate_correlation"
    ):

        return calculate_correlation(
            df
        )


    if tool_name == "list_columns":

        return list_columns(
            df
        )



    if tool_name == "dataset_overview":

        return dataset_overview(
            df
        )


    if tool_name == "column_information":

        column_name = arguments.get(
            "column_name"
        )

        return column_information(
            df=df,
            column_name=column_name,
        )


    # ------------------------------------------------------
    # Visualization
    # ------------------------------------------------------

    if tool_name == (
        "create_histogram"
    ):

        column_name = arguments.get(
            "column_name"
        )

        if not column_name:

            return {

                "error": (
                    "column_name "
                    "is required."
                )

            }

        try:

            chart_path = (
                create_histogram(

                    df=df,

                    column_name=column_name,
                )
            )

            return {

                "type": "chart",

                "chart_path": (
                    chart_path
                ),

                "message": (
                    "Histogram created "
                    "successfully."
                ),

            }

        except ValueError as e:

            return {

                "error": str(e)

            }


    # ------------------------------------------------------
    # Unknown Tool
    # ------------------------------------------------------

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

    """
    Run the data analyst agent.

    The agent sends the user question to the LLM,
    allows the LLM to select an analysis tool,
    executes the selected tool, and sends the
    result back to the LLM to generate the
    final natural language answer.
    """

    # ------------------------------------------------------
    # Initial Messages
    # ------------------------------------------------------

    messages = [

        {
            "role": "system",

            "content": (
                "You are a data analyst "
                "assistant. "
                "Use the available tools "
                "to analyze the dataset. "
                "Do not invent data. "
                "If the user asks for a "
                "histogram or distribution "
                "of a numeric column, use "
                "the create_histogram tool."
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
    
    print("=" * 50)
    print("FIRST RESPONSE")
    print(response)
    print("=" * 50)


    # ------------------------------------------------------
    # Extract Assistant Message
    # ------------------------------------------------------

    message = (
        response["choices"][0]
        ["message"]
    )


    # ------------------------------------------------------
    # Check Tool Calls
    # ------------------------------------------------------

    tool_calls = (
        message.get(
            "tool_calls"
        )
    )


    # ------------------------------------------------------
    # No Tool Call
    # ------------------------------------------------------

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



    tool_arguments = json.loads(

        tool_call["function"]
        ["arguments"]

)


    # ------------------------------------------------------
    # Extract Tool Arguments
    # ------------------------------------------------------

    raw_arguments = (
        tool_call["function"]
        .get(
            "arguments",
            "{}",
        )
    )


    try:

        arguments = json.loads(
            raw_arguments
        )

    except json.JSONDecodeError:

        arguments = {}


    # ------------------------------------------------------
    # Execute Tool
    # ------------------------------------------------------

    tool_result = execute_tool(

        tool_name=tool_name,

        df=df,

        arguments=tool_arguments,
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
    
    print("=" * 50)
    print("FINAL RESPONSE")
    print(final_response)
    print("=" * 50)


    # ------------------------------------------------------
    # Return Final Answer
    # ------------------------------------------------------

    final_message = (
        final_response["choices"][0]
        ["message"]
    )


    content = (
        final_message.get(
            "content"
        )
    )


    # ------------------------------------------------------
    # Chart Result
    # ------------------------------------------------------

    if isinstance(
        tool_result,
        dict
    ):

        if (
            tool_result.get("type")
            ==
            "chart"
        ):

            return AgentResponse(

                type="chart",

                answer=(

                    tool_result.get(
                        "message",
                        "Chart created."
                    )

                ),

                chart_path=(

                    tool_result.get(
                        "chart_path"
                    )

                ),

            )


    # ------------------------------------------------------
    # Text Result
    # ------------------------------------------------------

    return AgentResponse(

        type="text",

        answer=(

            content
            or
            "Analysis completed."

        ),

    )





'''    return (

        final_response["choices"][0]

        ["message"]

        ["content"]

    )'''