from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Organization(Base):
	__tablename__ = "organizations"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	name: Mapped[str] = mapped_column(String(255), nullable=False)
	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

	users: Mapped[list[UserAccount]] = relationship(back_populates="organization", cascade="all, delete-orphan")  # type: ignore[name-defined]
	channels: Mapped[list[Channel]] = relationship(back_populates="organization", cascade="all, delete-orphan")  # type: ignore[name-defined]


class UserAccount(Base):
	__tablename__ = "users"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)  # Clerk user id
	org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
	email: Mapped[Optional[str]] = mapped_column(String(320), nullable=True)
	role: Mapped[str] = mapped_column(String(32), default="member")
	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

	organization: Mapped[Organization] = relationship(back_populates="users")  # type: ignore[name-defined]

	__table_args__ = (
		UniqueConstraint("org_id", "email", name="uq_users_org_email"),
	)


class Channel(Base):
	__tablename__ = "channels"

	id: Mapped[str] = mapped_column(String(36), primary_key=True)
	org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
	provider: Mapped[str] = mapped_column(String(32), index=True)  # e.g., meta, linkedin, tiktok
	account_ref: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)  # page id, account id, etc
	access_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # TODO: encrypt at rest
	refresh_token: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
	created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)

	organization: Mapped[Organization] = relationship(back_populates="channels")  # type: ignore[name-defined]

	__table_args__ = (
		UniqueConstraint("org_id", "provider", "account_ref", name="uq_channel_org_provider_ref"),
	)



