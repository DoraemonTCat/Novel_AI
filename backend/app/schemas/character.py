"""Character schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=9999)
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    relationships: Optional[dict] = None
    role: str = Field(default="supporting", pattern="^(protagonist|antagonist|supporting|minor)$")


class CharacterUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=9999)
    appearance: Optional[str] = None
    personality: Optional[str] = None
    background: Optional[str] = None
    relationships: Optional[dict] = None
    role: Optional[str] = None


class CharacterResponse(BaseModel):
    id: UUID
    novel_id: UUID
    name: str
    age: Optional[int]
    appearance: Optional[str]
    personality: Optional[str]
    background: Optional[str]
    relationships: Optional[dict]
    role: str
    created_at: datetime

    class Config:
        from_attributes = True
