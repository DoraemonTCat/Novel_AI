"""Chapter schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ChapterCreate(BaseModel):
    chapter_number: int = Field(..., ge=1)
    title: str = Field(default="", max_length=500)
    content: str = Field(default="")


class ChapterUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None


class ChapterResponse(BaseModel):
    id: UUID
    novel_id: UUID
    chapter_number: int
    title: str
    content: str
    word_count: int
    status: str
    current_version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ChapterListResponse(BaseModel):
    id: UUID
    novel_id: UUID
    chapter_number: int
    title: str
    word_count: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
