"""
Summary Routes
Endpoints for AI-powered document summarization
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.schemas.summary import (
    SummaryCreate,
    SummaryResponse,
    SummaryList
)
from app.services.summarization_service import create_summary
from app.dependencies import get_current_active_user
from app.models.user import User
from app.models.summary import Summary


router = APIRouter()


@router.post("/generate", response_model=SummaryResponse, status_code=status.HTTP_201_CREATED)
async def generate_summary(
    summary_data: SummaryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate AI summary for a document
    
    - **document_id**: ID of document to summarize
    - **max_length**: Maximum summary length (default: 150)
    - **min_length**: Minimum summary length (default: 50)
    
    Uses BART model to generate abstractive summary
    Requires verified email to generate summaries
    """
    try:
        summary = create_summary(
            db=db,
            document_id=summary_data.document_id,
            user_id=current_user.id,
            max_length=summary_data.max_length,
            min_length=summary_data.min_length
        )
        return summary
    except Exception as e:
        print(f"[!] Error generating summary: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.get("/", response_model=SummaryList)
async def list_summaries(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all summaries for current user
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    
    Returns list of user's generated summaries
    """
    summaries = db.query(Summary)\
        .filter(Summary.owner_id == current_user.id)\
        .order_by(Summary.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    total = db.query(Summary).filter(Summary.owner_id == current_user.id).count()
    
    return {
        "summaries": summaries,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(
    summary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific summary by ID
    
    - **summary_id**: Summary ID
    
    Returns summary details with full text
    """
    summary = db.query(Summary)\
        .filter(Summary.id == summary_id)\
        .first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    # Check ownership
    if summary.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return summary


@router.delete("/{summary_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(
    summary_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a summary
    
    - **summary_id**: Summary ID
    
    Removes summary from database
    """
    summary = db.query(Summary)\
        .filter(Summary.id == summary_id)\
        .first()
    
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Summary not found"
        )
    
    # Check ownership
    if summary.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    db.delete(summary)
    db.commit()
    
    return None


@router.get("/document/{document_id}", response_model=SummaryList)
async def get_document_summaries(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all summaries for a specific document
    
    - **document_id**: Document ID
    
    Returns all summaries generated for this document
    """
    summaries = db.query(Summary)\
        .filter(
            Summary.document_id == document_id,
            Summary.owner_id == current_user.id
        )\
        .order_by(Summary.created_at.desc())\
        .all()
    
    return {
        "summaries": summaries,
        "total": len(summaries),
        "skip": 0,
        "limit": len(summaries)
    }