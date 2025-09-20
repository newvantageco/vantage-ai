"""
Performance Tracking API Router
Handles performance tracking, benchmarking, and goal management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.api.deps import get_db, get_current_user
from app.models.cms import UserAccount
from app.services.performance_tracking import PerformanceTracker, PerformanceMetric

router = APIRouter()


class PerformanceGoal(BaseModel):
    """Schema for performance goals"""
    metric: str
    target_value: float
    deadline: Optional[str] = None
    priority: str = "medium"  # low, medium, high


class PerformanceGoalsRequest(BaseModel):
    """Schema for setting performance goals"""
    goals: List[PerformanceGoal]


@router.get("/performance/summary")
async def get_performance_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platforms: Optional[List[str]] = Query(None, description="Platforms to filter by"),
    metrics: Optional[List[str]] = Query(None, description="Specific metrics to include"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance summary for the specified period.
    """
    try:
        performance_tracker = PerformanceTracker(db)
        
        # Convert string metrics to PerformanceMetric enum if provided
        performance_metrics = None
        if metrics:
            performance_metrics = []
            for metric_str in metrics:
                try:
                    performance_metrics.append(PerformanceMetric(metric_str))
                except ValueError:
                    # Skip invalid metrics
                    continue
        
        summary = performance_tracker.get_performance_summary(
            org_id=current_user.organization_id,
            days=days,
            platforms=platforms,
            metrics=performance_metrics
        )
        
        return summary
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance summary: {str(e)}"
        )


