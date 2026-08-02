from fastapi import APIRouter, UploadFile, File

from app.services.file_service import save_file
from app.schemas.file_schema import FileUploadResponse


router = APIRouter()


@router.post(
    "/upload",
    response_model=FileUploadResponse
)
def upload_file(
    file: UploadFile = File(...)
):

    file_info = save_file(file)

    return {
        "filename": file_info["filename"],
        "file_id": file_info["file_id"],
        "status": "uploaded",
    }