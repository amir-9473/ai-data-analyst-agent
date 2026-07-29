from pydantic import BaseModel


class FileUploadResponse(BaseModel):
    filename: str
    file_id: str
    status: str