from __future__ import annotations

import asyncio
import logging
import mimetypes
import os
from typing import Optional, Sequence, Dict, Any

from .base import Publisher, PostResult
from .common import sanitize_caption, truncate_for_platform, PLATFORM_LIMITS
from app.integrations.oauth.meta import MetaOAuth
from app.utils.http import HTTPClient, mask_token
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MetaPublisher(Publisher):
    can_schedule = True

    def __init__(self):
        self.settings = get_settings()
        self.oauth = MetaOAuth()

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
            "[Meta] publish called | caption=%r media_paths=%r first_comment=%r idem=%r",
            caption,
            list(media_paths),
            first_comment,
            idempotency_key,
        )

        if self.settings.dry_run:
            logger.info("[Meta] DRY RUN - Would publish to Facebook and Instagram")
            sanitized_caption = sanitize_caption(caption)
            fb_caption = truncate_for_platform(sanitized_caption, "facebook", PLATFORM_LIMITS["facebook"])
            ig_caption = truncate_for_platform(sanitized_caption, "instagram", PLATFORM_LIMITS["instagram"])
            return PostResult(id="meta_dry_run", url="https://facebook.com/dry_run")

        try:
            # Get valid access token
            access_token = await self._get_access_token(org_id, account_ref)
            
            # Sanitize caption
            sanitized_caption = sanitize_caption(caption)
            fb_caption = truncate_for_platform(sanitized_caption, "facebook", PLATFORM_LIMITS["facebook"])
            ig_caption = truncate_for_platform(sanitized_caption, "instagram", PLATFORM_LIMITS["instagram"])
            
            # Get page access token using the account_ref (page_id) from channel
            from app.services.channel_service import ChannelService
            from app.db.session import get_db
            
            db = next(get_db())
            try:
                channel_service = ChannelService(db)
                credentials = await channel_service.get_channel_credentials(org_id, "meta", account_ref)
                page_id = credentials["page_id"] if credentials else self.settings.meta_page_id
                page_access_token = await self.oauth.get_page_access_token(access_token, page_id)
            finally:
                db.close()
            
            # Post to Facebook Page
            fb_post_id = await self._post_to_facebook(page_access_token, fb_caption, media_paths, idempotency_key)
            
            # Post to Instagram Business (if configured)
            ig_post_id = None
            if self.settings.meta_ig_business_id:
                ig_post_id = await self._post_to_instagram(page_access_token, ig_caption, media_paths, idempotency_key)
            
            # Return Facebook post as primary result
            permalink = f"https://facebook.com/{self.settings.meta_page_id}/posts/{fb_post_id}"
            
            logger.info(f"[Meta] Post created successfully - FB: {fb_post_id}, IG: {ig_post_id}")
            
            # Store external references for both platforms
            external_refs = {"facebook": fb_post_id}
            if ig_post_id:
                external_refs["instagram"] = ig_post_id
            
            return PostResult(
                id=fb_post_id, 
                url=permalink,
                external_refs=external_refs
            )
            
        except Exception as e:
            logger.error(f"[Meta] Failed to publish: {e}")
            raise

    async def _get_access_token(self, org_id: str, account_ref: Optional[str] = None) -> str:
        """Get valid access token from storage."""
        from app.services.channel_service import ChannelService
        from app.db.session import get_db
        
        # Get database session
        db = next(get_db())
        try:
            channel_service = ChannelService(db)
            
            # Get credentials for Meta
            credentials = await channel_service.get_channel_credentials(org_id, "meta", account_ref)
            
            if not credentials or not credentials.get("access_token"):
                raise ValueError("Meta access token not found. Please connect your Meta account first.")
            
            return credentials["access_token"]
        finally:
            db.close()

    async def _post_to_facebook(
        self, 
        page_access_token: str, 
        caption: str, 
        media_paths: Sequence[str],
        idempotency_key: Optional[str] = None
    ) -> str:
        """Post to Facebook Page."""
        async with HTTPClient() as client:
            if media_paths:
                # Upload photos first
                photo_ids = await self._upload_facebook_photos(page_access_token, media_paths)
                
                # Create photo post
                post_data = {
                    "message": caption,
                    "attached_media": [{"media_fbid": photo_id} for photo_id in photo_ids]
                }
            else:
                # Text-only post
                post_data = {"message": caption}
            
            response = await client.request(
                "POST",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{self.settings.meta_page_id}/feed",
                params={
                    "access_token": page_access_token,
                    **post_data
                },
                idempotency_key=idempotency_key
            )
            
            result = response.json()
            post_id = result["id"]
            logger.info(f"[Meta] Facebook post created: {post_id}")
            return post_id

    async def _upload_facebook_photos(self, page_access_token: str, media_paths: Sequence[str]) -> list[str]:
        """Upload photos to Facebook and return photo IDs."""
        photo_ids = []
        
        async with HTTPClient() as client:
            for media_path in media_paths:
                if not os.path.exists(media_path):
                    logger.warning(f"[Meta] Media file not found: {media_path}")
                    continue
                
                mime_type, _ = mimetypes.guess_type(media_path)
                if not mime_type or not mime_type.startswith("image/"):
                    logger.warning(f"[Meta] Unsupported media type: {mime_type}")
                    continue
                
                with open(media_path, "rb") as f:
                    response = await client.request(
                        "POST",
                        f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{self.settings.meta_page_id}/photos",
                        params={"access_token": page_access_token},
                        files={"source": (os.path.basename(media_path), f, mime_type)}
                    )
                
                result = response.json()
                if "id" in result:
                    photo_ids.append(result["id"])
                    logger.info(f"[Meta] Photo uploaded: {result['id']}")
                else:
                    logger.error(f"[Meta] Failed to upload photo: {result}")
        
        return photo_ids

    async def _post_to_instagram(
        self, 
        page_access_token: str, 
        caption: str, 
        media_paths: Sequence[str],
        idempotency_key: Optional[str] = None
    ) -> str:
        """Post to Instagram Business account."""
        async with HTTPClient() as client:
            if not media_paths:
                raise ValueError("Instagram requires at least one image")
            
            # For single image
            if len(media_paths) == 1:
                return await self._post_instagram_single_image(page_access_token, caption, media_paths[0], idempotency_key)
            else:
                # For multiple images (carousel)
                return await self._post_instagram_carousel(page_access_token, caption, media_paths, idempotency_key)

    async def _post_instagram_single_image(
        self, 
        page_access_token: str, 
        caption: str, 
        image_path: str,
        idempotency_key: Optional[str] = None
    ) -> str:
        """Post single image to Instagram."""
        async with HTTPClient() as client:
            # Step 1: Create media container
            mime_type, _ = mimetypes.guess_type(image_path)
            with open(image_path, "rb") as f:
                response = await client.request(
                    "POST",
                    f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{self.settings.meta_ig_business_id}/media",
                    params={
                        "access_token": page_access_token,
                        "image_url": f"file://{os.path.abspath(image_path)}",  # This should be a public URL in production
                        "caption": caption
                    }
                )
            
            container_data = response.json()
            container_id = container_data["id"]
            
            # Step 2: Publish the container
            publish_response = await client.request(
                "POST",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{self.settings.meta_ig_business_id}/media_publish",
                params={
                    "access_token": page_access_token,
                    "creation_id": container_id
                },
                idempotency_key=idempotency_key
            )
            
            publish_data = publish_response.json()
            post_id = publish_data["id"]
            logger.info(f"[Meta] Instagram single image post created: {post_id}")
            return post_id

    async def _post_instagram_carousel(
        self, 
        page_access_token: str, 
        caption: str, 
        image_paths: Sequence[str],
        idempotency_key: Optional[str] = None
    ) -> str:
        """Post carousel to Instagram."""
        async with HTTPClient() as client:
            # Step 1: Create media containers for each image
            container_ids = []
            for i, image_path in enumerate(image_paths[:10]):  # Instagram carousel max 10 images
                mime_type, _ = mimetypes.guess_type(image_path)
                with open(image_path, "rb") as f:
                    response = await client.request(
                        "POST",
                        f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{self.settings.meta_ig_business_id}/media",
                        params={
                            "access_token": page_access_token,
                            "image_url": f"file://{os.path.abspath(image_path)}",  # This should be a public URL in production
                            "is_carousel_item": "true"
                        }
                    )
                
                container_data = response.json()
                container_ids.append(container_data["id"])
            
            # Step 2: Create carousel container
            carousel_response = await client.request(
                "POST",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{self.settings.meta_ig_business_id}/media",
                params={
                    "access_token": page_access_token,
                    "media_type": "CAROUSEL",
                    "children": ",".join(container_ids),
                    "caption": caption
                }
            )
            
            carousel_data = carousel_response.json()
            carousel_id = carousel_data["id"]
            
            # Step 3: Publish the carousel
            publish_response = await client.request(
                "POST",
                f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{self.settings.meta_ig_business_id}/media_publish",
                params={
                    "access_token": page_access_token,
                    "creation_id": carousel_id
                },
                idempotency_key=idempotency_key
            )
            
            publish_data = publish_response.json()
            post_id = publish_data["id"]
            logger.info(f"[Meta] Instagram carousel post created: {post_id}")
            return post_id


