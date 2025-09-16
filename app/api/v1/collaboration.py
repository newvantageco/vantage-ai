from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import secrets

from app.db.session import get_db
from app.models.collaboration import (
    Comment, VersionHistory, CollaborationSession, ContentLock, Notification,
    CollaborationActions, LockTypes, NotificationTypes
)
from app.models.entities import Organization
from app.api.deps import get_current_user
from pydantic import BaseModel

router = APIRouter()


class CommentCreate(BaseModel):
    content_id: str
    text: str
    parent_id: Optional[str] = None
    mentioned_user_ids: Optional[List[str]] = None


class CommentResponse(BaseModel):
    id: str
    content_id: str
    user_id: str
    text: str
    parent_id: Optional[str]
    mentioned_user_ids: List[str]
    is_resolved: bool
    is_edited: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class VersionHistoryResponse(BaseModel):
    id: str
    content_id: str
    user_id: str
    version_number: int
    action: str
    diff: Dict[str, Any]
    change_summary: Optional[str]
    is_auto_save: bool
    created_at: str

    class Config:
        from_attributes = True


class CollaborationSessionResponse(BaseModel):
    id: str
    content_id: str
    user_id: str
    user_name: str
    user_email: Optional[str]
    cursor_position: Dict[str, Any]
    last_activity: str
    created_at: str

    class Config:
        from_attributes = True


class ContentLockResponse(BaseModel):
    id: str
    content_id: str
    user_id: str
    user_name: str
    lock_type: str
    expires_at: str
    created_at: str

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    content_id: Optional[str]
    comment_id: Optional[str]
    version_id: Optional[str]
    is_read: bool
    is_archived: bool
    created_at: str
    read_at: Optional[str]

    class Config:
        from_attributes = True


@router.post("/comments", response_model=CommentResponse)
async def create_comment(
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new comment."""
    
    # Verify content belongs to org (this would need to be implemented based on your content model)
    # For now, we'll assume it's valid
    
    # Create comment
    comment = Comment(
        id=secrets.token_urlsafe(16),
        content_id=comment_data.content_id,
        org_id=current_user["org_id"],
        user_id=current_user["user_id"],
        text=comment_data.text,
        parent_id=comment_data.parent_id,
        mentioned_user_ids=json.dumps(comment_data.mentioned_user_ids or [])
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Create notifications for mentioned users
    if comment_data.mentioned_user_ids:
        for mentioned_user_id in comment_data.mentioned_user_ids:
            notification = Notification(
                id=secrets.token_urlsafe(16),
                org_id=current_user["org_id"],
                user_id=mentioned_user_id,
                type=NotificationTypes.MENTION,
                title="You were mentioned in a comment",
                message=f"{current_user.get('name', 'Someone')} mentioned you in a comment",
                content_id=comment_data.content_id,
                comment_id=comment.id
            )
            db.add(notification)
    
    db.commit()
    
    return CommentResponse(
        id=comment.id,
        content_id=comment.content_id,
        user_id=comment.user_id,
        text=comment.text,
        parent_id=comment.parent_id,
        mentioned_user_ids=comment.get_mentioned_user_ids(),
        is_resolved=comment.is_resolved,
        is_edited=comment.is_edited,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat()
    )


@router.get("/comments", response_model=List[CommentResponse])
async def list_comments(
    content_id: str,
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List comments for a content item."""
    comments = db.query(Comment).filter(
        Comment.content_id == content_id,
        Comment.org_id == current_user["org_id"]
    ).order_by(Comment.created_at.asc()).offset(offset).limit(limit).all()
    
    return [
        CommentResponse(
            id=comment.id,
            content_id=comment.content_id,
            user_id=comment.user_id,
            text=comment.text,
            parent_id=comment.parent_id,
            mentioned_user_ids=comment.get_mentioned_user_ids(),
            is_resolved=comment.is_resolved,
            is_edited=comment.is_edited,
            created_at=comment.created_at.isoformat(),
            updated_at=comment.updated_at.isoformat()
        )
        for comment in comments
    ]


@router.put("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    text: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Update a comment."""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.org_id == current_user["org_id"],
        Comment.user_id == current_user["user_id"]
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    comment.text = text
    comment.is_edited = True
    db.commit()
    db.refresh(comment)
    
    return CommentResponse(
        id=comment.id,
        content_id=comment.content_id,
        user_id=comment.user_id,
        text=comment.text,
        parent_id=comment.parent_id,
        mentioned_user_ids=comment.get_mentioned_user_ids(),
        is_resolved=comment.is_resolved,
        is_edited=comment.is_edited,
        created_at=comment.created_at.isoformat(),
        updated_at=comment.updated_at.isoformat()
    )


@router.delete("/comments/{comment_id}")
async def delete_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Delete a comment."""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.org_id == current_user["org_id"],
        Comment.user_id == current_user["user_id"]
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    db.delete(comment)
    db.commit()
    
    return {"message": "Comment deleted successfully"}


@router.post("/comments/{comment_id}/resolve")
async def resolve_comment(
    comment_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Resolve a comment."""
    comment = db.query(Comment).filter(
        Comment.id == comment_id,
        Comment.org_id == current_user["org_id"]
    ).first()
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    comment.is_resolved = True
    db.commit()
    
    return {"message": "Comment resolved successfully"}


@router.get("/version-history/{content_id}", response_model=List[VersionHistoryResponse])
async def get_version_history(
    content_id: str,
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get version history for a content item."""
    versions = db.query(VersionHistory).filter(
        VersionHistory.content_id == content_id,
        VersionHistory.org_id == current_user["org_id"]
    ).order_by(desc(VersionHistory.version_number)).offset(offset).limit(limit).all()
    
    return [
        VersionHistoryResponse(
            id=version.id,
            content_id=version.content_id,
            user_id=version.user_id,
            version_number=version.version_number,
            action=version.action,
            diff=version.get_diff(),
            change_summary=version.change_summary,
            is_auto_save=version.is_auto_save,
            created_at=version.created_at.isoformat()
        )
        for version in versions
    ]


@router.post("/version-history", response_model=VersionHistoryResponse)
async def create_version(
    content_id: str,
    action: str,
    diff: Dict[str, Any],
    change_summary: Optional[str] = None,
    is_auto_save: bool = False,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Create a new version entry."""
    
    # Get the next version number
    last_version = db.query(VersionHistory).filter(
        VersionHistory.content_id == content_id
    ).order_by(desc(VersionHistory.version_number)).first()
    
    version_number = (last_version.version_number + 1) if last_version else 1
    
    # Create version
    version = VersionHistory(
        id=secrets.token_urlsafe(16),
        content_id=content_id,
        org_id=current_user["org_id"],
        user_id=current_user["user_id"],
        version_number=version_number,
        action=action,
        diff_json=json.dumps(diff),
        change_summary=change_summary,
        is_auto_save=is_auto_save
    )
    
    db.add(version)
    db.commit()
    db.refresh(version)
    
    return VersionHistoryResponse(
        id=version.id,
        content_id=version.content_id,
        user_id=version.user_id,
        version_number=version.version_number,
        action=version.action,
        diff=version.get_diff(),
        change_summary=version.change_summary,
        is_auto_save=version.is_auto_save,
        created_at=version.created_at.isoformat()
    )


@router.get("/collaboration-sessions/{content_id}", response_model=List[CollaborationSessionResponse])
async def get_collaboration_sessions(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get active collaboration sessions for a content item."""
    # Clean up expired sessions
    expired_sessions = db.query(CollaborationSession).filter(
        CollaborationSession.content_id == content_id,
        CollaborationSession.last_activity < datetime.utcnow() - timedelta(minutes=5)
    ).all()
    
    for session in expired_sessions:
        db.delete(session)
    
    db.commit()
    
    # Get active sessions
    sessions = db.query(CollaborationSession).filter(
        CollaborationSession.content_id == content_id,
        CollaborationSession.org_id == current_user["org_id"]
    ).all()
    
    return [
        CollaborationSessionResponse(
            id=session.id,
            content_id=session.content_id,
            user_id=session.user_id,
            user_name=session.user_name,
            user_email=session.user_email,
            cursor_position=session.get_cursor_position(),
            last_activity=session.last_activity.isoformat(),
            created_at=session.created_at.isoformat()
        )
        for session in sessions
    ]


@router.post("/collaboration-sessions", response_model=CollaborationSessionResponse)
async def join_collaboration_session(
    content_id: str,
    user_name: str,
    user_email: Optional[str] = None,
    cursor_position: Optional[Dict[str, Any]] = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Join a collaboration session."""
    
    # Check if user already has a session
    existing_session = db.query(CollaborationSession).filter(
        CollaborationSession.content_id == content_id,
        CollaborationSession.user_id == current_user["user_id"]
    ).first()
    
    if existing_session:
        # Update existing session
        existing_session.user_name = user_name
        existing_session.user_email = user_email
        existing_session.last_activity = datetime.utcnow()
        if cursor_position:
            existing_session.set_cursor_position(cursor_position)
        
        db.commit()
        db.refresh(existing_session)
        
        return CollaborationSessionResponse(
            id=existing_session.id,
            content_id=existing_session.content_id,
            user_id=existing_session.user_id,
            user_name=existing_session.user_name,
            user_email=existing_session.user_email,
            cursor_position=existing_session.get_cursor_position(),
            last_activity=existing_session.last_activity.isoformat(),
            created_at=existing_session.created_at.isoformat()
        )
    
    # Create new session
    session = CollaborationSession(
        id=secrets.token_urlsafe(16),
        content_id=content_id,
        org_id=current_user["org_id"],
        user_id=current_user["user_id"],
        user_name=user_name,
        user_email=user_email,
        cursor_position=json.dumps(cursor_position or {})
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return CollaborationSessionResponse(
        id=session.id,
        content_id=session.content_id,
        user_id=session.user_id,
        user_name=session.user_name,
        user_email=session.user_email,
        cursor_position=session.get_cursor_position(),
        last_activity=session.last_activity.isoformat(),
        created_at=session.created_at.isoformat()
    )


@router.delete("/collaboration-sessions/{session_id}")
async def leave_collaboration_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Leave a collaboration session."""
    session = db.query(CollaborationSession).filter(
        CollaborationSession.id == session_id,
        CollaborationSession.user_id == current_user["user_id"]
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collaboration session not found"
        )
    
    db.delete(session)
    db.commit()
    
    return {"message": "Left collaboration session successfully"}


@router.post("/content-locks", response_model=ContentLockResponse)
async def lock_content(
    content_id: str,
    lock_type: str,
    user_name: str,
    duration_minutes: int = 30,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Lock content for editing."""
    
    # Check if content is already locked
    existing_lock = db.query(ContentLock).filter(
        ContentLock.content_id == content_id
    ).first()
    
    if existing_lock and not existing_lock.is_expired():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Content is already locked by {existing_lock.user_name}"
        )
    
    # Remove expired locks
    if existing_lock and existing_lock.is_expired():
        db.delete(existing_lock)
    
    # Create new lock
    lock = ContentLock(
        id=secrets.token_urlsafe(16),
        content_id=content_id,
        org_id=current_user["org_id"],
        user_id=current_user["user_id"],
        user_name=user_name,
        lock_type=lock_type,
        expires_at=datetime.utcnow() + timedelta(minutes=duration_minutes)
    )
    
    db.add(lock)
    db.commit()
    db.refresh(lock)
    
    return ContentLockResponse(
        id=lock.id,
        content_id=lock.content_id,
        user_id=lock.user_id,
        user_name=lock.user_name,
        lock_type=lock.lock_type,
        expires_at=lock.expires_at.isoformat(),
        created_at=lock.created_at.isoformat()
    )


@router.delete("/content-locks/{content_id}")
async def unlock_content(
    content_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Unlock content."""
    lock = db.query(ContentLock).filter(
        ContentLock.content_id == content_id,
        ContentLock.user_id == current_user["user_id"]
    ).first()
    
    if not lock:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content lock not found"
        )
    
    db.delete(lock)
    db.commit()
    
    return {"message": "Content unlocked successfully"}


@router.get("/notifications", response_model=List[NotificationResponse])
async def list_notifications(
    is_read: Optional[bool] = None,
    limit: int = Query(50, description="Number of results to return"),
    offset: int = Query(0, description="Number of results to skip"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """List notifications for the current user."""
    query = db.query(Notification).filter(
        Notification.user_id == current_user["user_id"],
        Notification.is_archived == False
    )
    
    if is_read is not None:
        query = query.filter(Notification.is_read == is_read)
    
    notifications = query.order_by(desc(Notification.created_at)).offset(offset).limit(limit).all()
    
    return [
        NotificationResponse(
            id=notification.id,
            type=notification.type,
            title=notification.title,
            message=notification.message,
            content_id=notification.content_id,
            comment_id=notification.comment_id,
            version_id=notification.version_id,
            is_read=notification.is_read,
            is_archived=notification.is_archived,
            created_at=notification.created_at.isoformat(),
            read_at=notification.read_at.isoformat() if notification.read_at else None
        )
        for notification in notifications
    ]


@router.put("/notifications/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Mark a notification as read."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user["user_id"]
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Notification marked as read"}


@router.put("/notifications/{notification_id}/archive")
async def archive_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Archive a notification."""
    notification = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user["user_id"]
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_archived = True
    db.commit()
    
    return {"message": "Notification archived"}


@router.get("/collaboration/available-actions")
async def get_available_actions():
    """Get available collaboration actions and types."""
    return {
        "actions": CollaborationActions.ALL_ACTIONS,
        "lock_types": LockTypes.ALL_TYPES,
        "notification_types": NotificationTypes.ALL_TYPES
    }
