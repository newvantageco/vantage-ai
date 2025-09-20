from __future__ import annotations

import os
from typing import Any, Dict, Optional
from fastapi import Request, Response
from fastapi.responses import JSONResponse


class MockProvider:
    """Provides mock responses for E2E testing when E2E_MOCKS=true"""
    
    def __init__(self) -> None:
        self.enabled = False  # Disabled for production
    
    def is_enabled(self) -> bool:
        """Check if mock mode is enabled"""
        return self.enabled
    
    def get_oauth_mock(self, provider: str) -> Dict[str, Any]:
        """Get OAuth mock data for provider"""
        if provider == "meta":
            return {
                "auth_url": "https://www.facebook.com/v20.0/dialog/oauth?client_id=mock_app_id&redirect_uri=mock_redirect&state=mock_state",
                "state": "mock_state_123"
            }
        elif provider == "linkedin":
            return {
                "auth_url": "https://www.linkedin.com/oauth/v2/authorization?client_id=mock_linkedin_id&redirect_uri=mock_redirect&state=mock_state",
                "state": "mock_state_123"
            }
        return {}
    
    def get_oauth_callback_mock(self, provider: str) -> Dict[str, Any]:
        """Get OAuth callback mock data for provider"""
        if provider == "meta":
            return {
                "success": True,
                "access_token": "mock_meta_access_token_123",
                "user_id": "mock_meta_user_123",
                "expires_in": 3600
            }
        elif provider == "linkedin":
            return {
                "success": True,
                "access_token": "mock_linkedin_access_token_123",
                "user_id": "mock_linkedin_user_123",
                "expires_in": 3600
            }
        return {"success": False, "error": "Invalid provider"}
    
    def get_publisher_pages_mock(self, provider: str) -> Dict[str, Any]:
        """Get publisher pages mock data"""
        if provider == "meta":
            return [
                {
                    "id": "mock_meta_page_123",
                    "name": "Mock Facebook Page",
                    "access_token": "mock_meta_page_token_123",
                    "category": "Business"
                }
            ]
        elif provider == "linkedin":
            return [
                {
                    "id": "mock_linkedin_page_123",
                    "name": "Mock LinkedIn Page",
                    "access_token": "mock_linkedin_page_token_123",
                    "category": "Company"
                }
            ]
        return []
    
    def get_publisher_post_mock(self, provider: str) -> Dict[str, Any]:
        """Get publisher post mock data"""
        if provider == "meta":
            return {
                "id": "mock_meta_post_123",
                "success": True,
                "url": "https://facebook.com/mock_post_123",
                "created_time": "2024-01-01T12:00:00Z"
            }
        elif provider == "linkedin":
            return {
                "id": "mock_linkedin_post_123",
                "success": True,
                "url": "https://linkedin.com/posts/mock_post_123",
                "created_time": "2024-01-01T12:00:00Z"
            }
        return {"success": False, "error": "Invalid provider"}
    
    def get_insights_mock(self, provider: str) -> Dict[str, Any]:
        """Get insights mock data"""
        if provider == "meta":
            return [
                {
                    "post_id": "mock_meta_post_123",
                    "impressions": 1250,
                    "reach": 980,
                    "likes": 45,
                    "comments": 12,
                    "shares": 8,
                    "clicks": 23,
                    "engagement_rate": 0.08,
                    "date": "2024-01-01"
                }
            ]
        elif provider == "linkedin":
            return [
                {
                    "post_id": "mock_linkedin_post_123",
                    "impressions": 890,
                    "likes": 32,
                    "comments": 7,
                    "shares": 5,
                    "clicks": 18,
                    "engagement_rate": 0.06,
                    "date": "2024-01-01"
                }
            ]
        return []
    
    def get_content_plan_mock(self) -> Dict[str, Any]:
        """Get content plan mock data"""
        return [
            {
                "id": "mock_plan_1",
                "title": "Product Launch Announcement",
                "caption": "Exciting news! Our new product is launching soon. Stay tuned for updates!",
                "hashtags": ["#productlaunch", "#innovation", "#tech"],
                "scheduled_at": "2024-01-02T10:00:00Z",
                "platform": "meta"
            },
            {
                "id": "mock_plan_2",
                "title": "Behind the Scenes",
                "caption": "Take a look at our development process and team culture.",
                "hashtags": ["#behindthescenes", "#team", "#culture"],
                "scheduled_at": "2024-01-03T14:00:00Z",
                "platform": "linkedin"
            }
        ]
    
    def get_campaigns_mock(self) -> Dict[str, Any]:
        """Get campaigns mock data"""
        return [
            {
                "id": "mock_campaign_1",
                "name": "Q1 Product Launch",
                "objective": "Increase brand awareness and drive product adoption",
                "start_date": "2024-01-01",
                "end_date": "2024-03-31",
                "status": "active"
            }
        ]
    
    def get_schedule_mock(self) -> Dict[str, Any]:
        """Get schedule mock data"""
        return {
            "processed": 2,
            "posted": 2,
            "failed": 0,
            "results": [
                {
                    "id": "mock_schedule_1",
                    "status": "posted",
                    "post_id": "mock_meta_post_123"
                },
                {
                    "id": "mock_schedule_2",
                    "status": "posted",
                    "post_id": "mock_linkedin_post_123"
                }
            ]
        }
    
    def get_weekly_brief_mock(self) -> Dict[str, Any]:
        """Get weekly brief mock data"""
        return {
            "period": "2024-01-01 to 2024-01-07",
            "top_performers": [
                {
                    "post_id": "mock_post_1",
                    "caption": "Top performing post",
                    "metrics": {
                        "impressions": 1500,
                        "engagement_rate": 0.08,
                        "clicks": 25
                    }
                }
            ],
            "recommendations": [
                {
                    "type": "timing",
                    "message": "Post more content on Tuesday mornings for better engagement",
                    "priority": "high"
                },
                {
                    "type": "content",
                    "message": "Product-related posts perform 40% better than general content",
                    "priority": "medium"
                }
            ],
            "summary": {
                "total_posts": 5,
                "total_impressions": 4500,
                "avg_engagement_rate": 0.07,
                "growth_rate": 0.15
            }
        }


