"""
Summary Model
Stores generated summaries
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Summary(Base):
    """Generated summary model"""
    
    __tablename__ = "summaries"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Summary Content
    summary_text = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=True)
    compression_ratio = Column(Float, nullable=True)  # original_words / summary_words
    
    # Generation Parameters
    model_name = Column(String, default="facebook/bart-large-cnn")
    max_length = Column(Integer, default=150)
    min_length = Column(Integer, default=30)
    generation_time = Column(Float, nullable=True)  # Seconds
    
    # Export Info
    export_format = Column(String, nullable=True)  # pdf, docx, txt
    export_path = Column(String, nullable=True)
    email_sent = Column(DateTime(timezone=True), nullable=True)
    
    # Foreign Keys
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    document = relationship("Document", back_populates="summaries")
    owner = relationship("User", back_populates="summaries")
    
    def __repr__(self):
        return f"<Summary(id={self.id}, document_id={self.document_id}, owner_id={self.owner_id})>"
