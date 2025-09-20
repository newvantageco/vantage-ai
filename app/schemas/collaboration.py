"""
Collaboration Pydantic Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    EDITOR = "editor"
    ANALYST = "analyst"


class ActivityType(str, Enum):
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


class InvitationStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


# Activity Log Schemas
class ActivityLogCreate(BaseModel):
    activity_type: ActivityType = Field(..., description="Type of activity")
    title: str = Field(..., description="Activity title")
    description: Optional[str] = Field(None, description="Activity description")
    entity_type: Optional[str] = Field(None, description="Related entity type")
    entity_id: Optional[int] = Field(None, description="Related entity ID")
    entity_name: Optional[str] = Field(None, description="Related entity name")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class ActivityLogResponse(BaseModel):
    id: int
    organization_id: int
    user_id: Optional[int]
    activity_type: ActivityType
    title: str
    description: Optional[str]
    entity_type: Optional[str]
    entity_id: Optional[int]
    entity_name: Optional[str]
    metadata: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Webhook Endpoint Schemas
class WebhookEndpointCreate(BaseModel):
    source: str = Field(..., description="Webhook source (stripe, meta, etc.)")
    endpoint_url: str = Field(..., description="Webhook endpoint URL")
    secret: Optional[str] = Field(None, description="Webhook secret for verification")
    events: Optional[List[str]] = Field(None, description="Events to listen for")
    is_active: bool = Field(True, description="Whether webhook is active")


class WebhookEndpointUpdate(BaseModel):
    endpoint_url: Optional[str] = None
    secret: Optional[str] = None
    events: Optional[List[str]] = None
    is_active: Optional[bool] = None


class WebhookEndpointResponse(BaseModel):
    id: int
    organization_id: int
    source: str
    endpoint_url: str
    secret: Optional[str]
    events: Optional[List[str]]
    is_active: bool
    total_requests: int
    successful_requests: int
    failed_requests: int
    last_request_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Webhook Event Schemas
class WebhookEventResponse(BaseModel):
    id: int
    organization_id: int
    webhook_endpoint_id: Optional[int]
    source: str
    event_type: str
    event_id: Optional[str]
    payload: Dict[str, Any]
    headers: Optional[Dict[str, Any]]
    status: str
    processed: bool
    processed_at: Optional[datetime]
    error_message: Optional[str]
    received_at: datetime

    class Config:
        from_attributes = True


# Team Invitation Schemas
class TeamInvitationCreate(BaseModel):
    email: str = Field(..., description="Email address to invite")
    role: UserRole = Field(..., description="Role to assign to the user")


class TeamInvitationResponse(BaseModel):
    id: int
    organization_id: int
    invited_by_id: int
    email: str
    role: UserRole
    invitation_token: str
    status: InvitationStatus
    accepted_at: Optional[datetime]
    expires_at: datetime
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# Notification Schemas
class NotificationCreate(BaseModel):
    title: str = Field(..., description="Notification title")
    message: str = Field(..., description="Notification message")
    notification_type: NotificationType = Field(..., description="Notification type")
    entity_type: Optional[str] = Field(None, description="Related entity type")
    entity_id: Optional[int] = Field(None, description="Related entity ID")
    action_url: Optional[str] = Field(None, description="Action URL")


class NotificationResponse(BaseModel):
    id: int
    organization_id: int
    user_id: int
    title: str
    message: str
    notification_type: NotificationType
    entity_type: Optional[str]
    entity_id: Optional[int]
    action_url: Optional[str]
    is_read: bool
    read_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# Team Management Schemas
class TeamMemberResponse(BaseModel):
    id: int
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    role: UserRole
    is_active: bool
    last_login_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class TeamMemberUpdate(BaseModel):
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class TeamStatsResponse(BaseModel):
    total_members: int
    active_members: int
    pending_invitations: int
    role_breakdown: Dict[str, int]
    recent_activity: List[ActivityLogResponse]


# Permission Schemas
class PermissionResponse(BaseModel):
    resource: str
    actions: List[str]
    conditions: Optional[Dict[str, Any]] = None


class UserPermissionsResponse(BaseModel):
    user_id: int
    role: UserRole
    permissions: List[PermissionResponse]
    inherited_permissions: List[PermissionResponse]


# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    organization_id: int
    user_id: Optional[int]
    action: str
    resource_type: str
    resource_id: Optional[int]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# Collaboration Settings Schemas
class CollaborationSettingsResponse(BaseModel):
    organization_id: int
    allow_guest_access: bool
    require_approval_for_publishing: bool
    allow_team_members_to_invite: bool
    notification_preferences: Dict[str, Any]
    webhook_settings: Dict[str, Any]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class CollaborationSettingsUpdate(BaseModel):
    allow_guest_access: Optional[bool] = None
    require_approval_for_publishing: Optional[bool] = None
    allow_team_members_to_invite: Optional[bool] = None
    notification_preferences: Optional[Dict[str, Any]] = None
    webhook_settings: Optional[Dict[str, Any]] = None


# Content Approval Schemas
class ContentApprovalCreate(BaseModel):
    content_id: int = Field(..., description="ID of the content to approve")
    requires_multiple_approvals: bool = Field(False, description="Whether multiple approvals are required")
    approval_workflow_id: Optional[int] = Field(None, description="Specific approval workflow to use")


class ContentApprovalResponse(BaseModel):
    id: int
    organization_id: int
    content_id: int
    requested_by_id: int
    requested_at: datetime
    status: str
    approver_id: Optional[int]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    requires_multiple_approvals: bool
    approval_workflow_id: Optional[int]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ContentApprovalUpdate(BaseModel):
    status: str = Field(..., description="New approval status")
    rejection_reason: Optional[str] = Field(None, description="Reason for rejection if applicable")


# Approval Workflow Schemas
class ApprovalWorkflowCreate(BaseModel):
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    content_types: Optional[List[str]] = Field(None, description="Content types this applies to")
    required_approvers: List[str] = Field(..., description="Required approver roles")
    auto_approve_conditions: Optional[Dict[str, Any]] = Field(None, description="Auto-approval conditions")


class ApprovalWorkflowResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    description: Optional[str]
    is_active: bool
    content_types: Optional[List[str]]
    required_approvers: List[str]
    auto_approve_conditions: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApprovalWorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    content_types: Optional[List[str]] = None
    required_approvers: Optional[List[str]] = None
    auto_approve_conditions: Optional[Dict[str, Any]] = None


# Content Comment Schemas
class ContentCommentCreate(BaseModel):
    content_id: int = Field(..., description="ID of the content to comment on")
    content: str = Field(..., description="Comment content")
    comment_type: str = Field("comment", description="Type of comment")
    parent_comment_id: Optional[int] = Field(None, description="Parent comment ID for replies")
    mentioned_user_ids: Optional[List[int]] = Field(None, description="Mentioned user IDs")
    tags: Optional[List[str]] = Field(None, description="Comment tags")


class ContentCommentResponse(BaseModel):
    id: int
    organization_id: int
    content_id: int
    user_id: int
    parent_comment_id: Optional[int]
    content: str
    comment_type: str
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolved_by_id: Optional[int]
    mentioned_user_ids: Optional[List[int]]
    tags: Optional[List[str]]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ContentCommentUpdate(BaseModel):
    content: Optional[str] = None
    comment_type: Optional[str] = None
    is_resolved: Optional[bool] = None
    mentioned_user_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None


# Content Version Schemas
class ContentVersionCreate(BaseModel):
    content_id: int = Field(..., description="ID of the content to version")
    change_summary: Optional[str] = Field(None, description="Summary of changes")
    change_type: str = Field("edit", description="Type of change")
    is_auto_save: bool = Field(False, description="Whether this is an auto-save")


class ContentVersionResponse(BaseModel):
    id: int
    organization_id: int
    content_id: int
    created_by_id: int
    version_number: int
    title: Optional[str]
    content: Optional[str]
    content_type: Optional[str]
    media_urls: Optional[List[str]]
    hashtags: Optional[List[str]]
    mentions: Optional[List[str]]
    platform_content: Optional[Dict[str, Any]]
    tags: Optional[List[str]]
    content_metadata: Optional[Dict[str, Any]]
    change_summary: Optional[str]
    change_type: str
    is_auto_save: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Content Feedback Schemas
class ContentFeedbackCreate(BaseModel):
    content_id: int = Field(..., description="ID of the content to provide feedback on")
    feedback_type: str = Field(..., description="Type of feedback")
    rating: Optional[int] = Field(None, description="1-5 star rating")
    comment: Optional[str] = Field(None, description="Feedback comment")
    is_anonymous: bool = Field(False, description="Whether feedback is anonymous")
    categories: Optional[List[str]] = Field(None, description="Feedback categories")


class ContentFeedbackResponse(BaseModel):
    id: int
    organization_id: int
    content_id: int
    user_id: int
    feedback_type: str
    rating: Optional[int]
    comment: Optional[str]
    is_anonymous: bool
    categories: Optional[List[str]]
    is_acknowledged: bool
    acknowledged_by_id: Optional[int]
    acknowledged_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ContentFeedbackUpdate(BaseModel):
    is_acknowledged: Optional[bool] = None
    categories: Optional[List[str]] = None
