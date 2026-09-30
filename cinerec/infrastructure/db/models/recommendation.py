from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, Integer, Numeric, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base, TimestampMixin, generate_uuid

class RecommendationRequest(Base, TimestampMixin):
    __tablename__ = "recommendation_requests"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="SET NULL"))
    surface: Mapped[str] = mapped_column(String(100), nullable=False)
    model_version: Mapped[str] = mapped_column(String(100))
    experiment_id: Mapped[Optional[str]] = mapped_column(String(100))
    experiment_variant: Mapped[Optional[str]] = mapped_column(String(100))
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False)
    request_context: Mapped[Optional[dict]] = mapped_column(JSONB)
    completed_at: Mapped[Optional[datetime]] = mapped_column()

class RecommendationItem(Base, TimestampMixin):
    __tablename__ = "recommendation_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    recommendation_request_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recommendation_requests.id", ondelete="CASCADE"))
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    final_score: Mapped[float] = mapped_column(Numeric(10, 8), nullable=False)
    candidate_score: Mapped[Optional[float]] = mapped_column(Numeric(10, 8))
    candidate_sources: Mapped[Optional[dict]] = mapped_column(JSONB)
    explanation_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    was_displayed: Mapped[bool] = mapped_column(Boolean, default=False)

class RecommendationFeedback(Base, TimestampMixin):
    __tablename__ = "recommendation_feedback"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    recommendation_item_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("recommendation_items.id", ondelete="CASCADE"))
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    feedback_type: Mapped[str] = mapped_column(String(50), nullable=False) # e.g. ACCEPTED, REJECTED, SAVED
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)

class ModelVersion(Base, TimestampMixin):
    __tablename__ = "model_versions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    model_key: Mapped[str] = mapped_column(String(100), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
    training_dataset_id: Mapped[Optional[str]] = mapped_column(String(255))
    artifact_uri: Mapped[Optional[str]] = mapped_column(String(1024))
    configuration: Mapped[Optional[dict]] = mapped_column(JSONB)
    metrics: Mapped[Optional[dict]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="STAGING") # STAGING, ACTIVE, RETIRED
    activated_at: Mapped[Optional[datetime]] = mapped_column()
    retired_at: Mapped[Optional[datetime]] = mapped_column()
