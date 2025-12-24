"""
Security utilities 
- Password hashing with bcrypt
- JWT token generation and verification
"""

from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import settings

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto") 

def hash_password(password: str) -> str:
    """
    Hash a password
    Args:
        password (str): Password to hash
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password
    Args:
        plain_password (str): Password to verify
        hashed_password (str): Hashed password to compare against
    Returns:
        bool: True if the password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    Args:
        data (dict): Data to encode in the token
        expires_delta (Optional[timedelta]): Time until the token expires
    Returns:
        str: JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> Optional[dict]:
    """
    Decode a JWT access token
    Args:
        token (str): JWT access token to decode
    Returns:
        Optional[dict]: Decoded token data if successful, None otherwise
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

def create_verification_token(email: str) -> str:
    """
    Create a verification token
    Args:
        email (str): Email address to create token for
    Returns:
        str: Verification token
    """
    data = {
        "sub": email,
        "type": "email_verification"
    }
    
    # Verify token expires in 1 day
    expires_in = timedelta(days=1)
    
    # Create token
    token = create_access_token(data, expires_in)
    return token