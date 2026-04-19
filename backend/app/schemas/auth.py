"""Auth schemas for login, tokens, and user responses."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    avatar_url: Optional[str] = None
    is_active: bool
    preferences: Optional[dict] = None
    created_at: datetime
    last_login: datetime

    class Config:
        from_attributes = True


class GoogleUserInfo(BaseModel):
    """Data extracted from Google OAuth profile."""
    google_id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
