from typing import Optional
from datetime import datetime
import uuid
from sqlalchemy import String, UniqueConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin, generate_uuid

class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(String(1024))
    locale: Mapped[str] = mapped_column(String(10), default="en-US")
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    region_code: Mapped[str] = mapped_column(String(2), default="IN")
    onboarding_status: Mapped[str] = mapped_column(String(50), default="PENDING")
    deleted_at: Mapped[Optional[datetime]] = mapped_column()

    identities = relationship("UserIdentity", back_populates="user", cascade="all, delete-orphan")
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")

class UserIdentity(Base, TimestampMixin):
    __tablename__ = "user_identities"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=generate_uuid)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)
    provider_subject: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    email_verified: Mapped[bool] = mapped_column(default=False)

    __table_args__ = (
        UniqueConstraint("provider", "provider_subject", name="uix_provider_subject"),
        UniqueConstraint("user_id", "provider", name="uix_user_provider"),
    )

    user = relationship("User", back_populates="identities")

class UserProfile(Base, TimestampMixin):
    __tablename__ = "user_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    bio: Mapped[Optional[str]] = mapped_column(String(1000))
    preferences_version: Mapped[int] = mapped_column(default=1)

    user = relationship("User", back_populates="profile")
