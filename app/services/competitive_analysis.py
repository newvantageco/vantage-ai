"""
Competitive Analysis Service
Handles competitor tracking, benchmarking, and competitive intelligence
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
import logging
import requests
import json

from app.models.analytics import PostMetrics
from app.models.entities import Organization
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class CompetitorProfile:
    """Represents a competitor profile"""
    
    def __init__(self, name: str, handle: str, platforms: List[str], industry: str = None):
        self.name = name
        self.handle = handle
        self.platforms = platforms
        self.industry = industry
        self.metrics = {}
        self.last_updated = None


class CompetitiveAnalysisService:
    """Service for competitive analysis and benchmarking"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
    
    def add_competitor(
        self,
        org_id: int,
        name: str,
        handle: str,
        platforms: List[str],
        industry: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a new competitor to track
        
        Args:
            org_id: Organization ID
            name: Competitor name
            handle: Social media handle/username
            platforms: List of platforms to track
            industry: Optional industry classification
            
        Returns:
            Competitor profile data
        """
        try:
            # In a real implementation, you would store this in a database
            # For now, we'll use a simple in-memory approach
            competitor = CompetitorProfile(
                name=name,
                handle=handle,
                platforms=platforms,
                industry=industry
            )
            
            # TODO: Store competitor in database
            # competitor_record = Competitor(
            #     organization_id=org_id,
            #     name=name,
            #     handle=handle,
            #     platforms=platforms,
            #     industry=industry
            # )
            # self.db.add(competitor_record)
            # self.db.commit()
            
            return {
                "name": competitor.name,
                "handle": competitor.handle,
                "platforms": competitor.platforms,
                "industry": competitor.industry,
                "added_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error adding competitor: {e}")
            raise
    
    def get_competitor_metrics(
        self,
        competitor_handle: str,
        platform: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get metrics for a specific competitor
        
        Args:
            competitor_handle: Competitor's social media handle
            platform: Platform to analyze
            days: Number of days to analyze
            
        Returns:
            Competitor metrics data
        """
        try:
            # In a real implementation, you would fetch this from social media APIs
            # For now, we'll generate realistic mock data
            
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Generate mock competitor metrics
            competitor_metrics = self._generate_mock_competitor_metrics(
                competitor_handle, platform, start_date, end_date
            )
            
            return competitor_metrics
            
        except Exception as e:
            logger.error(f"Error getting competitor metrics: {e}")
            raise
    
    def benchmark_against_competitors(
        self,
        org_id: int,
        competitors: List[str],
        platforms: List[str],
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Benchmark organization performance against competitors
        
        Args:
            org_id: Organization ID
            competitors: List of competitor handles
            platforms: List of platforms to compare
            days: Number of days to analyze
            
        Returns:
            Benchmarking analysis data
        """
        try:
            # Get organization metrics
            org_metrics = self.analytics_service.get_analytics_summary(
                org_id=org_id,
                days=days
            )
            
            # Get competitor metrics
            competitor_data = {}
            for competitor in competitors:
                competitor_metrics = {}
                for platform in platforms:
                    try:
                        metrics = self.get_competitor_metrics(competitor, platform, days)
                        competitor_metrics[platform] = metrics
                    except Exception as e:
                        logger.warning(f"Could not get metrics for {competitor} on {platform}: {e}")
                        continue
                
                if competitor_metrics:
                    competitor_data[competitor] = competitor_metrics
            
            # Calculate benchmarking analysis
            benchmark_analysis = self._calculate_benchmark_analysis(
                org_metrics, competitor_data, platforms
            )
            
            return benchmark_analysis
            
        except Exception as e:
            logger.error(f"Error benchmarking against competitors: {e}")
            raise
    
    def get_industry_benchmarks(
        self,
        industry: str,
        platforms: List[str],
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get industry benchmark data
        
        Args:
            industry: Industry to analyze
            platforms: List of platforms
            days: Number of days to analyze
            
        Returns:
            Industry benchmark data
        """
        try:
            # In a real implementation, you would fetch this from industry data sources
            # For now, we'll generate realistic mock data
            
            industry_benchmarks = self._generate_industry_benchmarks(
                industry, platforms, days
            )
            
            return industry_benchmarks
            
        except Exception as e:
            logger.error(f"Error getting industry benchmarks: {e}")
            raise
    
    def analyze_content_gaps(
        self,
        org_id: int,
        competitor_handles: List[str],
        platforms: List[str],
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze content gaps compared to competitors
        
        Args:
            org_id: Organization ID
            competitor_handles: List of competitor handles
            platforms: List of platforms to analyze
            days: Number of days to analyze
            
        Returns:
            Content gap analysis
        """
        try:
            # Get organization's top content
            org_top_content = self._get_organization_top_content(org_id, platforms, days)
            
            # Get competitor content themes (mock data)
            competitor_themes = self._get_competitor_content_themes(competitor_handles, platforms, days)
            
            # Analyze gaps
            content_gaps = self._analyze_content_gaps(org_top_content, competitor_themes)
            
            return content_gaps
            
        except Exception as e:
            logger.error(f"Error analyzing content gaps: {e}")
            raise
    
    def get_competitive_insights(
        self,
        org_id: int,
        competitors: List[str],
        platforms: List[str],
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive competitive insights
        
        Args:
            org_id: Organization ID
            competitors: List of competitor handles
            platforms: List of platforms to analyze
            days: Number of days to analyze
            
        Returns:
            Competitive insights data
        """
        try:
            # Get benchmarking data
            benchmark_data = self.benchmark_against_competitors(org_id, competitors, platforms, days)
            
            # Get content gap analysis
            content_gaps = self.analyze_content_gaps(org_id, competitors, platforms, days)
            
            # Get industry benchmarks
            industry_benchmarks = self.get_industry_benchmarks("technology", platforms, days)
            
            # Compile insights
            insights = {
                "analysis_period": {
                    "start_date": (datetime.utcnow() - timedelta(days=days)).isoformat(),
                    "end_date": datetime.utcnow().isoformat(),
                    "days": days
                },
                "competitors_analyzed": competitors,
                "platforms_analyzed": platforms,
                "benchmark_analysis": benchmark_data,
                "content_gaps": content_gaps,
                "industry_benchmarks": industry_benchmarks,
                "key_insights": self._generate_key_insights(benchmark_data, content_gaps, industry_benchmarks),
                "recommendations": self._generate_recommendations(benchmark_data, content_gaps, industry_benchmarks)
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error getting competitive insights: {e}")
            raise
    
    def _generate_mock_competitor_metrics(
        self,
        competitor_handle: str,
        platform: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """Generate mock competitor metrics"""
        import random
        
        # Platform-specific base metrics
        platform_multipliers = {
            'facebook': {'impressions': 5000, 'engagement': 0.03},
            'linkedin': {'impressions': 2000, 'engagement': 0.08},
            'twitter': {'impressions': 1000, 'engagement': 0.05},
            'instagram': {'impressions': 3000, 'engagement': 0.06},
        }
        
        base_metrics = platform_multipliers.get(platform, {'impressions': 2000, 'engagement': 0.05})
        
        # Generate realistic metrics with some variation
        total_posts = random.randint(10, 50)
        avg_impressions = int(base_metrics['impressions'] * random.uniform(0.5, 2.0))
        avg_engagement_rate = base_metrics['engagement'] * random.uniform(0.5, 1.5)
        
        total_impressions = total_posts * avg_impressions
        total_engagements = int(total_impressions * avg_engagement_rate)
        total_clicks = int(total_impressions * random.uniform(0.01, 0.05))
        total_conversions = int(total_clicks * random.uniform(0.001, 0.01))
        
        return {
            "competitor_handle": competitor_handle,
            "platform": platform,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "metrics": {
                "total_posts": total_posts,
                "total_impressions": total_impressions,
                "total_reach": int(total_impressions * 0.8),
                "total_clicks": total_clicks,
                "total_engagements": total_engagements,
                "total_conversions": total_conversions,
                "avg_engagement_rate": round(avg_engagement_rate * 100, 2),
                "avg_ctr": round((total_clicks / total_impressions * 100), 2),
                "avg_conversion_rate": round((total_conversions / total_clicks * 100), 2)
            },
            "posting_frequency": {
                "posts_per_day": round(total_posts / 30, 2),
                "posts_per_week": round(total_posts / 4, 2)
            }
        }
    
    def _calculate_benchmark_analysis(
        self,
        org_metrics: Dict[str, Any],
        competitor_data: Dict[str, Any],
        platforms: List[str]
    ) -> Dict[str, Any]:
        """Calculate benchmarking analysis"""
        
        if not competitor_data:
            return {"error": "No competitor data available"}
        
        # Calculate averages across all competitors
        competitor_totals = {
            "total_posts": 0,
            "total_impressions": 0,
            "total_engagements": 0,
            "total_clicks": 0,
            "total_conversions": 0
        }
        
        competitor_count = 0
        for competitor, platforms_data in competitor_data.items():
            for platform, metrics in platforms_data.items():
                if "metrics" in metrics:
                    competitor_totals["total_posts"] += metrics["metrics"]["total_posts"]
                    competitor_totals["total_impressions"] += metrics["metrics"]["total_impressions"]
                    competitor_totals["total_engagements"] += metrics["metrics"]["total_engagements"]
                    competitor_totals["total_clicks"] += metrics["metrics"]["total_clicks"]
                    competitor_totals["total_conversions"] += metrics["metrics"]["total_conversions"]
                    competitor_count += 1
        
        if competitor_count == 0:
            return {"error": "No valid competitor metrics found"}
        
        # Calculate averages
        avg_competitor_metrics = {
            key: value / competitor_count for key, value in competitor_totals.items()
        }
        
        # Calculate organization's performance relative to competitors
        org_performance = {}
        for metric in ["total_posts", "total_impressions", "total_engagements", "total_clicks", "total_conversions"]:
            org_value = org_metrics.get("metrics", {}).get(metric, 0)
            competitor_avg = avg_competitor_metrics.get(metric, 1)
            
            if competitor_avg > 0:
                performance_ratio = org_value / competitor_avg
                org_performance[metric] = {
                    "organization_value": org_value,
                    "competitor_average": competitor_avg,
                    "performance_ratio": round(performance_ratio, 2),
                    "performance_status": "above" if performance_ratio > 1.1 else "below" if performance_ratio < 0.9 else "similar"
                }
        
        return {
            "competitor_averages": avg_competitor_metrics,
            "organization_performance": org_performance,
            "competitors_analyzed": len(competitor_data),
            "platforms_analyzed": platforms
        }
    
    def _generate_industry_benchmarks(
        self,
        industry: str,
        platforms: List[str],
        days: int
    ) -> Dict[str, Any]:
        """Generate industry benchmark data"""
        import random
        
        # Industry-specific benchmarks (mock data)
        industry_benchmarks = {
            "technology": {
                "avg_engagement_rate": 0.05,
                "avg_ctr": 0.02,
                "avg_posts_per_week": 3.5,
                "avg_impressions_per_post": 2000
            },
            "retail": {
                "avg_engagement_rate": 0.08,
                "avg_ctr": 0.03,
                "avg_posts_per_week": 5.0,
                "avg_impressions_per_post": 1500
            },
            "healthcare": {
                "avg_engagement_rate": 0.04,
                "avg_ctr": 0.015,
                "avg_posts_per_week": 2.0,
                "avg_impressions_per_post": 1200
            }
        }
        
        base_benchmarks = industry_benchmarks.get(industry, industry_benchmarks["technology"])
        
        # Add some variation
        benchmarks = {}
        for key, value in base_benchmarks.items():
            benchmarks[key] = round(value * random.uniform(0.8, 1.2), 3)
        
        return {
            "industry": industry,
            "benchmarks": benchmarks,
            "platforms": platforms,
            "analysis_period_days": days,
            "data_source": "industry_analysis"
        }
    
    def _get_organization_top_content(
        self,
        org_id: int,
        platforms: List[str],
        days: int
    ) -> List[Dict[str, Any]]:
        """Get organization's top performing content"""
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.query(PostMetrics).filter(
                PostMetrics.organization_id == org_id,
                PostMetrics.metric_date >= start_date,
                PostMetrics.metric_date <= end_date
            )
            
            if platforms:
                query = query.filter(PostMetrics.platform.in_(platforms))
            
            top_content = query.order_by(PostMetrics.engagement_rate.desc()).limit(10).all()
            
            return [
                {
                    "platform": post.platform,
                    "external_id": post.external_id,
                    "engagement_rate": post.engagement_rate,
                    "impressions": post.impressions,
                    "engagements": post.engagements
                }
                for post in top_content
            ]
            
        except Exception as e:
            logger.error(f"Error getting organization top content: {e}")
            return []
    
    def _get_competitor_content_themes(
        self,
        competitor_handles: List[str],
        platforms: List[str],
        days: int
    ) -> Dict[str, List[str]]:
        """Get competitor content themes (mock data)"""
        import random
        
        # Mock content themes
        all_themes = [
            "product_announcements", "industry_insights", "company_culture",
            "thought_leadership", "customer_stories", "tutorials", "news",
            "behind_scenes", "user_generated_content", "promotional"
        ]
        
        competitor_themes = {}
        for competitor in competitor_handles:
            # Randomly select 3-5 themes for each competitor
            num_themes = random.randint(3, 5)
            themes = random.sample(all_themes, num_themes)
            competitor_themes[competitor] = themes
        
        return competitor_themes
    
    def _analyze_content_gaps(
        self,
        org_content: List[Dict[str, Any]],
        competitor_themes: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """Analyze content gaps compared to competitors"""
        
        # Mock analysis - in reality you would analyze actual content
        all_competitor_themes = set()
        for themes in competitor_themes.values():
            all_competitor_themes.update(themes)
        
        # Mock organization themes
        org_themes = ["product_announcements", "company_culture", "tutorials"]
        
        # Find gaps
        content_gaps = list(all_competitor_themes - set(org_themes))
        
        return {
            "organization_themes": org_themes,
            "competitor_themes": list(all_competitor_themes),
            "content_gaps": content_gaps,
            "gap_analysis": {
                "total_gaps": len(content_gaps),
                "high_priority_gaps": content_gaps[:3],  # Top 3 gaps
                "recommendations": [
                    f"Consider creating content around '{gap}' theme" for gap in content_gaps[:3]
                ]
            }
        }
    
    def _generate_key_insights(
        self,
        benchmark_data: Dict[str, Any],
        content_gaps: Dict[str, Any],
        industry_benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Generate key insights from the analysis"""
        insights = []
        
        if "organization_performance" in benchmark_data:
            for metric, data in benchmark_data["organization_performance"].items():
                if data["performance_status"] == "above":
                    insights.append(f"Outperforming competitors in {metric.replace('_', ' ')}")
                elif data["performance_status"] == "below":
                    insights.append(f"Underperforming competitors in {metric.replace('_', ' ')}")
        
        if "content_gaps" in content_gaps and content_gaps["content_gaps"]:
            insights.append(f"Missing {len(content_gaps['content_gaps'])} content themes that competitors are using")
        
        return insights
    
    def _generate_recommendations(
        self,
        benchmark_data: Dict[str, Any],
        content_gaps: Dict[str, Any],
        industry_benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if "organization_performance" in benchmark_data:
            for metric, data in benchmark_data["organization_performance"].items():
                if data["performance_status"] == "below":
                    recommendations.append(f"Focus on improving {metric.replace('_', ' ')} to match competitor performance")
        
        if "content_gaps" in content_gaps and content_gaps["content_gaps"]:
            recommendations.append("Develop content strategy around identified content gaps")
        
        recommendations.append("Monitor competitor activity weekly for new opportunities")
        recommendations.append("Set up automated competitive intelligence tracking")
        
        return recommendations
