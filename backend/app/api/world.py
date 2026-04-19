"""World Setting and Cover Image API routes."""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.novel import Novel
from app.models.world import WorldSetting
from app.models.user import User

router = APIRouter(prefix="/api/novels/{novel_id}/world", tags=["World Setting"])


class WorldSettingCreate(BaseModel):
    era: Optional[str] = None
    locations: Optional[list] = None
    rules: Optional[str] = None
    magic_system: Optional[str] = None
    technology_level: Optional[str] = None
    timeline: Optional[list] = None
    lore: Optional[str] = None


class WorldSettingResponse(BaseModel):
    id: UUID
    novel_id: UUID
    era: Optional[str]
    locations: Optional[list]
    rules: Optional[str]
    magic_system: Optional[str]
    technology_level: Optional[str]
    timeline: Optional[list]
    lore: Optional[str]

    class Config:
        from_attributes = True


@router.get("/", response_model=Optional[WorldSettingResponse])
@limiter.limit("60/minute")
async def get_world_setting(
    request: Request,
    novel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get the world setting for a novel."""
    # Verify ownership
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Novel not found")

    result = await db.execute(
        select(WorldSetting).where(WorldSetting.novel_id == novel_id)
    )
    return result.scalar_one_or_none()


@router.put("/", response_model=WorldSettingResponse)
@limiter.limit("30/minute")
async def upsert_world_setting(
    request: Request,
    novel_id: UUID,
    data: WorldSettingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create or update world setting."""
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Novel not found")

    result = await db.execute(
        select(WorldSetting).where(WorldSetting.novel_id == novel_id)
    )
    world = result.scalar_one_or_none()

    if world:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(world, field, value)
    else:
        world = WorldSetting(novel_id=novel_id, **data.model_dump())
        db.add(world)

    await db.flush()
    return world
