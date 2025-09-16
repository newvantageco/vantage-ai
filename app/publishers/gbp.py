from __future__ import annotations

import asyncio
import logging
import mimetypes
import os
from typing import Optional, Sequence, Dict, Any

from .base import Publisher, PostResult
from .common import sanitize_caption, truncate_for_platform, PLATFORM_LIMITS
from app.integrations.oauth.google import GoogleOAuth
from app.utils.http import HTTPClient, mask_token
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class GoogleBusinessPublisher(Publisher):
    can_schedule = True

    def __init__(self):
        self.settings = get_settings()
        self.oauth = GoogleOAuth()

    async def publish(
        self,
        *,
        caption: str,
        media_paths: Sequence[str],
        first_comment: Optional[str] = None,
        idempotency_key: Optional[str] = None,
    ) -> PostResult:
        logger.info(
            "[Google Business] publish called | caption=%r media_paths=%r first_comment=%r idem=%r",
            caption,
            list(media_paths),
            first_comment,
            idempotency_key,
        )

        # Check if GBP is enabled
        if not getattr(self.settings, 'gbp_enabled', False):
            logger.info("[Google Business] GBP_ENABLED=false - DRY RUN mode")
            sanitized_caption = sanitize_caption(caption)
            gbp_caption = truncate_for_platform(sanitized_caption, "google_business", PLATFORM_LIMITS.get("google_business", 1500))
            return PostResult(id="gbp_dry_run", url="https://business.google.com/dry_run")

        if self.settings.dry_run:
            logger.info("[Google Business] DRY RUN - Would publish to Google Business Profile")
            sanitized_caption = sanitize_caption(caption)
            gbp_caption = truncate_for_platform(sanitized_caption, "google_business", PLATFORM_LIMITS.get("google_business", 1500))
            return PostResult(id="gbp_dry_run", url="https://business.google.com/dry_run")

        try:
            # Get valid access token
            access_token = await self._get_access_token()
            
            # Sanitize caption
            sanitized_caption = sanitize_caption(caption)
            gbp_caption = truncate_for_platform(sanitized_caption, "google_business", PLATFORM_LIMITS.get("google_business", 1500))
            
            # Get business location ID
            location_id = await self._get_business_location_id(access_token)
            
            # Upload media if provided
            media_items = []
            if media_paths:
                media_items = await self._upload_media(access_token, media_paths)
            
            # Create local post
            post_id, permalink = await self._create_local_post(
                access_token, 
                location_id, 
                gbp_caption, 
                media_items,
                idempotency_key
            )
            
            logger.info(f"[Google Business] Post created successfully: {post_id}")
            return PostResult(id=post_id, url=permalink)
            
        except Exception as e:
            logger.error(f"[Google Business] Failed to publish: {e}")
            raise

    async def _get_access_token(self) -> str:
        """Get valid access token from storage."""
        # This would typically fetch from your database
        # For now, we'll raise an error indicating token is needed
        raise ValueError("Google access token not found. Please implement token storage.")

    async def _get_business_location_id(self, access_token: str) -> str:
        """Get business location ID from Google My Business API."""
        async with HTTPClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # If location ID is configured, use it
            if self.settings.google_business_location_id:
                logger.info(f"Using configured location ID: {self.settings.google_business_location_id}")
                return self.settings.google_business_location_id
            
            # Otherwise, discover locations
            response = await client.request(
                "GET",
                "https://mybusiness.googleapis.com/v4/accounts",
                headers=headers
            )
            
            data = response.json()
            accounts = data.get("accounts", [])
            
            if not accounts:
                raise ValueError("No Google Business accounts found for user")
            
            # Get locations for the first account
            account_name = accounts[0]["name"]
            locations_response = await client.request(
                "GET",
                f"https://mybusiness.googleapis.com/v4/{account_name}/locations",
                headers=headers
            )
            
            locations_data = locations_response.json()
            locations = locations_data.get("locations", [])
            
            if not locations:
                raise ValueError("No business locations found")
            
            location_id = locations[0]["name"].split("/")[-1]
            logger.info(f"Using discovered location ID: {location_id}")
            return location_id

    async def _upload_media(self, access_token: str, media_paths: Sequence[str]) -> list[Dict[str, Any]]:
        """Upload media files to Google My Business and return media items."""
        media_items = []
        
        async with HTTPClient() as client:
            for media_path in media_paths:
                if not os.path.exists(media_path):
                    logger.warning(f"[Google Business] Media file not found: {media_path}")
                    continue
                
                mime_type, _ = mimetypes.guess_type(media_path)
                if not mime_type or not mime_type.startswith("image/"):
                    logger.warning(f"[Google Business] Unsupported media type: {mime_type}")
                    continue
                
                # Upload media to Google My Business
                with open(media_path, "rb") as f:
                    response = await client.request(
                        "POST",
                        "https://mybusiness.googleapis.com/v4/media",
                        headers={
                            "Authorization": f"Bearer {access_token}",
                            "Content-Type": mime_type,
                        },
                        data=f.read()
                    )
                
                if response.status_code == 200:
                    media_data = response.json()
                    media_items.append({
                        "mediaFormat": "PHOTO",
                        "sourceUrl": media_data.get("resourceName"),
                        "thumbnailUrl": media_data.get("thumbnailUrl")
                    })
                    logger.info(f"[Google Business] Media uploaded successfully: {media_data.get('resourceName')}")
                else:
                    logger.error(f"[Google Business] Failed to upload media: {response.status_code}")
        
        return media_items

    async def _create_local_post(
        self, 
        access_token: str, 
        location_id: str, 
        caption: str, 
        media_items: list[Dict[str, Any]],
        idempotency_key: Optional[str] = None
    ) -> tuple[str, str]:
        """Create local post on Google Business Profile."""
        async with HTTPClient() as client:
            # Prepare local post data
            post_data = {
                "summary": caption,
                "callToAction": {
                    "actionType": "LEARN_MORE",
                    "url": ""  # Optional URL for call-to-action
                },
                "media": media_items if media_items else [],
                "state": "LIVE"
            }
            
            # Add idempotency key if provided
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            if idempotency_key:
                headers["X-Idempotency-Key"] = idempotency_key
            
            response = await client.request(
                "POST",
                f"https://mybusiness.googleapis.com/v4/accounts/{{account}}/locations/{location_id}/localPosts",
                headers=headers,
                json=post_data
            )
            
            post_data = response.json()
            post_id = post_data["name"].split("/")[-1]
            
            # Generate permalink (Google Business posts don't have direct URLs)
            permalink = f"https://business.google.com/posts/{post_id}"
            
            return post_id, permalink
