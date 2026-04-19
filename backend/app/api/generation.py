"""Generation API — trigger and manage novel generation tasks."""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.novel import Novel
from app.models.user import User
from app.schemas.generation import GenerationRequest, GenerationStatus

router = APIRouter(prefix="/api/generation", tags=["Generation"])


@router.post("/start", response_model=GenerationStatus)
@limiter.limit("10/minute")
async def start_generation(
    request: Request,
    gen_request: GenerationRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Start novel generation as an async Celery task."""
    # Verify ownership
    result = await db.execute(
        select(Novel).where(
            Novel.id == gen_request.novel_id,
            Novel.user_id == current_user.id,
        )
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    if novel.status == "generating":
        raise HTTPException(
            status_code=400, detail="Novel is already being generated"
        )

    # Import and trigger Celery task
    from app.tasks.generation_tasks import generate_novel_task

    task = generate_novel_task.delay(str(novel.id))
    novel.status = "generating"
    novel.celery_task_id = task.id
    await db.flush()

    return GenerationStatus(
        novel_id=novel.id,
        task_id=task.id,
        status="generating",
        total_chapters=novel.total_chapters,
    )


@router.get("/status/{novel_id}", response_model=GenerationStatus)
@limiter.limit("120/minute")
async def get_generation_status(
    request: Request,
    novel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Check the generation status of a novel."""
    result = await db.execute(
        select(Novel).where(
            Novel.id == novel_id,
            Novel.user_id == current_user.id,
        )
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    # Count completed chapters
    from sqlalchemy import func
    from app.models.chapter import Chapter

    completed = await db.execute(
        select(func.count(Chapter.id)).where(
            Chapter.novel_id == novel_id,
            Chapter.status == "completed",
        )
    )
    completed_chapters = completed.scalar() or 0
    progress = (completed_chapters / novel.total_chapters * 100) if novel.total_chapters > 0 else 0

    return GenerationStatus(
        novel_id=novel.id,
        task_id=novel.celery_task_id,
        status=novel.status,
        current_chapter=completed_chapters,
        total_chapters=novel.total_chapters,
        progress_percent=progress,
    )


@router.post("/cancel/{novel_id}")
@limiter.limit("10/minute")
async def cancel_generation(
    request: Request,
    novel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cancel an ongoing generation task."""
    result = await db.execute(
        select(Novel).where(
            Novel.id == novel_id,
            Novel.user_id == current_user.id,
        )
    )
    novel = result.scalar_one_or_none()
    if not novel:
        raise HTTPException(status_code=404, detail="Novel not found")

    if novel.status != "generating":
        raise HTTPException(status_code=400, detail="Novel is not currently generating")

    # Revoke Celery task
    if novel.celery_task_id:
        from app.tasks.celery_app import celery_app
        celery_app.control.revoke(novel.celery_task_id, terminate=True)

    novel.status = "paused"
    novel.celery_task_id = None
    await db.flush()

    return {"message": "Generation cancelled", "novel_id": str(novel_id)}
