"""
Channel Service
Manages social media channel tokens and credentials
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.entities import Channel, Organization
from app.integrations.oauth.meta import MetaOAuth
from app.integrations.oauth.linkedin import LinkedInOAuth
from app.integrations.oauth.google import GoogleOAuth
from app.core.config import get_settings
import logging

logger = logging.getLogger(__name__)


class ChannelService:
    """Service for managing social media channels and their credentials"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.settings = get_settings()
        
        # Initialize OAuth handlers
        self.oauth_handlers = {
            "meta": MetaOAuth(),
            "linkedin": LinkedInOAuth(),
            "google": GoogleOAuth()
        }
    
    async def get_channel_credentials(self, org_id: str, provider: str, account_ref: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get decrypted credentials for a channel
        
        Args:
            org_id: Organization ID
            provider: Platform provider (meta, linkedin, google)
            account_ref: Specific account reference (optional)
            
        Returns:
            Dictionary with decrypted tokens and metadata, or None if not found
        """
        try:
            # Build query
            query = self.db.query(Channel).filter(
                and_(
                    Channel.org_id == org_id,
                    Channel.provider == provider
                )
            )
            
            # Add account_ref filter if provided
            if account_ref:
                query = query.filter(Channel.account_ref == account_ref)
            
            # Get the first matching channel
            channel = query.first()
            
            if not channel or not channel.access_token:
                logger.warning(f"No channel found for org={org_id}, provider={provider}, account_ref={account_ref}")
                return None
            
            # Get OAuth handler
            oauth_handler = self.oauth_handlers.get(provider)
            if not oauth_handler:
                logger.error(f"No OAuth handler for provider: {provider}")
                return None
            
            # Decrypt tokens
            try:
                access_token = oauth_handler._decrypt_token(channel.access_token)
                refresh_token = oauth_handler._decrypt_token(channel.refresh_token) if channel.refresh_token else None
                
                # Parse metadata
                metadata = {}
                if channel.metadata_json:
                    metadata = json.loads(channel.metadata_json)
                
                credentials = {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "account_ref": channel.account_ref,
                    "metadata": metadata,
                    "channel_id": channel.id,
                    "provider": provider
                }
                
                # Add provider-specific data
                if provider == "meta":
                    credentials.update({
                        "page_id": channel.account_ref,
                        "graph_version": getattr(self.settings, 'meta_graph_version', 'v18.0')
                    })
                elif provider == "linkedin":
                    credentials.update({
                        "page_urn": f"urn:li:organization:{channel.account_ref}"
                    })
                elif provider == "google":
                    credentials.update({
                        "location_id": channel.account_ref
                    })
                
                logger.info(f"Successfully retrieved credentials for {provider} channel {channel.id}")
                return credentials
                
            except Exception as decrypt_error:
                logger.error(f"Failed to decrypt tokens for channel {channel.id}: {decrypt_error}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get channel credentials: {e}")
            return None
    
    async def store_channel_credentials(
        self, 
        org_id: str, 
        provider: str, 
        account_ref: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Store encrypted credentials for a channel
        
        Returns:
            Channel ID if successful, None otherwise
        """
        try:
            # Get OAuth handler
            oauth_handler = self.oauth_handlers.get(provider)
            if not oauth_handler:
                logger.error(f"No OAuth handler for provider: {provider}")
                return None
            
            # Encrypt tokens
            encrypted_access_token = oauth_handler._encrypt_token(access_token)
            encrypted_refresh_token = oauth_handler._encrypt_token(refresh_token) if refresh_token else None
            
            # Check if channel already exists
            existing_channel = self.db.query(Channel).filter(
                and_(
                    Channel.org_id == org_id,
                    Channel.provider == provider,
                    Channel.account_ref == account_ref
                )
            ).first()
            
            if existing_channel:
                # Update existing channel
                existing_channel.access_token = encrypted_access_token
                existing_channel.refresh_token = encrypted_refresh_token
                existing_channel.metadata_json = json.dumps(metadata) if metadata else None
                channel_id = existing_channel.id
                logger.info(f"Updated existing channel {channel_id}")
            else:
                # Create new channel
                import uuid
                new_channel = Channel(
                    id=str(uuid.uuid4()),
                    org_id=org_id,
                    provider=provider,
                    account_ref=account_ref,
                    access_token=encrypted_access_token,
                    refresh_token=encrypted_refresh_token,
                    metadata_json=json.dumps(metadata) if metadata else None
                )
                
                self.db.add(new_channel)
                channel_id = new_channel.id
                logger.info(f"Created new channel {channel_id}")
            
            self.db.commit()
            return channel_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to store channel credentials: {e}")
            return None
    
    async def refresh_channel_token(self, channel_id: str) -> bool:
        """
        Refresh an expired token for a channel
        
        Returns:
            True if successful, False otherwise
        """
        try:
            channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
            if not channel:
                logger.error(f"Channel not found: {channel_id}")
                return False
            
            oauth_handler = self.oauth_handlers.get(channel.provider)
            if not oauth_handler:
                logger.error(f"No OAuth handler for provider: {channel.provider}")
                return False
            
            # Decrypt current tokens
            current_access_token = oauth_handler._decrypt_token(channel.access_token)
            current_refresh_token = oauth_handler._decrypt_token(channel.refresh_token) if channel.refresh_token else None
            
            # Refresh token based on provider
            if channel.provider == "meta":
                # Meta tokens are long-lived and don't refresh automatically
                # User needs to re-authorize
                logger.warning(f"Meta token expired for channel {channel_id}. User re-authorization required.")
                return False
                
            elif channel.provider == "linkedin":
                if not current_refresh_token:
                    logger.error(f"No refresh token available for LinkedIn channel {channel_id}")
                    return False
                
                # Use LinkedIn refresh flow
                new_tokens = await oauth_handler.refresh_access_token(current_refresh_token)
                
                # Store new tokens
                channel.access_token = oauth_handler._encrypt_token(new_tokens["access_token"])
                if new_tokens.get("refresh_token"):
                    channel.refresh_token = oauth_handler._encrypt_token(new_tokens["refresh_token"])
                
                self.db.commit()
                logger.info(f"Successfully refreshed LinkedIn token for channel {channel_id}")
                return True
                
            elif channel.provider == "google":
                if not current_refresh_token:
                    logger.error(f"No refresh token available for Google channel {channel_id}")
                    return False
                
                # Use Google refresh flow
                new_tokens = await oauth_handler.refresh_access_token(current_refresh_token)
                
                # Store new tokens
                channel.access_token = oauth_handler._encrypt_token(new_tokens["access_token"])
                
                self.db.commit()
                logger.info(f"Successfully refreshed Google token for channel {channel_id}")
                return True
            
            else:
                logger.error(f"Token refresh not implemented for provider: {channel.provider}")
                return False
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to refresh token for channel {channel_id}: {e}")
            return False
    
    def get_organization_channels(self, org_id: str) -> List[Dict[str, Any]]:
        """Get all channels for an organization (without decrypted tokens)"""
        try:
            channels = self.db.query(Channel).filter(Channel.org_id == org_id).all()
            
            channel_list = []
            for channel in channels:
                metadata = {}
                if channel.metadata_json:
                    metadata = json.loads(channel.metadata_json)
                
                channel_info = {
                    "id": channel.id,
                    "provider": channel.provider,
                    "account_ref": channel.account_ref,
                    "has_access_token": bool(channel.access_token),
                    "has_refresh_token": bool(channel.refresh_token),
                    "metadata": metadata,
                    "created_at": channel.created_at.isoformat(),
                }
                channel_list.append(channel_info)
            
            return channel_list
            
        except Exception as e:
            logger.error(f"Failed to get organization channels: {e}")
            return []
    
    async def test_channel_connection(self, channel_id: str) -> Dict[str, Any]:
        """Test if a channel's credentials are working"""
        try:
            channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
            if not channel:
                return {"success": False, "error": "Channel not found"}
            
            credentials = await self.get_channel_credentials(
                channel.org_id, 
                channel.provider, 
                channel.account_ref
            )
            
            if not credentials:
                return {"success": False, "error": "Failed to get credentials"}
            
            # Test connection based on provider
            if channel.provider == "meta":
                # Test Meta connection by getting user info
                from app.utils.http import HTTPClient
                async with HTTPClient() as client:
                    response = await client.request(
                        "GET",
                        f"https://graph.facebook.com/v{credentials['graph_version']}/me",
                        params={"access_token": credentials["access_token"]}
                    )
                    return {"success": True, "user_info": response.json()}
                    
            elif channel.provider == "linkedin":
                # Test LinkedIn connection
                from app.utils.http import HTTPClient
                async with HTTPClient() as client:
                    response = await client.request(
                        "GET",
                        "https://api.linkedin.com/v2/me",
                        headers={"Authorization": f"Bearer {credentials['access_token']}"}
                    )
                    return {"success": True, "user_info": response.json()}
                    
            elif channel.provider == "google":
                # Test Google connection
                from app.utils.http import HTTPClient
                async with HTTPClient() as client:
                    response = await client.request(
                        "GET",
                        "https://www.googleapis.com/oauth2/v2/userinfo",
                        headers={"Authorization": f"Bearer {credentials['access_token']}"}
                    )
                    return {"success": True, "user_info": response.json()}
            
            else:
                return {"success": False, "error": f"Connection test not implemented for {channel.provider}"}
                
        except Exception as e:
            logger.error(f"Failed to test channel connection: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_channel(self, channel_id: str) -> bool:
        """Delete a channel and its credentials"""
        try:
            channel = self.db.query(Channel).filter(Channel.id == channel_id).first()
            if not channel:
                logger.warning(f"Channel not found for deletion: {channel_id}")
                return True  # Consider it deleted if not found
            
            self.db.delete(channel)
            self.db.commit()
            
            logger.info(f"Successfully deleted channel {channel_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete channel {channel_id}: {e}")
            return False
