from pydantic import BaseModel


class DatasetInfoResponse(BaseModel):

    file_id: str

    filename: str

    file_type: str

    rows: int

    columns: int

    column_names: list[str]