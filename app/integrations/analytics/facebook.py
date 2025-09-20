"""
Facebook Analytics Integration
Collects metrics from Facebook Graph API
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.utils.http import HTTPClient

logger = logging.getLogger(__name__)


class FacebookAnalytics:
    """Facebook analytics data collection"""
    
    def __init__(self):
        self.base_url = "https://graph.facebook.com/v18.0"
    
    async def get_post_metrics(
        self, 
        post_id: str, 
        access_token: str,
        page_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific Facebook post
        
        Args:
            post_id: Facebook post ID
            access_token: Facebook access token
            page_id: Optional page ID for page posts
            
        Returns:
            Dictionary with post metrics or None if failed
        """
        try:
            async with HTTPClient() as client:
                # Get basic post insights
                insights_response = await client.request(
                    "GET",
                    f"{self.base_url}/{post_id}/insights",
                    params={
                        "access_token": access_token,
                        "metric": "post_impressions,post_engaged_users,post_clicks,post_reactions_by_type_total,post_comments,post_shares"
                    }
                )
                
                insights_data = insights_response.json()
                insights = insights_data.get("data", [])
                
                # Process insights into metrics
                metrics = {
                    "impressions": 0,
                    "reach": 0,
                    "clicks": 0,
                    "engagements": 0,
                    "likes": 0,
                    "comments": 0,
                    "shares": 0,
                    "reactions": 0
                }
                
                for insight in insights:
                    metric_name = insight.get("name")
                    values = insight.get("values", [])
                    
                    if values and len(values) > 0:
                        value = values[0].get("value", 0)
                        
                        if metric_name == "post_impressions":
                            metrics["impressions"] = value
                        elif metric_name == "post_engaged_users":
                            metrics["reach"] = value
                        elif metric_name == "post_clicks":
                            metrics["clicks"] = value
                        elif metric_name == "post_comments":
                            metrics["comments"] = value
                        elif metric_name == "post_shares":
                            metrics["shares"] = value
                        elif metric_name == "post_reactions_by_type_total":
                            # Sum all reaction types
                            if isinstance(value, dict):
                                metrics["reactions"] = sum(value.values())
                            else:
                                metrics["reactions"] = value
                
                # Calculate total engagements
                metrics["engagements"] = (
                    metrics["likes"] + 
                    metrics["comments"] + 
                    metrics["shares"] + 
                    metrics["reactions"]
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
                
                logger.info(f"Collected Facebook metrics for post {post_id}: {metrics}")
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to collect Facebook metrics for post {post_id}: {str(e)}")
            return None
    
    async def get_page_metrics(
        self, 
        page_id: str, 
        access_token: str,
        days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Get page-level metrics for a Facebook page
        
        Args:
            page_id: Facebook page ID
            access_token: Facebook access token
            days: Number of days to analyze
            
        Returns:
            Dictionary with page metrics or None if failed
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            async with HTTPClient() as client:
                # Get page insights
                insights_response = await client.request(
                    "GET",
                    f"{self.base_url}/{page_id}/insights",
                    params={
                        "access_token": access_token,
                        "metric": "page_impressions,page_reach,page_engaged_users,page_fan_adds,page_fan_removes",
                        "period": "day",
                        "since": start_date.strftime("%Y-%m-%d"),
                        "until": end_date.strftime("%Y-%m-%d")
                    }
                )
                
                insights_data = insights_response.json()
                insights = insights_data.get("data", [])
                
                # Process page insights
                page_metrics = {
                    "total_impressions": 0,
                    "total_reach": 0,
                    "total_engaged_users": 0,
                    "fan_adds": 0,
                    "fan_removes": 0,
                    "net_fan_growth": 0
                }
                
                for insight in insights:
                    metric_name = insight.get("name")
                    values = insight.get("values", [])
                    
                    if values:
                        # Sum all daily values
                        total_value = sum(v.get("value", 0) for v in values)
                        
                        if metric_name == "page_impressions":
                            page_metrics["total_impressions"] = total_value
                        elif metric_name == "page_reach":
                            page_metrics["total_reach"] = total_value
                        elif metric_name == "page_engaged_users":
                            page_metrics["total_engaged_users"] = total_value
                        elif metric_name == "page_fan_adds":
                            page_metrics["fan_adds"] = total_value
                        elif metric_name == "page_fan_removes":
                            page_metrics["fan_removes"] = total_value
                
                page_metrics["net_fan_growth"] = page_metrics["fan_adds"] - page_metrics["fan_removes"]
                
                logger.info(f"Collected Facebook page metrics for page {page_id}: {page_metrics}")
                return page_metrics
                
        except Exception as e:
            logger.error(f"Failed to collect Facebook page metrics for page {page_id}: {str(e)}")
            return None
