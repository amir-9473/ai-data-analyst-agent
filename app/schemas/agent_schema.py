# ==========================================================
# Agent Response Schema
# ==========================================================

from pydantic import BaseModel


class AgentResponse(
    BaseModel
):

    """
    Standard response format
    for AI Data Analyst Agent.
    """

    type: str

    answer: str

    chart_path: str | None = None