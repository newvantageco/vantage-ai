from __future__ import annotations

import logging
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.conversations import Conversation, Message
from app.models.entities import UserAccount
from app.integrations.whatsapp import WhatsAppIntegration
from app.services.model_router import ModelRouter

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/inbox", tags=["inbox"])


@router.get("/threads")
async def get_conversation_threads(
    channel: Optional[str] = Query(None, description="Filter by channel (whatsapp, sms, etc.)"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get conversation threads for the organization."""
    query = db.query(Conversation).filter(Conversation.org_id == current_user.org_id)
    
    if channel:
        query = query.filter(Conversation.channel == channel)
    
    # Order by last message time (most recent first)
    query = query.order_by(Conversation.last_message_at.desc().nullslast())
    
    total = query.count()
    conversations = query.offset(offset).limit(limit).all()
    
    # Get message counts for each conversation
    for conv in conversations:
        conv.message_count = db.query(Message).filter(Message.conversation_id == conv.id).count()
    
    return {
        "threads": [conv.to_dict() for conv in conversations],
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.get("/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get a specific conversation with its messages."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.org_id == current_user.org_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Get messages
    messages_query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc())
    
    total_messages = messages_query.count()
    messages = messages_query.offset(offset).limit(limit).all()
    
    return {
        "conversation": conversation.to_dict(),
        "messages": [msg.to_dict() for msg in messages],
        "total_messages": total_messages,
        "offset": offset,
        "limit": limit
    }


@router.post("/{conversation_id}/reply")
async def reply_to_conversation(
    conversation_id: str,
    message_text: str,
    message_type: str = "text",
    media_url: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Send a reply to a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.org_id == current_user.org_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Send message via appropriate channel
        if conversation.channel == "whatsapp":
            whatsapp = WhatsAppIntegration()
            
            if message_type == "text":
                result = await whatsapp.send_message(conversation.peer_id, message_text)
            elif message_type in ["image", "video", "audio", "document"] and media_url:
                result = await whatsapp.send_media_message(
                    conversation.peer_id, 
                    media_url, 
                    message_type
                )
            else:
                raise HTTPException(status_code=400, detail="Invalid message type or missing media URL")
        else:
            # For other channels, you'd implement their respective integrations
            raise HTTPException(status_code=400, detail=f"Channel {conversation.channel} not supported yet")
        
        # Create message record
        message = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            direction="outbound",
            text=message_text,
            media_url=media_url,
            metadata={
                "channel": conversation.channel,
                "sent_by": current_user.id,
                "api_result": result
            }
        )
        
        db.add(message)
        
        # Update conversation last message time
        conversation.last_message_at = message.created_at
        
        db.commit()
        
        logger.info(f"Reply sent to conversation {conversation_id} via {conversation.channel}")
        
        return {
            "status": "success",
            "message": message.to_dict(),
            "api_result": result
        }
        
    except Exception as e:
        logger.error(f"Error sending reply to conversation {conversation_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to send reply: {str(e)}")


@router.post("/{conversation_id}/ai-draft")
async def generate_ai_draft(
    conversation_id: str,
    context: Optional[str] = None,
    tone: str = "professional",
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Generate an AI-drafted reply for a conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.org_id == current_user.org_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    try:
        # Get recent messages for context
        recent_messages = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at.desc()).limit(10).all()
        
        # Prepare context for AI
        message_history = []
        for msg in reversed(recent_messages):  # Reverse to get chronological order
            message_history.append({
                "direction": msg.direction,
                "text": msg.text,
                "timestamp": msg.created_at.isoformat()
            })
        
        # Get brand guide for context
        from app.models.content import BrandGuide
        brand_guide = db.query(BrandGuide).filter(
            BrandGuide.org_id == current_user.org_id
        ).first()
        
        # Prepare prompt for AI
        prompt_context = {
            "conversation_history": message_history,
            "customer_phone": conversation.peer_id,
            "channel": conversation.channel,
            "tone": tone,
            "additional_context": context,
            "brand_guide": {
                "voice": brand_guide.voice if brand_guide else None,
                "audience": brand_guide.audience if brand_guide else None,
                "pillars": brand_guide.pillars if brand_guide else None
            } if brand_guide else None
        }
        
        # Generate AI draft using model router
        model_router = ModelRouter()
        ai_draft = await model_router.rewrite_to_voice(
            prompt_context, 
            rewrite_type="whatsapp_reply"
        )
        
        return {
            "status": "success",
            "draft": ai_draft,
            "context_used": prompt_context
        }
        
    except Exception as e:
        logger.error(f"Error generating AI draft for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate AI draft: {str(e)}")


@router.get("/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get messages for a specific conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.org_id == current_user.org_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages_query = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc())
    
    total = messages_query.count()
    messages = messages_query.offset(offset).limit(limit).all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [msg.to_dict() for msg in messages],
        "total": total,
        "offset": offset,
        "limit": limit
    }


@router.post("/{conversation_id}/mark-read")
async def mark_conversation_read(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, str]:
    """Mark a conversation as read (for UI state management)."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.org_id == current_user.org_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # In a real implementation, you might track read status per user
    # For now, we'll just return success
    return {"status": "success", "message": "Conversation marked as read"}


@router.get("/stats/summary")
async def get_inbox_stats(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get inbox statistics for the organization."""
    # Total conversations
    total_conversations = db.query(Conversation).filter(
        Conversation.org_id == current_user.org_id
    ).count()
    
    # Unread conversations (conversations with messages in last 24h that haven't been "read")
    from datetime import datetime, timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    recent_conversations = db.query(Conversation).filter(
        Conversation.org_id == current_user.org_id,
        Conversation.last_message_at >= yesterday
    ).count()
    
    # Messages by channel
    channel_stats = {}
    channels = db.query(Conversation.channel).filter(
        Conversation.org_id == current_user.org_id
    ).distinct().all()
    
    for (channel,) in channels:
        count = db.query(Conversation).filter(
            Conversation.org_id == current_user.org_id,
            Conversation.channel == channel
        ).count()
        channel_stats[channel] = count
    
    return {
        "total_conversations": total_conversations,
        "recent_conversations": recent_conversations,
        "channel_breakdown": channel_stats,
        "generated_at": datetime.utcnow().isoformat()
    }
