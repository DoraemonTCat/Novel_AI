"""Novel model — the core entity of the application."""
import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Novel(Base):
    __tablename__ = "novels"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    genre: Mapped[str] = mapped_column(String(100), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="th")
    writing_style: Mapped[str] = mapped_column(String(100), nullable=False, default="contemporary")
    tone: Mapped[str] = mapped_column(String(100), nullable=False, default="balanced")
    pov: Mapped[str] = mapped_column(String(50), nullable=False, default="third_person")
    target_audience: Mapped[str] = mapped_column(String(50), nullable=False, default="general")
    chapter_length_target: Mapped[int] = mapped_column(Integer, nullable=False, default=3000)
    total_chapters: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    ai_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="gemini")
    ai_model: Mapped[str] = mapped_column(String(100), nullable=False, default="models/gemini-2.5-flash")
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="draft", index=True
    )  # draft, generating, completed, paused, error
    cover_image_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    outline: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    celery_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="novels")
    chapters = relationship("Chapter", back_populates="novel", cascade="all, delete-orphan",
                           order_by="Chapter.chapter_number")
    characters = relationship("Character", back_populates="novel", cascade="all, delete-orphan")
    world_setting = relationship("WorldSetting", back_populates="novel", uselist=False,
                                cascade="all, delete-orphan")
    story_memories = relationship("StoryMemory", back_populates="novel", cascade="all, delete-orphan",
                                  order_by="StoryMemory.chapter_number")

    def __repr__(self):
        return f"<Novel '{self.title}' ({self.status})>"
