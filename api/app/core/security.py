"""
Security utilities for authentication and authorization.
Implements JWT tokens and password hashing (bcrypt) and token handling (JWT).
FIXED: Ensures 'sub' claim is always a string for JWT compliance.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from config import get_settings

settings = get_settings()

# ------------------------
# Password Hashing
# ------------------------

def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    Output format: $2b$12$<salt+hash>
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password by comparing plaintext to stored hash.
    """
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


# ------------------------
# JWT Tokens
# ------------------------

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.
    FIXED: Ensures 'sub' is always a string.
    """
    to_encode = data.copy()
    
    # Ensure 'sub' is a string (JWT standard requires it)
    if 'sub' in to_encode:
        to_encode['sub'] = str(to_encode['sub'])
    
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Create JWT refresh token with longer expiration.
    FIXED: Ensures 'sub' is always a string.
    """
    to_encode = data.copy()
    
    # Ensure 'sub' is a string
    if 'sub' in to_encode:
        to_encode['sub'] = str(to_encode['sub'])
    
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token.
    FIXED: Converts 'sub' back to integer after decoding.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        
        # Convert 'sub' back to integer if it's the user ID
        if 'sub' in payload and payload['sub'].isdigit():
            payload['sub'] = int(payload['sub'])
            
        return payload
    except JWTError as e:
        raise e