"""
Document Schemas
Pydantic models for document-related requests/responses
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DocumentBase(BaseModel):
    """Base document schema"""
    filename: str
    file_type: str


class DocumentResponse(DocumentBase):
    """Schema for document response"""
    id: int
    original_filename: str
    file_path: str
    file_size: int
    mime_type: str
    word_count: Optional[int] = None
    extracted_text: Optional[str] = None
    created_at: datetime
    owner_id: int
    
    class Config:
        orm_mode = True


class DocumentList(BaseModel):
    """Schema for list of documents"""
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int


class DocumentStats(BaseModel):
    """Schema for document statistics"""
    total_documents: int
    total_words: int
    total_size_bytes: int
    total_size_mb: float
    file_types: dict
