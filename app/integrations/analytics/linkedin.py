"""
LinkedIn Analytics Integration
Collects metrics from LinkedIn API
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.utils.http import HTTPClient

logger = logging.getLogger(__name__)


class LinkedInAnalytics:
    """LinkedIn analytics data collection"""
    
    def __init__(self):
        self.base_url = "https://api.linkedin.com/v2"
    
    async def get_post_metrics(
        self, 
        post_id: str, 
        access_token: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific LinkedIn post
        
        Args:
            post_id: LinkedIn post URN (e.g., urn:li:ugcPost:123456)
            access_token: LinkedIn access token
            
        Returns:
            Dictionary with post metrics or None if failed
        """
        try:
            async with HTTPClient() as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Get post analytics
                analytics_response = await client.request(
                    "GET",
                    f"{self.base_url}/socialActions/{post_id}/statistics",
                    headers=headers
                )
                
                analytics_data = analytics_response.json()
                
                # Process analytics data
                metrics = {
                    "impressions": analytics_data.get("numViews", 0),
                    "clicks": analytics_data.get("numClicks", 0),
                    "likes": analytics_data.get("numLikes", 0),
                    "comments": analytics_data.get("numComments", 0),
                    "shares": analytics_data.get("numShares", 0),
                    "engagements": 0,
                    "engagement_rate": 0,
                    "ctr": 0
                }
                
                # Calculate total engagements
                metrics["engagements"] = (
                    metrics["likes"] + 
                    metrics["comments"] + 
                    metrics["shares"]
                )
                
                # Calculate engagement rate
                if metrics["impressions"] > 0:
                    metrics["engagement_rate"] = (metrics["engagements"] / metrics["impressions"]) * 100
                else:
                    metrics["engagement_rate"] = 0
                
                # Calculate CTR
                if metrics["impressions"] > 0:
                    metrics["ctr"] = (metrics["clicks"] / metrics["impressions"]) * 100
                else:
                    metrics["ctr"] = 0
                
                logger.info(f"Collected LinkedIn metrics for post {post_id}: {metrics}")
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to collect LinkedIn metrics for post {post_id}: {str(e)}")
            return None
    
    async def get_organization_metrics(
        self, 
        organization_urn: str, 
        access_token: str,
        days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Get organization-level metrics
        
        Args:
            organization_urn: LinkedIn organization URN
            access_token: LinkedIn access token
            days: Number of days to analyze
            
        Returns:
            Dictionary with organization metrics or None if failed
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            async with HTTPClient() as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Get organization analytics
                analytics_response = await client.request(
                    "GET",
                    f"{self.base_url}/organizationPageStatistics",
                    params={
                        "organization": organization_urn,
                        "timeGranularity": "DAILY",
                        "startTime": int(start_date.timestamp() * 1000),
                        "endTime": int(end_date.timestamp() * 1000)
                    },
                    headers=headers
                )
                
                analytics_data = analytics_response.json()
                
                # Process organization analytics
                org_metrics = {
                    "total_impressions": 0,
                    "total_clicks": 0,
                    "total_engagements": 0,
                    "follower_count": 0,
                    "follower_growth": 0
                }
                
                # Sum up daily metrics
                for day_data in analytics_data.get("elements", []):
                    org_metrics["total_impressions"] += day_data.get("impressionCount", 0)
                    org_metrics["total_clicks"] += day_data.get("clickCount", 0)
                    org_metrics["total_engagements"] += day_data.get("engagement", 0)
                
                # Get current follower count
                try:
                    follower_response = await client.request(
                        "GET",
                        f"{self.base_url}/organizationFollowerStatistics",
                        params={"organization": organization_urn},
                        headers=headers
                    )
                    
                    follower_data = follower_response.json()
                    org_metrics["follower_count"] = follower_data.get("followerCountsByAssociationType", {}).get("MEMBER", 0)
                    
                except Exception as e:
                    logger.warning(f"Could not get follower count: {e}")
                
                logger.info(f"Collected LinkedIn organization metrics for {organization_urn}: {org_metrics}")
                return org_metrics
                
        except Exception as e:
            logger.error(f"Failed to collect LinkedIn organization metrics for {organization_urn}: {str(e)}")
            return None
