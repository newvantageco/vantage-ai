"""
Collaboration API Router
Handles RBAC, activity logs, and team collaboration features
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.api.deps import get_db, get_current_user
from app.schemas.collaboration import (
    ActivityLogResponse, ActivityLogCreate,
    WebhookEndpointResponse, WebhookEndpointCreate, WebhookEndpointUpdate,
    WebhookEventResponse, TeamInvitationResponse, TeamInvitationCreate,
    NotificationResponse, NotificationCreate,
    ContentApprovalResponse, ContentApprovalCreate, ContentApprovalUpdate,
    ApprovalWorkflowResponse, ApprovalWorkflowCreate, ApprovalWorkflowUpdate,
    ContentCommentResponse, ContentCommentCreate, ContentCommentUpdate,
    ContentVersionResponse, ContentVersionCreate,
    ContentFeedbackResponse, ContentFeedbackCreate, ContentFeedbackUpdate
)
from app.models.collaboration import (
    ActivityLog, WebhookEndpoint, WebhookEvent, TeamInvitation, Notification,
    ContentApproval, ApprovalWorkflow, ContentComment, ContentVersion, ContentFeedback
)
from app.models.cms import UserAccount, Organization
from app.services.webhook_service import WebhookService

router = APIRouter()


# Activity Log endpoints
@router.post("/activity", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED)
async def create_activity_log(
    activity: ActivityLogCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ActivityLogResponse:
    """Create a new activity log entry."""
    activity_log = ActivityLog(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        **activity.dict()
    )
    db.add(activity_log)
    db.commit()
    db.refresh(activity_log)
    return ActivityLogResponse.from_orm(activity_log)


@router.get("/activity", response_model=List[ActivityLogResponse])
async def list_activity_logs(
    skip: int = 0,
    limit: int = 20,
    activity_type: Optional[str] = Query(None, description="Filter by activity type"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type"),
    entity_id: Optional[int] = Query(None, description="Filter by entity ID"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ActivityLogResponse]:
    """List activity logs for the current organization."""
    query = db.query(ActivityLog).filter(
        ActivityLog.organization_id == current_user.organization_id
    )
    
    if activity_type:
        query = query.filter(ActivityLog.activity_type == activity_type)
    if entity_type:
        query = query.filter(ActivityLog.entity_type == entity_type)
    if entity_id:
        query = query.filter(ActivityLog.entity_id == entity_id)
    
    activities = query.order_by(desc(ActivityLog.created_at)).offset(skip).limit(limit).all()
    return [ActivityLogResponse.from_orm(activity) for activity in activities]


@router.get("/activity/{activity_id}", response_model=ActivityLogResponse)
async def get_activity_log(
    activity_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ActivityLogResponse:
    """Get a specific activity log entry."""
    activity = db.query(ActivityLog).filter(
        ActivityLog.id == activity_id,
        ActivityLog.organization_id == current_user.organization_id
    ).first()
    
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity log not found"
        )
    
    return ActivityLogResponse.from_orm(activity)


# Webhook endpoints
@router.post("/webhooks", response_model=WebhookEndpointResponse, status_code=status.HTTP_201_CREATED)
async def create_webhook_endpoint(
    webhook: WebhookEndpointCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> WebhookEndpointResponse:
    """Create a new webhook endpoint."""
    webhook_endpoint = WebhookEndpoint(
        organization_id=current_user.organization_id,
        **webhook.dict()
    )
    db.add(webhook_endpoint)
    db.commit()
    db.refresh(webhook_endpoint)
    return WebhookEndpointResponse.from_orm(webhook_endpoint)


@router.get("/webhooks", response_model=List[WebhookEndpointResponse])
async def list_webhook_endpoints(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[WebhookEndpointResponse]:
    """List webhook endpoints for the current organization."""
    webhooks = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.organization_id == current_user.organization_id
    ).offset(skip).limit(limit).all()
    return [WebhookEndpointResponse.from_orm(webhook) for webhook in webhooks]


@router.get("/webhooks/{webhook_id}", response_model=WebhookEndpointResponse)
async def get_webhook_endpoint(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> WebhookEndpointResponse:
    """Get a specific webhook endpoint."""
    webhook = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.id == webhook_id,
        WebhookEndpoint.organization_id == current_user.organization_id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    return WebhookEndpointResponse.from_orm(webhook)


@router.put("/webhooks/{webhook_id}", response_model=WebhookEndpointResponse)
async def update_webhook_endpoint(
    webhook_id: int,
    webhook_update: WebhookEndpointUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> WebhookEndpointResponse:
    """Update a webhook endpoint."""
    webhook = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.id == webhook_id,
        WebhookEndpoint.organization_id == current_user.organization_id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    update_data = webhook_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(webhook, field, value)
    
    db.commit()
    db.refresh(webhook)
    return WebhookEndpointResponse.from_orm(webhook)


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_webhook_endpoint(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Delete a webhook endpoint."""
    webhook = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.id == webhook_id,
        WebhookEndpoint.organization_id == current_user.organization_id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    db.delete(webhook)
    db.commit()


