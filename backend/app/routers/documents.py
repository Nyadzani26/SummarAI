"""
Document Routes
Endpoints for document upload and management
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.document import (
    DocumentResponse,
    DocumentList,
    DocumentStats
)
from app.services.document_service import (
    create_document,
    get_user_documents,
    get_document_by_id,
    delete_document,
    get_document_stats
)
from app.dependencies import get_current_active_user
from app.models.user import User


router = APIRouter()


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Upload a new document
    
    - **file**: PDF, DOCX, or TXT file (max 10MB)
    
    Returns document metadata and extracted text info
    Requires verified email to upload documents
    """
    document = create_document(db, file, current_user)
    return document


@router.get("/", response_model=DocumentList)
async def list_documents(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all documents for current user
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    
    Returns list of user's documents
    """
    documents = get_user_documents(db, current_user.id, skip, limit)
    total = len(documents)
    
    return {
        "documents": documents,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/stats", response_model=DocumentStats)
async def get_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get document statistics for current user
    
    Returns total documents, words, file sizes, and file type breakdown
    """
    stats = get_document_stats(db, current_user.id)
    return stats


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific document by ID
    
    - **document_id**: Document ID
    
    Returns document details including extracted text
    """
    document = get_document_by_id(db, document_id, current_user.id)
    return document


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document_endpoint(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a document
    
    - **document_id**: Document ID
    
    Removes document from database and deletes file from disk
    """
    delete_document(db, document_id, current_user.id)
    return None