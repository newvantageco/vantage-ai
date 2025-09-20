"""
Google My Business Analytics Integration
Collects metrics from Google My Business API
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from app.utils.http import HTTPClient

logger = logging.getLogger(__name__)


class GoogleAnalytics:
    """Google My Business analytics data collection"""
    
    def __init__(self):
        self.base_url = "https://mybusiness.googleapis.com/v4"
    
    async def get_post_metrics(
        self, 
        post_id: str, 
        access_token: str,
        account_name: str,
        location_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metrics for a specific Google My Business post
        
        Args:
            post_id: Google My Business post ID
            access_token: Google access token
            account_name: Google Business account name
            location_name: Google Business location name
            
        Returns:
            Dictionary with post metrics or None if failed
        """
        try:
            async with HTTPClient() as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Get post insights
                insights_response = await client.request(
                    "GET",
                    f"{self.base_url}/{account_name}/locations/{location_name}/localPosts/{post_id}/insights",
                    headers=headers
                )
                
                insights_data = insights_response.json()
                
                # Process insights data
                metrics = {
                    "impressions": 0,
                    "clicks": 0,
                    "calls": 0,
                    "direction_requests": 0,
                    "website_clicks": 0,
                    "engagements": 0,
                    "engagement_rate": 0,
                    "ctr": 0
                }
                
                # Extract metrics from insights
                for insight in insights_data.get("insights", []):
                    metric_type = insight.get("metricType")
                    metric_value = insight.get("metricValue", {})
                    
                    if metric_type == "POST_VIEWS":
                        metrics["impressions"] = metric_value.get("value", 0)
                    elif metric_type == "POST_CLICKS":
                        metrics["clicks"] = metric_value.get("value", 0)
                    elif metric_type == "POST_CALLS":
                        metrics["calls"] = metric_value.get("value", 0)
                    elif metric_type == "POST_DIRECTION_REQUESTS":
                        metrics["direction_requests"] = metric_value.get("value", 0)
                    elif metric_type == "POST_WEBSITE_CLICKS":
                        metrics["website_clicks"] = metric_value.get("value", 0)
                
                # Calculate total engagements
                metrics["engagements"] = (
                    metrics["clicks"] + 
                    metrics["calls"] + 
                    metrics["direction_requests"] + 
                    metrics["website_clicks"]
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
                
                logger.info(f"Collected Google My Business metrics for post {post_id}: {metrics}")
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to collect Google My Business metrics for post {post_id}: {str(e)}")
            return None
    
    async def get_location_metrics(
        self, 
        location_name: str, 
        access_token: str,
        days: int = 30
    ) -> Optional[Dict[str, Any]]:
        """
        Get location-level metrics
        
        Args:
            location_name: Google Business location name
            access_token: Google access token
            days: Number of days to analyze
            
        Returns:
            Dictionary with location metrics or None if failed
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            async with HTTPClient() as client:
                headers = {"Authorization": f"Bearer {access_token}"}
                
                # Get location insights
                insights_response = await client.request(
                    "GET",
                    f"{self.base_url}/{location_name}/insights",
                    params={
                        "startDate": start_date.strftime("%Y-%m-%d"),
                        "endDate": end_date.strftime("%Y-%m-%d"),
                        "metric": "QUERIES_DIRECT,QUERIES_INDIRECT,QUERIES_CHAIN,VIEWS_MAPS,VIEWS_SEARCH,ACTIONS_WEBSITE,ACTIONS_PHONE,ACTIONS_DRIVING_DIRECTIONS,ACTIONS_PHOTO_VIEWS,ACTIONS_PHOTO_VIEWS_MERCHANT,ACTIONS_PHOTO_VIEWS_CUSTOMERS,ACTIONS_PHOTO_COUNT_MERCHANT,ACTIONS_PHOTO_COUNT_CUSTOMERS"
                    },
                    headers=headers
                )
                
                insights_data = insights_response.json()
                
                # Process location insights
                location_metrics = {
                    "total_queries": 0,
                    "direct_queries": 0,
                    "indirect_queries": 0,
                    "chain_queries": 0,
                    "total_views": 0,
                    "maps_views": 0,
                    "search_views": 0,
                    "website_clicks": 0,
                    "phone_calls": 0,
                    "direction_requests": 0,
                    "photo_views": 0,
                    "photo_count": 0
                }
                
                # Sum up daily metrics
                for day_data in insights_data.get("locationMetrics", []):
                    metric_values = day_data.get("metricValues", [])
                    
                    for metric in metric_values:
                        metric_type = metric.get("metric")
                        value = metric.get("dimensionalValues", [{}])[0].get("value", 0)
                        
                        if metric_type == "QUERIES_DIRECT":
                            location_metrics["direct_queries"] += value
                        elif metric_type == "QUERIES_INDIRECT":
                            location_metrics["indirect_queries"] += value
                        elif metric_type == "QUERIES_CHAIN":
                            location_metrics["chain_queries"] += value
                        elif metric_type == "VIEWS_MAPS":
                            location_metrics["maps_views"] += value
                        elif metric_type == "VIEWS_SEARCH":
                            location_metrics["search_views"] += value
                        elif metric_type == "ACTIONS_WEBSITE":
                            location_metrics["website_clicks"] += value
                        elif metric_type == "ACTIONS_PHONE":
                            location_metrics["phone_calls"] += value
                        elif metric_type == "ACTIONS_DRIVING_DIRECTIONS":
                            location_metrics["direction_requests"] += value
                        elif metric_type == "ACTIONS_PHOTO_VIEWS":
                            location_metrics["photo_views"] += value
                        elif metric_type == "ACTIONS_PHOTO_COUNT_MERCHANT":
                            location_metrics["photo_count"] += value
                
                # Calculate totals
                location_metrics["total_queries"] = (
                    location_metrics["direct_queries"] + 
                    location_metrics["indirect_queries"] + 
                    location_metrics["chain_queries"]
                )
                
                location_metrics["total_views"] = (
                    location_metrics["maps_views"] + 
                    location_metrics["search_views"]
                )
                
                logger.info(f"Collected Google My Business location metrics for {location_name}: {location_metrics}")
                return location_metrics
                
        except Exception as e:
            logger.error(f"Failed to collect Google My Business location metrics for {location_name}: {str(e)}")
            return None
