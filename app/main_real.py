"""VANTAGE AI Marketing SaaS Platform - Main Application"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn

# Import all the actual API routes
from app.api.v1 import health, content, schedule, ai, analytics, reports, content_plan
from app.routes import insights, rules, inbox
from app.db.session import get_db
from app.models.content import ContentItem, ContentStatus, Campaign, BrandGuide
from app.models.entities import Organization, Channel
from app.models.analytics import ScheduleMetrics
from app.services.model_router import ai_router
from app.ai.safety import validate_caption

# Create FastAPI app
app = FastAPI(
    title="VANTAGE AI Marketing Platform",
    description="AI-Powered Content Management and Social Media Automation Platform",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all API routes
app.include_router(health.router, prefix="/api/v1")
app.include_router(content.router, prefix="/api/v1")
app.include_router(schedule.router, prefix="/api/v1")
app.include_router(ai.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
app.include_router(content_plan.router, prefix="/api/v1")
app.include_router(insights.router, prefix="/api/v1")
app.include_router(rules.router, prefix="/api/v1")
app.include_router(inbox.router, prefix="/api/v1")

# Root endpoint with platform overview
@app.get("/")
async def root():
    return {
        "name": "VANTAGE AI Marketing Platform",
        "version": "2.0.0",
        "description": "AI-Powered Content Management and Social Media Automation",
        "features": [
            "AI Content Generation",
            "Multi-Channel Publishing", 
            "Advanced Analytics",
            "Team Collaboration",
            "Automation & Rules",
            "Enterprise Features"
        ],
        "docs": "/docs",
        "health": "/api/v1/health"
    }

# Dashboard data endpoint
@app.get("/api/v1/dashboard")
async def get_dashboard_data(db: Session = Depends(get_db)):
    """Get dashboard overview data"""
    try:
        # Get content statistics
        total_content = db.query(ContentItem).count()
        published_content = db.query(ContentItem).filter(ContentItem.status == ContentStatus.published).count()
        scheduled_content = db.query(ContentItem).filter(ContentItem.status == ContentStatus.scheduled).count()
        
        # Get organization count
        total_orgs = db.query(Organization).count()
        
        # Get channel count
        total_channels = db.query(Channel).count()
        
        # Get recent activity (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_content = db.query(ContentItem).filter(ContentItem.created_at >= week_ago).count()
        
        return {
            "overview": {
                "total_content": total_content,
                "published_content": published_content,
                "scheduled_content": scheduled_content,
                "total_organizations": total_orgs,
                "total_channels": total_channels,
                "recent_activity": recent_content
            },
            "status": "success"
        }
    except Exception as e:
        return {
            "overview": {
                "total_content": 0,
                "published_content": 0,
                "scheduled_content": 0,
                "total_organizations": 0,
                "total_channels": 0,
                "recent_activity": 0
            },
            "status": "error",
            "message": str(e)
        }

# Content creation endpoint
@app.post("/api/v1/content/create")
async def create_content(
    title: str,
    content: str,
    platform: str = "general",
    org_id: str = "demo-org",
    db: Session = Depends(get_db)
):
    """Create new content with AI assistance"""
    try:
        # Validate content safety
        validation = validate_caption(content)
        if not validation.is_safe:
            raise HTTPException(
                status_code=400,
                detail=f"Content validation failed: {validation.reason}"
            )
        
        # Create content item
        content_item = ContentItem(
            id=f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            org_id=org_id,
            title=title,
            content=content,
            status=ContentStatus.draft,
            platform=platform,
            created_at=datetime.utcnow()
        )
        
        db.add(content_item)
        db.commit()
        
        return {
            "id": content_item.id,
            "title": content_item.title,
            "content": content_item.content,
            "status": content_item.status.value,
            "platform": content_item.platform,
            "created_at": content_item.created_at.isoformat(),
            "message": "Content created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# AI content generation endpoint
@app.post("/api/v1/ai/generate")
async def generate_content(
    prompt: str,
    content_type: str = "social_media_post",
    platform: str = "general",
    tone: str = "professional"
):
    """Generate AI-powered content"""
    try:
        # Use the AI router to generate content
        system_prompt = f"""
        You are a professional social media content creator. 
        Create engaging {content_type} content for {platform} platform.
        Tone: {tone}
        Keep it concise, engaging, and platform-appropriate.
        """
        
        response = await ai_router.complete(
            prompt=prompt,
            system=system_prompt,
            max_tokens=500
        )
        
        return {
            "generated_content": response.text,
            "content_type": content_type,
            "platform": platform,
            "tone": tone,
            "prompt": prompt
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI generation failed: {str(e)}")

# Analytics endpoint
@app.get("/api/v1/analytics/overview")
async def get_analytics_overview(
    org_id: str = "demo-org",
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Get analytics overview for the organization"""
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get content performance data
        content_items = db.query(ContentItem).filter(
            ContentItem.org_id == org_id,
            ContentItem.created_at >= start_date
        ).all()
        
        # Mock analytics data (in real app, this would come from actual metrics)
        total_posts = len(content_items)
        engagement_rate = 0.045  # 4.5% average engagement
        reach = total_posts * 1000  # Mock reach data
        clicks = int(reach * 0.02)  # 2% click-through rate
        
        return {
            "period": f"Last {days} days",
            "metrics": {
                "total_posts": total_posts,
                "engagement_rate": f"{engagement_rate:.1%}",
                "total_reach": reach,
                "total_clicks": clicks,
                "avg_engagement_per_post": round(engagement_rate * reach / total_posts) if total_posts > 0 else 0
            },
            "trends": {
                "posts_trend": "up",  # up, down, stable
                "engagement_trend": "up",
                "reach_trend": "stable"
            }
        }
    except Exception as e:
        return {
            "period": f"Last {days} days",
            "metrics": {
                "total_posts": 0,
                "engagement_rate": "0%",
                "total_reach": 0,
                "total_clicks": 0,
                "avg_engagement_per_post": 0
            },
            "trends": {
                "posts_trend": "stable",
                "engagement_trend": "stable", 
                "reach_trend": "stable"
            },
            "error": str(e)
        }

# Schedule content endpoint
@app.post("/api/v1/schedule/create")
async def schedule_content(
    content_id: str,
    channel_id: str,
    scheduled_time: str,  # ISO format datetime
    db: Session = Depends(get_db)
):
    """Schedule content for publishing"""
    try:
        # Parse scheduled time
        scheduled_datetime = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
        
        # Create schedule (simplified - in real app would use Schedule model)
        schedule_data = {
            "id": f"schedule_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
            "content_id": content_id,
            "channel_id": channel_id,
            "scheduled_for": scheduled_datetime.isoformat(),
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        }
        
        return {
            "schedule": schedule_data,
            "message": "Content scheduled successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scheduling failed: {str(e)}")

# Team collaboration endpoint
@app.get("/api/v1/team/collaborators")
async def get_team_collaborators(org_id: str = "demo-org"):
    """Get team collaborators for the organization"""
    return {
        "organization_id": org_id,
        "collaborators": [
            {
                "id": "user_1",
                "name": "John Doe",
                "email": "john@example.com",
                "role": "Content Manager",
                "permissions": ["create", "edit", "schedule", "publish"]
            },
            {
                "id": "user_2", 
                "name": "Jane Smith",
                "email": "jane@example.com",
                "role": "Social Media Specialist",
                "permissions": ["create", "edit", "schedule"]
            },
            {
                "id": "user_3",
                "name": "Mike Johnson", 
                "email": "mike@example.com",
                "role": "Analytics Manager",
                "permissions": ["view", "analytics"]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
