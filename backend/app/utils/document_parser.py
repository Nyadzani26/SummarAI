"""
Document Parser Utilities
Extract text from various document formats
"""

import os
from typing import Dict, Optional
from pathlib import Path
import PyPDF2
from docx import Document as DocxDocument
import mimetypes


def get_file_mime_type(file_path: str) -> str:
    """
    Get MIME type of a file
    
    Args:
        file_path: Path to the file
    
    Returns:
        MIME type string
    """
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or "application/octet-stream"


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to PDF file
    
    Returns:
        Extracted text content
    
    Raises:
        Exception: If PDF extraction fails
    """
    try:
        text_content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            # Extract text from each page
            for page in pdf_reader.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        return "\n\n".join(text_content)
    
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_path: str) -> str:
    """
    Extract text from DOCX file
    
    Args:
        file_path: Path to DOCX file
    
    Returns:
        Extracted text content
    
    Raises:
        Exception: If DOCX extraction fails
    """
    try:
        doc = DocxDocument(file_path)
        
        # Extract text from all paragraphs
        text_content = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_content.append(paragraph.text)
        
        return "\n\n".join(text_content)
    
    except Exception as e:
        raise Exception(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_txt(file_path: str) -> str:
    """
    Extract text from TXT file
    
    Args:
        file_path: Path to TXT file
    
    Returns:
        Text content
    
    Raises:
        Exception: If TXT reading fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        try:
            with open(file_path, 'r', encoding='latin-1') as file:
                return file.read()
        except Exception as e:
            raise Exception(f"Failed to read TXT file: {str(e)}")
    except Exception as e:
        raise Exception(f"Failed to extract text from TXT: {str(e)}")


def extract_text_from_file(file_path: str, file_type: str) -> Dict[str, any]:
    """
    Extract text from any supported file type
    
    Args:
        file_path: Path to the file
        file_type: File extension (pdf, docx, txt)
    
    Returns:
        Dictionary with extracted text and metadata
    
    Raises:
        ValueError: If file type is not supported
        Exception: If extraction fails
    """
    file_type = file_type.lower().replace('.', '')
    
    # Extract text based on file type
    if file_type == 'pdf':
        extracted_text = extract_text_from_pdf(file_path)
    elif file_type in ['docx', 'doc']:
        extracted_text = extract_text_from_docx(file_path)
    elif file_type == 'txt':
        extracted_text = extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
    
    # Calculate word count
    word_count = len(extracted_text.split())
    
    # Calculate character count
    char_count = len(extracted_text)
    
    return {
        "text": extracted_text,
        "word_count": word_count,
        "char_count": char_count,
        "file_type": file_type
    }


def validate_file_size(file_size: int, max_size_mb: int = 10) -> bool:
    """
    Validate file size
    
    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB
    
    Returns:
        True if valid, False otherwise
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size <= max_size_bytes


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions
    
    Returns:
        True if valid, False otherwise
    """
    file_ext = Path(filename).suffix.lower().replace('.', '')
    return file_ext in [ext.lower().replace('.', '') for ext in allowed_extensions]