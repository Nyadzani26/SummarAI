"""
Summarization Service
AI-powered text summarization using BART model
"""

import os
from typing import Dict, Optional
import torch
from transformers import BartForConditionalGeneration, BartTokenizer
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
import time

from app.models.summary import Summary
from app.models.document import Document
from app.config import settings


# Global model cache
_model = None
_tokenizer = None


def load_model():
    """
    Load BART model and tokenizer (lazy loading)
    
    Returns:
        Tuple of (model, tokenizer)
    """
    global _model, _tokenizer
    
    if _model is None or _tokenizer is None:
        print("[*] Loading BART model...")
        
        model_path = os.path.join(settings.MODEL_PATH, "facebook", "bart-large-cnn")
        
        # Check if model exists
        if not os.path.exists(model_path):
            print(f"[!] Model not found at {model_path}")
            print("Downloading model from HuggingFace (this may take a while)...")
            model_path = "facebook/bart-large-cnn"
        
        try:
            _tokenizer = BartTokenizer.from_pretrained(model_path)
            _model = BartForConditionalGeneration.from_pretrained(model_path)
            
            # Move to GPU if available
            device = "cuda" if torch.cuda.is_available() else "cpu"
            _model = _model.to(device)
            
            print(f"[+] Model loaded successfully on {device}")
        
        except Exception as e:
            print(f"[!] Failed to load model: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to load AI model: {str(e)}"
            )
    
    return _model, _tokenizer


def generate_summary(
    text: str,
    max_length: int = 400,  # Significantly increased (≈300 words)
    min_length: int = 150,  # Force longer summaries (≈110 words)
    do_sample: bool = False
) -> Dict[str, any]:
    """
    Generate summary using BART model
    
    Args:
        text: Input text to summarize
        max_length: Maximum summary length in tokens
        min_length: Minimum summary length in tokens
        do_sample: Whether to use sampling for generation
    
    Returns:
        Dictionary with summary and metadata
    """
    # Load model
    model, tokenizer = load_model()
    
    # Start timing
    start_time = time.time()
    
    # Tokenize input
    inputs = tokenizer(
        text,
        max_length=1024,
        truncation=True,
        return_tensors="pt"
    )
    
    # Move to same device as model
    device = next(model.parameters()).device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    # Generate summary with aggressive settings for longer output
    with torch.no_grad():
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=max_length,
            min_length=min_length,
            length_penalty=0.5,  # Very low penalty to encourage length
            num_beams=6,  # More beams for better quality
            early_stopping=False,  # Never stop early
            do_sample=False,
            no_repeat_ngram_size=3,
            forced_bos_token_id=0,  # Force generation to continue
            repetition_penalty=1.2  # Slight penalty for repetition
        )  
    # Decode summary
    summary_text = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    
    # Calculate generation time
    generation_time = time.time() - start_time
    
    # Calculate compression ratio
    original_words = len(text.split())
    summary_words = len(summary_text.split())
    compression_ratio = summary_words / original_words if original_words > 0 else 0
    
    return {
        "summary_text": summary_text,
        "generation_time": round(generation_time, 2),
        "original_length": original_words,
        "summary_length": summary_words,
        "compression_ratio": round(compression_ratio, 3)
    }


def chunk_text(text: str, max_chunk_size: int = 1000) -> list:
    """
    Split long text into chunks for summarization
    
    Args:
        text: Text to chunk
        max_chunk_size: Maximum words per chunk
    
    Returns:
        List of text chunks
    """
    words = text.split()
    chunks = []
    
    for i in range(0, len(words), max_chunk_size):
        chunk = " ".join(words[i:i + max_chunk_size])
        chunks.append(chunk)
    
    return chunks


def summarize_long_text(
    text: str,
    max_length: int = 400,  # Updated to match new defaults
    min_length: int = 150   # Updated to match new defaults
) -> Dict[str, any]:
    """
    Summarize long text by chunking if necessary
    
    Args:
        text: Long text to summarize
        max_length: Max summary length
        min_length: Min summary length
    
    Returns:
        Summary dictionary
    """
    word_count = len(text.split())
    
    # If text is short enough, summarize directly
    if word_count <= 1000:
        return generate_summary(text, max_length, min_length)
    
    # For long text, chunk and summarize
    print(f"[*] Long text detected ({word_count} words), using chunking strategy...")
    
    chunks = chunk_text(text, max_chunk_size=800)
    chunk_summaries = []
    
    for i, chunk in enumerate(chunks):
        print(f"[*] Processing chunk {i+1}/{len(chunks)}...")
        result = generate_summary(chunk, max_length=200, min_length=80)  # Increased chunk summary length
        chunk_summaries.append(result["summary_text"])
    
    # Combine chunk summaries
    combined_summary = " ".join(chunk_summaries)
    
    # Generate final summary from combined chunks
    print("[*] Generating final summary...")
    final_result = generate_summary(combined_summary, max_length, min_length)
    
    return final_result


def create_summary(
    db: Session,
    document_id: int,
    user_id: int,
    max_length: int = 150,
    min_length: int = 50
) -> Summary:
    """
    Create a summary for a document
    
    Args:
        db: Database session
        document_id: Document ID to summarize
        user_id: User ID (for ownership check)
        max_length: Maximum summary length
        min_length: Minimum summary length
    
    Returns:
        Created summary object
    
    Raises:
        HTTPException: If document not found or access denied
    """
    # Get document
    document = db.query(Document).filter(Document.id == document_id).first()
    
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
    
    # Check if document has text
    if not document.extracted_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document has no extracted text"
        )
    
    # Generate summary
    result = summarize_long_text(
        document.extracted_text,
        max_length=max_length,
        min_length=min_length
    )
    
    # Create summary record
    summary = Summary(
        document_id=document_id,
        owner_id=user_id,
        summary_text=result["summary_text"],
        word_count=result["summary_length"],  # Use word_count field
        compression_ratio=result["compression_ratio"],
        generation_time=result["generation_time"],
        max_length=max_length,
        min_length=min_length
    )
    
    db.add(summary)
    db.commit()
    db.refresh(summary)
    
    return summary