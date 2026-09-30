from typing import Optional, List
from datetime import date
import uuid
from sqlalchemy import String, Integer, ForeignKey, UniqueConstraint, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin, generate_uuid

class Movie(Base, TimestampMixin):
    __tablename__ = "movies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    original_title: Mapped[Optional[str]] = mapped_column(String(512))
    overview: Mapped[Optional[str]] = mapped_column(String)
    release_date: Mapped[Optional[date]] = mapped_column(Date)
    release_year: Mapped[Optional[int]] = mapped_column(Integer)
    runtime_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    original_language: Mapped[Optional[str]] = mapped_column(String(10))
    poster_path: Mapped[Optional[str]] = mapped_column(String(255))
    backdrop_path: Mapped[Optional[str]] = mapped_column(String(255))
    logo_path: Mapped[Optional[str]] = mapped_column(String(255))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    adult_content: Mapped[bool] = mapped_column(default=False)

    provider_ids = relationship("MovieProviderId", back_populates="movie", cascade="all, delete-orphan")
    movie_genres = relationship("MovieGenre", back_populates="movie", cascade="all, delete-orphan")

class MovieProviderId(Base, TimestampMixin):
    __tablename__ = "movie_provider_ids"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)

    __table_args__ = (
        UniqueConstraint("provider", "external_id", name="uix_provider_external_id"),
    )

    movie = relationship("Movie", back_populates="provider_ids")

class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    movie_genres = relationship("MovieGenre", back_populates="genre", cascade="all, delete-orphan")

class MovieGenre(Base):
    __tablename__ = "movie_genres"

    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    genre_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("genres.id", ondelete="CASCADE"), primary_key=True)

    movie = relationship("Movie", back_populates="movie_genres")
    genre = relationship("Genre", back_populates="movie_genres")

class Person(Base):
    __tablename__ = "people"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_path: Mapped[Optional[str]] = mapped_column(String(255))
    known_for_department: Mapped[Optional[str]] = mapped_column(String(100))

class MovieCredit(Base):
    __tablename__ = "movie_credits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    person_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("people.id", ondelete="CASCADE"))
    role: Mapped[str] = mapped_column(String(100), nullable=False) # CAST, CREW
    character: Mapped[Optional[str]] = mapped_column(String(255))
    sort_order: Mapped[Optional[int]] = mapped_column(Integer)

class MovieKeyword(Base):
    __tablename__ = "movie_keywords"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    keyword_text: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)

class MovieKeywordLink(Base):
    __tablename__ = "movie_keyword_links"

    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    keyword_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movie_keywords.id", ondelete="CASCADE"), primary_key=True)

class MovieRelation(Base):
    __tablename__ = "movie_relations"

    source_movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    target_movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True)
    relation_type: Mapped[str] = mapped_column(String(50), primary_key=True) # e.g. SIMILAR, SEQUEL

class MovieWatchProvider(Base):
    __tablename__ = "movie_watch_providers"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    movie_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("movies.id", ondelete="CASCADE"))
    region: Mapped[str] = mapped_column(String(10), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(255), nullable=False)
