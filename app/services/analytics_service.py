"""
Analytics Service
Handles analytics queries, data aggregation, and reporting
"""

from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
from sqlalchemy.sql import text
import csv
import io
from fastapi.responses import StreamingResponse

from app.models.publishing import ExternalReference, PublishingStatus, PlatformType
from app.models.analytics import PostMetrics, AnalyticsSummary, AnalyticsExport
from app.models.entities import Organization


class AnalyticsService:
    """Service for analytics queries and data aggregation"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_analytics_summary(
        self,
        org_id: int, 
        days: int = 30,
        platform: Optional[PlatformType] = None,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get analytics summary for the specified period
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze (default 30)
            platform: Optional platform filter
            campaign_id: Optional campaign filter
            
        Returns:
            Dictionary with summary metrics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Base query for external references
        base_query = self.db.query(ExternalReference).filter(
            ExternalReference.organization_id == org_id,
            ExternalReference.created_at >= start_date,
            ExternalReference.created_at <= end_date
        )
        
        if platform:
            base_query = base_query.filter(ExternalReference.platform == platform)
        
        if campaign_id:
            base_query = base_query.filter(
                ExternalReference.platform_data['campaign_id'].astext == campaign_id
            )
        
        # Total posts published
        total_posts = base_query.filter(
            ExternalReference.status == PublishingStatus.PUBLISHED
        ).count()
        
        # Failed posts
        failed_posts = base_query.filter(
            ExternalReference.status == PublishingStatus.FAILED
        ).count()
        
        # Pending posts
        pending_posts = base_query.filter(
            ExternalReference.status == PublishingStatus.PENDING
        ).count()
        
        # Platform breakdown
        platform_breakdown = self.db.query(
            ExternalReference.platform,
            func.count(ExternalReference.id).label('count'),
            func.count(
                func.case(
                    (ExternalReference.status == PublishingStatus.PUBLISHED, 1),
                    else_=None
                )
            ).label('published_count')
        ).filter(
            ExternalReference.organization_id == org_id,
            ExternalReference.created_at >= start_date,
            ExternalReference.created_at <= end_date
        ).group_by(ExternalReference.platform).all()
        
        # Recent activity (last 7 days)
        recent_start = end_date - timedelta(days=7)
        recent_posts = base_query.filter(
            ExternalReference.created_at >= recent_start
        ).count()
        
        # Calculate success rate
        total_attempts = total_posts + failed_posts
        success_rate = (total_posts / total_attempts * 100) if total_attempts > 0 else 0
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "metrics": {
                "total_posts": total_posts,
                "failed_posts": failed_posts,
                "pending_posts": pending_posts,
                "success_rate": round(success_rate, 2),
                "recent_posts": recent_posts
            },
            "platform_breakdown": [
                {
                    "platform": platform.platform.value,
                    "total_count": platform.count,
                    "published_count": platform.published_count,
                    "success_rate": round(
                        (platform.published_count / platform.count * 100) if platform.count > 0 else 0, 2
                    )
                }
                for platform in platform_breakdown
            ]
        }
    
    def get_timeseries_data(
        self,
        org_id: int,
        days: int = 30,
        platform: Optional[PlatformType] = None,
        campaign_id: Optional[str] = None,
        group_by: str = "day"
    ) -> List[Dict[str, Any]]:
        """
        Get timeseries data for charts
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze
            platform: Optional platform filter
            campaign_id: Optional campaign filter
            group_by: Grouping period (day, week, month)
            
        Returns:
            List of timeseries data points
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Determine date truncation based on group_by
        if group_by == "day":
            date_trunc = func.date_trunc('day', ExternalReference.created_at)
        elif group_by == "week":
            date_trunc = func.date_trunc('week', ExternalReference.created_at)
        elif group_by == "month":
            date_trunc = func.date_trunc('month', ExternalReference.created_at)
        else:
            date_trunc = func.date_trunc('day', ExternalReference.created_at)
        
        # Base query
        base_query = self.db.query(
            date_trunc.label('date'),
            ExternalReference.platform,
            func.count(ExternalReference.id).label('total_count'),
            func.count(
                func.case(
                    (ExternalReference.status == PublishingStatus.PUBLISHED, 1),
                    else_=None
                )
            ).label('published_count'),
            func.count(
                func.case(
                    (ExternalReference.status == PublishingStatus.FAILED, 1),
                    else_=None
                )
            ).label('failed_count')
        ).filter(
            ExternalReference.organization_id == org_id,
            ExternalReference.created_at >= start_date,
            ExternalReference.created_at <= end_date
        )
        
        if platform:
            base_query = base_query.filter(ExternalReference.platform == platform)
        
        if campaign_id:
            base_query = base_query.filter(
                ExternalReference.platform_data['campaign_id'].astext == campaign_id
            )
        
        # Group by date and platform
        results = base_query.group_by(
            date_trunc, ExternalReference.platform
        ).order_by(date_trunc).all()
        
        # Format results
        timeseries_data = []
        for result in results:
            timeseries_data.append({
                "date": result.date.isoformat(),
                "platform": result.platform.value,
                "total_count": result.total_count,
                "published_count": result.published_count,
                "failed_count": result.failed_count,
                "success_rate": round(
                    (result.published_count / result.total_count * 100) if result.total_count > 0 else 0, 2
                )
            })
        
        return timeseries_data
    
    def get_platform_comparison(
        self,
        org_id: int,
        days: int = 30,
        campaign_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get platform comparison data for bar charts
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze
            campaign_id: Optional campaign filter
            
        Returns:
            List of platform comparison data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query for platform metrics
        results = self.db.query(
            ExternalReference.platform,
            func.count(ExternalReference.id).label('total_posts'),
            func.count(
                func.case(
                    (ExternalReference.status == PublishingStatus.PUBLISHED, 1),
                    else_=None
                )
            ).label('published_posts'),
            func.count(
                func.case(
                    (ExternalReference.status == PublishingStatus.FAILED, 1),
                    else_=None
                )
            ).label('failed_posts'),
            func.avg(
                func.case(
                    (ExternalReference.status == PublishingStatus.PUBLISHED, 1),
                    else_=0
                )
            ).label('success_rate')
        ).filter(
            ExternalReference.organization_id == org_id,
            ExternalReference.created_at >= start_date,
            ExternalReference.created_at <= end_date
        )
        
        if campaign_id:
            results = results.filter(
                ExternalReference.platform_data['campaign_id'].astext == campaign_id
            )
        
        results = results.group_by(ExternalReference.platform).all()
        
        # Format results
        platform_data = []
        for result in results:
            platform_data.append({
                "platform": result.platform.value,
                "total_posts": result.total_posts,
                "published_posts": result.published_posts,
                "failed_posts": result.failed_posts,
                "success_rate": round(result.success_rate * 100, 2) if result.success_rate else 0
            })
        
        return platform_data
    
    def get_ctr_over_time(
        self,
        org_id: int,
        days: int = 30,
        platform: Optional[PlatformType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get CTR (Click-Through Rate) over time data
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze
            platform: Optional platform filter
            
        Returns:
            List of CTR data points
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query for CTR data (this would typically come from analytics events)
        # For now, we'll simulate CTR data based on post performance
        base_query = self.db.query(
            func.date_trunc('day', ExternalReference.created_at).label('date'),
            ExternalReference.platform,
            func.count(ExternalReference.id).label('total_posts'),
            func.avg(
                func.cast(
                    ExternalReference.platform_data['clicks'].astext, 
                    func.Integer
                )
            ).label('avg_clicks'),
            func.avg(
                func.cast(
                    ExternalReference.platform_data['impressions'].astext, 
                    func.Integer
                )
            ).label('avg_impressions')
        ).filter(
            ExternalReference.organization_id == org_id,
            ExternalReference.created_at >= start_date,
            ExternalReference.created_at <= end_date,
            ExternalReference.status == PublishingStatus.PUBLISHED
        )
        
        if platform:
            base_query = base_query.filter(ExternalReference.platform == platform)
        
        results = base_query.group_by(
            func.date_trunc('day', ExternalReference.created_at),
            ExternalReference.platform
        ).order_by(func.date_trunc('day', ExternalReference.created_at)).all()
        
        # Format results and calculate CTR
        ctr_data = []
        for result in results:
            avg_clicks = result.avg_clicks or 0
            avg_impressions = result.avg_impressions or 0
            ctr = (avg_clicks / avg_impressions * 100) if avg_impressions > 0 else 0
            
            ctr_data.append({
                "date": result.date.isoformat(),
                "platform": result.platform.value,
                "total_posts": result.total_posts,
                "avg_clicks": round(avg_clicks, 2),
                "avg_impressions": round(avg_impressions, 2),
                "ctr": round(ctr, 2)
            })
        
        return ctr_data
    
    def export_analytics_csv(
        self,
        org_id: int,
        days: int = 30,
        platform: Optional[PlatformType] = None,
        campaign_id: Optional[str] = None,
        include_metrics: bool = True
    ) -> StreamingResponse:
        """
        Export analytics data as CSV with streaming response
        
        Args:
            org_id: Organization ID
            days: Number of days to analyze
            platform: Optional platform filter
            campaign_id: Optional campaign filter
            include_metrics: Whether to include detailed metrics
            
        Returns:
            StreamingResponse with CSV data
        """
        def generate_csv():
            # Create CSV in memory
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write headers
            if include_metrics:
                writer.writerow([
                    'Date', 'Platform', 'Post ID', 'Status', 'URL', 'Created At', 
                    'Published At', 'Clicks', 'Impressions', 'CTR', 'Campaign ID'
                ])
            else:
                writer.writerow([
                    'Date', 'Platform', 'Post ID', 'Status', 'URL', 'Created At', 'Published At'
                ])
            
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            
            # Query data in batches
            end_date = datetime.utcnow()
            start_date = end_date - timedelta(days=days)
            
            query = self.db.query(ExternalReference).filter(
                ExternalReference.organization_id == org_id,
                ExternalReference.created_at >= start_date,
                ExternalReference.created_at <= end_date
            )
            
            if platform:
                query = query.filter(ExternalReference.platform == platform)
            
            if campaign_id:
                query = query.filter(
                    ExternalReference.platform_data['campaign_id'].astext == campaign_id
                )
            
            # Process in batches
            batch_size = 1000
            offset = 0
            
            while True:
                batch = query.offset(offset).limit(batch_size).all()
                if not batch:
                    break
                
                for ref in batch:
                    row = [
                        ref.created_at.strftime('%Y-%m-%d'),
                        ref.platform.value,
                        ref.external_id,
                        ref.status.value,
                        ref.url or '',
                        ref.created_at.isoformat(),
                        ref.published_at.isoformat() if ref.published_at else ''
                    ]
                    
                    if include_metrics:
                        platform_data = ref.platform_data or {}
                        clicks = platform_data.get('clicks', 0)
                        impressions = platform_data.get('impressions', 0)
                        ctr = (clicks / impressions * 100) if impressions > 0 else 0
                        campaign_id_val = platform_data.get('campaign_id', '')
                        
                        row.extend([
                            clicks,
                            impressions,
                            round(ctr, 2),
                            campaign_id_val
                        ])
                    
                    writer.writerow(row)
                
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
                offset += batch_size
        
        return StreamingResponse(
            generate_csv(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics_export.csv"}
        )
    
    def get_campaign_analytics(
        self,
        org_id: int,
        campaign_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get analytics for a specific campaign
        
        Args:
            org_id: Organization ID
            campaign_id: Campaign ID
            days: Number of days to analyze
            
        Returns:
            Campaign analytics data
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query campaign data
        campaign_posts = self.db.query(ExternalReference).filter(
            ExternalReference.organization_id == org_id,
            ExternalReference.platform_data['campaign_id'].astext == campaign_id,
            ExternalReference.created_at >= start_date,
            ExternalReference.created_at <= end_date
        ).all()
        
        if not campaign_posts:
            return {
                "campaign_id": campaign_id,
                "error": "Campaign not found or no data available"
            }
        
        # Calculate metrics
        total_posts = len(campaign_posts)
        published_posts = len([p for p in campaign_posts if p.status == PublishingStatus.PUBLISHED])
        failed_posts = len([p for p in campaign_posts if p.status == PublishingStatus.FAILED])
        
        # Platform breakdown
        platform_breakdown = {}
        for post in campaign_posts:
            platform = post.platform.value
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {
                    "total": 0,
                    "published": 0,
                    "failed": 0
                }
            platform_breakdown[platform]["total"] += 1
            if post.status == PublishingStatus.PUBLISHED:
                platform_breakdown[platform]["published"] += 1
            elif post.status == PublishingStatus.FAILED:
                platform_breakdown[platform]["failed"] += 1
        
        return {
            "campaign_id": campaign_id,
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "days": days
            },
            "metrics": {
                "total_posts": total_posts,
                "published_posts": published_posts,
                "failed_posts": failed_posts,
                "success_rate": round((published_posts / total_posts * 100) if total_posts > 0 else 0, 2)
            },
            "platform_breakdown": platform_breakdown
        }
    
    def update_post_metrics(
        self,
        external_reference_id: int,
        platform: str,
        external_id: str,
        metrics_data: Dict[str, Any],
        metric_date: Optional[datetime] = None
    ) -> PostMetrics:
        """
        Update or create post metrics from platform data
        
        Args:
            external_reference_id: External reference ID
            platform: Platform name
            external_id: Platform-specific post ID
            metrics_data: Metrics data from platform
            metric_date: Date the metrics are for (defaults to now)
            
        Returns:
            PostMetrics object
        """
        if metric_date is None:
            metric_date = datetime.utcnow()
        
        # Check if metrics already exist for this post and date
        existing_metrics = self.db.query(PostMetrics).filter(
            PostMetrics.external_reference_id == external_reference_id,
            PostMetrics.platform == platform,
            PostMetrics.external_id == external_id,
            PostMetrics.metric_date == metric_date
        ).first()
        
        if existing_metrics:
            # Update existing metrics
            existing_metrics.impressions = metrics_data.get('impressions', existing_metrics.impressions)
            existing_metrics.reach = metrics_data.get('reach', existing_metrics.reach)
            existing_metrics.clicks = metrics_data.get('clicks', existing_metrics.clicks)
            existing_metrics.engagements = metrics_data.get('engagements', existing_metrics.engagements)
            existing_metrics.likes = metrics_data.get('likes', existing_metrics.likes)
            existing_metrics.comments = metrics_data.get('comments', existing_metrics.comments)
            existing_metrics.shares = metrics_data.get('shares', existing_metrics.shares)
            existing_metrics.saves = metrics_data.get('saves', existing_metrics.saves)
            existing_metrics.conversions = metrics_data.get('conversions', existing_metrics.conversions)
            existing_metrics.video_views = metrics_data.get('video_views', existing_metrics.video_views)
            existing_metrics.data_source = metrics_data.get('data_source', existing_metrics.data_source)
            existing_metrics.is_estimated = metrics_data.get('is_estimated', existing_metrics.is_estimated)
            
            # Recalculate derived metrics
            self._calculate_derived_metrics(existing_metrics)
            
            self.db.commit()
            self.db.refresh(existing_metrics)
            return existing_metrics
        else:
            # Create new metrics
            new_metrics = PostMetrics(
                organization_id=metrics_data.get('organization_id'),
                external_reference_id=external_reference_id,
                platform=platform,
                external_id=external_id,
                impressions=metrics_data.get('impressions', 0),
                reach=metrics_data.get('reach', 0),
                clicks=metrics_data.get('clicks', 0),
                engagements=metrics_data.get('engagements', 0),
                likes=metrics_data.get('likes', 0),
                comments=metrics_data.get('comments', 0),
                shares=metrics_data.get('shares', 0),
                saves=metrics_data.get('saves', 0),
                conversions=metrics_data.get('conversions', 0),
                video_views=metrics_data.get('video_views', 0),
                metric_date=metric_date,
                data_source=metrics_data.get('data_source', 'api'),
                is_estimated=metrics_data.get('is_estimated', False)
            )
            
            # Calculate derived metrics
            self._calculate_derived_metrics(new_metrics)
            
            self.db.add(new_metrics)
            self.db.commit()
            self.db.refresh(new_metrics)
            return new_metrics
    
    def _calculate_derived_metrics(self, metrics: PostMetrics) -> None:
        """Calculate derived metrics like CTR, engagement rate, etc."""
        # Calculate CTR
        if metrics.impressions > 0:
            metrics.ctr = (metrics.clicks / metrics.impressions) * 100
        else:
            metrics.ctr = 0.0
        
        # Calculate engagement rate
        if metrics.reach > 0:
            metrics.engagement_rate = (metrics.engagements / metrics.reach) * 100
        else:
            metrics.engagement_rate = 0.0
        
        # Calculate conversion rate
        if metrics.clicks > 0:
            metrics.conversion_rate = (metrics.conversions / metrics.clicks) * 100
        else:
            metrics.conversion_rate = 0.0
        
        # Calculate video completion rate
        if metrics.video_views > 0 and metrics.impressions > 0:
            metrics.video_completion_rate = (metrics.video_views / metrics.impressions) * 100
        else:
            metrics.video_completion_rate = 0.0
    
    def get_real_time_metrics(
        self,
        org_id: int,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Get real-time metrics for the last N hours
        
        Args:
            org_id: Organization ID
            hours: Number of hours to look back
            
        Returns:
            Real-time metrics data
        """
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get recent post metrics
        recent_metrics = self.db.query(PostMetrics).filter(
            PostMetrics.organization_id == org_id,
            PostMetrics.collected_at >= start_time,
            PostMetrics.collected_at <= end_time
        ).all()
        
        if not recent_metrics:
            return {
                "period_hours": hours,
                "total_posts": 0,
                "total_impressions": 0,
                "total_engagements": 0,
                "avg_engagement_rate": 0.0,
                "platform_breakdown": {},
                "top_performing_posts": []
            }
        
        # Calculate totals
        total_posts = len(recent_metrics)
        total_impressions = sum(m.impressions for m in recent_metrics)
        total_engagements = sum(m.engagements for m in recent_metrics)
        total_clicks = sum(m.clicks for m in recent_metrics)
        total_conversions = sum(m.conversions for m in recent_metrics)
        
        # Calculate averages
        avg_engagement_rate = sum(m.engagement_rate for m in recent_metrics) / total_posts if total_posts > 0 else 0
        avg_ctr = sum(m.ctr for m in recent_metrics) / total_posts if total_posts > 0 else 0
        avg_conversion_rate = sum(m.conversion_rate for m in recent_metrics) / total_posts if total_posts > 0 else 0
        
        # Platform breakdown
        platform_breakdown = {}
        for metric in recent_metrics:
            platform = metric.platform
            if platform not in platform_breakdown:
                platform_breakdown[platform] = {
                    "posts": 0,
                    "impressions": 0,
                    "engagements": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "avg_engagement_rate": 0.0
                }
            
            platform_breakdown[platform]["posts"] += 1
            platform_breakdown[platform]["impressions"] += metric.impressions
            platform_breakdown[platform]["engagements"] += metric.engagements
            platform_breakdown[platform]["clicks"] += metric.clicks
            platform_breakdown[platform]["conversions"] += metric.conversions
        
        # Calculate platform averages
        for platform_data in platform_breakdown.values():
            if platform_data["posts"] > 0:
                platform_data["avg_engagement_rate"] = (
                    platform_data["engagements"] / 
                    (platform_data["impressions"] or 1) * 100
                )
        
        # Top performing posts (by engagement rate)
        top_posts = sorted(
            recent_metrics,
            key=lambda x: x.engagement_rate,
            reverse=True
        )[:5]
        
        top_performing_posts = [
            {
                "platform": post.platform,
                "external_id": post.external_id,
                "engagement_rate": post.engagement_rate,
                "impressions": post.impressions,
                "engagements": post.engagements,
                "ctr": post.ctr
            }
            for post in top_posts
        ]
        
        return {
            "period_hours": hours,
            "total_posts": total_posts,
            "total_impressions": total_impressions,
            "total_engagements": total_engagements,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "avg_engagement_rate": round(avg_engagement_rate, 2),
            "avg_ctr": round(avg_ctr, 2),
            "avg_conversion_rate": round(avg_conversion_rate, 2),
            "platform_breakdown": platform_breakdown,
            "top_performing_posts": top_performing_posts,
            "last_updated": end_time.isoformat()
        }
    
    def generate_analytics_summary(
        self,
        org_id: int,
        period_start: datetime,
        period_end: datetime,
        period_type: str = "daily"
    ) -> AnalyticsSummary:
        """
        Generate analytics summary for a specific period
        
        Args:
            org_id: Organization ID
            period_start: Start of period
            period_end: End of period
            period_type: Type of period (daily, weekly, monthly)
            
        Returns:
            AnalyticsSummary object
        """
        # Get all post metrics for the period
        metrics = self.db.query(PostMetrics).filter(
            PostMetrics.organization_id == org_id,
            PostMetrics.metric_date >= period_start,
            PostMetrics.metric_date <= period_end
        ).all()
        
        if not metrics:
            # Create empty summary
            summary = AnalyticsSummary(
                organization_id=org_id,
                period_start=period_start,
                period_end=period_end,
                period_type=period_type,
                total_impressions=0,
                total_reach=0,
                total_clicks=0,
                total_engagements=0,
                total_conversions=0,
                avg_ctr=0.0,
                avg_engagement_rate=0.0,
                avg_conversion_rate=0.0,
                platform_breakdown={},
                top_content=[]
            )
        else:
            # Calculate aggregated metrics
            total_impressions = sum(m.impressions for m in metrics)
            total_reach = sum(m.reach for m in metrics)
            total_clicks = sum(m.clicks for m in metrics)
            total_engagements = sum(m.engagements for m in metrics)
            total_conversions = sum(m.conversions for m in metrics)
            
            # Calculate averages
            avg_ctr = sum(m.ctr for m in metrics) / len(metrics) if metrics else 0
            avg_engagement_rate = sum(m.engagement_rate for m in metrics) / len(metrics) if metrics else 0
            avg_conversion_rate = sum(m.conversion_rate for m in metrics) / len(metrics) if metrics else 0
            
            # Platform breakdown
            platform_breakdown = {}
            for metric in metrics:
                platform = metric.platform
                if platform not in platform_breakdown:
                    platform_breakdown[platform] = {
                        "impressions": 0,
                        "reach": 0,
                        "clicks": 0,
                        "engagements": 0,
                        "conversions": 0,
                        "posts": 0
                    }
                
                platform_breakdown[platform]["impressions"] += metric.impressions
                platform_breakdown[platform]["reach"] += metric.reach
                platform_breakdown[platform]["clicks"] += metric.clicks
                platform_breakdown[platform]["engagements"] += metric.engagements
                platform_breakdown[platform]["conversions"] += metric.conversions
                platform_breakdown[platform]["posts"] += 1
            
            # Top performing content
            top_content = sorted(
                metrics,
                key=lambda x: x.engagement_rate,
                reverse=True
            )[:10]
            
            top_content_data = [
                {
                    "platform": post.platform,
                    "external_id": post.external_id,
                    "engagement_rate": post.engagement_rate,
                    "impressions": post.impressions,
                    "engagements": post.engagements,
                    "ctr": post.ctr
                }
                for post in top_content
            ]
            
            summary = AnalyticsSummary(
                organization_id=org_id,
                period_start=period_start,
                period_end=period_end,
                period_type=period_type,
                total_impressions=total_impressions,
                total_reach=total_reach,
                total_clicks=total_clicks,
                total_engagements=total_engagements,
                total_conversions=total_conversions,
                avg_ctr=round(avg_ctr, 2),
                avg_engagement_rate=round(avg_engagement_rate, 2),
                avg_conversion_rate=round(avg_conversion_rate, 2),
                platform_breakdown=platform_breakdown,
                top_content=top_content_data
            )
        
        # Save or update summary
        existing_summary = self.db.query(AnalyticsSummary).filter(
            AnalyticsSummary.organization_id == org_id,
            AnalyticsSummary.period_start == period_start,
            AnalyticsSummary.period_end == period_end,
            AnalyticsSummary.period_type == period_type
        ).first()
        
        if existing_summary:
            # Update existing
            for key, value in summary.__dict__.items():
                if not key.startswith('_') and key != 'id':
                    setattr(existing_summary, key, value)
            self.db.commit()
            self.db.refresh(existing_summary)
            return existing_summary
        else:
            # Create new
            self.db.add(summary)
            self.db.commit()
            self.db.refresh(summary)
            return summary