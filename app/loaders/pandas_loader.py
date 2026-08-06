"""Load supported tabular formats from a path or uploaded file."""

import csv
from io import BytesIO, StringIO
from pathlib import Path

import pandas as pd


SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".json"}


def _content(source) -> bytes:
    if isinstance(source, (str, Path)):
        return Path(source).read_bytes()
    if hasattr(source, "getvalue"):
        return source.getvalue()
    position = source.tell() if hasattr(source, "tell") else None
    content = source.read()
    if position is not None:
        source.seek(position)
    return content


def _read_csv(content: bytes) -> pd.DataFrame:
    for encoding in ("utf-8-sig", "utf-8", "cp1256", "latin-1"):
        try:
            text = content.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover
        raise ValueError("Could not decode the CSV file.")

    sample = text[:8192]
    try:
        delimiter = csv.Sniffer().sniff(sample, delimiters=",;\t|\x1b").delimiter
    except csv.Error:
        counts = {candidate: sample.count(candidate) for candidate in (",", ";", "\t", "|", "\x1b")}
        delimiter = max(counts, key=counts.get) if max(counts.values()) else ","
    return pd.read_csv(StringIO(text), sep=delimiter)


def load_data(source: str | Path | object) -> pd.DataFrame:
    name = str(source) if isinstance(source, (str, Path)) else getattr(source, "name", "")
    extension = Path(name).suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension or 'unknown'}")
    if isinstance(source, (str, Path)) and not Path(source).exists():
        raise FileNotFoundError(f"File not found: {source}")

    content = _content(source)
    if extension == ".csv":
        frame = _read_csv(content)
    elif extension == ".xlsx":
        frame = pd.read_excel(BytesIO(content))
    else:
        frame = pd.read_json(BytesIO(content))

    frame.columns = [str(column).strip() for column in frame.columns]
    # Remove index columns accidentally exported by pandas or spreadsheet tools.
    generated_indexes = [
        column
        for column in frame.columns
        if column.casefold().startswith("unnamed:")
        and frame[column].reset_index(drop=True).equals(pd.Series(range(len(frame)), name=column))
    ]
    if generated_indexes:
        frame = frame.drop(columns=generated_indexes)
    return frame
