"""Generation schemas for novel generation requests and progress."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class GenerationRequest(BaseModel):
    """Request to start novel generation."""
    novel_id: UUID
    regenerate_outline: bool = False


class GenerationProgress(BaseModel):
    """Real-time progress update pushed via WebSocket."""
    novel_id: str
    task_id: str
    status: str  # queued, outline, generating, completed, error
    current_chapter: int = 0
    total_chapters: int = 0
    progress_percent: float = 0.0
    current_chapter_title: Optional[str] = None
    preview_text: Optional[str] = None
    error_message: Optional[str] = None


class GenerationStatus(BaseModel):
    """Response for generation status check."""
    novel_id: UUID
    task_id: Optional[str]
    status: str
    current_chapter: int = 0
    total_chapters: int = 0
    progress_percent: float = 0.0
