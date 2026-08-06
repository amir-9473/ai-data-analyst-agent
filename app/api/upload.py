from fastapi import APIRouter, File, HTTPException, UploadFile

from app.schemas.file_schema import FileUploadResponse
from app.services.file_service import save_file


router = APIRouter(tags=["Files"])


@router.post("/upload", response_model=FileUploadResponse)
def upload_file(file: UploadFile = File(...)):
    try:
        info = save_file(file)
        return {"filename": info["filename"], "file_id": info["file_id"], "status": "uploaded"}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
