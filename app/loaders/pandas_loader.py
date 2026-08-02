from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {
    ".csv",
    ".xlsx",
    ".json",
}


def load_data(
    file_path: str | Path,
) -> pd.DataFrame:

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