"""
Performance Tracking Service
Handles automated performance tracking and metric collection from social media platforms
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
import logging
import asyncio
from enum import Enum

from app.models.analytics import PostMetrics, AnalyticsSummary
from app.models.publishing import ExternalReference, PublishingStatus
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


class PerformanceMetric(Enum):
    """Performance metrics that can be tracked"""
    IMPRESSIONS = "impressions"
    REACH = "reach"
    CLICKS = "clicks"
    ENGAGEMENTS = "engagements"
    LIKES = "likes"
    COMMENTS = "comments"
    SHARES = "shares"
    SAVES = "saves"
    CONVERSIONS = "conversions"
    VIDEO_VIEWS = "video_views"
    ENGAGEMENT_RATE = "engagement_rate"
    CTR = "ctr"
    CONVERSION_RATE = "conversion_rate"


class PerformanceTracker:
    """Service for tracking and analyzing performance metrics"""
    
    def __init__(self, db: Session):
        self.db = db
        self.analytics_service = AnalyticsService(db)
    
    def track_post_performance(
        self,
        external_reference_id: int,
        platform: str,
        external_id: str,
        metrics_data: Dict[str, Any]
    ) -> PostMetrics:
        """
        Track performance metrics for a specific post
        
        Args:
            external_reference_id: External reference ID
            platform: Platform name
            external_id: Platform-specific post ID
            metrics_data: Metrics data from platform
            
        Returns:
            PostMetrics object
        """
        try:
            # Update metrics using analytics service
            post_metrics = self.analytics_service.update_post_metrics(
                external_reference_id=external_reference_id,
                platform=platform,
                external_id=external_id,
                metrics_data=metrics_data
            )
            
            # Track performance trends
            self._track_performance_trends(external_reference_id, post_metrics)
            
            logger.info(f"Tracked performance for {platform} post {external_id}")
            return post_metrics
            
        except Exception as e:
            logger.error(f"Error tracking post performance: {e}")
            raise
    
    def get_performance_summary(
        self,
        org_id: int,
        days: int = 30,
        platforms: Optional[List[str]] = None,
        metrics: Optional[List[PerformanceMetric]] = None
    ) -> Dict[str, Any]:
        """
        Get performance summary for the specified period
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze
            platforms: Optional platform filter
            metrics: Optional metrics to include
            
        Returns:
            Performance summary data
        """
        try:
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            # Base query
            query = self.db.query(PostMetrics).filter(
                PostMetrics.organization_id == org_id,
                PostMetrics.metric_date >= start_date,
                PostMetrics.metric_date <= end_date
            )
            
            if platforms:
                query = query.filter(PostMetrics.platform.in_(platforms))
            
            all_metrics = query.all()
            
            if not all_metrics:
                return self._empty_performance_summary(org_id, start_date, end_date)
            
            # Calculate performance summary
            summary = self._calculate_performance_summary(all_metrics, metrics)
            
            # Calculate trends
            trends = self._calculate_performance_trends(org_id, start_date, end_date, platforms)
            
            # Get top performing content
            top_content = self._get_top_performing_content(all_metrics, limit=10)
            
            # Get performance by platform
            platform_performance = self._get_platform_performance(all_metrics)
            
            # Get performance by time period
            time_performance = self._get_time_performance(all_metrics, group_by="day")
            
            return {
                "organization_id": org_id,
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "days": days
                },
                "summary": summary,
                "trends": trends,
                "top_content": top_content,
                "platform_performance": platform_performance,
                "time_performance": time_performance,
                "total_posts_analyzed": len(all_metrics)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance summary: {e}")
            raise
    
    def get_performance_benchmarks(
        self,
        org_id: int,
        days: int = 30,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get performance benchmarks and comparisons
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze
            platforms: Optional platform filter
            
        Returns:
            Performance benchmarks data
        """
        try:
            # Get current performance
            current_performance = self.get_performance_summary(org_id, days, platforms)
            
            # Get historical performance for comparison
            historical_days = min(days * 2, 90)  # Compare with previous period
            historical_performance = self.get_performance_summary(
                org_id, historical_days, platforms
            )
            
            # Calculate benchmarks
            benchmarks = self._calculate_benchmarks(current_performance, historical_performance)
            
            # Get industry benchmarks (mock data)
            industry_benchmarks = self._get_industry_benchmarks(platforms)
            
            return {
                "current_performance": current_performance,
                "historical_comparison": benchmarks,
                "industry_benchmarks": industry_benchmarks,
                "performance_score": self._calculate_performance_score(current_performance),
                "recommendations": self._generate_performance_recommendations(current_performance, benchmarks)
            }
            
        except Exception as e:
            logger.error(f"Error getting performance benchmarks: {e}")
            raise
    
    def track_performance_goals(
        self,
        org_id: int,
        goals: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Track performance against defined goals
        
        Args:
            org_id: Organization ID
            goals: Performance goals configuration
            
        Returns:
            Goals tracking data
        """
        try:
            # Get current performance
            current_performance = self.get_performance_summary(org_id, 30)
            
            # Calculate goal progress
            goal_progress = self._calculate_goal_progress(current_performance, goals)
            
            return {
                "goals": goals,
                "current_performance": current_performance["summary"],
                "goal_progress": goal_progress,
                "overall_progress": self._calculate_overall_progress(goal_progress),
                "next_milestones": self._get_next_milestones(goal_progress, goals)
            }
            
        except Exception as e:
            logger.error(f"Error tracking performance goals: {e}")
            raise
    
    def get_performance_alerts(
        self,
        org_id: int,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Get performance alerts and anomalies
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze
            
        Returns:
            List of performance alerts
        """
        try:
            alerts = []
            
            # Get recent performance
            recent_performance = self.get_performance_summary(org_id, days)
            
            # Check for performance drops
            if days >= 7:
                previous_performance = self.get_performance_summary(org_id, days * 2)
                performance_drop_alerts = self._check_performance_drops(
                    recent_performance, previous_performance
                )
                alerts.extend(performance_drop_alerts)
            
            # Check for unusual patterns
            anomaly_alerts = self._check_performance_anomalies(recent_performance)
            alerts.extend(anomaly_alerts)
            
            # Check for goal deviations
            goal_alerts = self._check_goal_deviations(org_id, recent_performance)
            alerts.extend(goal_alerts)
            
            return sorted(alerts, key=lambda x: x["severity"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting performance alerts: {e}")
            raise
    
    def _track_performance_trends(self, external_reference_id: int, post_metrics: PostMetrics):
        """Track performance trends for a post"""
        try:
            # In a real implementation, you would update trend tracking tables
            # For now, we'll just log the tracking
            logger.debug(f"Tracking trends for post {external_reference_id}")
            
        except Exception as e:
            logger.error(f"Error tracking performance trends: {e}")
    
    def _calculate_performance_summary(
        self,
        metrics: List[PostMetrics],
        requested_metrics: Optional[List[PerformanceMetric]] = None
    ) -> Dict[str, Any]:
        """Calculate performance summary from metrics"""
        if not metrics:
            return {}
        
        summary = {
            "total_posts": len(metrics),
            "total_impressions": sum(m.impressions for m in metrics),
            "total_reach": sum(m.reach for m in metrics),
            "total_clicks": sum(m.clicks for m in metrics),
            "total_engagements": sum(m.engagements for m in metrics),
            "total_conversions": sum(m.conversions for m in metrics),
            "avg_engagement_rate": sum(m.engagement_rate for m in metrics) / len(metrics),
            "avg_ctr": sum(m.ctr for m in metrics) / len(metrics),
            "avg_conversion_rate": sum(m.conversion_rate for m in metrics) / len(metrics),
            "best_performing_post": max(metrics, key=lambda x: x.engagement_rate).external_id if metrics else None,
            "worst_performing_post": min(metrics, key=lambda x: x.engagement_rate).external_id if metrics else None
        }
        
        # Filter by requested metrics if specified
        if requested_metrics:
            filtered_summary = {}
            for metric in requested_metrics:
                key = metric.value
                if key in summary:
                    filtered_summary[key] = round(summary[key], 2)
            return filtered_summary
        
        return {k: round(v, 2) if isinstance(v, float) else v for k, v in summary.items()}
    
    def _calculate_performance_trends(
        self,
        org_id: int,
        start_date: datetime,
        end_date: datetime,
        platforms: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Calculate performance trends"""
        try:
            # Get daily performance data
            daily_data = []
            current_date = start_date
            
            while current_date <= end_date:
                day_end = current_date + timedelta(days=1)
                
                query = self.db.query(PostMetrics).filter(
                    PostMetrics.organization_id == org_id,
                    PostMetrics.metric_date >= current_date,
                    PostMetrics.metric_date < day_end
                )
                
                if platforms:
                    query = query.filter(PostMetrics.platform.in_(platforms))
                
                day_metrics = query.all()
                
                if day_metrics:
                    day_summary = self._calculate_performance_summary(day_metrics)
                    daily_data.append({
                        "date": current_date.isoformat(),
                        "metrics": day_summary
                    })
                
                current_date += timedelta(days=1)
            
            # Calculate trends
            if len(daily_data) >= 2:
                first_half = daily_data[:len(daily_data)//2]
                second_half = daily_data[len(daily_data)//2:]
                
                first_avg_engagement = sum(d["metrics"]["avg_engagement_rate"] for d in first_half) / len(first_half)
                second_avg_engagement = sum(d["metrics"]["avg_engagement_rate"] for d in second_half) / len(second_half)
                
                engagement_trend = "up" if second_avg_engagement > first_avg_engagement else "down"
                engagement_change = ((second_avg_engagement - first_avg_engagement) / first_avg_engagement * 100) if first_avg_engagement > 0 else 0
            else:
                engagement_trend = "stable"
                engagement_change = 0
            
            return {
                "engagement_trend": engagement_trend,
                "engagement_change_percent": round(engagement_change, 2),
                "daily_data": daily_data,
                "trend_period": f"{start_date.isoformat()} to {end_date.isoformat()}"
            }
            
        except Exception as e:
            logger.error(f"Error calculating performance trends: {e}")
            return {"engagement_trend": "stable", "engagement_change_percent": 0, "daily_data": []}
    
    def _get_top_performing_content(self, metrics: List[PostMetrics], limit: int = 10) -> List[Dict[str, Any]]:
        """Get top performing content"""
        if not metrics:
            return []
        
        top_metrics = sorted(metrics, key=lambda x: x.engagement_rate, reverse=True)[:limit]
        
        return [
            {
                "platform": post.platform,
                "external_id": post.external_id,
                "engagement_rate": round(post.engagement_rate, 2),
                "impressions": post.impressions,
                "engagements": post.engagements,
                "ctr": round(post.ctr, 2),
                "metric_date": post.metric_date.isoformat()
            }
            for post in top_metrics
        ]
    
    def _get_platform_performance(self, metrics: List[PostMetrics]) -> Dict[str, Any]:
        """Get performance breakdown by platform"""
        if not metrics:
            return {}
        
        platform_data = {}
        for metric in metrics:
            platform = metric.platform
            if platform not in platform_data:
                platform_data[platform] = {
                    "posts": 0,
                    "total_impressions": 0,
                    "total_engagements": 0,
                    "avg_engagement_rate": 0
                }
            
            platform_data[platform]["posts"] += 1
            platform_data[platform]["total_impressions"] += metric.impressions
            platform_data[platform]["total_engagements"] += metric.engagements
        
        # Calculate averages
        for platform, data in platform_data.items():
            if data["posts"] > 0:
                data["avg_engagement_rate"] = round(
                    (data["total_engagements"] / data["total_impressions"] * 100) if data["total_impressions"] > 0 else 0, 2
                )
        
        return platform_data
    
    def _get_time_performance(self, metrics: List[PostMetrics], group_by: str = "day") -> List[Dict[str, Any]]:
        """Get performance by time period"""
        if not metrics:
            return []
        
        # Group metrics by time period
        grouped_data = {}
        for metric in metrics:
            if group_by == "day":
                date_key = metric.metric_date.date()
            elif group_by == "week":
                date_key = metric.metric_date.date() - timedelta(days=metric.metric_date.weekday())
            elif group_by == "month":
                date_key = metric.metric_date.date().replace(day=1)
            else:
                date_key = metric.metric_date.date()
            
            if date_key not in grouped_data:
                grouped_data[date_key] = []
            grouped_data[date_key].append(metric)
        
        # Calculate performance for each period
        time_performance = []
        for date_key, period_metrics in grouped_data.items():
            period_summary = self._calculate_performance_summary(period_metrics)
            time_performance.append({
                "date": date_key.isoformat(),
                "metrics": period_summary
            })
        
        return sorted(time_performance, key=lambda x: x["date"])
    
    def _calculate_benchmarks(
        self,
        current_performance: Dict[str, Any],
        historical_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate performance benchmarks"""
        current_summary = current_performance.get("summary", {})
        historical_summary = historical_performance.get("summary", {})
        
        benchmarks = {}
        for metric in ["avg_engagement_rate", "avg_ctr", "avg_conversion_rate"]:
            current_value = current_summary.get(metric, 0)
            historical_value = historical_summary.get(metric, 0)
            
            if historical_value > 0:
                change_percent = ((current_value - historical_value) / historical_value) * 100
                benchmarks[metric] = {
                    "current": current_value,
                    "historical": historical_value,
                    "change_percent": round(change_percent, 2),
                    "trend": "up" if change_percent > 0 else "down" if change_percent < 0 else "stable"
                }
            else:
                benchmarks[metric] = {
                    "current": current_value,
                    "historical": 0,
                    "change_percent": 0,
                    "trend": "stable"
                }
        
        return benchmarks
    
    def _get_industry_benchmarks(self, platforms: Optional[List[str]] = None) -> Dict[str, Any]:
        """Get industry benchmarks (mock data)"""
        # Mock industry benchmarks
        industry_benchmarks = {
            "avg_engagement_rate": 0.05,  # 5%
            "avg_ctr": 0.02,  # 2%
            "avg_conversion_rate": 0.01,  # 1%
            "avg_posts_per_week": 3.5,
            "avg_impressions_per_post": 2000
        }
        
        return industry_benchmarks
    
    def _calculate_performance_score(self, performance: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall performance score"""
        summary = performance.get("summary", {})
        
        # Calculate score based on key metrics
        engagement_rate = summary.get("avg_engagement_rate", 0)
        ctr = summary.get("avg_ctr", 0)
        conversion_rate = summary.get("avg_conversion_rate", 0)
        
        # Normalize scores (0-100 scale)
        engagement_score = min(100, max(0, engagement_rate * 10))  # 10% engagement = 100 points
        ctr_score = min(100, max(0, ctr * 25))  # 4% CTR = 100 points
        conversion_score = min(100, max(0, conversion_rate * 100))  # 1% conversion = 100 points
        
        overall_score = (engagement_score + ctr_score + conversion_score) / 3
        
        return {
            "overall_score": round(overall_score, 1),
            "engagement_score": round(engagement_score, 1),
            "ctr_score": round(ctr_score, 1),
            "conversion_score": round(conversion_score, 1),
            "grade": self._get_performance_grade(overall_score)
        }
    
    def _get_performance_grade(self, score: float) -> str:
        """Get performance grade based on score"""
        if score >= 90:
            return "A+"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        elif score >= 50:
            return "D"
        else:
            return "F"
    
    def _generate_performance_recommendations(
        self,
        performance: Dict[str, Any],
        benchmarks: Dict[str, Any]
    ) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        summary = performance.get("summary", {})
        
        engagement_rate = summary.get("avg_engagement_rate", 0)
        ctr = summary.get("avg_ctr", 0)
        conversion_rate = summary.get("avg_conversion_rate", 0)
        
        if engagement_rate < 0.03:  # 3%
            recommendations.append("Focus on creating more engaging content to improve engagement rates")
        
        if ctr < 0.01:  # 1%
            recommendations.append("Optimize call-to-action buttons and headlines to improve click-through rates")
        
        if conversion_rate < 0.005:  # 0.5%
            recommendations.append("Improve landing page experience and targeting to boost conversion rates")
        
        # Check trends
        for metric, data in benchmarks.items():
            if data["trend"] == "down":
                recommendations.append(f"Address declining {metric.replace('_', ' ')} performance")
        
        if not recommendations:
            recommendations.append("Continue current strategy - performance is on track")
        
        return recommendations
    
    def _empty_performance_summary(self, org_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Return empty performance summary when no data is available"""
        return {
            "organization_id": org_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "summary": {},
            "trends": {"engagement_trend": "stable", "engagement_change_percent": 0, "daily_data": []},
            "top_content": [],
            "platform_performance": {},
            "time_performance": [],
            "total_posts_analyzed": 0
        }
    
    def _calculate_goal_progress(self, performance: Dict[str, Any], goals: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate progress towards goals"""
        summary = performance.get("summary", {})
        goal_progress = {}
        
        for goal_name, target_value in goals.items():
            current_value = summary.get(goal_name, 0)
            progress_percent = (current_value / target_value * 100) if target_value > 0 else 0
            
            goal_progress[goal_name] = {
                "target": target_value,
                "current": current_value,
                "progress_percent": round(progress_percent, 2),
                "status": "achieved" if progress_percent >= 100 else "in_progress" if progress_percent >= 50 else "needs_attention"
            }
        
        return goal_progress
    
    def _calculate_overall_progress(self, goal_progress: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall progress across all goals"""
        if not goal_progress:
            return {"overall_progress": 0, "goals_achieved": 0, "total_goals": 0}
        
        total_progress = sum(goal["progress_percent"] for goal in goal_progress.values())
        overall_progress = total_progress / len(goal_progress)
        
        goals_achieved = sum(1 for goal in goal_progress.values() if goal["status"] == "achieved")
        
        return {
            "overall_progress": round(overall_progress, 2),
            "goals_achieved": goals_achieved,
            "total_goals": len(goal_progress),
            "completion_rate": round((goals_achieved / len(goal_progress)) * 100, 2)
        }
    
    def _get_next_milestones(self, goal_progress: Dict[str, Any], goals: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get next milestones to achieve"""
        milestones = []
        
        for goal_name, progress in goal_progress.items():
            if progress["status"] != "achieved":
                remaining = progress["target"] - progress["current"]
                milestones.append({
                    "goal": goal_name,
                    "remaining": remaining,
                    "progress_percent": progress["progress_percent"]
                })
        
        return sorted(milestones, key=lambda x: x["progress_percent"], reverse=True)
    
    def _check_performance_drops(
        self,
        recent_performance: Dict[str, Any],
        previous_performance: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Check for significant performance drops"""
        alerts = []
        
        recent_summary = recent_performance.get("summary", {})
        previous_summary = previous_performance.get("summary", {})
        
        for metric in ["avg_engagement_rate", "avg_ctr", "avg_conversion_rate"]:
            recent_value = recent_summary.get(metric, 0)
            previous_value = previous_summary.get(metric, 0)
            
            if previous_value > 0:
                drop_percent = ((previous_value - recent_value) / previous_value) * 100
                
                if drop_percent > 20:  # 20% drop threshold
                    alerts.append({
                        "type": "performance_drop",
                        "metric": metric,
                        "severity": "high" if drop_percent > 50 else "medium",
                        "message": f"{metric.replace('_', ' ').title()} dropped by {round(drop_percent, 1)}%",
                        "recent_value": recent_value,
                        "previous_value": previous_value,
                        "drop_percent": round(drop_percent, 1)
                    })
        
        return alerts
    
    def _check_performance_anomalies(self, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for performance anomalies"""
        alerts = []
        summary = performance.get("summary", {})
        
        # Check for unusually high or low metrics
        engagement_rate = summary.get("avg_engagement_rate", 0)
        if engagement_rate > 0.2:  # 20% engagement rate is unusually high
            alerts.append({
                "type": "anomaly",
                "metric": "avg_engagement_rate",
                "severity": "low",
                "message": "Unusually high engagement rate detected",
                "value": engagement_rate
            })
        elif engagement_rate < 0.001:  # 0.1% engagement rate is unusually low
            alerts.append({
                "type": "anomaly",
                "metric": "avg_engagement_rate",
                "severity": "high",
                "message": "Unusually low engagement rate detected",
                "value": engagement_rate
            })
        
        return alerts
    
    def _check_goal_deviations(self, org_id: int, performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for goal deviations"""
        # In a real implementation, you would fetch actual goals from the database
        # For now, return empty list
        return []
