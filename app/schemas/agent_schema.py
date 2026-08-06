from pydantic import BaseModel, Field


class ChartResult(BaseModel):
    type: str
    title: str
    path: str


class AgentResponse(BaseModel):
    type: str
    answer: str
    charts: list[ChartResult] = Field(default_factory=list)
    chart_path: str | None = None