# Global mock provider instance
mock_provider = MockProvider()


def get_mock_response(endpoint: str, method: str = "GET", **kwargs) -> Optional[JSONResponse]:
    """Get mock response for endpoint if mock mode is enabled"""
    if not mock_provider.is_enabled():
        return None
    
    # Route mock responses based on endpoint
    if endpoint.startswith("/oauth/meta/init"):
        return JSONResponse(content=mock_provider.get_oauth_mock("meta"))
    elif endpoint.startswith("/oauth/meta/callback"):
        return JSONResponse(content=mock_provider.get_oauth_callback_mock("meta"))
    elif endpoint.startswith("/oauth/linkedin/init"):
        return JSONResponse(content=mock_provider.get_oauth_mock("linkedin"))
    elif endpoint.startswith("/oauth/linkedin/callback"):
        return JSONResponse(content=mock_provider.get_oauth_callback_mock("linkedin"))
    elif endpoint.startswith("/publishers/meta/pages"):
        return JSONResponse(content=mock_provider.get_publisher_pages_mock("meta"))
    elif endpoint.startswith("/publishers/linkedin/pages"):
        return JSONResponse(content=mock_provider.get_publisher_pages_mock("linkedin"))
    elif endpoint.startswith("/publishers/meta/post"):
        return JSONResponse(content=mock_provider.get_publisher_post_mock("meta"))
    elif endpoint.startswith("/publishers/linkedin/post"):
        return JSONResponse(content=mock_provider.get_publisher_post_mock("linkedin"))
    elif endpoint.startswith("/insights/meta"):
        return JSONResponse(content=mock_provider.get_insights_mock("meta"))
    elif endpoint.startswith("/insights/linkedin"):
        return JSONResponse(content=mock_provider.get_insights_mock("linkedin"))
    elif endpoint.startswith("/content/plan/suggestions"):
        return JSONResponse(content=mock_provider.get_content_plan_mock())
    elif endpoint.startswith("/campaigns"):
        if method == "GET":
            return JSONResponse(content=mock_provider.get_campaigns_mock())
        elif method == "POST":
            return JSONResponse(content={"id": "mock_campaign_new", "name": "New Campaign", "objective": "Test objective"}, status_code=201)
    elif endpoint.startswith("/schedule/run"):
        return JSONResponse(content=mock_provider.get_schedule_mock())
    elif endpoint.startswith("/schedule/due"):
        return JSONResponse(content=[])
    elif endpoint.startswith("/schedule/bulk"):
        return JSONResponse(content={"success": True, "created": 1})
    elif endpoint.startswith("/reports/weekly-brief"):
        return JSONResponse(content=mock_provider.get_weekly_brief_mock())
    
    return None
