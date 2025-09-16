from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import String, ForeignKey, UniqueConstraint, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Role(str, Enum):
    owner = "owner"
    admin = "admin"
    editor = "editor"
    viewer = "viewer"


class UserOrgRole(Base):
    """User roles within an organization"""
    __tablename__ = "user_org_roles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role: Mapped[Role] = mapped_column(SAEnum(Role, name="user_role"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization")  # type: ignore[name-defined]
    user: Mapped[UserAccount] = relationship("UserAccount", foreign_keys=[user_id])  # type: ignore[name-defined]
    creator: Mapped[Optional[UserAccount]] = relationship("UserAccount", foreign_keys=[created_by])  # type: ignore[name-defined]

    __table_args__ = (
        UniqueConstraint("org_id", "user_id", name="uq_user_org_role"),
    )


# Role hierarchy for permission checking
ROLE_HIERARCHY = {
    Role.owner: 4,
    Role.admin: 3,
    Role.editor: 2,
    Role.viewer: 1,
}


def has_permission(user_role: Role, required_role: Role) -> bool:
    """Check if user role has permission for required role level"""
    return ROLE_HIERARCHY.get(user_role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