@router.get("/performance/benchmarks")
async def get_performance_benchmarks(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platforms: Optional[List[str]] = Query(None, description="Platforms to filter by"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance benchmarks and comparisons.
    """
    try:
        performance_tracker = PerformanceTracker(db)
        
        benchmarks = performance_tracker.get_performance_benchmarks(
            org_id=current_user.organization_id,
            days=days,
            platforms=platforms
        )
        
        return benchmarks
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance benchmarks: {str(e)}"
        )


@router.post("/performance/goals")
async def set_performance_goals(
    goals_request: PerformanceGoalsRequest,
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Set performance goals for the organization.
    """
    try:
        # Convert goals to dictionary format
        goals_dict = {}
        for goal in goals_request.goals:
            goals_dict[goal.metric] = goal.target_value
        
        performance_tracker = PerformanceTracker(db)
        
        # Track goals
        goal_tracking = performance_tracker.track_performance_goals(
            org_id=current_user.organization_id,
            goals=goals_dict
        )
        
        return {
            "message": "Performance goals set successfully",
            "goals": goals_dict,
            "tracking": goal_tracking
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set performance goals: {str(e)}"
        )


@router.get("/performance/goals/progress")
async def get_goals_progress(
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get progress towards performance goals.
    """
    try:
        # Mock goals for demonstration - in reality you would fetch from database
        mock_goals = {
            "avg_engagement_rate": 0.05,  # 5%
            "avg_ctr": 0.02,  # 2%
            "total_impressions": 10000
        }
        
        performance_tracker = PerformanceTracker(db)
        
        goal_progress = performance_tracker.track_performance_goals(
            org_id=current_user.organization_id,
            goals=mock_goals
        )
        
        return goal_progress
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get goals progress: {str(e)}"
        )


@router.get("/performance/alerts")
async def get_performance_alerts(
    days: int = Query(7, ge=1, le=30, description="Number of days to analyze for alerts"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get performance alerts and anomalies.
    """
    try:
        performance_tracker = PerformanceTracker(db)
        
        alerts = performance_tracker.get_performance_alerts(
            org_id=current_user.organization_id,
            days=days
        )
        
        return alerts
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance alerts: {str(e)}"
        )


@router.get("/performance/trends")
async def get_performance_trends(
    days: int = Query(30, ge=7, le=365, description="Number of days to analyze"),
    platforms: Optional[List[str]] = Query(None, description="Platforms to filter by"),
    metric: str = Query("avg_engagement_rate", description="Metric to analyze trends for"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance trends for a specific metric.
    """
    try:
        performance_tracker = PerformanceTracker(db)
        
        # Get performance summary which includes trends
        performance_data = performance_tracker.get_performance_summary(
            org_id=current_user.organization_id,
            days=days,
            platforms=platforms
        )
        
        trends = performance_data.get("trends", {})
        time_performance = performance_data.get("time_performance", [])
        
        # Extract trend data for the specific metric
        trend_data = []
        for data_point in time_performance:
            if "metrics" in data_point and metric in data_point["metrics"]:
                trend_data.append({
                    "date": data_point["date"],
                    "value": data_point["metrics"][metric]
                })
        
        return {
            "metric": metric,
            "period_days": days,
            "platforms": platforms,
            "trend_direction": trends.get("engagement_trend", "stable"),
            "change_percent": trends.get("engagement_change_percent", 0),
            "trend_data": trend_data,
            "total_data_points": len(trend_data)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance trends: {str(e)}"
        )


@router.get("/performance/top-content")
async def get_top_performing_content(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platforms: Optional[List[str]] = Query(None, description="Platforms to filter by"),
    limit: int = Query(10, ge=1, le=50, description="Number of top posts to return"),
    sort_by: str = Query("engagement_rate", description="Sort by: engagement_rate, impressions, clicks"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get top performing content for the specified period.
    """
    try:
        performance_tracker = PerformanceTracker(db)
        
        performance_data = performance_tracker.get_performance_summary(
            org_id=current_user.organization_id,
            days=days,
            platforms=platforms
        )
        
        top_content = performance_data.get("top_content", [])
        
        # Sort by specified metric if different from default
        if sort_by != "engagement_rate":
            top_content = sorted(top_content, key=lambda x: x.get(sort_by, 0), reverse=True)
        
        return {
            "period_days": days,
            "platforms": platforms,
            "sort_by": sort_by,
            "top_content": top_content[:limit],
            "total_posts_analyzed": performance_data.get("total_posts_analyzed", 0)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get top performing content: {str(e)}"
        )


@router.get("/performance/platform-breakdown")
async def get_platform_performance(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get performance breakdown by platform.
    """
    try:
        performance_tracker = PerformanceTracker(db)
        
        performance_data = performance_tracker.get_performance_summary(
            org_id=current_user.organization_id,
            days=days
        )
        
        platform_performance = performance_data.get("platform_performance", {})
        
        return {
            "period_days": days,
            "platform_performance": platform_performance,
            "total_platforms": len(platform_performance)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get platform performance: {str(e)}"
        )


@router.get("/performance/available-metrics")
async def get_available_metrics() -> List[Dict[str, str]]:
    """
    Get list of available performance metrics.
    """
    metrics = [
        {"key": "impressions", "name": "Impressions", "description": "Total number of impressions"},
        {"key": "reach", "name": "Reach", "description": "Total number of unique users reached"},
        {"key": "clicks", "name": "Clicks", "description": "Total number of clicks"},
        {"key": "engagements", "name": "Engagements", "description": "Total number of engagements"},
        {"key": "likes", "name": "Likes", "description": "Total number of likes"},
        {"key": "comments", "name": "Comments", "description": "Total number of comments"},
        {"key": "shares", "name": "Shares", "description": "Total number of shares"},
        {"key": "saves", "name": "Saves", "description": "Total number of saves"},
        {"key": "conversions", "name": "Conversions", "description": "Total number of conversions"},
        {"key": "video_views", "name": "Video Views", "description": "Total number of video views"},
        {"key": "engagement_rate", "name": "Engagement Rate", "description": "Average engagement rate percentage"},
        {"key": "ctr", "name": "Click-Through Rate", "description": "Average click-through rate percentage"},
        {"key": "conversion_rate", "name": "Conversion Rate", "description": "Average conversion rate percentage"}
    ]
    
    return metrics


@router.get("/performance/score")
async def get_performance_score(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    platforms: Optional[List[str]] = Query(None, description="Platforms to filter by"),
    db: Session = Depends(get_db),
    current_user: UserAccount = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get overall performance score and grade.
    """
    try:
        performance_tracker = PerformanceTracker(db)
        
        benchmarks = performance_tracker.get_performance_benchmarks(
            org_id=current_user.organization_id,
            days=days,
            platforms=platforms
        )
        
        performance_score = benchmarks.get("performance_score", {})
        
        return {
            "period_days": days,
            "platforms": platforms,
            "score": performance_score,
            "analysis_date": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get performance score: {str(e)}"
        )
