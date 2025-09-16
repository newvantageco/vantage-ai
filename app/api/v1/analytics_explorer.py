from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, asc, and_, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import json

from app.db.session import get_db
from app.models.content import Schedule, ContentItem
from app.models.post_metrics import PostMetrics
from app.models.entities import Channel, Organization
from app.core.security import get_current_user
from pydantic import BaseModel

router = APIRouter()


class AnalyticsQuery(BaseModel):
    groupby: str  # channel, format, timeslot, campaign, etc.
    metric: str  # engagement_rate, impressions, clicks, etc.
    period: str  # 7d, 30d, 90d, 1y
    filters: Optional[Dict[str, Any]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class AnalyticsResponse(BaseModel):
    data: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    query: Dict[str, Any]


@router.get("/explorer/metrics", response_model=AnalyticsResponse)
async def get_analytics_metrics(
    groupby: str = Query(..., description="Group by field"),
    metric: str = Query(..., description="Metric to calculate"),
    period: str = Query("30d", description="Time period"),
    filters: Optional[str] = Query(None, description="JSON filters"),
    date_from: Optional[str] = Query(None, description="Start date (ISO format)"),
    date_to: Optional[str] = Query(None, description="End date (ISO format)"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Get aggregated analytics metrics."""
    
    # Parse filters
    filter_dict = {}
    if filters:
        try:
            filter_dict = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid filters JSON"
            )
    
    # Calculate date range
    end_date = datetime.utcnow()
    if date_to:
        try:
            end_date = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format"
            )
    
    if date_from:
        try:
            start_date = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format"
            )
    else:
        # Calculate start date based on period
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid period. Must be one of: 7d, 30d, 90d, 1y"
            )
    
    # Build base query
    query = db.query(
        Schedule,
        PostMetrics,
        Channel,
        ContentItem
    ).join(
        PostMetrics, Schedule.id == PostMetrics.schedule_id, isouter=True
    ).join(
        Channel, Schedule.channel_id == Channel.id
    ).join(
        ContentItem, Schedule.content_item_id == ContentItem.id
    ).filter(
        Schedule.org_id == current_user["org_id"],
        Schedule.scheduled_at >= start_date,
        Schedule.scheduled_at <= end_date
    )
    
    # Apply filters
    if "channel_id" in filter_dict:
        query = query.filter(Schedule.channel_id == filter_dict["channel_id"])
    
    if "status" in filter_dict:
        query = query.filter(Schedule.status == filter_dict["status"])
    
    if "platform" in filter_dict:
        query = query.filter(Channel.provider == filter_dict["platform"])
    
    # Get data based on groupby
    if groupby == "channel":
        data = await get_channel_metrics(query, metric, db)
    elif groupby == "format":
        data = await get_format_metrics(query, metric, db)
    elif groupby == "timeslot":
        data = await get_timeslot_metrics(query, metric, start_date, end_date, db)
    elif groupby == "campaign":
        data = await get_campaign_metrics(query, metric, db)
    elif groupby == "platform":
        data = await get_platform_metrics(query, metric, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid groupby. Must be one of: channel, format, timeslot, campaign, platform"
        )
    
    # Calculate metadata
    total_records = len(data)
    total_value = sum(item.get("value", 0) for item in data)
    avg_value = total_value / total_records if total_records > 0 else 0
    
    return AnalyticsResponse(
        data=data,
        metadata={
            "total_records": total_records,
            "total_value": total_value,
            "avg_value": avg_value,
            "period": period,
            "date_from": start_date.isoformat(),
            "date_to": end_date.isoformat(),
            "groupby": groupby,
            "metric": metric
        },
        query={
            "groupby": groupby,
            "metric": metric,
            "period": period,
            "filters": filter_dict
        }
    )


async def get_channel_metrics(query, metric: str, db: Session) -> List[Dict[str, Any]]:
    """Get metrics grouped by channel."""
    results = query.group_by(Channel.id, Channel.provider, Channel.account_ref).all()
    
    data = []
    for result in results:
        schedule, metrics, channel, content = result
        
        if not metrics:
            continue
        
        # Calculate metric value
        value = calculate_metric_value(metrics, metric)
        
        data.append({
            "group": f"{channel.provider} - {channel.account_ref or 'Unknown'}",
            "channel_id": channel.id,
            "provider": channel.provider,
            "account_ref": channel.account_ref,
            "value": value,
            "posts_count": 1
        })
    
    return data


async def get_format_metrics(query, metric: str, db: Session) -> List[Dict[str, Any]]:
    """Get metrics grouped by content format."""
    results = query.group_by(ContentItem.asset_type).all()
    
    data = []
    format_counts = {}
    
    for result in results:
        schedule, metrics, channel, content = result
        
        if not metrics:
            continue
        
        format_type = getattr(content, 'asset_type', 'unknown')
        if format_type not in format_counts:
            format_counts[format_type] = {"value": 0, "count": 0}
        
        value = calculate_metric_value(metrics, metric)
        format_counts[format_type]["value"] += value
        format_counts[format_type]["count"] += 1
    
    for format_type, stats in format_counts.items():
        data.append({
            "group": format_type.title(),
            "format": format_type,
            "value": stats["value"],
            "posts_count": stats["count"]
        })
    
    return data


async def get_timeslot_metrics(query, metric: str, start_date: datetime, end_date: datetime, db: Session) -> List[Dict[str, Any]]:
    """Get metrics grouped by time slot."""
    results = query.all()
    
    # Group by hour of day
    hourly_data = {}
    
    for result in results:
        schedule, metrics, channel, content = result
        
        if not metrics or not schedule.scheduled_at:
            continue
        
        hour = schedule.scheduled_at.hour
        if hour not in hourly_data:
            hourly_data[hour] = {"value": 0, "count": 0}
        
        value = calculate_metric_value(metrics, metric)
        hourly_data[hour]["value"] += value
        hourly_data[hour]["count"] += 1
    
    data = []
    for hour in range(24):
        stats = hourly_data.get(hour, {"value": 0, "count": 0})
        data.append({
            "group": f"{hour:02d}:00",
            "hour": hour,
            "value": stats["value"],
            "posts_count": stats["count"]
        })
    
    return data


async def get_campaign_metrics(query, metric: str, db: Session) -> List[Dict[str, Any]]:
    """Get metrics grouped by campaign."""
    results = query.group_by(ContentItem.campaign_id).all()
    
    data = []
    campaign_counts = {}
    
    for result in results:
        schedule, metrics, channel, content = result
        
        if not metrics:
            continue
        
        campaign_id = getattr(content, 'campaign_id', 'no_campaign')
        if campaign_id not in campaign_counts:
            campaign_counts[campaign_id] = {"value": 0, "count": 0}
        
        value = calculate_metric_value(metrics, metric)
        campaign_counts[campaign_id]["value"] += value
        campaign_counts[campaign_id]["count"] += 1
    
    for campaign_id, stats in campaign_counts.items():
        data.append({
            "group": campaign_id if campaign_id != 'no_campaign' else 'No Campaign',
            "campaign_id": campaign_id,
            "value": stats["value"],
            "posts_count": stats["count"]
        })
    
    return data


async def get_platform_metrics(query, metric: str, db: Session) -> List[Dict[str, Any]]:
    """Get metrics grouped by platform."""
    results = query.group_by(Channel.provider).all()
    
    data = []
    platform_counts = {}
    
    for result in results:
        schedule, metrics, channel, content = result
        
        if not metrics:
            continue
        
        platform = channel.provider
        if platform not in platform_counts:
            platform_counts[platform] = {"value": 0, "count": 0}
        
        value = calculate_metric_value(metrics, metric)
        platform_counts[platform]["value"] += value
        platform_counts[platform]["count"] += 1
    
    for platform, stats in platform_counts.items():
        data.append({
            "group": platform.title(),
            "platform": platform,
            "value": stats["value"],
            "posts_count": stats["count"]
        })
    
    return data


def calculate_metric_value(metrics: PostMetrics, metric: str) -> float:
    """Calculate the value for a specific metric."""
    if metric == "engagement_rate":
        total_engagement = (metrics.likes or 0) + (metrics.comments or 0) + (metrics.shares or 0)
        impressions = metrics.impressions or 0
        return (total_engagement / impressions * 100) if impressions > 0 else 0
    
    elif metric == "impressions":
        return metrics.impressions or 0
    
    elif metric == "reach":
        return metrics.reach or 0
    
    elif metric == "likes":
        return metrics.likes or 0
    
    elif metric == "comments":
        return metrics.comments or 0
    
    elif metric == "shares":
        return metrics.shares or 0
    
    elif metric == "clicks":
        return metrics.clicks or 0
    
    elif metric == "video_views":
        return metrics.video_views or 0
    
    elif metric == "saves":
        return metrics.saves or 0
    
    elif metric == "total_engagement":
        return (metrics.likes or 0) + (metrics.comments or 0) + (metrics.shares or 0)
    
    elif metric == "ctr":
        clicks = metrics.clicks or 0
        impressions = metrics.impressions or 0
        return (clicks / impressions * 100) if impressions > 0 else 0
    
    else:
        return 0


@router.get("/explorer/available-metrics")
async def get_available_metrics():
    """Get list of available metrics."""
    return {
        "metrics": [
            {"id": "engagement_rate", "name": "Engagement Rate", "description": "Percentage of impressions that resulted in engagement"},
            {"id": "impressions", "name": "Impressions", "description": "Number of times content was displayed"},
            {"id": "reach", "name": "Reach", "description": "Number of unique users who saw the content"},
            {"id": "likes", "name": "Likes", "description": "Number of likes received"},
            {"id": "comments", "name": "Comments", "description": "Number of comments received"},
            {"id": "shares", "name": "Shares", "description": "Number of shares received"},
            {"id": "clicks", "name": "Clicks", "description": "Number of clicks received"},
            {"id": "video_views", "name": "Video Views", "description": "Number of video views"},
            {"id": "saves", "name": "Saves", "description": "Number of saves (Instagram)"},
            {"id": "total_engagement", "name": "Total Engagement", "description": "Sum of likes, comments, and shares"},
            {"id": "ctr", "name": "Click-Through Rate", "description": "Percentage of impressions that resulted in clicks"}
        ],
        "groupby_options": [
            {"id": "channel", "name": "Channel", "description": "Group by social media channel"},
            {"id": "format", "name": "Content Format", "description": "Group by content type"},
            {"id": "timeslot", "name": "Time Slot", "description": "Group by hour of day"},
            {"id": "campaign", "name": "Campaign", "description": "Group by marketing campaign"},
            {"id": "platform", "name": "Platform", "description": "Group by social media platform"}
        ],
        "periods": [
            {"id": "7d", "name": "Last 7 days"},
            {"id": "30d", "name": "Last 30 days"},
            {"id": "90d", "name": "Last 90 days"},
            {"id": "1y", "name": "Last year"}
        ]
    }
