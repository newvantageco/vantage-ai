from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict, Any
import json
import secrets
import hashlib
import hmac

from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Webhook(Base):
    """Webhook endpoints for external integrations."""
    __tablename__ = "webhooks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Webhook details
    target_url: Mapped[str] = mapped_column(String(500), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Events to trigger webhook
    events: Mapped[str] = mapped_column(Text, nullable=False)  # JSON array of events
    
    # Security
    secret: Mapped[str] = mapped_column(String(64), nullable=False)  # HMAC secret
    
    # Configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    retry_count: Mapped[int] = mapped_column(default=3, nullable=False)
    timeout_seconds: Mapped[int] = mapped_column(default=30, nullable=False)
    
    # Headers
    headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON object of custom headers
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_triggered_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_webhooks_org_id", "org_id"),
        Index("ix_webhooks_target_url", "target_url"),
        Index("ix_webhooks_is_active", "is_active"),
        Index("ix_webhooks_created_at", "created_at"),
    )

    def get_events(self) -> List[str]:
        """Get events as a list."""
        try:
            return json.loads(self.events)
        except (json.JSONDecodeError, TypeError):
            return []

    def set_events(self, events: List[str]) -> None:
        """Set events from a list."""
        self.events = json.dumps(events)

    def get_headers(self) -> Dict[str, str]:
        """Get headers as a dictionary."""
        try:
            return json.loads(self.headers) if self.headers else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_headers(self, headers: Dict[str, str]) -> None:
        """Set headers from a dictionary."""
        self.headers = json.dumps(headers)

    def generate_signature(self, payload: str) -> str:
        """Generate HMAC signature for payload."""
        return hmac.new(
            self.secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

    def verify_signature(self, payload: str, signature: str) -> bool:
        """Verify HMAC signature."""
        expected_signature = self.generate_signature(payload)
        return hmac.compare_digest(expected_signature, signature)

    @classmethod
    def generate_secret(cls) -> str:
        """Generate a random webhook secret."""
        return secrets.token_urlsafe(32)


class WebhookDelivery(Base):
    """Track webhook delivery attempts."""
    __tablename__ = "webhook_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    webhook_id: Mapped[str] = mapped_column(ForeignKey("webhooks.id", ondelete="CASCADE"), index=True)
    org_id: Mapped[str] = mapped_column(ForeignKey("organizations.id", ondelete="CASCADE"), index=True)
    
    # Delivery details
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)  # JSON payload sent
    response_status: Mapped[Optional[int]] = mapped_column(nullable=True)
    response_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    response_headers: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    
    # Delivery status
    status: Mapped[str] = mapped_column(String(20), default="pending", nullable=False)  # pending, delivered, failed, retrying
    attempt_count: Mapped[int] = mapped_column(default=1, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timing
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    next_retry_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_webhook_deliveries_webhook_id", "webhook_id"),
        Index("ix_webhook_deliveries_org_id", "org_id"),
        Index("ix_webhook_deliveries_status", "status"),
        Index("ix_webhook_deliveries_event_type", "event_type"),
        Index("ix_webhook_deliveries_started_at", "started_at"),
        Index("ix_webhook_deliveries_next_retry_at", "next_retry_at"),
    )

    def get_response_headers(self) -> Dict[str, str]:
        """Get response headers as a dictionary."""
        try:
            return json.loads(self.response_headers) if self.response_headers else {}
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_response_headers(self, headers: Dict[str, str]) -> None:
        """Set response headers from a dictionary."""
        self.response_headers = json.dumps(headers)

    def get_payload(self) -> Dict[str, Any]:
        """Get payload as a dictionary."""
        try:
            return json.loads(self.payload)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_payload(self, payload: Dict[str, Any]) -> None:
        """Set payload from a dictionary."""
        self.payload = json.dumps(payload)