@router.post("/webhooks/{webhook_id}/test", status_code=status.HTTP_200_OK)
async def test_webhook_endpoint(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Test a webhook endpoint."""
    webhook = db.query(WebhookEndpoint).filter(
        WebhookEndpoint.id == webhook_id,
        WebhookEndpoint.organization_id == current_user.organization_id
    ).first()
    
    if not webhook:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Webhook endpoint not found"
        )
    
    try:
        webhook_service = WebhookService()
        result = await webhook_service.test_webhook(webhook)
        return {"status": "success", "message": "Webhook test completed", "result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook test failed: {str(e)}"
        )


# Generic webhook receiver
@router.post("/webhooks/inbound/{source}")
async def receive_webhook(
    source: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """Generic webhook receiver for inbound events."""
    try:
        # Get webhook endpoints for this source
        webhooks = db.query(WebhookEndpoint).filter(
            WebhookEndpoint.source == source,
            WebhookEndpoint.is_active == True
        ).all()
        
        if not webhooks:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No active webhook endpoints found for source: {source}"
            )
        
        # Get request data
        payload = await request.json()
        headers = dict(request.headers)
        
        # Process webhook for each endpoint
        webhook_service = WebhookService()
        results = []
        
        for webhook in webhooks:
            try:
                # Verify webhook signature if secret is provided
                if webhook.secret:
                    is_valid = await webhook_service.verify_signature(
                        payload, headers, webhook.secret
                    )
                    if not is_valid:
                        continue
                
                # Process webhook
                result = await webhook_service.process_webhook(webhook, payload, headers)
                results.append({"webhook_id": webhook.id, "status": "success", "result": result})
                
                # Update webhook statistics
                webhook.total_requests += 1
                webhook.successful_requests += 1
                webhook.last_request_at = datetime.utcnow()
                
            except Exception as e:
                results.append({"webhook_id": webhook.id, "status": "failed", "error": str(e)})
                webhook.failed_requests += 1
        
        db.commit()
        
        return {"status": "success", "processed_webhooks": len(results), "results": results}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Webhook processing failed: {str(e)}"
        )


# Team Invitation endpoints
@router.post("/invitations", response_model=TeamInvitationResponse, status_code=status.HTTP_201_CREATED)
async def create_team_invitation(
    invitation: TeamInvitationCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> TeamInvitationResponse:
    """Create a team invitation."""
    # Check if user has permission to invite
    if current_user.role not in ["owner", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions to create invitations"
        )
    
    # Generate invitation token
    invitation_token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=7)  # 7 days expiry
    
    team_invitation = TeamInvitation(
        organization_id=current_user.organization_id,
        invited_by_id=current_user.id,
        email=invitation.email,
        role=invitation.role,
        invitation_token=invitation_token,
        expires_at=expires_at
    )
    
    db.add(team_invitation)
    db.commit()
    db.refresh(team_invitation)
    
    # FIXME: Send invitation email
    
    return TeamInvitationResponse.from_orm(team_invitation)


@router.get("/invitations", response_model=List[TeamInvitationResponse])
async def list_team_invitations(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[TeamInvitationResponse]:
    """List team invitations for the current organization."""
    query = db.query(TeamInvitation).filter(
        TeamInvitation.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(TeamInvitation.status == status)
    
    invitations = query.offset(skip).limit(limit).all()
    return [TeamInvitationResponse.from_orm(invitation) for invitation in invitations]


@router.post("/invitations/{invitation_id}/accept", status_code=status.HTTP_200_OK)
async def accept_team_invitation(
    invitation_id: int,
    token: str = Query(..., description="Invitation token"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Accept a team invitation."""
    invitation = db.query(TeamInvitation).filter(
        TeamInvitation.id == invitation_id,
        TeamInvitation.invitation_token == token,
        TeamInvitation.status == "pending"
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or already processed"
        )
    
    if invitation.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation has expired"
        )
    
    # Update invitation status
    invitation.status = "accepted"
    invitation.accepted_at = datetime.utcnow()
    
    # Update user role if they're in the same organization
    if current_user.organization_id == invitation.organization_id:
        current_user.role = invitation.role
        db.commit()
    
    return {"status": "success", "message": "Invitation accepted successfully"}


