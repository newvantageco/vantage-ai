from __future__ import annotations

from datetime import datetime
from typing import Optional, Dict, Any

from sqlalchemy import String, Text, ForeignKey, JSON, DateTime, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Conversation(Base):
    """WhatsApp conversations with customers"""
    __tablename__ = "conversations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    channel: Mapped[str] = mapped_column(String(32), nullable=False)  # whatsapp, sms, etc.
    peer_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)  # phone number, email, etc.
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    organization: Mapped[Organization] = relationship("Organization")  # type: ignore[name-defined]
    messages: Mapped[list[Message]] = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_conversations_org_channel", "org_id", "channel"),
        Index("ix_conversations_last_message", "last_message_at"),
        Index("ix_conversations_peer_id", "peer_id"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert conversation to dictionary for API responses."""
        return {
            "id": self.id,
            "org_id": self.org_id,
            "channel": self.channel,
            "peer_id": self.peer_id,
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "created_at": self.created_at.isoformat(),
            "message_count": len(self.messages) if self.messages else 0
        }


class Message(Base):
    """Individual messages within conversations"""
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    direction: Mapped[str] = mapped_column(String(16), nullable=False)  # inbound, outbound
    text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    media_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    conversation: Mapped[Conversation] = relationship("Conversation", back_populates="messages")  # type: ignore[name-defined]

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
        Index("ix_messages_direction", "direction"),
    )

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for API responses."""
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "direction": self.direction,
            "text": self.text,
            "media_url": self.media_url,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }
