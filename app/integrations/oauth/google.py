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


class GoogleOAuth:
    """Google OAuth token management with refresh capabilities for Google My Business API."""
    
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
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret,
                "redirect_uri": self.settings.google_redirect_url,
                "grant_type": "authorization_code",
                "code": code,
            }
            
            response = await client.request(
                "POST",
                "https://oauth2.googleapis.com/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            token_data = response.json()
            logger.info(f"Google token exchange successful: {mask_token(token_data.get('access_token', ''))}")
            return token_data
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        async with HTTPClient() as client:
            data = {
                "client_id": self.settings.google_client_id,
                "client_secret": self.settings.google_client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            }
            
            response = await client.request(
                "POST",
                "https://oauth2.googleapis.com/token",
                data=data,
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            
            token_data = response.json()
            logger.info(f"Google token refresh successful: {mask_token(token_data.get('access_token', ''))}")
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
            logger.info("Google token expired or expiring soon, refreshing...")
            refresh_token = self._decrypt_token(stored_token_data["refresh_token"])
            new_token_data = await self.refresh_access_token(refresh_token)
            
            # Update stored token data
            stored_token_data.update({
                "access_token": self._encrypt_token(new_token_data["access_token"]),
                "expires_at": datetime.utcnow() + timedelta(seconds=new_token_data["expires_in"]),
            })
            
            return new_token_data["access_token"]
        
        return access_token
    
    def get_authorization_url(self, state: str) -> str:
        """Generate Google OAuth authorization URL."""
        params = {
            "client_id": self.settings.google_client_id,
            "redirect_uri": self.settings.google_redirect_url,
            "scope": "https://www.googleapis.com/auth/business.manage",
            "response_type": "code",
            "access_type": "offline",
            "prompt": "consent",
            "state": state
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"https://accounts.google.com/o/oauth2/v2/auth?{query_string}"
    
    async def get_business_accounts(self, access_token: str) -> list[Dict[str, Any]]:
        """Get Google Business accounts for the authenticated user."""
        async with HTTPClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = await client.request(
                "GET",
                "https://mybusiness.googleapis.com/v4/accounts",
                headers=headers
            )
            
            data = response.json()
            accounts = data.get("accounts", [])
            logger.info(f"Found {len(accounts)} Google Business accounts")
            return accounts
    
    async def get_business_locations(self, access_token: str, account_name: str) -> list[Dict[str, Any]]:
        """Get business locations for a specific account."""
        async with HTTPClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = await client.request(
                "GET",
                f"https://mybusiness.googleapis.com/v4/{account_name}/locations",
                headers=headers
            )
            
            data = response.json()
            locations = data.get("locations", [])
            logger.info(f"Found {len(locations)} business locations for account {account_name}")
            return locations
