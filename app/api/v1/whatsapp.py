"""
WhatsApp Business API Router
Handles WhatsApp messaging, templates, and webhook events
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.api.deps import get_db, get_current_user
from app.schemas.whatsapp import (
    WhatsAppMessageResponse, WhatsAppMessageCreate,
    WhatsAppTemplateResponse, WhatsAppTemplateCreate,
    WhatsAppWebhookEventResponse, WhatsAppContactResponse,
    WhatsAppBusinessAccountResponse, WhatsAppBusinessAccountCreate
)
from app.models.whatsapp import (
    WhatsAppMessage, WhatsAppTemplate, WhatsAppWebhookEvent, 
    WhatsAppContact, WhatsAppBusinessAccount
)
from app.models.cms import UserAccount, Organization
from app.services.whatsapp_service import WhatsAppService

router = APIRouter()

# Initialize WhatsApp service
whatsapp_service = WhatsAppService()


@router.post("/whatsapp/send", response_model=WhatsAppMessageResponse, status_code=status.HTTP_201_CREATED)
async def send_whatsapp_message(
    message: WhatsAppMessageCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> WhatsAppMessageResponse:
    """
    Send a WhatsApp message.
    """
    try:
        # Get WhatsApp business account
        business_account = db.query(WhatsAppBusinessAccount).filter(
            WhatsAppBusinessAccount.organization_id == current_user.organization_id,
            WhatsAppBusinessAccount.is_active == True
        ).first()
        
        if not business_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active WhatsApp business account found"
            )
        
        # Send message via WhatsApp service
        result = await whatsapp_service.send_message(
            business_account=business_account,
            to_phone_number=message.to_phone_number,
            message_type=message.message_type,
            text_content=message.text_content,
            media_url=message.media_url,
            media_caption=message.media_caption,
            template_name=message.template_name,
            template_params=message.template_params
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to send message')
            )
        
        # Save message to database
        whatsapp_message = WhatsAppMessage(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            message_type=message.message_type,
            to_phone_number=message.to_phone_number,
            from_phone_number=business_account.phone_number,
            text_content=message.text_content,
            media_url=message.media_url,
            media_caption=message.media_caption,
            template_name=message.template_name,
            template_params=message.template_params,
            whatsapp_message_id=result.get('message_id'),
            whatsapp_business_account_id=business_account.whatsapp_business_account_id,
            status='sent'
        )
        
        db.add(whatsapp_message)
        db.commit()
        db.refresh(whatsapp_message)
        
        return WhatsAppMessageResponse.from_orm(whatsapp_message)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WhatsApp message sending failed: {str(e)}"
        )


@router.get("/whatsapp/messages", response_model=List[WhatsAppMessageResponse])
async def list_whatsapp_messages(
    skip: int = 0,
    limit: int = 20,
    to_phone_number: Optional[str] = None,
    message_type: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[WhatsAppMessageResponse]:
    """
    List WhatsApp messages for the current organization.
    """
    query = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.organization_id == current_user.organization_id
    )
    
    if to_phone_number:
        query = query.filter(WhatsAppMessage.to_phone_number == to_phone_number)
    if message_type:
        query = query.filter(WhatsAppMessage.message_type == message_type)
    if status:
        query = query.filter(WhatsAppMessage.status == status)
    
    messages = query.order_by(WhatsAppMessage.created_at.desc()).offset(skip).limit(limit).all()
    return [WhatsAppMessageResponse.from_orm(message) for message in messages]


@router.get("/whatsapp/messages/{message_id}", response_model=WhatsAppMessageResponse)
async def get_whatsapp_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> WhatsAppMessageResponse:
    """
    Get a specific WhatsApp message.
    """
    message = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.id == message_id,
        WhatsAppMessage.organization_id == current_user.organization_id
    ).first()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp message not found"
        )
    
    return WhatsAppMessageResponse.from_orm(message)


@router.get("/whatsapp/templates", response_model=List[WhatsAppTemplateResponse])
async def list_whatsapp_templates(
    skip: int = 0,
    limit: int = 20,
    category: Optional[str] = None,
    language: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[WhatsAppTemplateResponse]:
    """
    List WhatsApp message templates.
    """
    query = db.query(WhatsAppTemplate).filter(
        WhatsAppTemplate.organization_id == current_user.organization_id
    )
    
    if category:
        query = query.filter(WhatsAppTemplate.category == category)
    if language:
        query = query.filter(WhatsAppTemplate.language == language)
    if status:
        query = query.filter(WhatsAppTemplate.status == status)
    
    templates = query.offset(skip).limit(limit).all()
    return [WhatsAppTemplateResponse.from_orm(template) for template in templates]


@router.post("/whatsapp/templates", response_model=WhatsAppTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_whatsapp_template(
    template: WhatsAppTemplateCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> WhatsAppTemplateResponse:
    """
    Create a WhatsApp message template.
    """
    try:
        # Get WhatsApp business account
        business_account = db.query(WhatsAppBusinessAccount).filter(
            WhatsAppBusinessAccount.organization_id == current_user.organization_id,
            WhatsAppBusinessAccount.is_active == True
        ).first()
        
        if not business_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active WhatsApp business account found"
            )
        
        # Create template via WhatsApp service
        result = await whatsapp_service.create_template(
            business_account=business_account,
            name=template.name,
            category=template.category,
            language=template.language,
            header=template.header,
            body=template.body,
            footer=template.footer,
            buttons=template.buttons
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to create template')
            )
        
        # Save template to database
        whatsapp_template = WhatsAppTemplate(
            organization_id=current_user.organization_id,
            name=template.name,
            category=template.category,
            language=template.language,
            header=template.header,
            body=template.body,
            footer=template.footer,
            buttons=template.buttons,
            whatsapp_template_id=result.get('template_id'),
            status='pending'
        )
        
        db.add(whatsapp_template)
        db.commit()
        db.refresh(whatsapp_template)
        
        return WhatsAppTemplateResponse.from_orm(whatsapp_template)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WhatsApp template creation failed: {str(e)}"
        )


@router.get("/whatsapp/contacts", response_model=List[WhatsAppContactResponse])
async def list_whatsapp_contacts(
    skip: int = 0,
    limit: int = 20,
    is_blocked: Optional[bool] = None,
    is_opted_in: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[WhatsAppContactResponse]:
    """
    List WhatsApp contacts.
    """
    query = db.query(WhatsAppContact).filter(
        WhatsAppContact.organization_id == current_user.organization_id
    )
    
    if is_blocked is not None:
        query = query.filter(WhatsAppContact.is_blocked == is_blocked)
    if is_opted_in is not None:
        query = query.filter(WhatsAppContact.is_opted_in == is_opted_in)
    
    contacts = query.offset(skip).limit(limit).all()
    return [WhatsAppContactResponse.from_orm(contact) for contact in contacts]


@router.post("/whatsapp/contacts/{contact_id}/block", status_code=status.HTTP_200_OK)
async def block_whatsapp_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Block a WhatsApp contact.
    """
    contact = db.query(WhatsAppContact).filter(
        WhatsAppContact.id == contact_id,
        WhatsAppContact.organization_id == current_user.organization_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp contact not found"
        )
    
    contact.is_blocked = True
    db.commit()
    
    return {"status": "success", "message": "Contact blocked"}


