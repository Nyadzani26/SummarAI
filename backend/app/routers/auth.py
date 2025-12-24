"""
Authentication Routes
Endpoints for registration, login, and email verification
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserLogin,
    Token,
    VerifyEmail
)
from app.services.auth_services import (
    create_user,
    authenticate_user,
    verify_user_email
)
from app.utils.security import create_access_token
from app.config import settings
from app.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters
    - **full_name**: User's full name (optional)
    
    Returns created user object and sends verification email
    """
    # Create user
    user = create_user(db, user_data)
    
    # TODO: Send verification email
    # send_verification_email(user.email, user.verification_token)
    
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Login with email and password
    
    - **email**: User's email address
    - **password**: User's password
    
    Returns JWT access token for authenticated requests
    """
    # Authenticate user
    user = authenticate_user(db, login_data.email, login_data.password)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "email": user.email},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/verify-email/{token}", response_model=UserResponse)
async def verify_email(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Verify user's email address with token
    
    - **token**: Email verification token from registration
    
    Marks user as verified and allows full access
    """
    user = verify_user_email(db, token)
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information
    
    Requires authentication (JWT token in Authorization header)
    """
    return current_user


@router.post("/test-token", response_model=UserResponse)
async def test_token(
    current_user: User = Depends(get_current_user)
):
    """
    Test if JWT token is valid
    
    Useful for checking authentication status from frontend
    """
    return current_user