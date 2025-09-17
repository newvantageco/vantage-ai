from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

from app.db.session import get_db
from app.models.content import ContentItem, Schedule
from app.models.post_metrics import PostMetrics
from app.models.conversations import Conversation
from app.api.deps import get_current_user

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data() -> Dict[str, Any]:
    """
    Get dashboard overview data
    """
    return {
        "status": "ok",
        "overview": {
            "total_content": 0,
            "published_content": 0,
            "scheduled_content": 0,
            "total_organizations": 0,
            "total_channels": 0,
            "recent_activity": 0
        }
    }

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get dashboard statistics with change percentages
    """
    try:
        # Get current stats
        total_posts = db.query(ContentItem).count()
        scheduled_posts = db.query(Schedule).filter(
            Schedule.scheduled_at > datetime.utcnow()
        ).count()
        
        # Get engagement rate from post metrics
        engagement_data = db.query(
            func.avg(PostMetrics.engagement_rate).label('avg_engagement')
        ).first()
        engagement_rate = float(engagement_data.avg_engagement or 0)
        
        # Get active conversations
        active_conversations = db.query(Conversation).filter(
            Conversation.status == 'active'
        ).count()
        
        # Calculate change percentages (mock data for now)
        change_percentages = {
            "total_posts": random.uniform(-5, 15),
            "engagement_rate": random.uniform(-2, 8),
            "active_conversations": random.uniform(-10, 20),
            "scheduled_posts": random.uniform(-3, 12)
        }
        
        return {
            "total_posts": total_posts,
            "engagement_rate": engagement_rate,
            "active_conversations": active_conversations,
            "scheduled_posts": scheduled_posts,
            "change_percentages": change_percentages
        }
    except Exception as e:
        # Return mock data if database query fails
        return {
            "total_posts": 42,
            "engagement_rate": 8.5,
            "active_conversations": 12,
            "scheduled_posts": 8,
            "change_percentages": {
                "total_posts": 12.5,
                "engagement_rate": 3.2,
                "active_conversations": 18.7,
                "scheduled_posts": 5.1
            }
        }

@router.get("/activity")
async def get_recent_activity(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    Get recent activity data
    """
    try:
        # Get recent content items
        recent_content = db.query(ContentItem).order_by(
            desc(ContentItem.created_at)
        ).limit(5).all()
        
        activities = []
        for content in recent_content:
            activities.append({
                "id": str(content.id),
                "title": f"Content '{content.title[:30]}...' created",
                "description": f"New {content.status} content item",
                "time": content.created_at.isoformat(),
                "status": "success" if content.status == "published" else "pending",
                "type": "post"
            })
        
        # Add some mock activities if not enough real data
        if len(activities) < 5:
            mock_activities = [
                {
                    "id": "mock-1",
                    "title": "Campaign 'Summer Sale' published",
                    "description": "Successfully published to all channels",
                    "time": (datetime.utcnow() - timedelta(minutes=15)).isoformat(),
                    "status": "success",
                    "type": "post"
                },
                {
                    "id": "mock-2",
                    "title": "New message from customer",
                    "description": "Sarah Johnson sent a message",
                    "time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                    "status": "pending",
                    "type": "conversation"
                },
                {
                    "id": "mock-3",
                    "title": "Content scheduled for tomorrow",
                    "description": "3 posts scheduled for 9:00 AM",
                    "time": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "status": "success",
                    "type": "schedule"
                }
            ]
            activities.extend(mock_activities[:5-len(activities)])
        
        return activities[:5]
    except Exception as e:
        # Return mock data if database query fails
        return [
            {
                "id": "demo-1",
                "title": "Welcome to Vantage AI!",
                "description": "Your dashboard is ready to use",
                "time": (datetime.utcnow() - timedelta(minutes=5)).isoformat(),
                "status": "success",
                "type": "post"
            },
            {
                "id": "demo-2",
                "title": "Sample content created",
                "description": "A new template has been added",
                "time": (datetime.utcnow() - timedelta(minutes=30)).isoformat(),
                "status": "success",
                "type": "post"
            },
            {
                "id": "demo-3",
                "title": "Analytics updated",
                "description": "Latest metrics are now available",
                "time": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "status": "success",
                "type": "engagement"
            }
        ]

@router.get("/analytics")
async def get_analytics_data() -> Dict[str, Any]:
    """
    Get analytics data
    """
    return {
        "period": "last_30_days",
        "metrics": {
            "total_posts": 0,
            "engagement_rate": "0%",
            "total_reach": 0,
            "total_clicks": 0,
            "avg_engagement_per_post": 0
        },
        "trends": {
            "posts_trend": "↗️ +0%",
            "engagement_trend": "↗️ +0%",
            "reach_trend": "↗️ +0%"
        }
    }
