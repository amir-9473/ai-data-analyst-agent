from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.loaders.pandas_loader import load_data
from app.profiling.profiler import profile_dataset
from app.schemas.profile_schema import DatasetProfileResponse


router = APIRouter(
    prefix="/profile",
    tags=["Profiling"]
)


UPLOAD_DIR = Path("uploads")


@router.get(
    "/{file_id}",
    response_model=DatasetProfileResponse,
)
def get_profile(file_id: str):

    files = list(
        UPLOAD_DIR.glob(f"{file_id}.*")
    )

    if not files:
        raise HTTPException(
            status_code=404,
            detail="Dataset not found",
        )

    df = load_data(files[0])

    return profile_dataset(df)