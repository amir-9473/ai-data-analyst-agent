from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".json",
}


def load_data(file_path: str | Path) -> pd.DataFrame:
    """
    Load a supported data file into a pandas DataFrame.
    """

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = file_path.suffix.lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}"
        )

    if extension == ".csv":
        return pd.read_csv(file_path)

    if extension == ".xlsx":
        return pd.read_excel(file_path)

    if extension == ".json":
        return pd.read_json(file_path)

    raise ValueError(
        f"Unsupported file type: {extension}"
    )
    

def get_data_info(
    df: pd.DataFrame,
    file_path: str | Path,
) -> dict:
    """
    Return basic metadata about a loaded dataset.
    """

    file_path = Path(file_path)

    return {
        "filename": file_path.name,
        "file_type": file_path.suffix.lower(),
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": df.columns.tolist(),
    }