"""
Summary Schemas
Pydantic models for summary-related requests/responses
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class SummaryCreate(BaseModel):
    """Schema for creating a summary"""
    document_id: int
    max_length: int = Field(default=400, ge=100, le=1024, description="Max summary length in tokens (≈300 words)")
    min_length: int = Field(default=150, ge=50, le=400, description="Min summary length in tokens (≈110 words)")
    export_format: Optional[str] = Field(default="txt", description="Export format: pdf, docx, txt")


class SummaryResponse(BaseModel):
    """Schema for summary response"""
    id: int
    summary_text: str
    word_count: Optional[int] = None
    compression_ratio: Optional[float] = None
    model_name: str
    generation_time: Optional[float] = None
    export_format: Optional[str] = None
    created_at: datetime
    document_id: int
    owner_id: int
    
    class Config:
        orm_mode = True


class SummaryList(BaseModel):
    """Schema for list of summaries"""
    summaries: List[SummaryResponse]
    total: int


class EmailSummary(BaseModel):
    """Schema for emailing a summary"""
    summary_id: int
    recipient_email: Optional[str] = None  # If None, send to user's email
