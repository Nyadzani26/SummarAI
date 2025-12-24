"""
Document Service
Business logic for document management
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status, UploadFile
from typing import List, Optional
from pathlib import Path

from app.models.document import Document
from app.models.user import User
from app.config import settings
from app.utils.storage import save_upload_file, delete_file, get_file_size
from app.utils.document_parser import (
    extract_text_from_file,
    validate_file_size,
    validate_file_extension
)


def validate_upload_file(file: UploadFile) -> None:
    """
    Validate uploaded file
    
    Args:
        file: Uploaded file
    
    Raises:
        HTTPException: If validation fails
    """
    # Check if file exists
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    # Validate file extension
    if not validate_file_extension(file.filename, settings.ALLOWED_EXTENSIONS):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(settings.ALLOWED_EXTENSIONS)}"
        )
    
    # Read file size
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    # Validate file size
    max_size_mb = settings.MAX_FILE_SIZE // (1024 * 1024)
    if not validate_file_size(file_size, max_size_mb):
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Maximum size: {max_size_mb}MB"
        )


def create_document(
    db: Session,
    file: UploadFile,
    current_user: User
) -> Document:
    """
    Upload and process a document
    
    Args:
        db: Database session
        file: Uploaded file
        current_user: Current authenticated user
    
    Returns:
        Created document object
    
    Raises:
        HTTPException: If upload or processing fails
    """
    # Validate file
    validate_upload_file(file)
    
    try:
        # Save file to disk
        file_path, unique_filename = save_upload_file(file, settings.UPLOAD_DIR)
        
        # Get file info
        file_size = get_file_size(file_path)
        file_ext = Path(file.filename).suffix.lower().replace('.', '')
        
        # Extract text from document
        extracted_data = extract_text_from_file(file_path, file_ext)
        
        # Get MIME type
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file.filename)
        if not mime_type:
            mime_type = "application/octet-stream"
        
        # Create document record
        document = Document(
            filename=unique_filename,  # Stored filename
            original_filename=file.filename,  # Original upload name
            file_path=file_path,
            file_type=file_ext,
            file_size=file_size,
            mime_type=mime_type,
            extracted_text=extracted_data["text"],
            word_count=extracted_data["word_count"],
            owner_id=current_user.id
        )
        
        db.add(document)
        db.commit()
        db.refresh(document)
        
        return document
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Clean up file if database operation fails
        if 'file_path' in locals():
            delete_file(file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process document: {str(e)}"
        )


def get_user_documents(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Document]:
    """
    Get all documents for a user
    
    Args:
        db: Database session
        user_id: User ID
        skip: Number of records to skip
        limit: Maximum number of records to return
    
    Returns:
        List of documents
    """
    return db.query(Document)\
        .filter(Document.owner_id == user_id)\
        .order_by(Document.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()


def get_document_by_id(
    db: Session,
    document_id: int,
    user_id: int
) -> Document:
    """
    Get a specific document by ID
    
    Args:
        db: Database session
        document_id: Document ID
        user_id: User ID (for ownership check)
    
    Returns:
        Document object
    
    Raises:
        HTTPException: If document not found or access denied
    """
    document = db.query(Document)\
        .filter(Document.id == document_id)\
        .first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Check ownership
    if document.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return document


def delete_document(
    db: Session,
    document_id: int,
    user_id: int
) -> bool:
    """
    Delete a document
    
    Args:
        db: Database session
        document_id: Document ID
        user_id: User ID (for ownership check)
    
    Returns:
        True if deleted successfully
    
    Raises:
        HTTPException: If document not found or access denied
    """
    # Get document
    document = get_document_by_id(db, document_id, user_id)
    
    # Delete file from disk
    if document.file_path:
        delete_file(document.file_path)
    
    # Delete from database
    db.delete(document)
    db.commit()
    
    return True


def get_document_stats(db: Session, user_id: int) -> dict:
    """
    Get document statistics for a user
    
    Args:
        db: Database session
        user_id: User ID
    
    Returns:
        Dictionary with statistics
    """
    documents = db.query(Document)\
        .filter(Document.owner_id == user_id)\
        .all()
    
    total_documents = len(documents)
    total_words = sum(doc.word_count or 0 for doc in documents)
    total_size = sum(doc.file_size or 0 for doc in documents)
    
    # Count by file type
    file_types = {}
    for doc in documents:
        file_types[doc.file_type] = file_types.get(doc.file_type, 0) + 1
    
    return {
        "total_documents": total_documents,
        "total_words": total_words,
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "file_types": file_types
    }