@router.post("/whatsapp/contacts/{contact_id}/unblock", status_code=status.HTTP_200_OK)
async def unblock_whatsapp_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Unblock a WhatsApp contact.
    """
    contact = db.query(WhatsAppContact).filter(
        WhatsAppContact.id == contact_id,
        WhatsAppContact.organization_id == current_user.organization_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WhatsApp contact not found"
        )
    
    contact.is_blocked = False
    db.commit()
    
    return {"status": "success", "message": "Contact unblocked"}


@router.get("/whatsapp/business-accounts", response_model=List[WhatsAppBusinessAccountResponse])
async def list_whatsapp_business_accounts(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[WhatsAppBusinessAccountResponse]:
    """
    List WhatsApp business accounts for the current organization.
    """
    accounts = db.query(WhatsAppBusinessAccount).filter(
        WhatsAppBusinessAccount.organization_id == current_user.organization_id
    ).all()
    
    return [WhatsAppBusinessAccountResponse.from_orm(account) for account in accounts]


@router.post("/whatsapp/business-accounts", response_model=WhatsAppBusinessAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_whatsapp_business_account(
    account: WhatsAppBusinessAccountCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> WhatsAppBusinessAccountResponse:
    """
    Create a WhatsApp business account.
    """
    try:
        # Create business account via WhatsApp service
        result = await whatsapp_service.create_business_account(
            organization_id=current_user.organization_id,
            whatsapp_business_account_id=account.whatsapp_business_account_id,
            business_name=account.business_name,
            phone_number_id=account.phone_number_id,
            phone_number=account.phone_number,
            access_token=account.access_token,
            verify_token=account.verify_token,
            webhook_url=account.webhook_url
        )
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get('error', 'Failed to create business account')
            )
        
        # Save business account to database
        business_account = WhatsAppBusinessAccount(
            organization_id=current_user.organization_id,
            whatsapp_business_account_id=account.whatsapp_business_account_id,
            business_name=account.business_name,
            phone_number_id=account.phone_number_id,
            phone_number=account.phone_number,
            access_token=account.access_token,
            verify_token=account.verify_token,
            webhook_url=account.webhook_url,
            is_active=True,
            is_verified=True
        )
        
        db.add(business_account)
        db.commit()
        db.refresh(business_account)
        
        return WhatsAppBusinessAccountResponse.from_orm(business_account)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WhatsApp business account creation failed: {str(e)}"
        )


@router.post("/whatsapp/webhooks", status_code=status.HTTP_200_OK)
async def whatsapp_webhook(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle WhatsApp webhook events.
    """
    try:
        # Get webhook data
        body = await request.body()
        payload = json.loads(body)
        
        # Get query parameters
        hub_mode = request.query_params.get('hub.mode')
        hub_verify_token = request.query_params.get('hub.verify_token')
        hub_challenge = request.query_params.get('hub.challenge')
        
        # Handle webhook verification
        if hub_mode == 'subscribe':
            # Find business account with matching verify token
            business_account = db.query(WhatsAppBusinessAccount).filter(
                WhatsAppBusinessAccount.verify_token == hub_verify_token
            ).first()
            
            if business_account:
                return int(hub_challenge)
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Verification failed"
                )
        
        # Handle webhook events
        entries = payload.get('entry', [])
        
        for entry in entries:
            changes = entry.get('changes', [])
            for change in changes:
                field = change.get('field')
                value = change.get('value', {})
                
                if field == 'messages':
                    # Handle incoming messages
                    await _handle_whatsapp_messages(value, db)
                elif field == 'message_status':
                    # Handle message status updates
                    await _handle_message_status(value, db)
                elif field == 'message_template_status_update':
                    # Handle template status updates
                    await _handle_template_status_update(value, db)
        
        return {"status": "success"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"WhatsApp webhook processing failed: {str(e)}"
        )


