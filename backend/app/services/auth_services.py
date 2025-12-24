"""
Authentication Service
Business logic for user authentication
"""

from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional

from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import hash_password, verify_password, create_verification_token


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email address"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create new user account
    
    Args:
        db: Database session
        user_data: User registration data
    
    Returns:
        Created user object
    
    Raises:
        HTTPException: If email already exists
    """
    # Check if email already exists
    existing_user = get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = hash_password(user_data.password)
    
    # Create verification token
    verification_token = create_verification_token(user_data.email)
    
    # Create user
    db_user = User(
        email=user_data.email,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        verification_token=verification_token,
        is_verified=False,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def authenticate_user(db: Session, email: str, password: str) -> User:
    """
    Authenticate user with email and password
    
    Args:
        db: Database session
        email: User's email
        password: User's password
    
    Returns:
        User object if authentication succeeds
    
    Raises:
        HTTPException: If authentication fails
    """
    user = get_user_by_email(db, email)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    return user


def verify_user_email(db: Session, token: str) -> User:
    """
    Verify user's email with token
    
    Args:
        db: Database session
        token: Verification token
    
    Returns:
        Verified user object
    
    Raises:
        HTTPException: If token is invalid
    """
    user = db.query(User).filter(User.verification_token == token).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification token"
        )
    
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already verified"
        )
    
    # Mark as verified
    user.is_verified = True
    user.verification_token = None
    db.commit()
    db.refresh(user)
    
    return user