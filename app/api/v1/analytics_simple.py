"""
Simple Analytics API
A minimal analytics endpoint that works with existing infrastructure
"""

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import logging

router = APIRouter()


class AnalyticsMetric(BaseModel):
    name: str
    value: int
    change_percent: Optional[float] = None
    trend: Optional[str] = None  # "up", "down", "stable"


class PlatformAnalytics(BaseModel):
    platform: str
    total_posts: int
    total_impressions: int
    total_engagement: int
    engagement_rate: float
    metrics: List[AnalyticsMetric]


class AnalyticsSummary(BaseModel):
    period: str
    total_posts: int
    total_impressions: int
    total_engagement: int
    average_engagement_rate: float
    platforms: List[PlatformAnalytics]
    top_performing_posts: List[Dict[str, Any]]


class PostPerformance(BaseModel):
    post_id: str
    platform: str
    content_preview: str
    published_at: str
    impressions: int
    engagement: int
    engagement_rate: float
    likes: int
    comments: int
    shares: int


@router.get("/analytics/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    period: str = Query("last_30d", description="Time period: last_7d, last_30d, last_90d"),
    platform: Optional[str] = Query(None, description="Filter by platform")
) -> AnalyticsSummary:
    """
    Get analytics summary for the specified period
    """
    try:
        # Mock analytics data (in real implementation, this would query the database)
        mock_data = {
            "last_7d": {
                "total_posts": 12,
                "total_impressions": 15420,
                "total_engagement": 892,
                "average_engagement_rate": 5.78,
                "platforms": [
                    {
                        "platform": "facebook",
                        "total_posts": 5,
                        "total_impressions": 8200,
                        "total_engagement": 456,
                        "engagement_rate": 5.56,
                        "metrics": [
                            {"name": "Impressions", "value": 8200, "change_percent": 12.5, "trend": "up"},
                            {"name": "Engagement", "value": 456, "change_percent": 8.3, "trend": "up"},
                            {"name": "Reach", "value": 7200, "change_percent": 15.2, "trend": "up"}
                        ]
                    },
                    {
                        "platform": "linkedin",
                        "total_posts": 4,
                        "total_impressions": 4200,
                        "total_engagement": 234,
                        "engagement_rate": 5.57,
                        "metrics": [
                            {"name": "Impressions", "value": 4200, "change_percent": 6.8, "trend": "up"},
                            {"name": "Engagement", "value": 234, "change_percent": 12.1, "trend": "up"},
                            {"name": "Clicks", "value": 89, "change_percent": 4.2, "trend": "up"}
                        ]
                    },
                    {
                        "platform": "instagram",
                        "total_posts": 3,
                        "total_impressions": 3020,
                        "total_engagement": 202,
                        "engagement_rate": 6.69,
                        "metrics": [
                            {"name": "Impressions", "value": 3020, "change_percent": 18.5, "trend": "up"},
                            {"name": "Engagement", "value": 202, "change_percent": 22.3, "trend": "up"},
                            {"name": "Saves", "value": 45, "change_percent": 15.6, "trend": "up"}
                        ]
                    }
                ],
                "top_performing_posts": [
                    {
                        "post_id": "post_123",
                        "platform": "instagram",
                        "content_preview": "🚀 Exciting news! We're launching our new AI-powered marketing platform...",
                        "impressions": 1250,
                        "engagement": 89,
                        "engagement_rate": 7.12
                    },
                    {
                        "post_id": "post_124",
                        "platform": "facebook",
                        "content_preview": "📱 Transform your social media strategy with AI...",
                        "impressions": 2100,
                        "engagement": 134,
                        "engagement_rate": 6.38
                    }
                ]
            },
            "last_30d": {
                "total_posts": 45,
                "total_impressions": 67890,
                "total_engagement": 3456,
                "average_engagement_rate": 5.09,
                "platforms": [
                    {
                        "platform": "facebook",
                        "total_posts": 18,
                        "total_impressions": 32100,
                        "total_engagement": 1634,
                        "engagement_rate": 5.09,
                        "metrics": [
                            {"name": "Impressions", "value": 32100, "change_percent": 8.2, "trend": "up"},
                            {"name": "Engagement", "value": 1634, "change_percent": 12.5, "trend": "up"},
                            {"name": "Reach", "value": 28900, "change_percent": 6.8, "trend": "up"}
                        ]
                    },
                    {
                        "platform": "linkedin",
                        "total_posts": 15,
                        "total_impressions": 18900,
                        "total_engagement": 945,
                        "engagement_rate": 5.00,
                        "metrics": [
                            {"name": "Impressions", "value": 18900, "change_percent": 15.3, "trend": "up"},
                            {"name": "Engagement", "value": 945, "change_percent": 18.7, "trend": "up"},
                            {"name": "Clicks", "value": 234, "change_percent": 22.1, "trend": "up"}
                        ]
                    },
                    {
                        "platform": "instagram",
                        "total_posts": 12,
                        "total_impressions": 16890,
                        "total_engagement": 877,
                        "engagement_rate": 5.19,
                        "metrics": [
                            {"name": "Impressions", "value": 16890, "change_percent": 25.6, "trend": "up"},
                            {"name": "Engagement", "value": 877, "change_percent": 28.9, "trend": "up"},
                            {"name": "Saves", "value": 156, "change_percent": 31.2, "trend": "up"}
                        ]
                    }
                ],
                "top_performing_posts": [
                    {
                        "post_id": "post_456",
                        "platform": "instagram",
                        "content_preview": "🎉 Just hit 10K followers! Thank you for your amazing support...",
                        "impressions": 3450,
                        "engagement": 267,
                        "engagement_rate": 7.74
                    },
                    {
                        "post_id": "post_457",
                        "platform": "facebook",
                        "content_preview": "📊 Our latest campaign results are in! Here's what we learned...",
                        "impressions": 4200,
                        "engagement": 298,
                        "engagement_rate": 7.10
                    }
                ]
            }
        }
        
        # Get data for the requested period
        period_data = mock_data.get(period, mock_data["last_30d"])
        
        # Filter by platform if specified
        if platform:
            period_data["platforms"] = [p for p in period_data["platforms"] if p["platform"] == platform]
        
        return AnalyticsSummary(
            period=period,
            total_posts=period_data["total_posts"],
            total_impressions=period_data["total_impressions"],
            total_engagement=period_data["total_engagement"],
            average_engagement_rate=period_data["average_engagement_rate"],
            platforms=[PlatformAnalytics(**p) for p in period_data["platforms"]],
            top_performing_posts=period_data["top_performing_posts"]
        )
        
    except Exception as e:
        logger.error(f"Analytics summary error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get analytics summary: {str(e)}"
        )


