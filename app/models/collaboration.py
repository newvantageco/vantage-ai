"""
Collaboration Models
Handles RBAC, activity logs, and team collaboration features
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base_class import Base
import enum


class UserRole(str, enum.Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    ANALYST = "analyst"


class ActivityType(str, enum.Enum):
    CONTENT_CREATED = "content_created"
    CONTENT_UPDATED = "content_updated"
    CONTENT_PUBLISHED = "content_published"
    CONTENT_DELETED = "content_deleted"
    CAMPAIGN_CREATED = "campaign_created"
    CAMPAIGN_UPDATED = "campaign_updated"
    CAMPAIGN_DELETED = "campaign_deleted"
    BRAND_GUIDE_UPDATED = "brand_guide_updated"
    INTEGRATION_CONNECTED = "integration_connected"
    INTEGRATION_DISCONNECTED = "integration_disconnected"
    USER_INVITED = "user_invited"
    USER_ROLE_CHANGED = "user_role_changed"
    BILLING_UPDATED = "billing_updated"
    EXPORT_CREATED = "export_created"


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=True)  # Nullable for system events
    
    # Activity details
    activity_type = Column(Enum(ActivityType), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Related entities
    entity_type = Column(String(50), nullable=True)  # content_item, campaign, etc.
    entity_id = Column(Integer, nullable=True)
    entity_name = Column(String(255), nullable=True)
    
    # Additional data
    activity_metadata = Column(JSON, nullable=True)  # Additional context data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("UserAccount")


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Webhook details
    source = Column(String(50), nullable=False)  # stripe, meta, linkedin, etc.
    endpoint_url = Column(String(500), nullable=False)
    secret = Column(String(255), nullable=True)  # Webhook secret for verification
    
    # Configuration
    events = Column(JSON, nullable=True)  # Array of events to listen for
    is_active = Column(Boolean, default=True)
    
    # Statistics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    last_request_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")


class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    webhook_endpoint_id = Column(Integer, ForeignKey("webhook_endpoints.id"), nullable=True)
    
    # Event details
    source = Column(String(50), nullable=False)
    event_type = Column(String(100), nullable=False)
    event_id = Column(String(255), nullable=True)  # External event ID
    
    # Payload
    payload = Column(JSON, nullable=False)
    headers = Column(JSON, nullable=True)
    
    # Processing status
    status = Column(String(20), default="pending")  # pending, processed, failed, ignored
    processed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    received_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    webhook_endpoint = relationship("WebhookEndpoint")


class TeamInvitation(Base):
    __tablename__ = "team_invitations"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    invited_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Invitation details
    email = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    invitation_token = Column(String(255), unique=True, nullable=False, index=True)
    
    # Status
    status = Column(String(20), default="pending")  # pending, accepted, expired, cancelled
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    invited_by = relationship("UserAccount")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String(50), nullable=False)  # info, warning, error, success
    
    # Related entity
    entity_type = Column(String(50), nullable=True)
    entity_id = Column(Integer, nullable=True)
    action_url = Column(String(500), nullable=True)
    
    # Status
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    user = relationship("UserAccount")


class ContentApproval(Base):
    __tablename__ = "content_approvals"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    requested_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    requested_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Approval details
    status = Column(String(20), default="pending")  # pending, approved, rejected, cancelled
    approver_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Approval workflow
    requires_multiple_approvals = Column(Boolean, default=False)
    approval_workflow_id = Column(Integer, ForeignKey("approval_workflows.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    content_item = relationship("ContentItem")
    requested_by = relationship("UserAccount", foreign_keys=[requested_by_id])
    approver = relationship("UserAccount", foreign_keys=[approver_id])
    approval_workflow = relationship("ApprovalWorkflow")


class ApprovalWorkflow(Base):
    __tablename__ = "approval_workflows"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    
    # Workflow details
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)
    
    # Workflow rules
    content_types = Column(JSON, nullable=True)  # Array of content types this applies to
    required_approvers = Column(JSON, nullable=False)  # Array of role requirements
    auto_approve_conditions = Column(JSON, nullable=True)  # Conditions for auto-approval
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    content_approvals = relationship("ContentApproval", back_populates="approval_workflow")


class ContentComment(Base):
    __tablename__ = "content_comments"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("content_comments.id"), nullable=True)
    
    # Comment details
    content = Column(Text, nullable=False)
    comment_type = Column(String(20), default="comment")  # comment, suggestion, question, feedback
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    
    # Mentions and tags
    mentioned_user_ids = Column(JSON, nullable=True)  # Array of user IDs mentioned
    tags = Column(JSON, nullable=True)  # Array of tags
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    content_item = relationship("ContentItem")
    user = relationship("UserAccount", foreign_keys=[user_id])
    parent_comment = relationship("ContentComment", remote_side=[id])
    child_comments = relationship("ContentComment", back_populates="parent_comment")
    resolved_by = relationship("UserAccount", foreign_keys=[resolved_by_id])


class ContentVersion(Base):
    __tablename__ = "content_versions"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Version details
    version_number = Column(Integer, nullable=False)
    title = Column(String(255), nullable=True)
    content = Column(Text, nullable=True)
    content_type = Column(String(50), nullable=True)
    media_urls = Column(JSON, nullable=True)
    hashtags = Column(JSON, nullable=True)
    mentions = Column(JSON, nullable=True)
    platform_content = Column(JSON, nullable=True)
    tags = Column(JSON, nullable=True)
    content_metadata = Column(JSON, nullable=True)
    
    # Version metadata
    change_summary = Column(Text, nullable=True)
    change_type = Column(String(20), default="edit")  # edit, revert, restore, auto_save
    is_auto_save = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    content_item = relationship("ContentItem")
    created_by = relationship("UserAccount")


class ContentFeedback(Base):
    __tablename__ = "content_feedback"

    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("content_items.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=False)
    
    # Feedback details
    feedback_type = Column(String(20), nullable=False)  # like, dislike, suggestion, issue
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    comment = Column(Text, nullable=True)
    is_anonymous = Column(Boolean, default=False)
    
    # Feedback categories
    categories = Column(JSON, nullable=True)  # Array of feedback categories
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_by_id = Column(Integer, ForeignKey("user_accounts.id"), nullable=True)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    organization = relationship("Organization")
    content_item = relationship("ContentItem")
    user = relationship("UserAccount", foreign_keys=[user_id])
    acknowledged_by = relationship("UserAccount", foreign_keys=[acknowledged_by_id])