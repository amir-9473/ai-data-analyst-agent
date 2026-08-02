from pathlib import Path
import shutil
import uuid


UPLOAD_DIR = Path("uploads")


def save_file(file):

    UPLOAD_DIR.mkdir(
        exist_ok=True
    )

    file_id = str(
        uuid.uuid4()
    )

    extension = Path(
        file.filename
    ).suffix.lower()

    stored_filename = (
        f"{file_id}{extension}"
    )

    file_path = (
        UPLOAD_DIR / stored_filename
    )

    with file_path.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )

    return {
        "file_id": file_id,
        "filename": file.filename,
        "file_path": file_path,
    }
    


def get_file_path(
    file_id: str,
) -> Path:

    matches = list(
        UPLOAD_DIR.glob(
            f"{file_id}.*"
        )
    )

    if not matches:

        raise FileNotFoundError(
            f"File not found: "
            f"{file_id}"
        )

    return matches[0]