from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any

from sqlalchemy import String, Text, ForeignKey, Enum as SAEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TemplateType(str, Enum):
    image = "image"
    video = "video"


class AssetTemplate(Base):
    """Reusable templates for creating branded images and videos"""
    __tablename__ = "asset_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[Optional[str]] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[TemplateType] = mapped_column(SAEnum(TemplateType, name="template_type"), nullable=False)
    spec: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)  # Template specification JSON
    is_public: Mapped[bool] = mapped_column(default=False, nullable=False)  # Public templates available to all orgs
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    created_by: Mapped[Optional[str]] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Relationships
    organization: Mapped[Optional[Organization]] = relationship("Organization")  # type: ignore[name-defined]
    creator: Mapped[Optional[UserAccount]] = relationship("UserAccount", foreign_keys=[created_by])  # type: ignore[name-defined]

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for API responses."""
        return {
            "id": self.id,
            "org_id": self.org_id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value,
            "spec": self.spec,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by
        }


class TemplateUsage(Base):
    """Track usage of templates for analytics"""
    __tablename__ = "template_usage"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    template_id: Mapped[str] = mapped_column(ForeignKey("asset_templates.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    content_item_id: Mapped[Optional[str]] = mapped_column(ForeignKey("content_items.id", ondelete="SET NULL"), nullable=True, index=True)
    used_at: Mapped[datetime] = mapped_column(default=datetime.utcnow, nullable=False)
    inputs: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # Inputs used for generation

    # Relationships
    template: Mapped[AssetTemplate] = relationship("AssetTemplate")
    organization: Mapped[Organization] = relationship("Organization")  # type: ignore[name-defined]
    content_item: Mapped[Optional[ContentItem]] = relationship("ContentItem")  # type: ignore[name-defined]
