from __future__ import annotations

import asyncio
import logging
import mimetypes
import os
from typing import Optional, Sequence, Dict, Any

from .base import Publisher, PostResult
from .common import sanitize_caption, truncate_for_platform, PLATFORM_LIMITS
from app.integrations.oauth.linkedin import LinkedInOAuth
from app.utils.http import HTTPClient, mask_token
from app.core.config import get_settings
from app.models.external_refs import ScheduleExternal

logger = logging.getLogger(__name__)


class LinkedInPublisher(Publisher):
    can_schedule = True

    def __init__(self):
        self.settings = get_settings()
        self.oauth = LinkedInOAuth()

    async def publish(
        self,
        *,
        org_id: str,
        caption: str,
        media_paths: Sequence[str],
        first_comment: Optional[str] = None,
        account_ref: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PostResult:
        logger.info(
            "[LinkedIn] publish called | caption=%r media_paths=%r first_comment=%r idem=%r",
            caption,
            list(media_paths),
            first_comment,
            idempotency_key,
        )

        if self.settings.dry_run:
            logger.info("[LinkedIn] DRY RUN - Would publish with sanitized caption")
            sanitized_caption = sanitize_caption(caption)
            sanitized_caption = truncate_for_platform(sanitized_caption, "linkedin", PLATFORM_LIMITS["linkedin"])
            return PostResult(id="li_dry_run", url="https://linkedin.com/feed/update/dry_run")

        try:
            # Get valid access token from channel service
            access_token = await self._get_access_token(org_id, account_ref)
            
            # Sanitize caption
            sanitized_caption = sanitize_caption(caption)
            sanitized_caption = truncate_for_platform(sanitized_caption, "linkedin", PLATFORM_LIMITS["linkedin"])
            
            # Get page URN
            page_urn = await self.oauth.get_page_urn(access_token)
            
            # Upload media if provided
            media_urns = []
            if media_paths:
                media_urns = await self._upload_media(access_token, media_paths)
            
            # Create UGC post
            post_id, permalink = await self._create_ugc_post(
                access_token, 
                page_urn, 
                sanitized_caption, 
                media_urns,
                idempotency_key
            )
            
            logger.info(f"[LinkedIn] Post created successfully: {post_id}")
            
            # Store external reference if database session is available
            external_refs = {"linkedin": post_id}
            
            return PostResult(
                id=post_id, 
                url=permalink,
                external_refs=external_refs
            )
            
        except Exception as e:
            logger.error(f"[LinkedIn] Failed to publish: {e}")
            raise

    async def _get_access_token(self, org_id: str, account_ref: Optional[str] = None) -> str:
        """Get valid access token from storage."""
        from app.services.channel_service import ChannelService
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        try:
            channel_service = ChannelService(db)
            
            # Get credentials for LinkedIn
            credentials = await channel_service.get_channel_credentials(org_id, "linkedin", account_ref)
            
            if not credentials or not credentials.get("access_token"):
                raise ValueError("LinkedIn access token not found. Please connect your LinkedIn account first.")
            
            return credentials["access_token"]
        finally:
            db.close()

    async def _upload_media(self, access_token: str, media_paths: Sequence[str]) -> list[str]:
        """Upload media files to LinkedIn and return asset URNs."""
        media_urns = []
        
        async with HTTPClient() as client:
            for media_path in media_paths:
                if not os.path.exists(media_path):
                    logger.warning(f"[LinkedIn] Media file not found: {media_path}")
                    continue
                
                # Register upload
                register_response = await client.request(
                    "POST",
                    "https://api.linkedin.com/v2/assets?action=registerUpload",
                    headers={
                        "Authorization": f"Bearer {access_token}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "registerUploadRequest": {
                            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
                            "owner": "urn:li:person:YOUR_PERSON_URN",  # This should be dynamic
                            "serviceRelationships": [
                                {
                                    "relationshipType": "OWNER",
                                    "identifier": "urn:li:userGeneratedContent"
                                }
                            ]
                        }
                    }
                )
                
                register_data = register_response.json()
                upload_url = register_data["value"]["uploadMechanism"]["com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"]["uploadUrl"]
                asset_urn = register_data["value"]["asset"]
                
                # Upload file
                mime_type, _ = mimetypes.guess_type(media_path)
                with open(media_path, "rb") as f:
                    upload_response = await client.request(
                        "PUT",
                        upload_url,
                        headers={"Content-Type": mime_type or "application/octet-stream"},
                        data=f.read()
                    )
                
                if upload_response.status_code == 201:
                    media_urns.append(asset_urn)
                    logger.info(f"[LinkedIn] Media uploaded successfully: {asset_urn}")
                else:
                    logger.error(f"[LinkedIn] Failed to upload media: {upload_response.status_code}")
        
        return media_urns

    async def _create_ugc_post(
        self, 
        access_token: str, 
        page_urn: str, 
        caption: str, 
        media_urns: list[str],
        idempotency_key: Optional[str] = None
    ) -> tuple[str, str]:
        """Create UGC post on LinkedIn."""
        async with HTTPClient() as client:
            # Prepare UGC post data
            ugc_data = {
                "author": page_urn,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": caption
                        },
                        "shareMediaCategory": "IMAGE" if media_urns else "NONE"
                    }
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
                }
            }
            
            # Add media if available
            if media_urns:
                ugc_data["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
                    {
                        "status": "READY",
                        "description": {
                            "text": caption
                        },
                        "media": media_urn,
                        "title": {
                            "text": "Image"
                        }
                    }
                    for media_urn in media_urns
                ]
            
            response = await client.request(
                "POST",
                "https://api.linkedin.com/v2/ugcPosts",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "X-Restli-Protocol-Version": "2.0.0"
                },
                json=ugc_data,
                idempotency_key=idempotency_key
            )
            
            post_data = response.json()
            post_id = post_data["id"]
            
            # Get permalink (this would require additional API call)
            permalink = f"https://www.linkedin.com/feed/update/{post_id}"
            
            return post_id, permalink


