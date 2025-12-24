"""
Document Model
Stores uploaded document metadata
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Document(Base):
    """Uploaded document model"""
    
    __tablename__ = "documents"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Document Info
    filename = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=False)  # In bytes
    file_type = Column(String, nullable=False)  # pdf, docx, txt
    mime_type = Column(String, nullable=False)
    
    # Content
    extracted_text = Column(Text, nullable=True)  # Extracted text from document
    word_count = Column(Integer, nullable=True)
    
    # Foreign Key
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    owner = relationship("User", back_populates="documents")
    summaries = relationship("Summary", back_populates="document", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Document(id={self.id}, filename='{self.filename}', owner_id={self.owner_id})>"
