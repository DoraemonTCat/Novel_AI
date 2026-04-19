"""World Setting and Story Memory models."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class WorldSetting(Base):
    __tablename__ = "world_settings"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    novel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False,
        unique=True, index=True
    )
    era: Mapped[str | None] = mapped_column(String(255), nullable=True)
    locations: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    magic_system: Mapped[str | None] = mapped_column(Text, nullable=True)
    technology_level: Mapped[str | None] = mapped_column(String(100), nullable=True)
    timeline: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    lore: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    novel = relationship("Novel", back_populates="world_setting")

    def __repr__(self):
        return f"<WorldSetting era='{self.era}'>"


class StoryMemory(Base):
    """Tracks narrative memory across chapters for AI context management."""
    __tablename__ = "story_memories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    novel_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("novels.id", ondelete="CASCADE"), nullable=False, index=True
    )
    chapter_number: Mapped[int] = mapped_column(Integer, nullable=False)
    plot_threads: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    character_states: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=dict)
    foreshadowing: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    unresolved_conflicts: Mapped[dict | None] = mapped_column(JSONB, nullable=True, default=list)
    chapter_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    emotional_tone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    novel = relationship("Novel", back_populates="story_memories")

    def __repr__(self):
        return f"<StoryMemory ch.{self.chapter_number}>"
