"""
Analytics API Router
Handles metrics collection, reporting, and data export
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import csv
import io

from app.api.deps import get_db, get_current_user
from app.schemas.analytics import (
    AnalyticsSummaryResponse, TimeseriesResponse, 
    PostMetricsResponse, AnalyticsExportResponse,
    AnalyticsExportCreate, PlatformBreakdownResponse
)
from app.models.analytics import PostMetrics, AnalyticsSummary, AnalyticsExport
from app.models.cms import UserAccount
from app.services.analytics_service import AnalyticsService
from app.workers.tasks.analytics_tasks import collect_platform_metrics_task, generate_analytics_export_task

router = APIRouter()


@router.get("/analytics/summary", response_model=AnalyticsSummaryResponse)
async def get_analytics_summary(
    range: str = Query("last_30d", description="Time range: last_7d, last_30d, last_90d, custom"),
    start_date: Optional[datetime] = Query(None, description="Start date for custom range"),
    end_date: Optional[datetime] = Query(None, description="End date for custom range"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> AnalyticsSummaryResponse:
    """
    Get analytics summary for the specified time range.
    """
    try:
        # Calculate date range
        end_date = end_date or datetime.utcnow()
        if range == "last_7d":
            start_date = end_date - timedelta(days=7)
        elif range == "last_30d":
            start_date = end_date - timedelta(days=30)
        elif range == "last_90d":
            start_date = end_date - timedelta(days=90)
        elif range == "custom":
            if not start_date:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="start_date is required for custom range"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid range. Use: last_7d, last_30d, last_90d, custom"
            )
        
        # Build query
        query = db.query(PostMetrics).filter(
            PostMetrics.organization_id == current_user.organization_id,
            PostMetrics.metric_date >= start_date,
            PostMetrics.metric_date <= end_date
        )
        
        if platform:
            query = query.filter(PostMetrics.platform == platform)
        
        # Get aggregated metrics
        metrics = query.all()
        
        # Calculate totals
        total_impressions = sum(m.impressions for m in metrics)
        total_reach = sum(m.reach for m in metrics)
        total_clicks = sum(m.clicks for m in metrics)
        total_engagements = sum(m.engagements for m in metrics)
        total_conversions = sum(m.conversions for m in metrics)
        
        # Calculate averages
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_engagement_rate = (total_engagements / total_impressions * 100) if total_impressions > 0 else 0
        avg_conversion_rate = (total_conversions / total_impressions * 100) if total_impressions > 0 else 0
        
        # Platform breakdown
        platform_breakdown = {}
        for metric in metrics:
            if metric.platform not in platform_breakdown:
                platform_breakdown[metric.platform] = {
                    "impressions": 0,
                    "reach": 0,
                    "clicks": 0,
                    "engagements": 0,
                    "conversions": 0
                }
            platform_breakdown[metric.platform]["impressions"] += metric.impressions
            platform_breakdown[metric.platform]["reach"] += metric.reach
            platform_breakdown[metric.platform]["clicks"] += metric.clicks
            platform_breakdown[metric.platform]["engagements"] += metric.engagements
            platform_breakdown[metric.platform]["conversions"] += metric.conversions
        
        return AnalyticsSummaryResponse(
            period_start=start_date,
            period_end=end_date,
            total_impressions=total_impressions,
            total_reach=total_reach,
            total_clicks=total_clicks,
            total_engagements=total_engagements,
            total_conversions=total_conversions,
            avg_ctr=round(avg_ctr, 2),
            avg_engagement_rate=round(avg_engagement_rate, 2),
            avg_conversion_rate=round(avg_conversion_rate, 2),
            platform_breakdown=platform_breakdown
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics summary failed: {str(e)}"
        )


@router.get("/analytics/timeseries", response_model=TimeseriesResponse)
async def get_analytics_timeseries(
    metric: str = Query("impressions", description="Metric to analyze"),
    group_by: str = Query("platform", description="Group by: platform, day, week, month"),
    from_date: datetime = Query(..., description="Start date"),
    to_date: datetime = Query(..., description="End date"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> TimeseriesResponse:
    """
    Get time series analytics data.
    """
    try:
        # Validate metric
        valid_metrics = ["impressions", "reach", "clicks", "engagements", "conversions", "ctr", "engagement_rate"]
        if metric not in valid_metrics:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid metric. Use: {', '.join(valid_metrics)}"
            )
        
        # Build query
        query = db.query(PostMetrics).filter(
            PostMetrics.organization_id == current_user.organization_id,
            PostMetrics.metric_date >= from_date,
            PostMetrics.metric_date <= to_date
        )
        
        if platform:
            query = query.filter(PostMetrics.platform == platform)
        
        # Group by time period
        if group_by == "day":
            query = query.group_by(
                func.date(PostMetrics.metric_date),
                PostMetrics.platform
            )
        elif group_by == "week":
            query = query.group_by(
                func.date_trunc('week', PostMetrics.metric_date),
                PostMetrics.platform
            )
        elif group_by == "month":
            query = query.group_by(
                func.date_trunc('month', PostMetrics.metric_date),
                PostMetrics.platform
            )
        else:  # platform
            query = query.group_by(PostMetrics.platform)
        
        # Get metrics
        if metric == "impressions":
            query = query.with_entities(
                PostMetrics.platform,
                PostMetrics.metric_date,
                func.sum(PostMetrics.impressions).label('value')
            )
        elif metric == "reach":
            query = query.with_entities(
                PostMetrics.platform,
                PostMetrics.metric_date,
                func.sum(PostMetrics.reach).label('value')
            )
        elif metric == "clicks":
            query = query.with_entities(
                PostMetrics.platform,
                PostMetrics.metric_date,
                func.sum(PostMetrics.clicks).label('value')
            )
        elif metric == "engagements":
            query = query.with_entities(
                PostMetrics.platform,
                PostMetrics.metric_date,
                func.sum(PostMetrics.engagements).label('value')
            )
        elif metric == "conversions":
            query = query.with_entities(
                PostMetrics.platform,
                PostMetrics.metric_date,
                func.sum(PostMetrics.conversions).label('value')
            )
        elif metric == "ctr":
            query = query.with_entities(
                PostMetrics.platform,
                PostMetrics.metric_date,
                func.avg(PostMetrics.ctr).label('value')
            )
        elif metric == "engagement_rate":
            query = query.with_entities(
                PostMetrics.platform,
                PostMetrics.metric_date,
                func.avg(PostMetrics.engagement_rate).label('value')
            )
        
        results = query.all()
        
        # Format data
        data = []
        for result in results:
            data.append({
                "platform": result.platform,
                "date": result.metric_date.isoformat() if result.metric_date else None,
                "value": float(result.value) if result.value else 0
            })
        
        return TimeseriesResponse(
            metric=metric,
            group_by=group_by,
            data=data,
            from_date=from_date,
            to_date=to_date
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics timeseries failed: {str(e)}"
        )


@router.get("/analytics/posts", response_model=List[PostMetricsResponse])
async def get_post_metrics(
    skip: int = 0,
    limit: int = 20,
    platform: Optional[str] = Query(None, description="Filter by platform"),
    from_date: Optional[datetime] = Query(None, description="Start date"),
    to_date: Optional[datetime] = Query(None, description="End date"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[PostMetricsResponse]:
    """
    Get post-level metrics.
    """
    query = db.query(PostMetrics).filter(
        PostMetrics.organization_id == current_user.organization_id
    )
    
    if platform:
        query = query.filter(PostMetrics.platform == platform)
    if from_date:
        query = query.filter(PostMetrics.metric_date >= from_date)
    if to_date:
        query = query.filter(PostMetrics.metric_date <= to_date)
    
    metrics = query.offset(skip).limit(limit).all()
    return [PostMetricsResponse.from_orm(metric) for metric in metrics]


@router.post("/analytics/export", response_model=AnalyticsExportResponse)
async def create_analytics_export(
    export_request: AnalyticsExportCreate,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> AnalyticsExportResponse:
    """
    Create an analytics export.
    """
    try:
        # Create export record
        export = AnalyticsExport(
            organization_id=current_user.organization_id,
            user_id=current_user.id,
            export_type=export_request.export_type,
            date_range_start=export_request.date_range_start,
            date_range_end=export_request.date_range_end,
            platforms=export_request.platforms,
            metrics=export_request.metrics,
            status="pending"
        )
        
        db.add(export)
        db.commit()
        db.refresh(export)
        
        # Queue export task
        task = generate_analytics_export_task.delay(
            export_id=export.id,
            organization_id=current_user.organization_id,
            export_type=export_request.export_type,
            date_range_start=export_request.date_range_start,
            date_range_end=export_request.date_range_end,
            platforms=export_request.platforms,
            metrics=export_request.metrics
        )
        
        return AnalyticsExportResponse.from_orm(export)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analytics export creation failed: {str(e)}"
        )


@router.get("/analytics/realtime")
async def get_realtime_analytics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get real-time analytics metrics for the last N hours.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        realtime_data = analytics_service.get_real_time_metrics(
            org_id=current_user.organization_id,
            hours=hours
        )
        
        return realtime_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get real-time analytics: {str(e)}"
        )


@router.post("/analytics/collect-metrics")
async def trigger_metrics_collection(
    platform: Optional[str] = Query(None, description="Platform to collect metrics for"),
    days: int = Query(7, ge=1, le=30, description="Number of days to collect metrics for"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Trigger metrics collection for a specific platform or all platforms.
    """
    try:
        from datetime import datetime, timedelta
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        if platform:
            # Collect metrics for specific platform
            task = collect_platform_metrics_task.delay(
                platform=platform,
                organization_id=current_user.organization_id,
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat()
            )
            
            return {
                "message": f"Metrics collection started for {platform}",
                "task_id": task.id,
                "platform": platform,
                "date_range": f"{start_date.isoformat()} to {end_date.isoformat()}"
            }
        else:
            # Collect metrics for all platforms
            from app.models.publishing import ExternalReference
            from sqlalchemy import distinct
            
            platforms = db.query(distinct(ExternalReference.platform)).filter(
                ExternalReference.organization_id == current_user.organization_id
            ).all()
            
            task_ids = []
            for platform_tuple in platforms:
                platform_name = platform_tuple[0]
                task = collect_platform_metrics_task.delay(
                    platform=platform_name,
                    organization_id=current_user.organization_id,
                    start_date=start_date.isoformat(),
                    end_date=end_date.isoformat()
                )
                task_ids.append(task.id)
            
            return {
                "message": f"Metrics collection started for all platforms",
                "task_ids": task_ids,
                "platforms": [p[0] for p in platforms],
                "date_range": f"{start_date.isoformat()} to {end_date.isoformat()}"
            }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger metrics collection: {str(e)}"
        )


