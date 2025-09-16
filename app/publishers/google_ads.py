import requests
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleAdsProvider:
    """Google Ads API provider."""
    
    def __init__(self):
        self.base_url = "https://googleads.googleapis.com/v14"
        self.access_token = settings.GOOGLE_ADS_ACCESS_TOKEN
        self.customer_id = settings.GOOGLE_ADS_CUSTOMER_ID
        self.developer_token = settings.GOOGLE_ADS_DEVELOPER_TOKEN
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "developer-token": self.developer_token
        }
    
    def create_campaign(self, campaign_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Ads campaign."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/campaigns:mutate"
            
            # Create campaign operation
            campaign_operation = {
                "create": {
                    "name": campaign_data["name"],
                    "advertising_channel_type": "SEARCH",  # Default to search
                    "status": "ENABLED" if campaign_data.get("status", "active") == "active" else "PAUSED",
                    "campaign_budget": f"customers/{self.customer_id}/campaignBudgets/{campaign_data.get('budget_id', '1')}",
                    "network_settings": {
                        "target_google_search": True,
                        "target_search_network": True,
                        "target_content_network": False,
                        "target_partner_search_network": False
                    },
                    "bidding_strategy_type": "TARGET_SPEND",
                    "target_spend": {
                        "target_spend_micros": campaign_data.get("budget", 1000000)  # Convert to micros
                    }
                }
            }
            
            payload = {
                "operations": [campaign_operation]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            campaign_id = result["results"][0]["resource_name"].split("/")[-1]
            
            return {
                "campaign_id": campaign_id,
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to create Google Ads campaign: {e}")
            return {
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def create_ad_group(self, ad_group_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Ads ad group."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/adGroups:mutate"
            
            # Create ad group operation
            ad_group_operation = {
                "create": {
                    "name": ad_group_data["name"],
                    "campaign": f"customers/{self.customer_id}/campaigns/{ad_group_data['campaign_id']}",
                    "status": "ENABLED" if ad_group_data.get("status", "active") == "active" else "PAUSED",
                    "type": "SEARCH_STANDARD",
                    "cpc_bid_micros": ad_group_data.get("bid_micros", 1000000)  # Convert to micros
                }
            }
            
            payload = {
                "operations": [ad_group_operation]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            ad_group_id = result["results"][0]["resource_name"].split("/")[-1]
            
            return {
                "ad_group_id": ad_group_id,
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to create Google Ads ad group: {e}")
            return {
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def create_text_ad(self, ad_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Google Ads text ad."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/adGroupAds:mutate"
            
            # Create ad group ad operation
            ad_group_ad_operation = {
                "create": {
                    "ad_group": f"customers/{self.customer_id}/adGroups/{ad_data['ad_group_id']}",
                    "status": "ENABLED" if ad_data.get("status", "active") == "active" else "PAUSED",
                    "ad": {
                        "type": "RESPONSIVE_SEARCH_AD",
                        "responsive_search_ad": {
                            "headlines": [
                                {"text": ad_data.get("headline_1", "Default Headline 1")},
                                {"text": ad_data.get("headline_2", "Default Headline 2")},
                                {"text": ad_data.get("headline_3", "Default Headline 3")}
                            ],
                            "descriptions": [
                                {"text": ad_data.get("description_1", "Default Description 1")},
                                {"text": ad_data.get("description_2", "Default Description 2")}
                            ],
                            "path1": ad_data.get("path1", ""),
                            "path2": ad_data.get("path2", "")
                        }
                    }
                }
            }
            
            payload = {
                "operations": [ad_group_ad_operation]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            ad_id = result["results"][0]["resource_name"].split("/")[-1]
            
            return {
                "ad_id": ad_id,
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to create Google Ads text ad: {e}")
            return {
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def get_campaign_metrics(self, campaign_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Google Ads campaign metrics."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/googleAds:search"
            
            query = f"""
                SELECT 
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion
                FROM campaign 
                WHERE campaign.id = {campaign_id}
                AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            payload = {"query": query}
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            # Process metrics
            rows = result.get("results", [])
            if not rows:
                return {
                    "campaign_id": campaign_id,
                    "metrics": {},
                    "status": "success",
                    "platform": "google_ads"
                }
            
            # Aggregate metrics across all rows
            total_impressions = sum(row["metrics"]["impressions"] for row in rows)
            total_clicks = sum(row["metrics"]["clicks"] for row in rows)
            total_cost = sum(row["metrics"]["cost_micros"] for row in rows)
            total_conversions = sum(row["metrics"]["conversions"] for row in rows)
            
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_cost / total_clicks / 1000000) if total_clicks > 0 else 0  # Convert from micros
            cpa = (total_cost / total_conversions / 1000000) if total_conversions > 0 else 0  # Convert from micros
            
            return {
                "campaign_id": campaign_id,
                "metrics": {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "cost": total_cost / 1000000,  # Convert from micros to dollars
                    "conversions": total_conversions,
                    "ctr": ctr,
                    "cpc": cpc,
                    "cpm": (total_cost / total_impressions / 1000000 * 1000) if total_impressions > 0 else 0,
                    "cpa": cpa
                },
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Google Ads campaign metrics: {e}")
            return {
                "campaign_id": campaign_id,
                "metrics": {},
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def get_ad_group_metrics(self, ad_group_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Google Ads ad group metrics."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/googleAds:search"
            
            query = f"""
                SELECT 
                    ad_group.id,
                    ad_group.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion
                FROM ad_group 
                WHERE ad_group.id = {ad_group_id}
                AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            payload = {"query": query}
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            # Process metrics
            rows = result.get("results", [])
            if not rows:
                return {
                    "ad_group_id": ad_group_id,
                    "metrics": {},
                    "status": "success",
                    "platform": "google_ads"
                }
            
            # Aggregate metrics across all rows
            total_impressions = sum(row["metrics"]["impressions"] for row in rows)
            total_clicks = sum(row["metrics"]["clicks"] for row in rows)
            total_cost = sum(row["metrics"]["cost_micros"] for row in rows)
            total_conversions = sum(row["metrics"]["conversions"] for row in rows)
            
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_cost / total_clicks / 1000000) if total_clicks > 0 else 0  # Convert from micros
            cpa = (total_cost / total_conversions / 1000000) if total_conversions > 0 else 0  # Convert from micros
            
            return {
                "ad_group_id": ad_group_id,
                "metrics": {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "cost": total_cost / 1000000,  # Convert from micros to dollars
                    "conversions": total_conversions,
                    "ctr": ctr,
                    "cpc": cpc,
                    "cpm": (total_cost / total_impressions / 1000000 * 1000) if total_impressions > 0 else 0,
                    "cpa": cpa
                },
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Google Ads ad group metrics: {e}")
            return {
                "ad_group_id": ad_group_id,
                "metrics": {},
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def get_ad_metrics(self, ad_id: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get Google Ads ad metrics."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/googleAds:search"
            
            query = f"""
                SELECT 
                    ad_group_ad.ad.id,
                    ad_group_ad.ad.responsive_search_ad.headlines,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.cost_per_conversion
                FROM ad_group_ad 
                WHERE ad_group_ad.ad.id = {ad_id}
                AND segments.date BETWEEN '{start_date}' AND '{end_date}'
            """
            
            payload = {"query": query}
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            # Process metrics
            rows = result.get("results", [])
            if not rows:
                return {
                    "ad_id": ad_id,
                    "metrics": {},
                    "status": "success",
                    "platform": "google_ads"
                }
            
            # Aggregate metrics across all rows
            total_impressions = sum(row["metrics"]["impressions"] for row in rows)
            total_clicks = sum(row["metrics"]["clicks"] for row in rows)
            total_cost = sum(row["metrics"]["cost_micros"] for row in rows)
            total_conversions = sum(row["metrics"]["conversions"] for row in rows)
            
            ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
            cpc = (total_cost / total_clicks / 1000000) if total_clicks > 0 else 0  # Convert from micros
            cpa = (total_cost / total_conversions / 1000000) if total_conversions > 0 else 0  # Convert from micros
            
            return {
                "ad_id": ad_id,
                "metrics": {
                    "impressions": total_impressions,
                    "clicks": total_clicks,
                    "cost": total_cost / 1000000,  # Convert from micros to dollars
                    "conversions": total_conversions,
                    "ctr": ctr,
                    "cpc": cpc,
                    "cpm": (total_cost / total_impressions / 1000000 * 1000) if total_impressions > 0 else 0,
                    "cpa": cpa
                },
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to get Google Ads ad metrics: {e}")
            return {
                "ad_id": ad_id,
                "metrics": {},
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def update_campaign_budget(self, campaign_id: str, budget: int) -> Dict[str, Any]:
        """Update Google Ads campaign budget."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/campaignBudgets:mutate"
            
            # Create budget operation
            budget_operation = {
                "update": {
                    "resource_name": f"customers/{self.customer_id}/campaignBudgets/{campaign_id}",
                    "amount_micros": budget * 1000000  # Convert to micros
                }
            }
            
            payload = {
                "operations": [budget_operation]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            return {
                "campaign_id": campaign_id,
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to update Google Ads campaign budget: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def pause_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Pause a Google Ads campaign."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/campaigns:mutate"
            
            # Create campaign operation
            campaign_operation = {
                "update": {
                    "resource_name": f"customers/{self.customer_id}/campaigns/{campaign_id}",
                    "status": "PAUSED"
                }
            }
            
            payload = {
                "operations": [campaign_operation]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            return {
                "campaign_id": campaign_id,
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to pause Google Ads campaign: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
    
    def resume_campaign(self, campaign_id: str) -> Dict[str, Any]:
        """Resume a Google Ads campaign."""
        try:
            url = f"{self.base_url}/customers/{self.customer_id}/campaigns:mutate"
            
            # Create campaign operation
            campaign_operation = {
                "update": {
                    "resource_name": f"customers/{self.customer_id}/campaigns/{campaign_id}",
                    "status": "ENABLED"
                }
            }
            
            payload = {
                "operations": [campaign_operation]
            }
            
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if "error" in result:
                raise Exception(f"Google Ads API error: {result['error']['message']}")
            
            return {
                "campaign_id": campaign_id,
                "status": "success",
                "platform": "google_ads"
            }
            
        except Exception as e:
            logger.error(f"Failed to resume Google Ads campaign: {e}")
            return {
                "campaign_id": campaign_id,
                "status": "error",
                "error": str(e),
                "platform": "google_ads"
            }
