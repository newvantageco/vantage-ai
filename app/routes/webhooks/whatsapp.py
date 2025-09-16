from __future__ import annotations

import logging
from typing import Dict, Any, Optional

from fastapi import APIRouter, Request, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.integrations.whatsapp import WhatsAppIntegration
from app.models.conversations import Conversation, Message

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/whatsapp", tags=["webhooks-whatsapp"])


@router.get("/")
async def verify_webhook(
    hub_mode: str,
    hub_verify_token: str,
    hub_challenge: str,
    db: Session = Depends(get_db)
) -> str:
    """Verify WhatsApp webhook token."""
    whatsapp = WhatsAppIntegration()
    challenge = whatsapp.verify_webhook(hub_mode, hub_verify_token, hub_challenge)
    
    if challenge:
        logger.info("WhatsApp webhook verification successful")
        return challenge
    else:
        logger.warning("WhatsApp webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/")
async def handle_webhook(
    request: Request,
    db: Session = Depends(get_db)
) -> Dict[str, str]:
    """Handle incoming WhatsApp messages."""
    try:
        # Parse webhook data
        webhook_data = await request.json()
        logger.info(f"WhatsApp webhook received: {webhook_data}")
        
        whatsapp = WhatsAppIntegration()
        messages = whatsapp.parse_webhook_message(webhook_data)
        
        # Process each message
        for message_data in messages:
            await process_incoming_message(message_data, db)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing WhatsApp webhook: {e}")
        raise HTTPException(status_code=500, detail="Webhook processing failed")


async def process_incoming_message(message_data: Dict[str, Any], db: Session):
    """Process an incoming WhatsApp message."""
    try:
        from_number = message_data.get("from")
        message_id = message_data.get("message_id")
        text = message_data.get("text")
        media = message_data.get("media")
        metadata = message_data.get("metadata", {})
        
        if not from_number:
            logger.warning("No phone number in message data")
            return
        
        # Get or create conversation
        conversation = await get_or_create_conversation(
            db, from_number, metadata.get("phone_number_id")
        )
        
        # Create message record
        message = Message(
            id=message_id,
            conversation_id=conversation.id,
            direction="inbound",
            text=text,
            media_url=await get_media_url(media) if media else None,
            metadata=message_data,
            created_at=message_data.get("timestamp")
        )
        
        db.add(message)
        
        # Update conversation last message time
        conversation.last_message_at = message.created_at
        
        db.commit()
        
        logger.info(f"Processed WhatsApp message from {from_number}: {message_id}")
        
    except Exception as e:
        logger.error(f"Error processing individual message: {e}")
        db.rollback()


async def get_or_create_conversation(
    db: Session, 
    phone_number: str, 
    phone_id: Optional[str]
) -> Conversation:
    """Get or create a conversation for the phone number."""
    # Look for existing conversation
    conversation = db.query(Conversation).filter(
        Conversation.peer_id == phone_number,
        Conversation.channel == "whatsapp"
    ).first()
    
    if conversation:
        return conversation
    
    # Create new conversation
    conversation = Conversation(
        id=f"whatsapp_{phone_number}_{phone_id or 'unknown'}",
        org_id="default_org",  # TODO: Determine org from phone_id or other context
        channel="whatsapp",
        peer_id=phone_number,
        last_message_at=None
    )
    
    db.add(conversation)
    db.flush()  # Get the ID without committing
    
    return conversation


async def get_media_url(media_data: Dict[str, Any]) -> Optional[str]:
    """Get media URL from WhatsApp API."""
    if not media_data or not media_data.get("id"):
        return None
    
    whatsapp = WhatsAppIntegration()
    return await whatsapp.get_media_url(media_data["id"])


@router.post("/send")
async def send_message(
    phone_number: str,
    message_text: str,
    message_type: str = "text",
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Send a message via WhatsApp (for testing)."""
    try:
        whatsapp = WhatsAppIntegration()
        
        if message_type == "text":
            result = await whatsapp.send_message(phone_number, message_text)
        else:
            # For media messages, you'd need to provide media_url
            raise HTTPException(status_code=400, detail="Media messages require media_url")
        
        # Log the sent message
        logger.info(f"WhatsApp message sent to {phone_number}: {result}")
        
        return {
            "status": "success",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error sending WhatsApp message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send message: {str(e)}")


@router.get("/conversations")
async def get_conversations(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get WhatsApp conversations (for testing)."""
    conversations = db.query(Conversation).filter(
        Conversation.channel == "whatsapp"
    ).offset(offset).limit(limit).all()
    
    return {
        "conversations": [
            {
                "id": conv.id,
                "peer_id": conv.peer_id,
                "last_message_at": conv.last_message_at.isoformat() if conv.last_message_at else None,
                "message_count": len(conv.messages) if hasattr(conv, 'messages') else 0
            }
            for conv in conversations
        ],
        "total": db.query(Conversation).filter(Conversation.channel == "whatsapp").count(),
        "offset": offset,
        "limit": limit
    }


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Get messages for a specific conversation."""
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "id": msg.id,
                "direction": msg.direction,
                "text": msg.text,
                "media_url": msg.media_url,
                "created_at": msg.created_at.isoformat(),
                "metadata": msg.metadata
            }
            for msg in messages
        ],
        "total": db.query(Message).filter(Message.conversation_id == conversation_id).count(),
        "offset": offset,
        "limit": limit
    }
