from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, Integer, Numeric, ForeignKey, Column
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from pgvector.sqlalchemy import Vector

from .base import Base, TimestampMixin, generate_uuid

class Memory(Base, TimestampMixin):
    __tablename__ = "memories"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    memory_type: Mapped[str] = mapped_column(String(100), nullable=False)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    value: Mapped[Optional[dict]] = mapped_column(JSONB)
    polarity: Mapped[str] = mapped_column(String(50), nullable=False) # POSITIVE, NEGATIVE, NEUTRAL
    confidence: Mapped[float] = mapped_column(Numeric(4, 3), nullable=False) # 0.0 - 1.0
    source: Mapped[str] = mapped_column(String(100), nullable=False) # USER_EXPLICIT, BEHAVIOR_INFERRED, CONVERSATION_INFERRED, SYSTEM_DERIVED
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="ACTIVE") # ACTIVE, DISABLED, SUPERSEDED, DELETED
    evidence_count: Mapped[int] = mapped_column(Integer, default=0)
    last_evidence_at: Mapped[Optional[datetime]] = mapped_column()

class MemoryEvidence(Base, TimestampMixin):
    __tablename__ = "memory_evidence"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    memory_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("memories.id", ondelete="CASCADE"))
    interaction_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("interactions.id", ondelete="SET NULL"))
    conversation_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="SET NULL"))
    evidence_type: Mapped[str] = mapped_column(String(100), nullable=False)
    weight: Mapped[float] = mapped_column(Numeric(4, 3), default=1.0)

class TasteProfile(Base, TimestampMixin):
    __tablename__ = "taste_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    profile_version: Mapped[int] = mapped_column(Integer, default=1)
    profile_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    generated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

class UserEmbedding(Base, TimestampMixin):
    __tablename__ = "user_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    embedding_type: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    # Using Column for pgvector 
    embedding = Column(Vector(768), nullable=False)

class MovieEmbedding(Base, TimestampMixin):
    __tablename__ = "movie_embeddings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    embedding_type: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    embedding = Column(Vector(768), nullable=False)