async def _handle_whatsapp_messages(value: Dict[str, Any], db: Session):
    """
    Handle incoming WhatsApp messages.
    """
    try:
        messages = value.get('messages', [])
        
        for message_data in messages:
            # Create webhook event record
            webhook_event = WhatsAppWebhookEvent(
                organization_id=1,  # FIXME: Get from business account
                event_type='messages',
                payload=message_data,
                processed=False
            )
            
            db.add(webhook_event)
            
            # Process message
            await _process_incoming_message(message_data, db)
        
        db.commit()
        
    except Exception as e:
        print(f"Error handling WhatsApp messages: {e}")


async def _handle_message_status(value: Dict[str, Any], db: Session):
    """
    Handle message status updates.
    """
    try:
        statuses = value.get('statuses', [])
        
        for status_data in statuses:
            # Update message status in database
            message = db.query(WhatsAppMessage).filter(
                WhatsAppMessage.whatsapp_message_id == status_data.get('id')
            ).first()
            
            if message:
                message.status = status_data.get('status')
                if status_data.get('status') == 'delivered':
                    message.delivered_at = datetime.utcnow()
                elif status_data.get('status') == 'read':
                    message.read_at = datetime.utcnow()
                elif status_data.get('status') == 'failed':
                    message.error_message = status_data.get('errors', [{}])[0].get('title', 'Unknown error')
                    message.error_code = status_data.get('errors', [{}])[0].get('code')
        
        db.commit()
        
    except Exception as e:
        print(f"Error handling message status: {e}")


