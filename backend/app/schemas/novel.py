"""Novel schemas for CRUD operations."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NovelCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    prompt: str = Field(..., min_length=10)
    genre: str = Field(..., min_length=1, max_length=100)
    language: str = Field(default="th", pattern="^(th|en|mixed)$")
    writing_style: str = Field(default="contemporary", max_length=100)
    tone: str = Field(default="balanced", max_length=100)
    pov: str = Field(default="third_person", max_length=50)
    target_audience: str = Field(default="general", max_length=50)
    chapter_length_target: int = Field(default=3000, ge=500, le=10000)
    total_chapters: int = Field(default=10, ge=1, le=100)
    ai_provider: str = Field(default="gemini", pattern="^(gemini|ollama)$")
    ai_model: Optional[str] = None
    description: Optional[str] = None


class NovelUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    genre: Optional[str] = None
    language: Optional[str] = None
    writing_style: Optional[str] = None
    tone: Optional[str] = None
    pov: Optional[str] = None
    target_audience: Optional[str] = None
    chapter_length_target: Optional[int] = Field(None, ge=500, le=10000)
    total_chapters: Optional[int] = Field(None, ge=1, le=100)
    ai_provider: Optional[str] = None
    ai_model: Optional[str] = None
    cover_image_url: Optional[str] = None


class NovelResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    prompt: str
    genre: str
    language: str
    writing_style: str
    tone: str
    pov: str
    target_audience: str
    chapter_length_target: int
    total_chapters: int
    ai_provider: str
    ai_model: str
    status: str
    cover_image_url: Optional[str]
    outline: Optional[dict]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NovelListResponse(BaseModel):
    id: UUID
    title: str
    genre: str
    language: str
    status: str
    cover_image_url: Optional[str]
    total_chapters: int
    ai_provider: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
