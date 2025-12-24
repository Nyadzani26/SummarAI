"""
File Storage Utilities
Handle file uploads and storage
"""

import os
import uuid
from pathlib import Path
from datetime import datetime
from typing import Tuple
from fastapi import UploadFile


def generate_unique_filename(original_filename: str) -> str:
    """
    Generate unique filename to avoid collisions
    
    Args:
        original_filename: Original uploaded filename
    
    Returns:
        Unique filename with timestamp and UUID
    """
    # Get file extension
    file_ext = Path(original_filename).suffix
    
    # Generate unique name: timestamp_uuid_originalname
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    base_name = Path(original_filename).stem[:50]  # Limit length
    
    return f"{timestamp}_{unique_id}_{base_name}{file_ext}"


def save_upload_file(upload_file: UploadFile, upload_dir: str) -> Tuple[str, str]:
    """
    Save uploaded file to disk
    
    Args:
        upload_file: FastAPI UploadFile object
        upload_dir: Directory to save files
    
    Returns:
        Tuple of (file_path, filename)
    
    Raises:
        Exception: If file save fails
    """
    try:
        # Ensure upload directory exists
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = generate_unique_filename(upload_file.filename)
        
        # Full file path
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = upload_file.file.read()
            buffer.write(content)
        
        return file_path, unique_filename
    
    except Exception as e:
        raise Exception(f"Failed to save file: {str(e)}")


def delete_file(file_path: str) -> bool:
    """
    Delete a file from disk
    
    Args:
        file_path: Path to the file
    
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def get_file_size(file_path: str) -> int:
    """
    Get file size in bytes
    
    Args:
        file_path: Path to the file
    
    Returns:
        File size in bytes
    """
    return os.path.getsize(file_path)