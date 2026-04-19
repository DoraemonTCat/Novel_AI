"""Character CRUD API routes."""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth import get_current_user
from app.middleware.rate_limit import limiter
from app.models.character import Character
from app.models.novel import Novel
from app.models.user import User
from app.schemas.character import CharacterCreate, CharacterUpdate, CharacterResponse

router = APIRouter(prefix="/api/novels/{novel_id}/characters", tags=["Characters"])


@router.get("/", response_model=List[CharacterResponse])
@limiter.limit("60/minute")
async def list_characters(
    request: Request,
    novel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all characters of a novel."""
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Novel not found")

    result = await db.execute(
        select(Character).where(Character.novel_id == novel_id).order_by(Character.name)
    )
    return result.scalars().all()


@router.post("/", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def create_character(
    request: Request,
    novel_id: UUID,
    char_data: CharacterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a character to a novel."""
    result = await db.execute(
        select(Novel).where(Novel.id == novel_id, Novel.user_id == current_user.id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Novel not found")

    character = Character(novel_id=novel_id, **char_data.model_dump())
    db.add(character)
    await db.flush()
    return character


@router.patch("/{character_id}", response_model=CharacterResponse)
@limiter.limit("30/minute")
async def update_character(
    request: Request,
    novel_id: UUID,
    character_id: UUID,
    char_data: CharacterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a character."""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.novel_id == novel_id,
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    update_data = char_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(character, field, value)
    await db.flush()
    return character


@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("20/minute")
async def delete_character(
    request: Request,
    novel_id: UUID,
    character_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a character."""
    result = await db.execute(
        select(Character).where(
            Character.id == character_id,
            Character.novel_id == novel_id,
        )
    )
    character = result.scalar_one_or_none()
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")

    await db.delete(character)
    await db.flush()
