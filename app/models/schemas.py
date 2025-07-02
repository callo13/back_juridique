from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class FolderBase(BaseModel):
    name: str

class FolderCreate(FolderBase):
    pass

class FolderRead(FolderBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class DocumentBase(BaseModel):
    folder_id: int
    filename: str
    file_path: Optional[str] = None
    file_type: Optional[str] = None
    file_size: Optional[int] = None
    chunk_count: Optional[int] = 0
    processing_status: Optional[str] = "pending"

class DocumentCreate(DocumentBase):
    pass

class DocumentRead(DocumentBase):
    id: int
    created_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        orm_mode = True 