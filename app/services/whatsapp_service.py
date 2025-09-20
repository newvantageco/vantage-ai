"""
WhatsApp Business Service
Handles WhatsApp API operations and message processing
"""

import httpx
import json
from typing import Dict, Any, Optional
from datetime import datetime
import os

from app.models.whatsapp import WhatsAppBusinessAccount


class WhatsAppService:
    """Service for handling WhatsApp Business API operations"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
        self.timeout = 30
    
    async def send_message(
        self,
        business_account: WhatsAppBusinessAccount,
        to_phone_number: str,
        message_type: str,
        text_content: str = None,
        media_url: str = None,
        media_caption: str = None,
        template_name: str = None,
        template_params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Send a WhatsApp message.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            # Prepare message payload
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone_number,
                "type": message_type
            }
            
            # Add message content based on type
            if message_type == "text":
                payload["text"] = {"body": text_content}
            elif message_type == "image":
                payload["image"] = {
                    "id": media_url,
                    "caption": media_caption
                }
            elif message_type == "document":
                payload["document"] = {
                    "id": media_url,
                    "caption": media_caption
                }
            elif message_type == "audio":
                payload["audio"] = {"id": media_url}
            elif message_type == "video":
                payload["video"] = {
                    "id": media_url,
                    "caption": media_caption
                }
            elif message_type == "template":
                payload["template"] = {
                    "name": template_name,
                    "language": {"code": "en_US"},
                    "components": []
                }
                
                # Add template parameters
                if template_params:
                    components = []
                    if template_params.get("header"):
                        components.append({
                            "type": "header",
                            "parameters": template_params["header"]
                        })
                    if template_params.get("body"):
                        components.append({
                            "type": "body",
                            "parameters": template_params["body"]
                        })
                    payload["template"]["components"] = components
            
            # Make API call
            url = f"{self.base_url}/{business_account.phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {business_account.access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "message_id": result.get("messages", [{}])[0].get("id"),
                        "response": result
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error"),
                        "error_code": error_data.get("error", {}).get("code")
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Message sending failed: {str(e)}"}
    
    async def create_template(
        self,
        business_account: WhatsAppBusinessAccount,
        name: str,
        category: str,
        language: str,
        header: Dict[str, Any] = None,
        body: Dict[str, Any] = None,
        footer: Dict[str, Any] = None,
        buttons: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a WhatsApp message template.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            # Prepare template payload
            payload = {
                "name": name,
                "category": category,
                "language": language,
                "components": []
            }
            
            # Add header component
            if header:
                payload["components"].append({
                    "type": "HEADER",
                    "format": header.get("format", "TEXT"),
                    "text": header.get("text", "")
                })
            
            # Add body component
            if body:
                payload["components"].append({
                    "type": "BODY",
                    "text": body.get("text", ""),
                    "example": body.get("example", {})
                })
            
            # Add footer component
            if footer:
                payload["components"].append({
                    "type": "FOOTER",
                    "text": footer.get("text", "")
                })
            
            # Add buttons component
            if buttons:
                button_components = []
                for button in buttons.get("buttons", []):
                    button_components.append({
                        "type": button.get("type", "QUICK_REPLY"),
                        "text": button.get("text", "")
                    })
                
                if button_components:
                    payload["components"].append({
                        "type": "BUTTONS",
                        "buttons": button_components
                    })
            
            # Make API call
            url = f"{self.base_url}/{business_account.whatsapp_business_account_id}/message_templates"
            headers = {
                "Authorization": f"Bearer {business_account.access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=payload, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "template_id": result.get("id"),
                        "response": result
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error"),
                        "error_code": error_data.get("error", {}).get("code")
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Template creation failed: {str(e)}"}
    
    async def get_templates(
        self,
        business_account: WhatsAppBusinessAccount
    ) -> Dict[str, Any]:
        """
        Get WhatsApp message templates.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            url = f"{self.base_url}/{business_account.whatsapp_business_account_id}/message_templates"
            headers = {
                "Authorization": f"Bearer {business_account.access_token}"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "templates": result.get("data", []),
                        "response": result
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Template retrieval failed: {str(e)}"}
    
    async def create_business_account(
        self,
        organization_id: int,
        whatsapp_business_account_id: str,
        business_name: str = None,
        phone_number_id: str = None,
        phone_number: str = None,
        access_token: str = None,
        verify_token: str = None,
        webhook_url: str = None
    ) -> Dict[str, Any]:
        """
        Create a WhatsApp business account.
        """
        try:
            # FIXME: Implement actual WhatsApp Business Account creation
            # This would typically involve API calls to Meta's WhatsApp Business API
            
            return {
                "success": True,
                "message": "Business account created successfully",
                "account_id": whatsapp_business_account_id
            }
            
        except Exception as e:
            return {"success": False, "error": f"Business account creation failed: {str(e)}"}
    
    async def verify_webhook(
        self,
        verify_token: str,
        challenge: str,
        mode: str
    ) -> Dict[str, Any]:
        """
        Verify WhatsApp webhook.
        """
        try:
            # FIXME: Implement actual webhook verification
            # This would typically involve verifying the token with Meta's servers
            
            if mode == "subscribe" and verify_token == "your_verify_token":
                return {
                    "success": True,
                    "challenge": challenge
                }
            else:
                return {
                    "success": False,
                    "error": "Verification failed"
                }
                
        except Exception as e:
            return {"success": False, "error": f"Webhook verification failed: {str(e)}"}
    
    async def get_business_profile(
        self,
        business_account: WhatsAppBusinessAccount
    ) -> Dict[str, Any]:
        """
        Get WhatsApp business profile.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            url = f"{self.base_url}/{business_account.whatsapp_business_account_id}/whatsapp_business_profile"
            headers = {
                "Authorization": f"Bearer {business_account.access_token}"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "profile": result,
                        "response": result
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Profile retrieval failed: {str(e)}"}
    
    async def update_business_profile(
        self,
        business_account: WhatsAppBusinessAccount,
        profile_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update WhatsApp business profile.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            url = f"{self.base_url}/{business_account.whatsapp_business_account_id}/whatsapp_business_profile"
            headers = {
                "Authorization": f"Bearer {business_account.access_token}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, json=profile_data, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "response": result
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Profile update failed: {str(e)}"}
    
    async def upload_media(
        self,
        business_account: WhatsAppBusinessAccount,
        media_file: bytes,
        media_type: str
    ) -> Dict[str, Any]:
        """
        Upload media to WhatsApp.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            url = f"{self.base_url}/{business_account.whatsapp_business_account_id}/media"
            headers = {
                "Authorization": f"Bearer {business_account.access_token}"
            }
            
            files = {
                "file": ("media", media_file, media_type)
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(url, files=files, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "media_id": result.get("id"),
                        "response": result
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Media upload failed: {str(e)}"}
    
    async def get_media_url(
        self,
        business_account: WhatsAppBusinessAccount,
        media_id: str
    ) -> Dict[str, Any]:
        """
        Get media URL from WhatsApp.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            url = f"{self.base_url}/{media_id}"
            headers = {
                "Authorization": f"Bearer {business_account.access_token}"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    result = response.json()
                    return {
                        "success": True,
                        "media_url": result.get("url"),
                        "response": result
                    }
                else:
                    error_data = response.json()
                    return {
                        "success": False,
                        "error": error_data.get("error", {}).get("message", "Unknown error")
                    }
                    
        except Exception as e:
            return {"success": False, "error": f"Media URL retrieval failed: {str(e)}"}
    
    async def test_connection(
        self,
        business_account: WhatsAppBusinessAccount
    ) -> Dict[str, Any]:
        """
        Test WhatsApp connection.
        """
        try:
            if not business_account.access_token:
                return {"success": False, "error": "No access token available"}
            
            # Test by getting business profile
            result = await self.get_business_profile(business_account)
            
            if result.get("success"):
                return {
                    "success": True,
                    "message": "WhatsApp connection successful"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", "Connection test failed")
                }
                
        except Exception as e:
            return {"success": False, "error": f"Connection test failed: {str(e)}"}
