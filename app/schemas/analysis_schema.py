from pydantic import BaseModel

from app.schemas.agent_schema import AgentResponse


class AnalyzeRequest(BaseModel):
    file_id: str
    question: str


class AnalyzeResponse(AgentResponse):
    file_id: str
    question: str