@router.post("/invitations/{invitation_id}/cancel", status_code=status.HTTP_200_OK)
async def cancel_team_invitation(
    invitation_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Cancel a team invitation."""
    invitation = db.query(TeamInvitation).filter(
        TeamInvitation.id == invitation_id,
        TeamInvitation.organization_id == current_user.organization_id
    ).first()
    
    if not invitation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found"
        )
    
    if invitation.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invitation cannot be cancelled"
        )
    
    invitation.status = "cancelled"
    db.commit()
    
    return {"status": "success", "message": "Invitation cancelled successfully"}


# Notification endpoints
@router.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    skip: int = 0,
    limit: int = 20,
    unread_only: bool = Query(False, description="Show only unread notifications"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[NotificationResponse]:
    """List notifications for the current user."""
    query = db.query(Notification).filter(
        Notification.user_id == current_user.id
    )
    
    if unread_only:
        query = query.filter(Notification.is_read == False)
    
    notifications = query.order_by(desc(Notification.created_at)).offset(skip).limit(limit).all()
    return [NotificationResponse.from_orm(notification) for notification in notifications]


@router.post("/notifications/{notification_id}/read", status_code=status.HTTP_200_OK)
async def mark_notification_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"status": "success", "message": "Notification marked as read"}


@router.post("/notifications/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_notifications_read(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """Mark all notifications as read for the current user."""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False
    ).update({
        "is_read": True,
        "read_at": datetime.utcnow()
    })
    db.commit()
    
    return {"status": "success", "message": "All notifications marked as read"}


# Content Approval endpoints
@router.post("/content-approvals", response_model=ContentApprovalResponse, status_code=status.HTTP_201_CREATED)
async def create_content_approval(
    approval: ContentApprovalCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentApprovalResponse:
    """Create a content approval request."""
    content_approval = ContentApproval(
        organization_id=current_user.organization_id,
        requested_by_id=current_user.id,
        **approval.dict()
    )
    db.add(content_approval)
    db.commit()
    db.refresh(content_approval)
    return ContentApprovalResponse.from_orm(content_approval)


@router.get("/content-approvals", response_model=List[ContentApprovalResponse])
async def list_content_approvals(
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = Query(None, description="Filter by status"),
    content_id: Optional[int] = Query(None, description="Filter by content ID"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ContentApprovalResponse]:
    """List content approvals for the current organization."""
    query = db.query(ContentApproval).filter(
        ContentApproval.organization_id == current_user.organization_id
    )
    
    if status:
        query = query.filter(ContentApproval.status == status)
    if content_id:
        query = query.filter(ContentApproval.content_id == content_id)
    
    approvals = query.order_by(desc(ContentApproval.created_at)).offset(skip).limit(limit).all()
    return [ContentApprovalResponse.from_orm(approval) for approval in approvals]


@router.put("/content-approvals/{approval_id}", response_model=ContentApprovalResponse)
async def update_content_approval(
    approval_id: int,
    approval_update: ContentApprovalUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentApprovalResponse:
    """Update a content approval (approve/reject)."""
    approval = db.query(ContentApproval).filter(
        ContentApproval.id == approval_id,
        ContentApproval.organization_id == current_user.organization_id
    ).first()
    
    if not approval:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content approval not found"
        )
    
    # Update approval
    approval.status = approval_update.status
    approval.approver_id = current_user.id
    approval.approved_at = datetime.utcnow()
    
    if approval_update.rejection_reason:
        approval.rejection_reason = approval_update.rejection_reason
    
    db.commit()
    db.refresh(approval)
    return ContentApprovalResponse.from_orm(approval)


# Approval Workflow endpoints
@router.post("/approval-workflows", response_model=ApprovalWorkflowResponse, status_code=status.HTTP_201_CREATED)
async def create_approval_workflow(
    workflow: ApprovalWorkflowCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ApprovalWorkflowResponse:
    """Create an approval workflow."""
    approval_workflow = ApprovalWorkflow(
        organization_id=current_user.organization_id,
        **workflow.dict()
    )
    db.add(approval_workflow)
    db.commit()
    db.refresh(approval_workflow)
    return ApprovalWorkflowResponse.from_orm(approval_workflow)


@router.get("/approval-workflows", response_model=List[ApprovalWorkflowResponse])
async def list_approval_workflows(
    skip: int = 0,
    limit: int = 20,
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ApprovalWorkflowResponse]:
    """List approval workflows for the current organization."""
    query = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.organization_id == current_user.organization_id
    )
    
    if is_active is not None:
        query = query.filter(ApprovalWorkflow.is_active == is_active)
    
    workflows = query.order_by(desc(ApprovalWorkflow.created_at)).offset(skip).limit(limit).all()
    return [ApprovalWorkflowResponse.from_orm(workflow) for workflow in workflows]


@router.put("/approval-workflows/{workflow_id}", response_model=ApprovalWorkflowResponse)
async def update_approval_workflow(
    workflow_id: int,
    workflow_update: ApprovalWorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ApprovalWorkflowResponse:
    """Update an approval workflow."""
    workflow = db.query(ApprovalWorkflow).filter(
        ApprovalWorkflow.id == workflow_id,
        ApprovalWorkflow.organization_id == current_user.organization_id
    ).first()
    
    if not workflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approval workflow not found"
        )
    
    update_data = workflow_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    return ApprovalWorkflowResponse.from_orm(workflow)


# Content Comment endpoints
@router.post("/content-comments", response_model=ContentCommentResponse, status_code=status.HTTP_201_CREATED)
async def create_content_comment(
    comment: ContentCommentCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentCommentResponse:
    """Create a content comment."""
    content_comment = ContentComment(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        **comment.dict()
    )
    db.add(content_comment)
    db.commit()
    db.refresh(content_comment)
    return ContentCommentResponse.from_orm(content_comment)


@router.get("/content-comments", response_model=List[ContentCommentResponse])
async def list_content_comments(
    content_id: int = Query(..., description="Content ID to get comments for"),
    skip: int = 0,
    limit: int = 20,
    comment_type: Optional[str] = Query(None, description="Filter by comment type"),
    is_resolved: Optional[bool] = Query(None, description="Filter by resolved status"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ContentCommentResponse]:
    """List comments for a specific content item."""
    query = db.query(ContentComment).filter(
        ContentComment.organization_id == current_user.organization_id,
        ContentComment.content_id == content_id
    )
    
    if comment_type:
        query = query.filter(ContentComment.comment_type == comment_type)
    if is_resolved is not None:
        query = query.filter(ContentComment.is_resolved == is_resolved)
    
    comments = query.order_by(ContentComment.created_at).offset(skip).limit(limit).all()
    return [ContentCommentResponse.from_orm(comment) for comment in comments]


@router.put("/content-comments/{comment_id}", response_model=ContentCommentResponse)
async def update_content_comment(
    comment_id: int,
    comment_update: ContentCommentUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentCommentResponse:
    """Update a content comment."""
    comment = db.query(ContentComment).filter(
        ContentComment.id == comment_id,
        ContentComment.organization_id == current_user.organization_id,
        ContentComment.user_id == current_user.id
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content comment not found"
        )
    
    update_data = comment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    
    if comment_update.is_resolved:
        comment.resolved_at = datetime.utcnow()
        comment.resolved_by_id = current_user.id
    
    db.commit()
    db.refresh(comment)
    return ContentCommentResponse.from_orm(comment)


# Content Version endpoints
@router.post("/content-versions", response_model=ContentVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_content_version(
    version: ContentVersionCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentVersionResponse:
    """Create a content version."""
    # Get the latest version number
    latest_version = db.query(ContentVersion).filter(
        ContentVersion.content_id == version.content_id
    ).order_by(desc(ContentVersion.version_number)).first()
    
    version_number = (latest_version.version_number + 1) if latest_version else 1
    
    content_version = ContentVersion(
        organization_id=current_user.organization_id,
        created_by_id=current_user.id,
        version_number=version_number,
        **version.dict()
    )
    db.add(content_version)
    db.commit()
    db.refresh(content_version)
    return ContentVersionResponse.from_orm(content_version)


@router.get("/content-versions", response_model=List[ContentVersionResponse])
async def list_content_versions(
    content_id: int = Query(..., description="Content ID to get versions for"),
    skip: int = 0,
    limit: int = 20,
    change_type: Optional[str] = Query(None, description="Filter by change type"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ContentVersionResponse]:
    """List versions for a specific content item."""
    query = db.query(ContentVersion).filter(
        ContentVersion.organization_id == current_user.organization_id,
        ContentVersion.content_id == content_id
    )
    
    if change_type:
        query = query.filter(ContentVersion.change_type == change_type)
    
    versions = query.order_by(desc(ContentVersion.version_number)).offset(skip).limit(limit).all()
    return [ContentVersionResponse.from_orm(version) for version in versions]


# Content Feedback endpoints
@router.post("/content-feedback", response_model=ContentFeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_content_feedback(
    feedback: ContentFeedbackCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentFeedbackResponse:
    """Create content feedback."""
    content_feedback = ContentFeedback(
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        **feedback.dict()
    )
    db.add(content_feedback)
    db.commit()
    db.refresh(content_feedback)
    return ContentFeedbackResponse.from_orm(content_feedback)


@router.get("/content-feedback", response_model=List[ContentFeedbackResponse])
async def list_content_feedback(
    content_id: int = Query(..., description="Content ID to get feedback for"),
    skip: int = 0,
    limit: int = 20,
    feedback_type: Optional[str] = Query(None, description="Filter by feedback type"),
    is_acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[ContentFeedbackResponse]:
    """List feedback for a specific content item."""
    query = db.query(ContentFeedback).filter(
        ContentFeedback.organization_id == current_user.organization_id,
        ContentFeedback.content_id == content_id
    )
    
    if feedback_type:
        query = query.filter(ContentFeedback.feedback_type == feedback_type)
    if is_acknowledged is not None:
        query = query.filter(ContentFeedback.is_acknowledged == is_acknowledged)
    
    feedback_list = query.order_by(desc(ContentFeedback.created_at)).offset(skip).limit(limit).all()
    return [ContentFeedbackResponse.from_orm(feedback) for feedback in feedback_list]


@router.put("/content-feedback/{feedback_id}", response_model=ContentFeedbackResponse)
async def update_content_feedback(
    feedback_id: int,
    feedback_update: ContentFeedbackUpdate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> ContentFeedbackResponse:
    """Update content feedback (acknowledge, categorize)."""
    feedback = db.query(ContentFeedback).filter(
        ContentFeedback.id == feedback_id,
        ContentFeedback.organization_id == current_user.organization_id
    ).first()
    
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content feedback not found"
        )
    
    update_data = feedback_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(feedback, field, value)
    
    if feedback_update.is_acknowledged:
        feedback.acknowledged_at = datetime.utcnow()
        feedback.acknowledged_by_id = current_user.id
    
    db.commit()
    db.refresh(feedback)
    return ContentFeedbackResponse.from_orm(feedback)