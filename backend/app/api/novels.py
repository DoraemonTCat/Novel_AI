"""Novel CRUD API routes."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.novel import Novel
from app.models.chapter import Chapter
from app.models.user import User
from app.schemas.novel import NovelCreate, NovelUpdate, NovelResponse, NovelListResponse

router = APIRouter(prefix="/api/novels", tags=["Novels"])


@router.get("/", response_model=List[NovelListResponse])
@limiter.limit("60/minute")
async def list_novels(
    request: Request,
    skip: int = 0,
    limit: int = 20,
    status_filter: str = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all novels for the current user."""
    query = select(Novel).where(Novel.user_id == current_user.id)
    if status_filter:
        query = query.where(Novel.status == status_filter)
    query = query.order_by(Novel.updated_at.desc()).offset(skip).limit(limit)

    result = await db.execute(query)
    novels = result.scalars().all()
    return novels


@router.get("/stats")
@limiter.limit("60/minute")
async def get_stats(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get user's novel statistics."""
    # Total novels
    novel_count = await db.execute(
        select(func.count(Novel.id)).where(Novel.user_id == current_user.id)
    )
    total_novels = novel_count.scalar() or 0

    # Total chapters
    chapter_count = await db.execute(
        select(func.count(Chapter.id))
        .join(Novel)
        .where(Novel.user_id == current_user.id)
    )
    total_chapters = chapter_count.scalar() or 0

    # Total words
    word_count = await db.execute(
        select(func.coalesce(func.sum(Chapter.word_count), 0))
        .join(Novel)
        .where(Novel.user_id == current_user.id)
    )
    total_words = word_count.scalar() or 0

    # Generating count
    generating_count = await db.execute(
        select(func.count(Novel.id))
        .where(Novel.user_id == current_user.id, Novel.status == "generating")
    )
    generating = generating_count.scalar() or 0

    return {
        "total_novels": total_novels,
        "total_chapters": total_chapters,
        "total_words": total_words,
        "generating": generating,
    }


@router.post("/", response_model=NovelResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_novel(
    request: Request,
    novel_data: NovelCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new novel."""
    # Set default model based on provider
    ai_model = novel_data.ai_model
    if not ai_model:
        from app.config import settings
        if novel_data.ai_provider == "gemini":
            ai_model = settings.GEMINI_MODEL
        else:
            ai_model = settings.OLLAMA_MODEL

    novel = Novel(
        user_id=current_user.id,
        title=novel_data.title,
        description=novel_data.description,
        prompt=novel_data.prompt,
        genre=novel_data.genre,
        language=novel_data.language,
        writing_style=novel_data.writing_style,
        tone=novel_data.tone,
        pov=novel_data.pov,
        target_audience=novel_data.target_audience,
        chapter_length_target=novel_data.chapter_length_target,
        total_chapters=novel_data.total_chapters,
        ai_provider=novel_data.ai_provider,
        ai_model=ai_model,
        status="draft",
    )
    db.add(novel)
    await db.flush()
    return novel


@router.get("/{novel_id}", response_model=NovelResponse)
@limiter.limit("60/minute")
async def get_novel(
    request: Request,
    novel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific novel by ID."""
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == current_user.id)
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")
    return novel


@router.patch("/{novel_id}", response_model=NovelResponse)
@limiter.limit("30/minute")
async def update_novel(
    request: Request,
    novel_id: UUID,
    novel_data: NovelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a novel."""
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == current_user.id)
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    update_data = novel_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(novel, field, value)

    await db.flush()
    return novel


@router.delete("/{novel_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_novel(
    request: Request,
    novel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a novel and all associated data."""
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == current_user.id)
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    await db.delete(novel)
    await db.flush()