async def _handle_template_status_update(value: Dict[str, Any], db: Session):
    """
    Handle template status updates.
    """
    try:
        template_statuses = value.get('message_template_status_update', [])
        
        for status_data in template_statuses:
            # Update template status in database
            template = db.query(WhatsAppTemplate).filter(
                WhatsAppTemplate.whatsapp_template_id == status_data.get('id')
            ).first()
            
            if template:
                template.status = status_data.get('status')
                if status_data.get('status') == 'APPROVED':
                    template.approved_at = datetime.utcnow()
        
        db.commit()
        
    except Exception as e:
        print(f"Error handling template status update: {e}")


async def _process_incoming_message(message_data: Dict[str, Any], db: Session):
    """
    Process incoming WhatsApp message.
    """
    try:
        # Extract message details
        from_number = message_data.get('from')
        message_id = message_data.get('id')
        timestamp = message_data.get('timestamp')
        message_type = message_data.get('type')
        
        # Get or create contact
        contact = db.query(WhatsAppContact).filter(
            WhatsAppContact.phone_number == from_number
        ).first()
        
        if not contact:
            contact = WhatsAppContact(
                organization_id=1,  # FIXME: Get from business account
                phone_number=from_number,
                whatsapp_id=from_number,
                is_opted_in=True,
                opt_in_date=datetime.utcnow()
            )
            db.add(contact)
        
        # Update contact statistics
        contact.total_messages_received += 1
        contact.last_message_at = datetime.utcnow()
        
        # Create message record
        message = WhatsAppMessage(
            organization_id=1,  # FIXME: Get from business account
            message_type=message_type,
            to_phone_number='business',  # FIXME: Get business phone number
            from_phone_number=from_number,
            whatsapp_message_id=message_id,
            status='received'
        )
        
        # Extract message content based on type
        if message_type == 'text':
            message.text_content = message_data.get('text', {}).get('body')
        elif message_type == 'image':
            message.media_url = message_data.get('image', {}).get('id')
            message.media_caption = message_data.get('image', {}).get('caption')
        elif message_type == 'document':
            message.media_url = message_data.get('document', {}).get('id')
            message.media_caption = message_data.get('document', {}).get('caption')
        elif message_type == 'audio':
            message.media_url = message_data.get('audio', {}).get('id')
        elif message_type == 'video':
            message.media_url = message_data.get('video', {}).get('id')
            message.media_caption = message_data.get('video', {}).get('caption')
        
        db.add(message)
        
    except Exception as e:
        print(f"Error processing incoming message: {e}")


@router.get("/whatsapp/webhook-events", response_model=List[WhatsAppWebhookEventResponse])
async def list_whatsapp_webhook_events(
    skip: int = 0,
    limit: int = 20,
    event_type: Optional[str] = None,
    processed: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[WhatsAppWebhookEventResponse]:
    """
    List WhatsApp webhook events.
    """
    query = db.query(WhatsAppWebhookEvent).filter(
        WhatsAppWebhookEvent.organization_id == current_user.organization_id
    )
    
    if event_type:
        query = query.filter(WhatsAppWebhookEvent.event_type == event_type)
    if processed is not None:
        query = query.filter(WhatsAppWebhookEvent.processed == processed)
    
    events = query.order_by(WhatsAppWebhookEvent.received_at.desc()).offset(skip).limit(limit).all()
    return [WhatsAppWebhookEventResponse.from_orm(event) for event in events]