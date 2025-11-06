"""
Authentication schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr
from typing import Optional


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Decoded token data."""
    user_id: Optional[int] = None
    username: Optional[str] = None
    tenant_id: Optional[int] = None
    role: Optional[str] = None


class LoginRequest(BaseModel):
    """Login request payload."""
    username: str
    password: str


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    """Change password request."""
    current_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    """Password reset request."""
    email: EmailStr


class ResetPasswordConfirm(BaseModel):
    """Password reset confirmation."""
    token: str
    new_password: str
