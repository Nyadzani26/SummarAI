"""
Application Configuration
Loads settings from environment variables
"""

try:
    # Pydantic v2
    from pydantic_settings import BaseSettings
except ImportError:
    # Pydantic v1
    from pydantic import BaseSettings

from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # App Info
    APP_NAME: str = "Document Summarizer"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    ENVIRONMENT: str = "development"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    DATABASE_ECHO: bool = False
    
    # Security & JWT
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "test@example.com"
    SMTP_PASSWORD: str = "testpassword"
    SMTP_FROM: str = "noreply@documentsummarizer.com"  # Changed from EmailStr
    SMTP_FROM_NAME: str = "Document Summarizer"
    
    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"
    
    # File Upload
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["pdf", "docx", "txt"]
    UPLOAD_DIR: str = "/tmp/uploads"  # Use /tmp for cloud deployments
    
    # ML Model
    MODEL_PATH: str = "/tmp/models"  # Use /tmp for cloud deployments
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure upload directory exists
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)


# Global settings instance
settings = Settings()
