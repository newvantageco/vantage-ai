import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class TikTokAdsProvider:
    """TikTok Business Ads API provider."""
    
    def __init__(self):
        self.base_url = "https://business-api.tiktok.com/open_api/v1.3"
        self.access_token = settings.TIKTOK_ACCESS_TOKEN
        self.advertiser_id = settings.TIKTOK_ADVERTISER_ID
        self.headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a TikTok campaign."""
        try:
            url = f"{self.base_url}/campaign/create/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_name": campaign_data["name"],
                "objective_type": campaign_data.get("objective", "TRAFFIC"),
                "budget_mode": campaign_data.get("budget_mode", "BUDGET_MODE_DAY"),
                "budget": campaign_data.get("budget", 100),  # Daily budget in cents
                "landing_page_url": campaign_data.get("landing_page_url"),
                "status": "ENABLE" if campaign_data.get("status", "active") == "active" else "DISABLE"
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            return {
                "campaign_id": result["data"]["campaign_id"],
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to create TikTok campaign: {e}")
            return {
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def create_ad_group(self, ad_group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a TikTok ad group."""
        try:
            url = f"{self.base_url}/adgroup/create/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": ad_group_data["campaign_id"],
                "adgroup_name": ad_group_data["name"],
                "placement_type": ad_group_data.get("placement_type", "AUTOMATIC"),
                "bidding_type": ad_group_data.get("bidding_type", "BIDDING_TYPE_NO_BID"),
                "budget_mode": ad_group_data.get("budget_mode", "BUDGET_MODE_DAY"),
                "budget": ad_group_data.get("budget", 50),  # Daily budget in cents
                "optimization_goal": ad_group_data.get("optimization_goal", "CLICK"),
                "pacing": ad_group_data.get("pacing", "PACING_MODE_STANDARD"),
                "bid_price": ad_group_data.get("bid_price", 100),  # Bid in cents
                "schedule_type": ad_group_data.get("schedule_type", "SCHEDULE_FROM_NOW"),
                "schedule_start_time": ad_group_data.get("schedule_start_time"),
                "schedule_end_time": ad_group_data.get("schedule_end_time"),
                "status": "ENABLE" if ad_group_data.get("status", "active") == "active" else "DISABLE"
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            return {
                "ad_group_id": result["data"]["adgroup_id"],
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to create TikTok ad group: {e}")
            return {
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def create_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a TikTok ad."""
        try:
            url = f"{self.base_url}/ad/create/"
            
            # Prepare creative data
            creative_data = {
                "ad_name": ad_data["name"],
                "adgroup_id": ad_data["ad_group_id"],
                "call_to_action": ad_data.get("call_to_action", "LEARN_MORE"),
                "landing_page_url": ad_data.get("landing_page_url"),
                "display_name": ad_data.get("display_name"),
                "profile_image_url": ad_data.get("profile_image_url"),
                "video_id": ad_data.get("video_id"),
                "image_ids": ad_data.get("image_ids", []),
                "ad_text": ad_data.get("ad_text"),
                "status": "ENABLE" if ad_data.get("status", "active") == "active" else "DISABLE"
            }
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "creative": creative_data
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            return {
                "ad_id": result["data"]["ad_id"],
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to create TikTok ad: {e}")
            return {
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def get_campaign_metrics(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get TikTok campaign metrics."""
        try:
            url = f"{self.base_url}/reports/integrated/get/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "service_type": "AUCTION",
                "report_type": "BASIC",
                "data_level": "AUCTION_CAMPAIGN",
                "dimensions": ["campaign_id"],
                "metrics": [
                    "impressions",
                    "clicks",
                    "cost",
                    "conversions",
                    "ctr",
                    "cpc",
                    "cpm",
                    "cpa"
                ],
                "start_date": start_date,
                "end_date": end_date,
                "filters": [
                    {
                        "field": "campaign_id",
                        "operator": "IN",
                        "values": [campaign_id]
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            # Process metrics
            metrics_data = result.get("data", {}).get("list", [])
            if not metrics_data:
                return {
                    "campaign_id": campaign_id,
                    "metrics": {},
                    "status": "success",
                    "platform": "tiktok"
                }
            
            metrics = metrics_data[0]
            return {
                "campaign_id": campaign_id,
                "metrics": {
                    "impressions": metrics.get("impressions", 0),
                    "clicks": metrics.get("clicks", 0),
                    "cost": metrics.get("cost", 0),
                    "conversions": metrics.get("conversions", 0),
                    "ctr": metrics.get("ctr", 0),
                    "cpc": metrics.get("cpc", 0),
                    "cpm": metrics.get("cpm", 0),
                    "cpa": metrics.get("cpa", 0)
                },
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to get TikTok campaign metrics: {e}")
            return {
                "campaign_id": campaign_id,
                "metrics": {},
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def get_ad_group_metrics(self, ad_group_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get TikTok ad group metrics."""
        try:
            url = f"{self.base_url}/reports/integrated/get/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "service_type": "AUCTION",
                "report_type": "BASIC",
                "data_level": "AUCTION_ADGROUP",
                "dimensions": ["adgroup_id"],
                "metrics": [
                    "impressions",
                    "clicks",
                    "cost",
                    "conversions",
                    "ctr",
                    "cpc",
                    "cpm",
                    "cpa"
                ],
                "start_date": start_date,
                "end_date": end_date,
                "filters": [
                    {
                        "field": "adgroup_id",
                        "operator": "IN",
                        "values": [ad_group_id]
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            # Process metrics
            metrics_data = result.get("data", {}).get("list", [])
            if not metrics_data:
                return {
                    "ad_group_id": ad_group_id,
                    "metrics": {},
                    "status": "success",
                    "platform": "tiktok"
                }
            
            metrics = metrics_data[0]
            return {
                "ad_group_id": ad_group_id,
                "metrics": {
                    "impressions": metrics.get("impressions", 0),
                    "clicks": metrics.get("clicks", 0),
                    "cost": metrics.get("cost", 0),
                    "conversions": metrics.get("conversions", 0),
                    "ctr": metrics.get("ctr", 0),
                    "cpc": metrics.get("cpc", 0),
                    "cpm": metrics.get("cpm", 0),
                    "cpa": metrics.get("cpa", 0)
                },
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to get TikTok ad group metrics: {e}")
            return {
                "ad_group_id": ad_group_id,
                "metrics": {},
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def get_ad_metrics(self, ad_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get TikTok ad metrics."""
        try:
            url = f"{self.base_url}/reports/integrated/get/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "service_type": "AUCTION",
                "report_type": "BASIC",
                "data_level": "AUCTION_AD",
                "dimensions": ["ad_id"],
                "metrics": [
                    "impressions",
                    "clicks",
                    "cost",
                    "conversions",
                    "ctr",
                    "cpc",
                    "cpm",
                    "cpa"
                ],
                "start_date": start_date,
                "end_date": end_date,
                "filters": [
                    {
                        "field": "ad_id",
                        "operator": "IN",
                        "values": [ad_id]
                    }
                ]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            # Process metrics
            metrics_data = result.get("data", {}).get("list", [])
            if not metrics_data:
                return {
                    "ad_id": ad_id,
                    "metrics": {},
                    "status": "success",
                    "platform": "tiktok"
                }
            
            metrics = metrics_data[0]
            return {
                "ad_id": ad_id,
                "metrics": {
                    "impressions": metrics.get("impressions", 0),
                    "clicks": metrics.get("clicks", 0),
                    "cost": metrics.get("cost", 0),
                    "conversions": metrics.get("conversions", 0),
                    "ctr": metrics.get("ctr", 0),
                    "cpc": metrics.get("cpc", 0),
                    "cpm": metrics.get("cpm", 0),
                    "cpa": metrics.get("cpa", 0)
                },
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to get TikTok ad metrics: {e}")
            return {
                "ad_id": ad_id,
                "metrics": {},
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def update_campaign_budget(self, campaign_id: str, budget: int) -> Dict[str, Any]:
        """Update TikTok campaign budget."""
        try:
            url = f"{self.base_url}/campaign/update/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": campaign_id,
                "budget": budget
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            return {
                "campaign_id": campaign_id,
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to update TikTok campaign budget: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pause a TikTok campaign."""
        try:
            url = f"{self.base_url}/campaign/update/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": campaign_id,
                "status": "DISABLE"
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            return {
                "campaign_id": campaign_id,
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to pause TikTok campaign: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
    
    def resume_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Resume a TikTok campaign."""
        try:
            url = f"{self.base_url}/campaign/update/"
            
            payload = {
                "advertiser_id": self.advertiser_id,
                "campaign_id": campaign_id,
                "status": "ENABLE"
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if result.get("code") != 0:
                raise Exception(f"TikTok API error: {result.get('message', 'Unknown error')}")
            
            return {
                "campaign_id": campaign_id,
                "status": "success",
                "platform": "tiktok"
            }
            
        except Exception as e:
            logger.error(f"Failed to resume TikTok campaign: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e),
                "platform": "tiktok"
            }
