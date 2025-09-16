from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List

from app.integrations.oauth.linkedin import LinkedInOAuth
from app.utils.http import HTTPClient, mask_token
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class LinkedInInsightsFetcher:
    """Fetches insights from LinkedIn UGC Posts API."""
    
    def __init__(self):
        self.settings = get_settings()
        self.oauth = LinkedInOAuth()
        self.http_client = HTTPClient()
    
    async def get_ugc_stats(self, ugc_post_urn: str, access_token: str) -> Dict[str, Any]:
        """
        Fetch LinkedIn UGC post statistics.
        
        Args:
            ugc_post_urn: LinkedIn UGC post URN (e.g., "urn:li:ugcPost:123456789")
            access_token: Valid LinkedIn access token
            
        Returns:
            Dict containing normalized insights data
        """
        logger.info(f"[LinkedIn Insights] Fetching UGC stats for {ugc_post_urn}")
        
        try:
            # LinkedIn UGC Posts API endpoint for statistics
            url = f"https://api.linkedin.com/v2/ugcPosts/{ugc_post_urn}/statistics"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"[LinkedIn Insights] UGC stats fetched successfully for {ugc_post_urn}")
            
            # Process and normalize the response
            return self._process_ugc_stats(data)
            
        except Exception as e:
            logger.error(f"[LinkedIn Insights] Failed to fetch UGC stats for {ugc_post_urn}: {e}")
            raise
    
    async def get_ugc_post_details(self, ugc_post_urn: str, access_token: str) -> Dict[str, Any]:
        """
        Fetch additional LinkedIn UGC post details that might contain metrics.
        
        Args:
            ugc_post_urn: LinkedIn UGC post URN
            access_token: Valid LinkedIn access token
            
        Returns:
            Dict containing post details
        """
        logger.info(f"[LinkedIn Insights] Fetching UGC post details for {ugc_post_urn}")
        
        try:
            # LinkedIn UGC Posts API endpoint for post details
            url = f"https://api.linkedin.com/v2/ugcPosts/{ugc_post_urn}"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            response = await self.http_client.get(url, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logger.info(f"[LinkedIn Insights] UGC post details fetched successfully for {ugc_post_urn}")
            
            return data
            
        except Exception as e:
            logger.error(f"[LinkedIn Insights] Failed to fetch UGC post details for {ugc_post_urn}: {e}")
            raise
    
    def _process_ugc_stats(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process LinkedIn UGC statistics response into normalized format."""
        insights = {}
        
        # LinkedIn UGC stats structure
        if "elements" in data:
            for element in data["elements"]:
                # LinkedIn provides different metric types
                metric_type = element.get("metricType", "")
                value = element.get("value", 0)
                
                # Map LinkedIn metric types to our standard names
                if metric_type == "IMPRESSION_COUNT":
                    insights["impressions"] = int(value)
                elif metric_type == "LIKE_COUNT":
                    insights["likes"] = int(value)
                elif metric_type == "COMMENT_COUNT":
                    insights["comments"] = int(value)
                elif metric_type == "SHARE_COUNT":
                    insights["shares"] = int(value)
                elif metric_type == "CLICK_COUNT":
                    insights["clicks"] = int(value)
                elif metric_type == "VIDEO_VIEW_COUNT":
                    insights["video_views"] = int(value)
        
        # Also check for direct fields in the response
        if "impressionCount" in data:
            insights["impressions"] = int(data["impressionCount"])
        if "likeCount" in data:
            insights["likes"] = int(data["likeCount"])
        if "commentCount" in data:
            insights["comments"] = int(data["commentCount"])
        if "shareCount" in data:
            insights["shares"] = int(data["shareCount"])
        if "clickCount" in data:
            insights["clicks"] = int(data["clickCount"])
        if "videoViewCount" in data:
            insights["video_views"] = int(data["videoViewCount"])
        
        return insights
    
    async def get_post_insights(self, post_urn: str, access_token: str) -> Dict[str, Any]:
        """
        Get comprehensive insights for a LinkedIn UGC post.
        
        Args:
            post_urn: LinkedIn UGC post URN
            access_token: Valid LinkedIn access token
            
        Returns:
            Dict containing normalized insights
        """
        try:
            # Try to get statistics first
            stats = await self.get_ugc_stats(post_urn, access_token)
            
            # If stats are empty, try getting post details
            if not stats:
                details = await self.get_ugc_post_details(post_urn, access_token)
                # Extract any metrics from post details
                stats = self._extract_metrics_from_details(details)
            
            return stats
            
        except Exception as e:
            logger.error(f"[LinkedIn Insights] Failed to get insights for {post_urn}: {e}")
            return {}
    
    def _extract_metrics_from_details(self, details: Dict[str, Any]) -> Dict[str, Any]:
        """Extract metrics from LinkedIn UGC post details."""
        insights = {}
        
        # Look for metrics in various parts of the response
        if "numLikes" in details:
            insights["likes"] = int(details["numLikes"])
        if "numComments" in details:
            insights["comments"] = int(details["numComments"])
        if "numShares" in details:
            insights["shares"] = int(details["numShares"])
        if "numViews" in details:
            insights["impressions"] = int(details["numViews"])
        
        return insights
    
    async def get_multiple_posts_insights(
        self, 
        post_urns: List[str], 
        access_token: str
    ) -> Dict[str, Dict[str, Any]]:
        """
        Fetch insights for multiple LinkedIn UGC posts in batch.
        
        Args:
            post_urns: List of LinkedIn UGC post URNs
            access_token: Valid LinkedIn access token
            
        Returns:
            Dict mapping post_urn to insights data
        """
        results = {}
        
        # Process posts in batches to avoid rate limits
        batch_size = 3  # LinkedIn has stricter rate limits
        for i in range(0, len(post_urns), batch_size):
            batch = post_urns[i:i + batch_size]
            
            # Process batch concurrently
            tasks = [
                self.get_post_insights(post_urn, access_token)
                for post_urn in batch
            ]
            
            try:
                batch_results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for post_urn, result in zip(batch, batch_results):
                    if isinstance(result, Exception):
                        logger.error(f"[LinkedIn Insights] Failed to fetch insights for {post_urn}: {result}")
                        results[post_urn] = {}
                    else:
                        results[post_urn] = result
                        
            except Exception as e:
                logger.error(f"[LinkedIn Insights] Batch processing failed: {e}")
                # Mark all posts in this batch as failed
                for post_urn in batch:
                    results[post_urn] = {}
            
            # Longer delay between batches for LinkedIn
            if i + batch_size < len(post_urns):
                await asyncio.sleep(2)
        
        return results
    
    async def get_organization_ugc_posts(
        self, 
        organization_urn: str, 
        access_token: str,
        count: int = 10
    ) -> List[str]:
        """
        Get UGC post URNs for an organization.
        
        Args:
            organization_urn: LinkedIn organization URN
            access_token: Valid LinkedIn access token
            count: Number of posts to retrieve
            
        Returns:
            List of UGC post URNs
        """
        logger.info(f"[LinkedIn Insights] Fetching UGC posts for organization {organization_urn}")
        
        try:
            url = f"https://api.linkedin.com/v2/ugcPosts"
            
            headers = {
                "Authorization": f"Bearer {access_token}",
                "X-Restli-Protocol-Version": "2.0.0"
            }
            
            params = {
                "q": "authors",
                "authors": organization_urn,
                "count": count
            }
            
            response = await self.http_client.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            post_urns = []
            if "elements" in data:
                for element in data["elements"]:
                    if "id" in element:
                        post_urns.append(element["id"])
            
            logger.info(f"[LinkedIn Insights] Found {len(post_urns)} UGC posts for organization")
            return post_urns
            
        except Exception as e:
            logger.error(f"[LinkedIn Insights] Failed to fetch UGC posts for organization: {e}")
            return []
