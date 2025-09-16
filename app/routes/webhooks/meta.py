from __future__ import annotations

import logging
from fastapi import APIRouter, HTTPException, Request, Query
from typing import Dict, Any

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/webhooks/meta", tags=["webhooks"])


@router.get("/verify")
async def verify_meta_webhook(
    hub_mode: str = Query(..., alias="hub.mode"),
    hub_challenge: str = Query(..., alias="hub.challenge"),
    hub_verify_token: str = Query(..., alias="hub.verify_token"),
):
    """Verify Meta webhook subscription."""
    logger.info(f"Meta webhook verification request: mode={hub_mode}, token={hub_verify_token}")
    
    # In production, verify the token matches your configured verify token
    # For now, we'll accept any token
    if hub_mode == "subscribe":
        logger.info("Meta webhook verified successfully")
        return int(hub_challenge)
    else:
        logger.warning(f"Invalid hub.mode: {hub_mode}")
        raise HTTPException(status_code=400, detail="Invalid hub.mode")


@router.post("/events")
async def handle_meta_webhook_events(request: Request):
    """Handle Meta webhook events."""
    try:
        body = await request.body()
        headers = dict(request.headers)
        
        logger.info(f"Meta webhook event received: {len(body)} bytes")
        logger.debug(f"Headers: {headers}")
        
        # Parse JSON payload
        import json
        try:
            payload = json.loads(body.decode())
            logger.info(f"Meta webhook payload: {json.dumps(payload, indent=2)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Meta webhook JSON: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Store raw payload for debugging (in production, you'd save to database)
        # await store_webhook_payload("meta", payload)
        
        # Process different event types
        if "entry" in payload:
            for entry in payload["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        await process_meta_change(change)
        
        return {"status": "success"}
        
    except Exception as e:
        logger.error(f"Error processing Meta webhook: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def process_meta_change(change: Dict[str, Any]):
    """Process individual Meta webhook change."""
    change_type = change.get("field")
    value = change.get("value", {})
    
    logger.info(f"Processing Meta change: {change_type}")
    
    if change_type == "feed":
        # Handle feed changes (new posts, comments, etc.)
        logger.info("Processing feed change")
    elif change_type == "mention":
        # Handle mentions
        logger.info("Processing mention")
    else:
        logger.info(f"Unhandled change type: {change_type}")
