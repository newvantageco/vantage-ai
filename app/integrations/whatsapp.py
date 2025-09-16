from __future__ import annotations

import asyncio
import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.core.config import get_settings
from app.utils.http import HTTPClient, mask_token

logger = logging.getLogger(__name__)


class WhatsAppIntegration:
    """WhatsApp Cloud API integration for sending messages and handling webhooks."""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def send_message(
        self, 
        phone_number: str, 
        message_text: str,
        message_type: str = "text"
    ) -> Dict[str, Any]:
        """Send a message to WhatsApp."""
        if not self.settings.whatsapp_access_token or not self.settings.whatsapp_phone_id:
            logger.warning("WhatsApp credentials not configured, mocking message send")
            return {
                "messaging_product": "whatsapp",
                "contacts": [{"input": phone_number, "wa_id": phone_number}],
                "messages": [{"id": "mock_message_id"}]
            }
        
        async with HTTPClient() as client:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": message_type,
                "text": {"body": message_text}
            }
            
            headers = {
                "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
                "Content-Type": "application/json"
            }
            
            response = await client.request(
                "POST",
                f"{self.base_url}/{self.settings.whatsapp_phone_id}/messages",
                headers=headers,
                json=payload
            )
            
            result = response.json()
            logger.info(f"WhatsApp message sent to {mask_token(phone_number)}: {result.get('messages', [{}])[0].get('id', 'unknown')}")
            return result
    
    async def send_media_message(
        self, 
        phone_number: str, 
        media_url: str,
        media_type: str = "image",
        caption: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a media message to WhatsApp."""
        if not self.settings.whatsapp_access_token or not self.settings.whatsapp_phone_id:
            logger.warning("WhatsApp credentials not configured, mocking media message send")
            return {
                "messaging_product": "whatsapp",
                "contacts": [{"input": phone_number, "wa_id": phone_number}],
                "messages": [{"id": "mock_media_message_id"}]
            }
        
        async with HTTPClient() as client:
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_number,
                "type": media_type,
                "image": {
                    "link": media_url,
                    "caption": caption
                } if media_type == "image" else {
                    "link": media_url,
                    "caption": caption
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.settings.whatsapp_access_token}",
                "Content-Type": "application/json"
            }
            
            response = await client.request(
                "POST",
                f"{self.base_url}/{self.settings.whatsapp_phone_id}/messages",
                headers=headers,
                json=payload
            )
            
            result = response.json()
            logger.info(f"WhatsApp media message sent to {mask_token(phone_number)}: {result.get('messages', [{}])[0].get('id', 'unknown')}")
            return result
    
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify WhatsApp webhook token."""
        if mode == "subscribe" and token == self.settings.whatsapp_verify_token:
            logger.info("WhatsApp webhook verification successful")
            return challenge
        else:
            logger.warning(f"WhatsApp webhook verification failed: mode={mode}, token={mask_token(token)}")
            return None
    
    def parse_webhook_message(self, webhook_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse incoming webhook messages."""
        messages = []
        
        try:
            entries = webhook_data.get("entry", [])
            for entry in entries:
                changes = entry.get("changes", [])
                for change in changes:
                    if change.get("field") == "messages":
                        value = change.get("value", {})
                        message_events = value.get("messages", [])
                        
                        for message in message_events:
                            parsed_message = {
                                "message_id": message.get("id"),
                                "from": message.get("from"),
                                "timestamp": message.get("timestamp"),
                                "type": message.get("type"),
                                "text": message.get("text", {}).get("body") if message.get("type") == "text" else None,
                                "media": self._extract_media_info(message),
                                "metadata": {
                                    "phone_number_id": value.get("metadata", {}).get("phone_number_id"),
                                    "display_phone_number": value.get("metadata", {}).get("display_phone_number"),
                                }
                            }
                            messages.append(parsed_message)
                            
        except Exception as e:
            logger.error(f"Error parsing WhatsApp webhook message: {e}")
        
        return messages
    
    def _extract_media_info(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Extract media information from message."""
        message_type = message.get("type")
        
        if message_type in ["image", "video", "audio", "document"]:
            media_data = message.get(message_type, {})
            return {
                "id": media_data.get("id"),
                "mime_type": media_data.get("mime_type"),
                "sha256": media_data.get("sha256"),
                "caption": media_data.get("caption"),
                "filename": media_data.get("filename")
            }
        
        return None
    
    async def get_media_url(self, media_id: str) -> Optional[str]:
        """Get media URL from WhatsApp API."""
        if not self.settings.whatsapp_access_token:
            logger.warning("WhatsApp access token not configured, cannot fetch media URL")
            return None
        
        async with HTTPClient() as client:
            headers = {
                "Authorization": f"Bearer {self.settings.whatsapp_access_token}"
            }
            
            response = await client.request(
                "GET",
                f"{self.base_url}/{media_id}",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("url")
            else:
                logger.error(f"Failed to get media URL for {media_id}: {response.status_code}")
                return None
    
    async def download_media(self, media_url: str) -> Optional[bytes]:
        """Download media from WhatsApp."""
        if not self.settings.whatsapp_access_token:
            logger.warning("WhatsApp access token not configured, cannot download media")
            return None
        
        async with HTTPClient() as client:
            headers = {
                "Authorization": f"Bearer {self.settings.whatsapp_access_token}"
            }
            
            response = await client.request(
                "GET",
                media_url,
                headers=headers
            )
            
            if response.status_code == 200:
                return response.content
            else:
                logger.error(f"Failed to download media from {media_url}: {response.status_code}")
                return None
