from pydantic import BaseModel


class AnalyzeRequest(
    BaseModel
):

    file_id: str

    question: str



class AnalyzeResponse(
    BaseModel
):

    file_id: str

    question: str

    type: str

    answer: str

    chart_path: str | None = None