@router.get("/analytics/performance-trends")
async def get_performance_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    metric: str = Query("engagement_rate", description="Metric to analyze: engagement_rate, ctr, impressions"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance trends for the specified metric.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        # Get timeseries data
        timeseries_data = analytics_service.get_timeseries_data(
            org_id=current_user.organization_id,
            days=days,
            platform=platform,
            group_by="day"
        )
        
        # Extract trend data for the specified metric
        trend_data = []
        for data_point in timeseries_data:
            if metric == "engagement_rate":
                value = data_point.get("avg_engagement_rate", 0)
            elif metric == "ctr":
                value = data_point.get("avg_ctr", 0)
            elif metric == "impressions":
                value = data_point.get("total_impressions", 0)
            else:
                value = 0
            
            trend_data.append({
                "date": data_point["date"],
                "platform": data_point["platform"],
                "value": value
            })
        
        # Calculate trend direction
        if len(trend_data) >= 2:
            recent_avg = sum(d["value"] for d in trend_data[-7:]) / min(7, len(trend_data))
            older_avg = sum(d["value"] for d in trend_data[:-7]) / max(1, len(trend_data) - 7)
            trend_direction = "up" if recent_avg > older_avg else "down" if recent_avg < older_avg else "stable"
            trend_percentage = ((recent_avg - older_avg) / older_avg * 100) if older_avg > 0 else 0
        else:
            trend_direction = "stable"
            trend_percentage = 0
        
        return {
            "metric": metric,
            "days": days,
            "platform": platform,
            "trend_data": trend_data,
            "trend_direction": trend_direction,
            "trend_percentage": round(trend_percentage, 2),
            "total_data_points": len(trend_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance trends: {str(e)}"
        )


@router.get("/analytics/top-content")
async def get_top_content(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    limit: int = Query(10, ge=1, le=50, description="Number of top posts to return"),
    sort_by: str = Query("engagement_rate", description="Sort by: engagement_rate, impressions, clicks"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get top performing content for the specified period.
    """
    try:
        analytics_service = AnalyticsService(db)
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Query for top content
        query = db.query(PostMetrics).filter(
            PostMetrics.organization_id == current_user.organization_id,
            PostMetrics.metric_date >= start_date,
            PostMetrics.metric_date <= end_date
        )
        
        if platform:
            query = query.filter(PostMetrics.platform == platform)
        
        # Sort by specified metric
        if sort_by == "engagement_rate":
            query = query.order_by(PostMetrics.engagement_rate.desc())
        elif sort_by == "impressions":
            query = query.order_by(PostMetrics.impressions.desc())
        elif sort_by == "clicks":
            query = query.order_by(PostMetrics.clicks.desc())
        else:
            query = query.order_by(PostMetrics.engagement_rate.desc())
        
        top_posts = query.limit(limit).all()
        
        # Format results
        top_content = []
        for post in top_posts:
            top_content.append({
                "platform": post.platform,
                "external_id": post.external_id,
                "engagement_rate": post.engagement_rate,
                "impressions": post.impressions,
                "reach": post.reach,
                "clicks": post.clicks,
                "engagements": post.engagements,
                "likes": post.likes,
                "comments": post.comments,
                "shares": post.shares,
                "ctr": post.ctr,
                "conversion_rate": post.conversion_rate,
                "metric_date": post.metric_date.isoformat(),
                "data_source": post.data_source,
                "is_estimated": post.is_estimated
            })
        
        return {
            "period_days": days,
            "platform": platform,
            "sort_by": sort_by,
            "top_content": top_content,
            "total_posts_analyzed": len(top_posts)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top content: {str(e)}"
        )


@router.get("/analytics/export/{export_id}", response_model=AnalyticsExportResponse)
async def get_analytics_export(
    export_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> AnalyticsExportResponse:
    """
    Get analytics export status and download URL.
    """
    export = db.query(AnalyticsExport).filter(
        AnalyticsExport.id == export_id,
        AnalyticsExport.organization_id == current_user.organization_id
    ).first()
    
    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found"
        )
    
    return AnalyticsExportResponse.from_orm(export)


@router.get("/analytics/export/{export_id}/download")
async def download_analytics_export(
    export_id: int,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Download analytics export file.
    """
    export = db.query(AnalyticsExport).filter(
        AnalyticsExport.id == export_id,
        AnalyticsExport.organization_id == current_user.organization_id
    ).first()
    
    if not export:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export not found"
        )
    
    if export.status != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Export not ready for download"
        )
    
    if not export.file_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Export file not available"
        )
    
    # FIXME: Implement actual file download logic
    # For now, return a placeholder response
    return {"message": "Export download not implemented yet", "file_url": export.file_url}


@router.get("/analytics/export.csv")
async def export_analytics_csv(
    from_date: datetime = Query(..., description="Start date"),
    to_date: datetime = Query(..., description="End date"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Export analytics data as CSV.
    """
    try:
        # Build query
        query = db.query(PostMetrics).filter(
            PostMetrics.organization_id == current_user.organization_id,
            PostMetrics.metric_date >= from_date,
            PostMetrics.metric_date <= to_date
        )
        
        if platform:
            query = query.filter(PostMetrics.platform == platform)
        
        metrics = query.all()
        
        # Create CSV
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            "Date", "Platform", "External ID", "Impressions", "Reach", "Clicks",
            "CTR", "Engagements", "Engagement Rate", "Conversions", "Conversion Rate"
        ])
        
        # Write data
        for metric in metrics:
            writer.writerow([
                metric.metric_date.strftime("%Y-%m-%d"),
                metric.platform,
                metric.external_id,
                metric.impressions,
                metric.reach,
                metric.clicks,
                metric.ctr,
                metric.engagements,
                metric.engagement_rate,
                metric.conversions,
                metric.conversion_rate
            ])
        
        output.seek(0)
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=analytics_export.csv"}
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CSV export failed: {str(e)}"
        )


@router.post("/analytics/collect", status_code=status.HTTP_202_ACCEPTED)
async def trigger_metrics_collection(
    platform: str = Query(..., description="Platform to collect metrics from"),
    start_date: datetime = Query(..., description="Start date for metrics collection"),
    end_date: datetime = Query(..., description="End date for metrics collection"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
):
    """
    Trigger metrics collection for a specific platform.
    """
    try:
        # Queue metrics collection task
        task = collect_platform_metrics_task.delay(
            platform=platform,
            organization_id=current_user.organization_id,
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat()
        )
        
        return {
            "message": "Metrics collection started",
            "task_id": task.id,
            "platform": platform,
            "date_range": f"{start_date.date()} to {end_date.date()}"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Metrics collection failed: {str(e)}"
        )
