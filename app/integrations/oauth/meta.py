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


class MetaOAuth:
    """Meta OAuth token management with refresh capabilities."""
    
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
                "client_id": self.settings.meta_app_id,
                "client_secret": self.settings.meta_app_secret,
                "redirect_uri": self.settings.meta_redirect_uri,
                "code": code,
            }
            
            response = await client.request(
                "GET",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/oauth/access_token",
                params=data
            )
            
            token_data = response.json()
            logger.info(f"Meta token exchange successful: {mask_token(token_data.get('access_token', ''))}")
            return token_data
    
    async def get_long_lived_token(self, short_lived_token: str) -> Dict[str, Any]:
        """Exchange short-lived token for long-lived token."""
        async with HTTPClient() as client:
            data = {
                "grant_type": "fb_exchange_token",
                "client_id": self.settings.meta_app_id,
                "client_secret": self.settings.meta_app_secret,
                "fb_exchange_token": short_lived_token,
            }
            
            response = await client.request(
                "GET",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/oauth/access_token",
                params=data
            )
            
            token_data = response.json()
            logger.info(f"Meta long-lived token obtained: {mask_token(token_data.get('access_token', ''))}")
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
            logger.info("Meta token expired or expiring soon, refreshing...")
            # For Meta, we need to get a new long-lived token
            # This requires user re-authorization in practice
            raise ValueError("Meta token expired. User needs to re-authorize.")
        
        return access_token
    
    async def get_page_access_token(self, user_access_token: str, page_id: str) -> str:
        """Get page access token for posting to Facebook Page."""
        async with HTTPClient() as client:
            response = await client.request(
                "GET",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{page_id}",
                params={
                    "fields": "access_token",
                    "access_token": user_access_token
                }
            )
            
            data = response.json()
            page_token = data["access_token"]
            logger.info(f"Meta page access token obtained: {mask_token(page_token)}")
            return page_token
    
    async def get_instagram_business_id(self, page_access_token: str, page_id: str) -> str:
        """Get Instagram Business account ID from Facebook Page."""
        async with HTTPClient() as client:
            response = await client.request(
                "GET",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{page_id}",
                params={
                    "fields": "instagram_business_account",
                    "access_token": page_access_token
                }
            )
            
            data = response.json()
            ig_business_id = data["instagram_business_account"]["id"]
            logger.info(f"Instagram Business ID obtained: {ig_business_id}")
            return ig_business_id
