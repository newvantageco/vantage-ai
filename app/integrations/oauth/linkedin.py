from __future__ import annotations

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

import httpx
from cryptography.fernet import Fernet
from app.core.config import get_settings
from app.utils.http import HTTPClient, mask_token

logger = logging.getLogger(__name__)


class LinkedInOAuth:
    """LinkedIn OAuth token management with refresh capabilities."""
    
    def __init__(self):
        self.settings = get_settings()
        self._cipher = Fernet(self.settings.secret_key.encode())
    
    def _encrypt_token(self, token: str) -> str:
        """Encrypt token for storage."""
        return self._cipher.encrypt(token.encode()).decode()
    
    def _decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt token from storage."""
        return self._cipher.decrypt(encrypted_token.encode()).decode()
    
    async def get_access_token(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        async with HTTPClient() as client:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "client_id": self.settings.linkedin_client_id,
                "client_secret": self.settings.linkedin_client_secret,
                "redirect_uri": self.settings.linkedin_redirect_url,
            }
            
            response = await client.request(
                "POST",
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            token_data = response.json()
            logger.info(f"LinkedIn token exchange successful: {mask_token(token_data.get('access_token', ''))}")
            return token_data
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        async with HTTPClient() as client:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": self.settings.linkedin_client_id,
                "client_secret": self.settings.linkedin_client_secret,
            }
            
            response = await client.request(
                "POST",
                "https://www.linkedin.com/oauth/v2/accessToken",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            token_data = response.json()
            logger.info(f"LinkedIn token refresh successful: {mask_token(token_data.get('access_token', ''))}")
            return token_data
    
    def is_token_expired(self, expires_at: Optional[datetime]) -> bool:
        """Check if token is expired or will expire within 5 minutes."""
        if not expires_at:
            return True
        return datetime.utcnow() + timedelta(minutes=5) >= expires_at
    
    async def get_valid_token(self, stored_token_data: Dict[str, Any]) -> str:
        """Get valid access token, refreshing if necessary."""
        access_token = self._decrypt_token(stored_token_data["access_token"])
        expires_at = stored_token_data.get("expires_at")
        
        if self.is_token_expired(expires_at):
            logger.info("LinkedIn token expired or expiring soon, refreshing...")
            refresh_token = self._decrypt_token(stored_token_data["refresh_token"])
            new_token_data = await self.refresh_access_token(refresh_token)
            
            # Update stored token data
            stored_token_data.update({
                "access_token": self._encrypt_token(new_token_data["access_token"]),
                "expires_at": datetime.utcnow() + timedelta(seconds=new_token_data["expires_in"]),
            })
            
            return new_token_data["access_token"]
        
        return access_token
    
    async def get_page_urn(self, access_token: str) -> str:
        """Get LinkedIn Page URN for the authenticated user."""
        async with HTTPClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = await client.request(
                "GET",
                "https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee&role=ADMINISTRATOR",
                headers=headers
            )
            
            data = response.json()
            elements = data.get("elements", [])
            
            if not elements:
                raise ValueError("No LinkedIn pages found for user")
            
            # Use the first page or the configured page URN
            if self.settings.linkedin_page_urn:
                return self.settings.linkedin_page_urn
            
            page_urn = elements[0]["organizationalTarget"]
            logger.info(f"Using LinkedIn page URN: {page_urn}")
            return page_urn
