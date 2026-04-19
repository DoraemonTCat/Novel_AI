"""Export schemas."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ExportRequest(BaseModel):
    novel_id: UUID
    format: str = Field(..., pattern="^(pdf|epub|markdown|txt)$")
    chapters: Optional[list[int]] = None  # None = all chapters
    include_cover: bool = True
    include_toc: bool = True
