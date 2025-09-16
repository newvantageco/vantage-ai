from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List

from app.integrations.oauth.meta import MetaOAuth
from app.utils.http import HTTPClient, mask_token
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class MetaInsightsFetcher:
    """Fetches insights from Meta Graph API for Facebook and Instagram posts."""
    
    def __init__(self):
        self.settings = get_settings()
        self.oauth = MetaOAuth()
        self.http_client = HTTPClient()
    
    async def get_fb_post_insights(self, page_post_id: str, access_token: str) -> Dict[str, Any]:
        """
        Fetch Facebook Page post insights.
        
        Args:
            page_post_id: Facebook Page post ID (e.g., "123456789_987654321")
            access_token: Valid page access token
            
        Returns:
            Dict containing insights data
        """
        logger.info(f"[Meta Insights] Fetching FB post insights for {page_post_id}")
        
        try:
            # Get page access token if needed
            page_access_token = await self.oauth.get_page_access_token(access_token, self.settings.meta_page_id)
            
            # Fetch insights with specified fields
            fields = self.settings.meta_insights_fields_fb
            url = f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{page_post_id}/insights"
            
            params = {
                "metric": fields,
                "access_token": page_access_token,
                "period": "lifetime"  # Get lifetime metrics
            }
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"[Meta Insights] FB insights fetched successfully for {page_post_id}")
            
            # Process and normalize the response
            return self._process_fb_insights(data)
            
        except Exception as e:
            logger.error(f"[Meta Insights] Failed to fetch FB insights for {page_post_id}: {e}")
            raise
    
    async def get_ig_media_insights(self, ig_media_id: str, access_token: str) -> Dict[str, Any]:
        """
        Fetch Instagram Business media insights.
        
        Args:
            ig_media_id: Instagram media ID
            access_token: Valid page access token
            
        Returns:
            Dict containing insights data
        """
        logger.info(f"[Meta Insights] Fetching IG media insights for {ig_media_id}")
        
        try:
            # Get page access token if needed
            page_access_token = await self.oauth.get_page_access_token(access_token, self.settings.meta_page_id)
            
            # Fetch insights with specified metrics
            metrics = self.settings.ig_insights_metrics
            url = f"https://graph.facebook.com/v{self.settings.meta_graph_version}/{ig_media_id}/insights"
            
            params = {
                "metric": metrics,
                "access_token": page_access_token,
                "period": "lifetime"  # Get lifetime metrics
            }
            
            response = await self.http_client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"[Meta Insights] IG insights fetched successfully for {ig_media_id}")
            
            # Process and normalize the response
            return self._process_ig_insights(data)
            
        except Exception as e:
            logger.error(f"[Meta Insights] Failed to fetch IG insights for {ig_media_id}: {e}")
            raise
    
    def _process_fb_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Facebook insights response into normalized format."""
        insights = {}
        
        if "data" in data:
            for metric in data["data"]:
                metric_name = metric.get("name", "")
                values = metric.get("values", [])
                
                if values and len(values) > 0:
                    value = values[0].get("value", 0)
                    
                    # Map Facebook metric names to our standard names
                    if metric_name == "impressions":
                        insights["impressions"] = int(value)
                    elif metric_name == "post_impressions_unique":
                        insights["reach"] = int(value)
                    elif metric_name == "likes":
                        insights["likes"] = int(value)
                    elif metric_name == "comments":
                        insights["comments"] = int(value)
                    elif metric_name == "shares":
                        insights["shares"] = int(value)
                    elif metric_name == "clicks":
                        insights["clicks"] = int(value)
        
        return insights
    
    def _process_ig_insights(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process Instagram insights response into normalized format."""
        insights = {}
        
        if "data" in data:
            for metric in data["data"]:
                metric_name = metric.get("name", "")
                values = metric.get("values", [])
                
                if values and len(values) > 0:
                    value = values[0].get("value", 0)
                    
                    # Map Instagram metric names to our standard names
                    if metric_name == "impressions":
                        insights["impressions"] = int(value)
                    elif metric_name == "reach":
                        insights["reach"] = int(value)
                    elif metric_name == "likes":
                        insights["likes"] = int(value)
                    elif metric_name == "comments":
                        insights["comments"] = int(value)
                    elif metric_name == "saves":
                        insights["saves"] = int(value)
                    elif metric_name == "video_views":
                        insights["video_views"] = int(value)
        
        return insights
    
    async def get_post_insights(self, post_id: str, provider: str, access_token: str) -> Dict[str, Any]:
        """
        Unified method to get insights for any Meta post.
        
        Args:
            post_id: Platform post ID
            provider: 'facebook' or 'instagram'
            access_token: Valid access token
            
        Returns:
            Dict containing normalized insights
        """
        if provider.lower() == "facebook":
            return await self.get_fb_post_insights(post_id, access_token)
        elif provider.lower() == "instagram":
            return await self.get_ig_media_insights(post_id, access_token)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    async def get_multiple_posts_insights(
        self, 
        post_ids: List[str], 
        provider: str, 
        access_token: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch insights for multiple posts in batch.
        
        Args:
            post_ids: List of platform post IDs
            provider: 'facebook' or 'instagram'
            access_token: Valid access token
            
        Returns:
            Dict mapping post_id to insights data
        """
        results = {}
        
        # Process posts in batches to avoid rate limits
        batch_size = 5
        for i in range(0, len(post_ids), batch_size):
            batch = post_ids[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [
                self.get_post_insights(post_id, provider, access_token)
                for post_id in batch
            ]
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for post_id, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"[Meta Insights] Failed to fetch insights for {post_id}: {result}")
                        results[post_id] = {}
                    else:
                        results[post_id] = result
                        
            except Exception as e:
                logger.error(f"[Meta Insights] Batch processing failed: {e}")
                # Mark all posts in this batch as failed
                for post_id in batch:
                    results[post_id] = {}
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(post_ids):
                await asyncio.sleep(1)
        
        return results
