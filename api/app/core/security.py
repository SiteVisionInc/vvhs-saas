"""
Security utilities for authentication and authorization.
Implements JWT tokens and password hashing (bcrypt) and token handling (JWT).
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt, ExpiredSignatureError
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

def _utcnow():
    return datetime.now(timezone.utc)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    now = _utcnow()
    exp = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {**data, "type": "access", "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    now = _utcnow()
    exp = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {**data, "type": "refresh", "iat": int(now.timestamp()), "exp": int(exp.timestamp())}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except ExpiredSignatureError:
        # temporary clarity
        raise JWTError("token_expired")
    except JWTError as e:
        raise
