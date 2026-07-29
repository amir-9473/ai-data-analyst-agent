from pathlib import Path
import shutil


UPLOAD_DIR = Path("uploads")


def save_file(file):

    UPLOAD_DIR.mkdir(
        exist_ok=True
    )

    file_path = UPLOAD_DIR / file.filename


    with file_path.open("wb") as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    return file_path