class WebhookEvent(Base):
    """Define webhook event types and their schemas."""
    __tablename__ = "webhook_events"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    schema_json: Mapped[str] = mapped_column(Text, nullable=False)  # JSON schema for payload
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_webhook_events_event_type", "event_type"),
    )

    def get_schema(self) -> Dict[str, Any]:
        """Get event schema as a dictionary."""
        try:
            return json.loads(self.schema_json)
        except (json.JSONDecodeError, TypeError):
            return {}

    def set_schema(self, schema: Dict[str, Any]) -> None:
        """Set event schema from a dictionary."""
        self.schema_json = json.dumps(schema)


# Available webhook events
WEBHOOK_EVENTS = {
    "POSTED": {
        "name": "Post Published",
        "description": "Triggered when a scheduled post is published",
        "schema": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "const": "POSTED"},
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "string"},
                        "content_id": {"type": "string"},
                        "channel_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "platform_post_id": {"type": "string"},
                        "platform_url": {"type": "string"},
                        "scheduled_at": {"type": "string", "format": "date-time"},
                        "published_at": {"type": "string", "format": "date-time"}
                    },
                    "required": ["schedule_id", "content_id", "channel_id", "platform"]
                }
            },
            "required": ["event", "timestamp", "data"]
        }
    },
    "METRICS_UPDATED": {
        "name": "Metrics Updated",
        "description": "Triggered when post metrics are updated",
        "schema": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "const": "METRICS_UPDATED"},
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {
                    "type": "object",
                    "properties": {
                        "schedule_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "metrics": {
                            "type": "object",
                            "properties": {
                                "impressions": {"type": "integer"},
                                "reach": {"type": "integer"},
                                "likes": {"type": "integer"},
                                "comments": {"type": "integer"},
                                "shares": {"type": "integer"},
                                "clicks": {"type": "integer"},
                                "video_views": {"type": "integer"},
                                "saves": {"type": "integer"},
                                "cost_cents": {"type": "integer"}
                            }
                        },
                        "fetched_at": {"type": "string", "format": "date-time"}
                    },
                    "required": ["schedule_id", "platform", "metrics"]
                }
            },
            "required": ["event", "timestamp", "data"]
        }
    },
    "CONVERSATION_RECEIVED": {
        "name": "Conversation Received",
        "description": "Triggered when a new conversation message is received",
        "schema": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "const": "CONVERSATION_RECEIVED"},
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {"type": "string"},
                        "channel_id": {"type": "string"},
                        "platform": {"type": "string"},
                        "sender_id": {"type": "string"},
                        "sender_name": {"type": "string"},
                        "message_text": {"type": "string"},
                        "message_type": {"type": "string"},
                        "is_from_customer": {"type": "boolean"},
                        "received_at": {"type": "string", "format": "date-time"}
                    },
                    "required": ["conversation_id", "channel_id", "platform", "sender_id", "message_text"]
                }
            },
            "required": ["event", "timestamp", "data"]
        }
    },
    "CAMPAIGN_CREATED": {
        "name": "Campaign Created",
        "description": "Triggered when a new campaign is created",
        "schema": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "const": "CAMPAIGN_CREATED"},
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {
                    "type": "object",
                    "properties": {
                        "campaign_id": {"type": "string"},
                        "name": {"type": "string"},
                        "objective": {"type": "string"},
                        "start_date": {"type": "string", "format": "date"},
                        "end_date": {"type": "string", "format": "date"},
                        "created_by": {"type": "string"}
                    },
                    "required": ["campaign_id", "name"]
                }
            },
            "required": ["event", "timestamp", "data"]
        }
    },
    "CONTENT_APPROVED": {
        "name": "Content Approved",
        "description": "Triggered when content is approved for publishing",
        "schema": {
            "type": "object",
            "properties": {
                "event": {"type": "string", "const": "CONTENT_APPROVED"},
                "timestamp": {"type": "string", "format": "date-time"},
                "data": {
                    "type": "object",
                    "properties": {
                        "content_id": {"type": "string"},
                        "title": {"type": "string"},
                        "status": {"type": "string"},
                        "approved_by": {"type": "string"},
                        "approved_at": {"type": "string", "format": "date-time"}
                    },
                    "required": ["content_id", "title", "status"]
                }
            },
            "required": ["event", "timestamp", "data"]
        }
    }
}
