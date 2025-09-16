from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/linkedin", tags=["webhooks"])


@router.get("/verify")
async def verify_linkedin_webhook(
    challenge: str = Query(..., alias="challenge"),
    verification_token: str = Query(..., alias="verification_token"),
):
    """Verify LinkedIn webhook subscription."""
    logger.info(f"LinkedIn webhook verification request: token={verification_token}")
    
    # In production, verify the token matches your configured verification token
    # For now, we'll accept any token
    logger.info("LinkedIn webhook verified successfully")
    return challenge


@router.post("/events")
async def handle_linkedin_webhook_events(request: Request):
    """Handle LinkedIn webhook events."""
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        logger.info(f"LinkedIn webhook event received: {len(body)} bytes")
        logger.debug(f"Headers: {headers}")
        
        # Parse JSON payload
        import json
        try:
            payload = json.loads(body.decode())
            logger.info(f"LinkedIn webhook payload: {json.dumps(payload, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LinkedIn webhook JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Store raw payload for debugging (in production, you'd save to database)
        # await store_webhook_payload("linkedin", payload)
        
        # Process different event types
        if "events" in payload:
            for event in payload["events"]:
                await process_linkedin_event(event)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing LinkedIn webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_linkedin_event(event: Dict[str, Any]):
    """Process individual LinkedIn webhook event."""
    event_type = event.get("eventType")
    entity_urn = event.get("entityUrn")
    
    logger.info(f"Processing LinkedIn event: {event_type} for {entity_urn}")
    
    if event_type == "UGC_POST_CREATED":
        # Handle new UGC post creation
        logger.info("Processing UGC post creation")
    elif event_type == "UGC_POST_UPDATED":
        # Handle UGC post updates
        logger.info("Processing UGC post update")
    elif event_type == "UGC_POST_DELETED":
        # Handle UGC post deletion
        logger.info("Processing UGC post deletion")
    else:
        logger.info(f"Unhandled event type: {event_type}")
