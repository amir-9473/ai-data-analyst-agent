from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.loaders.pandas_loader import load_data
from app.schemas.dataset_schema import DatasetInfoResponse


router = APIRouter(
    prefix="/files",
    tags=["Dataset"]
)


UPLOAD_DIR = Path("uploads")


@router.get(
    "/{file_id}",
    response_model=DatasetInfoResponse
)
def get_dataset_info(
    file_id: str
):

    matching_files = list(
        UPLOAD_DIR.glob(
            f"{file_id}.*"
        )
    )

    if not matching_files:

        raise HTTPException(
            status_code=404,
            detail="File not found"
        )

    file_path = matching_files[0]

    try:

        df = load_data(
            file_path
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc)
        )

    return {

        "file_id": file_id,

        "filename": file_path.name,

        "file_type": file_path.suffix.lower(),

        "rows": len(df),

        "columns": len(df.columns),

        "column_names": df.columns.tolist(),

    }