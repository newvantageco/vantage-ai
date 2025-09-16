from __future__ import annotations

import logging
from datetime import datetime
from typing import Dict, Any, Optional

from app.models.post_metrics import PostMetrics
from app.models.external_refs import ScheduleExternal
from app.integrations.meta_insights import MetaInsightsFetcher
from app.integrations.linkedin_insights import LinkedInInsightsFetcher
from app.core.config import get_settings

logger = logging.getLogger(__name__)


class InsightsMapper:
    """Maps platform-specific insights to standardized PostMetrics schema."""
    
    def __init__(self):
        self.settings = get_settings()
        self.meta_fetcher = MetaInsightsFetcher()
        self.linkedin_fetcher = LinkedInInsightsFetcher()
    
    def map_meta_to_post_metrics(
        self, 
        insights: Dict[str, Any], 
        schedule_id: str,
        provider: str
    ) -> PostMetrics:
        """
        Map Meta (Facebook/Instagram) insights to PostMetrics.
        
        Args:
            insights: Raw insights data from Meta API
            schedule_id: Schedule ID
            provider: 'facebook' or 'instagram'
            
        Returns:
            PostMetrics object with normalized data
        """
        logger.info(f"[Insights Mapper] Mapping Meta {provider} insights for schedule {schedule_id}")
        
        # Create PostMetrics with Meta-specific mapping
        post_metrics = PostMetrics(
            id=f"{schedule_id}_{provider}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            schedule_id=schedule_id,
            impressions=insights.get("impressions"),
            reach=insights.get("reach"),
            likes=insights.get("likes"),
            comments=insights.get("comments"),
            shares=insights.get("shares"),
            clicks=insights.get("clicks"),
            video_views=insights.get("video_views"),
            saves=insights.get("saves"),  # Instagram-specific
            cost_cents=None,  # Not available from basic insights
            fetched_at=datetime.utcnow()
        )
        
        logger.info(f"[Insights Mapper] Mapped Meta {provider} metrics: impressions={post_metrics.impressions}, "
                   f"likes={post_metrics.likes}, comments={post_metrics.comments}")
        
        return post_metrics
    
    def map_linkedin_to_post_metrics(
        self, 
        insights: Dict[str, Any], 
        schedule_id: str
    ) -> PostMetrics:
        """
        Map LinkedIn UGC insights to PostMetrics.
        
        Args:
            insights: Raw insights data from LinkedIn API
            schedule_id: Schedule ID
            
        Returns:
            PostMetrics object with normalized data
        """
        logger.info(f"[Insights Mapper] Mapping LinkedIn insights for schedule {schedule_id}")
        
        # Create PostMetrics with LinkedIn-specific mapping
        post_metrics = PostMetrics(
            id=f"{schedule_id}_linkedin_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            schedule_id=schedule_id,
            impressions=insights.get("impressions"),
            reach=None,  # LinkedIn doesn't provide reach separately
            likes=insights.get("likes"),
            comments=insights.get("comments"),
            shares=insights.get("shares"),
            clicks=insights.get("clicks"),
            video_views=insights.get("video_views"),
            saves=None,  # Not applicable for LinkedIn
            cost_cents=None,  # Not available from basic insights
            fetched_at=datetime.utcnow()
        )
        
        logger.info(f"[Insights Mapper] Mapped LinkedIn metrics: impressions={post_metrics.impressions}, "
                   f"likes={post_metrics.likes}, comments={post_metrics.comments}")
        
        return post_metrics
    
    def map_platform_to_post_metrics(
        self, 
        insights: Dict[str, Any], 
        schedule_id: str,
        provider: str
    ) -> PostMetrics:
        """
        Unified method to map any platform insights to PostMetrics.
        
        Args:
            insights: Raw insights data
            schedule_id: Schedule ID
            provider: Platform name ('facebook', 'instagram', 'linkedin')
            
        Returns:
            PostMetrics object with normalized data
        """
        provider_lower = provider.lower()
        
        if provider_lower in ["facebook", "instagram"]:
            return self.map_meta_to_post_metrics(insights, schedule_id, provider_lower)
        elif provider_lower == "linkedin":
            return self.map_linkedin_to_post_metrics(insights, schedule_id)
        else:
            raise ValueError(f"Unsupported provider for insights mapping: {provider}")
    
    def generate_fake_metrics(self, schedule_id: str, provider: str) -> PostMetrics:
        """
        Generate fake metrics for testing/development.
        
        Args:
            schedule_id: Schedule ID
            provider: Platform name
            
        Returns:
            PostMetrics object with fake data
        """
        import random
        
        logger.info(f"[Insights Mapper] Generating fake metrics for {provider} schedule {schedule_id}")
        
        # Generate realistic fake metrics based on platform
        if provider.lower() in ["facebook", "instagram"]:
            base_impressions = random.randint(100, 5000)
            base_likes = random.randint(5, 200)
            base_comments = random.randint(0, 50)
            base_shares = random.randint(0, 30)
            base_clicks = random.randint(0, 100)
        else:  # LinkedIn
            base_impressions = random.randint(50, 2000)
            base_likes = random.randint(2, 100)
            base_comments = random.randint(0, 25)
            base_shares = random.randint(0, 15)
            base_clicks = random.randint(0, 50)
        
        post_metrics = PostMetrics(
            id=f"{schedule_id}_{provider}_fake_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            schedule_id=schedule_id,
            impressions=base_impressions,
            reach=base_impressions - random.randint(0, base_impressions // 4),  # Reach is usually less than impressions
            likes=base_likes,
            comments=base_comments,
            shares=base_shares,
            clicks=base_clicks,
            video_views=random.randint(0, base_impressions) if random.random() > 0.5 else None,
            saves=random.randint(0, base_likes) if provider.lower() == "instagram" else None,
            cost_cents=None,
            fetched_at=datetime.utcnow()
        )
        
        logger.info(f"[Insights Mapper] Generated fake metrics: impressions={post_metrics.impressions}, "
                   f"likes={post_metrics.likes}, comments={post_metrics.comments}")
        
        return post_metrics
    
    def normalize_metrics_for_analytics(self, post_metrics: PostMetrics) -> Dict[str, float]:
        """
        Convert PostMetrics to normalized values for analytics computation.
        
        Args:
            post_metrics: PostMetrics object
            
        Returns:
            Dict with normalized metrics (0.0 to 1.0)
        """
        # These would be used to compute the existing ScheduleMetrics fields
        # (ctr, engagement_rate, reach_norm, conv_rate)
        
        metrics = {}
        
        # Calculate CTR (Click-through rate)
        if post_metrics.impressions and post_metrics.clicks:
            metrics["ctr"] = min(1.0, post_metrics.clicks / post_metrics.impressions)
        else:
            metrics["ctr"] = 0.0
        
        # Calculate engagement rate
        if post_metrics.impressions:
            total_engagement = (post_metrics.likes or 0) + (post_metrics.comments or 0) + (post_metrics.shares or 0)
            metrics["engagement_rate"] = min(1.0, total_engagement / post_metrics.impressions)
        else:
            metrics["engagement_rate"] = 0.0
        
        # Calculate reach normalization (reach as percentage of impressions)
        if post_metrics.impressions and post_metrics.reach:
            metrics["reach_norm"] = min(1.0, post_metrics.reach / post_metrics.impressions)
        else:
            metrics["reach_norm"] = 1.0  # Assume full reach if not available
        
        # Conversion rate (placeholder - would need conversion tracking)
        metrics["conv_rate"] = 0.0
        
        return metrics
    
    def should_fetch_real_insights(self) -> bool:
        """Check if real insights should be fetched based on configuration."""
        return not self.settings.feature_fake_insights
