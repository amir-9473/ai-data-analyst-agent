from pathlib import Path
from shutil import copyfileobj
from uuid import UUID, uuid4


UPLOAD_DIR = Path(__file__).resolve().parents[2] / "uploads"
SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".json"}


def save_file(file) -> dict:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension or 'unknown'}")
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    file_id = str(uuid4())
    path = UPLOAD_DIR / f"{file_id}{extension}"
    with path.open("wb") as buffer:
        copyfileobj(file.file, buffer)
    return {"file_id": file_id, "filename": file.filename, "file_path": path}


def get_file_path(file_id: str) -> Path:
    try:
        safe_id = str(UUID(file_id))
    except ValueError as exc:
        raise FileNotFoundError(file_id) from exc
    match = next(UPLOAD_DIR.glob(f"{safe_id}.*"), None)
    if not match:
        raise FileNotFoundError(file_id)
    return match
