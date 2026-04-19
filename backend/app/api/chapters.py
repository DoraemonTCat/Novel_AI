"""Chapter CRUD API routes."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.chapter import Chapter, ChapterVersion
from app.models.novel import Novel
from app.models.user import User
from app.schemas.chapter import ChapterCreate, ChapterUpdate, ChapterResponse, ChapterListResponse

router = APIRouter(prefix="/api/novels/{novel_id}/chapters", tags=["Chapters"])


async def _verify_novel_ownership(
    novel_id: UUID, user: User, db: AsyncSession
) -> Novel:
    """Verify the user owns this novel."""
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == user.id)
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel


@router.get("/", response_model=List[ChapterListResponse])
@limiter.limit("60/minute")
async def list_chapters(
    request: Request,
    novel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all chapters of a novel."""
    await _verify_novel_ownership(novel_id, current_user, db)
    result = await db.execute(
        select(Chapter)
        .where(Chapter.novel_id == novel_id)
        .order_by(Chapter.chapter_number)
    )
    return result.scalars().all()


@router.get("/{chapter_id}", response_model=ChapterResponse)
@limiter.limit("60/minute")
async def get_chapter(
    request: Request,
    novel_id: UUID,
    chapter_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific chapter with full content."""
    await _verify_novel_ownership(novel_id, current_user, db)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.novel_id == novel_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    return chapter


@router.patch("/{chapter_id}", response_model=ChapterResponse)
@limiter.limit("30/minute")
async def update_chapter(
    request: Request,
    novel_id: UUID,
    chapter_id: UUID,
    chapter_data: ChapterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update chapter content (manual edit). Creates a version snapshot."""
    await _verify_novel_ownership(novel_id, current_user, db)
    result = await db.execute(
        select(Chapter).where(Chapter.id == chapter_id, Chapter.novel_id == novel_id)
    )
    chapter = result.scalar_one_or_none()
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")

    # Save current version before updating
    if chapter_data.content is not None and chapter_data.content != chapter.content:
        version = ChapterVersion(
            chapter_id=chapter.id,
            content=chapter.content,
            version_number=chapter.current_version,
            change_description="Manual edit",
        )
        db.add(version)
        chapter.current_version += 1

    update_data = chapter_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(chapter, field, value)

    # Recalculate word count
    if chapter_data.content is not None:
        chapter.word_count = len(chapter.content.split())

    await db.flush()
    return chapter
