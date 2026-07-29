from pathlib import Path
import shutil
import uuid


UPLOAD_DIR = Path("uploads")


def save_file(file):
    """
    Save an uploaded file and return its file ID and path.
    """

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

    return file_id, file_path