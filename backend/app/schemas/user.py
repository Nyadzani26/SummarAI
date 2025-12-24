"""
User Schemas
Pydantic models for user-related requests/responses
"""

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None


class UserResponse(UserBase):
    """Schema for user response"""
    id: int
    is_verified: bool
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True


class Token(BaseModel):
    """JWT Token response"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Token payload data"""
    user_id: Optional[int] = None
    email: Optional[str] = None


class VerifyEmail(BaseModel):
    """Email verification request"""
    token: str


class ResendVerification(BaseModel):
    """Resend verification email"""
    email: EmailStr


class ForgotPassword(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPassword(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=8)
