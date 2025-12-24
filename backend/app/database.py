"""
Database Configuration
SQLAlchemy setup and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings


# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DATABASE_ECHO,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,
    max_overflow=20
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency for getting database sessions
    
    Usage in FastAPI endpoints:
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database
    Create all tables
    """
    # Import all models here to ensure they're registered with Base
    from app.models import user, document, summary  # noqa
    
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created")


# Auto-initialize database on module import
try:
    print("[*] Auto-initializing database...")
    from app.models import user, document, summary  # noqa
    Base.metadata.create_all(bind=engine)
    print("[+] Database tables created successfully!")
except Exception as e:
    print(f"[!] Database initialization error: {e}")
    import traceback
    traceback.print_exc()
