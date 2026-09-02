from datetime import datetime
from typing import List
from pydantic import BaseModel


class DocumentResponse(BaseModel):
    id: str
    original_filename: str
    file_size: int
    status: str
    chunk_count: int
    created_at: datetime
    user_id: int

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    total: int
    documents: List[DocumentResponse]


class DocumentUploadResponse(BaseModel):
    message: str
    document_id: str
    original_filename: str
    chunks: int
    file_size: int
