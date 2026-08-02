from pydantic import BaseModel


class DatasetProfileResponse(BaseModel):

    rows: int

    columns: int

    column_names: list[str]

    numeric_columns: list[str]

    categorical_columns: list[str]

    missing_values: dict[str, int]

    duplicate_rows: int