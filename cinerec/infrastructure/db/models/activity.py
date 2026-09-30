from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB

from .base import Base, TimestampMixin, generate_uuid

class Rating(Base, TimestampMixin):
    __tablename__ = "ratings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    rating: Mapped[float] = mapped_column(Numeric(2, 1), nullable=False) # 1.0 - 5.0

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uix_rating_user_movie"),
    )

class MoviePreference(Base, TimestampMixin):
    __tablename__ = "movie_preferences"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    preference: Mapped[str] = mapped_column(String(20), nullable=False) # LIKE / DISLIKE

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uix_pref_user_movie"),
    )

class Watchlist(Base, TimestampMixin):
    __tablename__ = "watchlists"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)

class ViewingHistory(Base, TimestampMixin):
    __tablename__ = "viewing_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    status: Mapped[str] = mapped_column(String(50), nullable=False) # STARTED, COMPLETED, ABANDONED
    started_at: Mapped[Optional[datetime]] = mapped_column()
    completed_at: Mapped[Optional[datetime]] = mapped_column()
    last_watched_at: Mapped[Optional[datetime]] = mapped_column()

class Interaction(Base, TimestampMixin):
    __tablename__ = "interactions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    movie_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("movies.id", ondelete="SET NULL"))
    interaction_type: Mapped[str] = mapped_column(String(100), nullable=False)
    value: Mapped[Optional[str]] = mapped_column(String(255))
    session_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("conversation_sessions.id", ondelete="SET NULL"))
    recommendation_request_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True)) # no FK constraint yet, will add later or keep loose
    surface: Mapped[Optional[str]] = mapped_column(String(100))
    metadata_json: Mapped[Optional[dict]] = mapped_column(JSONB)
