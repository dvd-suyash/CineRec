from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base, TimestampMixin, generate_uuid

class ConversationSession(Base, TimestampMixin):
    __tablename__ = "conversation_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE") # ACTIVE, COMPLETED, ABANDONED, ERROR
    started_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    ended_at: Mapped[Optional[datetime]] = mapped_column()

class ConversationMessage(Base, TimestampMixin):
    __tablename__ = "conversation_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(50), nullable=False) # USER, ASSISTANT, SYSTEM, TOOL
    content: Mapped[str] = mapped_column(String, nullable=False)
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)

    __table_args__ = (
        UniqueConstraint("session_id", "sequence_number", name="uix_msg_session_seq"),
    )

class ConversationIntent(Base, TimestampMixin):
    __tablename__ = "conversation_intents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    session_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="CASCADE"), unique=True)
    mood: Mapped[Optional[dict]] = mapped_column(JSONB)
    desired_emotions: Mapped[Optional[dict]] = mapped_column(JSONB)
    energy_level: Mapped[Optional[str]] = mapped_column(String(50))
    emotional_intensity: Mapped[Optional[str]] = mapped_column(String(50))
    complexity_level: Mapped[Optional[str]] = mapped_column(String(50))
    pacing_preference: Mapped[Optional[str]] = mapped_column(String(50))
    positive_genres: Mapped[Optional[dict]] = mapped_column(JSONB)
    negative_genres: Mapped[Optional[dict]] = mapped_column(JSONB)
    themes: Mapped[Optional[dict]] = mapped_column(JSONB)
    max_runtime_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    min_runtime_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    languages: Mapped[Optional[dict]] = mapped_column(JSONB)
    viewing_context: Mapped[Optional[str]] = mapped_column(String(255))
    exploration_level: Mapped[Optional[str]] = mapped_column(String(50))