@router.get("/analytics/posts", response_model=List[PostPerformance])
async def get_post_performance(
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(10, description="Number of posts to return")
) -> List[PostPerformance]:
    """
    Get performance data for individual posts
    """
    try:
        # Mock post performance data
        mock_posts = [
            PostPerformance(
                post_id="post_123",
                platform="instagram",
                content_preview="🚀 Exciting news! We're launching our new AI-powered marketing platform...",
                published_at="2024-01-15T10:00:00Z",
                impressions=1250,
                engagement=89,
                engagement_rate=7.12,
                likes=67,
                comments=12,
                shares=10
            ),
            PostPerformance(
                post_id="post_124",
                platform="facebook",
                content_preview="📱 Transform your social media strategy with AI...",
                published_at="2024-01-14T15:30:00Z",
                impressions=2100,
                engagement=134,
                engagement_rate=6.38,
                likes=98,
                comments=23,
                shares=13
            ),
            PostPerformance(
                post_id="post_125",
                platform="linkedin",
                content_preview="💼 Professional insights: How AI is changing the marketing landscape...",
                published_at="2024-01-13T09:15:00Z",
                impressions=1800,
                engagement=95,
                engagement_rate=5.28,
                likes=72,
                comments=18,
                shares=5
            ),
            PostPerformance(
                post_id="post_126",
                platform="instagram",
                content_preview="📸 Behind the scenes: Our team working on the next big feature...",
                published_at="2024-01-12T14:20:00Z",
                impressions=980,
                engagement=76,
                engagement_rate=7.76,
                likes=58,
                comments=12,
                shares=6
            ),
            PostPerformance(
                post_id="post_127",
                platform="facebook",
                content_preview="🎯 Case study: How Company X increased engagement by 300%...",
                published_at="2024-01-11T11:45:00Z",
                impressions=1650,
                engagement=112,
                engagement_rate=6.79,
                likes=89,
                comments=15,
                shares=8
            )
        ]
        
        # Filter by platform if specified
        if platform:
            mock_posts = [p for p in mock_posts if p.platform == platform]
        
        # Limit results
        return mock_posts[:limit]
        
    except Exception as e:
        logger.error(f"Post performance error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get post performance: {str(e)}"
        )


@router.get("/analytics/platforms")
async def get_platform_analytics():
    """Get analytics capabilities for each platform"""
    return {
        "platforms": [
            {
                "platform": "facebook",
                "metrics_available": [
                    "impressions", "reach", "engagement", "likes", "comments", "shares", "clicks"
                ],
                "data_retention": "2 years",
                "update_frequency": "real-time",
                "status": "active"
            },
            {
                "platform": "instagram",
                "metrics_available": [
                    "impressions", "reach", "engagement", "likes", "comments", "saves", "video_views"
                ],
                "data_retention": "2 years",
                "update_frequency": "real-time",
                "status": "active"
            },
            {
                "platform": "linkedin",
                "metrics_available": [
                    "impressions", "clicks", "engagement", "likes", "comments", "shares"
                ],
                "data_retention": "1 year",
                "update_frequency": "daily",
                "status": "active"
            },
            {
                "platform": "google_gbp",
                "metrics_available": [
                    "views", "actions", "direction_requests", "phone_calls"
                ],
                "data_retention": "1 year",
                "update_frequency": "daily",
                "status": "active"
            }
        ]
    }


@router.get("/analytics/status")
async def get_analytics_status():
    """Get analytics service status"""
    return {
        "status": "operational",
        "features": [
            "performance_tracking",
            "engagement_metrics",
            "platform_analytics",
            "historical_data",
            "trend_analysis"
        ],
        "supported_platforms": ["facebook", "instagram", "linkedin", "google_gbp"],
        "data_sources": ["api", "webhook", "manual"],
        "version": "1.0.0",
        "message": "Analytics service is ready for performance tracking!"
    }
