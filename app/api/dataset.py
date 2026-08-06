from fastapi import APIRouter, HTTPException

from app.loaders.pandas_loader import load_data
from app.schemas.dataset_schema import DatasetInfoResponse
from app.services.file_service import get_file_path


router = APIRouter(prefix="/files", tags=["Dataset"])


@router.get("/{file_id}", response_model=DatasetInfoResponse)
def get_dataset_info(file_id: str):
    try:
        path = get_file_path(file_id)
        frame = load_data(path)
        return {
            "file_id": file_id,
            "filename": path.name,
            "file_type": path.suffix.lower(),
            "rows": len(frame),
            "columns": len(frame.columns),
            "column_names": frame.columns.tolist(),
        }
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="File not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
