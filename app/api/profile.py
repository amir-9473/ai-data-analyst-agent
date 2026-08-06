from fastapi import APIRouter, HTTPException

from app.loaders.pandas_loader import load_data
from app.profiling.profiler import profile_dataset
from app.schemas.profile_schema import DatasetProfileResponse
from app.services.file_service import get_file_path


router = APIRouter(prefix="/profile", tags=["Profiling"])


@router.get("/{file_id}", response_model=DatasetProfileResponse)
def get_profile(file_id: str):
    try:
        return profile_dataset(load_data(get_file_path(file_id)))
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Dataset not found") from exc
