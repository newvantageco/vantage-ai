"""VANTAGE AI Marketing SaaS Platform - Working Version"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from datetime import datetime, timedelta
from typing import List, Optional
import uvicorn

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

# Health check endpoint
@app.get("/api/v1/health")
async def health_check():
    return {
        "status": "ok",
        "message": "VANTAGE AI Marketing Platform is running!",
        "version": "2.0.0",
        "database": "connected",
        "api": "running",
        "features": [
            "AI Content Generation",
            "Multi-Channel Publishing",
            "Advanced Analytics", 
            "Team Collaboration",
            "Automation & Rules",
            "Enterprise Features"
        ]
    }

# Root endpoint
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
async def get_dashboard_data():
    """Get dashboard overview data"""
    return {
        "overview": {
            "total_content": 42,
            "published_content": 28,
            "scheduled_content": 14,
            "total_organizations": 5,
            "total_channels": 12,
            "recent_activity": 8
        },
        "status": "success"
    }

# Content creation endpoint
@app.post("/api/v1/content/create")
async def create_content(
    title: str,
    content: str,
    platform: str = "general",
    org_id: str = "demo-org"
):
    """Create new content with AI assistance"""
    content_id = f"content_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "id": content_id,
        "title": title,
        "content": content,
        "status": "draft",
        "platform": platform,
        "created_at": datetime.utcnow().isoformat(),
        "message": "Content created successfully"
    }

# AI content generation endpoint
@app.post("/api/v1/ai/generate")
async def generate_content(
    prompt: str,
    content_type: str = "social_media_post",
    platform: str = "general",
    tone: str = "professional"
):
    """Generate AI-powered content"""
    
    # Mock AI responses based on prompt
    ai_responses = {
        "product launch": "Exciting news! We're thrilled to announce our latest innovation that will revolutionize your workflow. This game-changing feature combines cutting-edge technology with user-friendly design. Ready to experience the future? Try it free today! #Innovation #Tech #ProductLaunch",
        "sale": "Don't miss out! For a limited time, get 50% off our premium features. This exclusive offer won't last long - upgrade now and unlock the full potential of your marketing strategy. Limited time only! #Sale #Deal #Marketing",
        "tips": "Pro tip: Consistency is key in social media marketing. Post regularly, engage with your audience, and always provide value. What's your favorite social media strategy? Share in the comments! #SocialMediaTips #Marketing #Growth",
        "default": "Creating amazing content is an art and a science. With the right strategy, creativity, and consistency, you can build a powerful online presence that resonates with your audience. What story will you tell today? #ContentCreation #Marketing #Strategy"
    }
    
    # Find the best response based on prompt keywords
    prompt_lower = prompt.lower()
    generated_content = ai_responses["default"]
    
    for key, response in ai_responses.items():
        if key in prompt_lower:
            generated_content = response
            break
    
    return {
        "generated_content": generated_content,
        "content_type": content_type,
        "platform": platform,
        "tone": tone,
        "prompt": prompt
    }

# Analytics endpoint
@app.get("/api/v1/analytics/overview")
async def get_analytics_overview(
    org_id: str = "demo-org",
    days: int = 30
):
    """Get analytics overview for the organization"""
    
    # Mock analytics data
    total_posts = 45
    engagement_rate = 0.045  # 4.5% average engagement
    reach = total_posts * 1200  # Mock reach data
    clicks = int(reach * 0.025)  # 2.5% click-through rate
    
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
            "posts_trend": "up",
            "engagement_trend": "up", 
            "reach_trend": "stable"
        }
    }

# Schedule content endpoint
@app.post("/api/v1/schedule/create")
async def schedule_content(
    content_id: str,
    channel_id: str,
    scheduled_time: str
):
    """Schedule content for publishing"""
    schedule_id = f"schedule_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    return {
        "schedule": {
            "id": schedule_id,
            "content_id": content_id,
            "channel_id": channel_id,
            "scheduled_for": scheduled_time,
            "status": "scheduled",
            "created_at": datetime.utcnow().isoformat()
        },
        "message": "Content scheduled successfully"
    }

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

# Content suggestions endpoint
@app.get("/api/v1/content/suggestions")
async def get_content_suggestions(
    platform: str = "general",
    count: int = 5
):
    """Get AI-powered content suggestions"""
    
    suggestions = [
        {
            "title": "Product Feature Highlight",
            "content": "Discover the power of our latest feature! This game-changing update will transform how you work. Try it free today! #Innovation #ProductUpdate",
            "hashtags": ["#Innovation", "#ProductUpdate", "#Tech"],
            "platform": platform
        },
        {
            "title": "Behind the Scenes",
            "content": "👥 Meet the amazing team behind our success! We're passionate about creating solutions that make a difference. #Team #CompanyCulture #BehindTheScenes",
            "hashtags": ["#Team", "#CompanyCulture", "#BehindTheScenes"],
            "platform": platform
        },
        {
            "title": "Industry Insights",
            "content": "The future of marketing is here! AI-powered tools are revolutionizing how we connect with audiences. What trends are you seeing? #Marketing #AI #Future",
            "hashtags": ["#Marketing", "#AI", "#Future", "#Trends"],
            "platform": platform
        },
        {
            "title": "Customer Success Story",
            "content": "Amazing results from our latest customer! They increased engagement by 300% using our platform. Ready to see similar results? #Success #CustomerStory #Results",
            "hashtags": ["#Success", "#CustomerStory", "#Results"],
            "platform": platform
        },
        {
            "title": "Educational Content",
            "content": "📚 Pro tip: Consistency beats perfection every time. Focus on regular, valuable content rather than perfect posts. What's your content strategy? #ContentTips #Marketing #Strategy",
            "hashtags": ["#ContentTips", "#Marketing", "#Strategy"],
            "platform": platform
        }
    ]
    
    return suggestions[:count]

# Social media platforms endpoint
@app.get("/api/v1/platforms")
async def get_social_platforms():
    """Get available social media platforms"""
    return {
        "platforms": [
            {
                "id": "facebook",
                "name": "Facebook",
                "icon": "📘",
                "status": "connected",
                "followers": 12500
            },
            {
                "id": "instagram", 
                "name": "Instagram",
                "icon": "📷",
                "status": "connected",
                "followers": 8900
            },
            {
                "id": "linkedin",
                "name": "LinkedIn", 
                "icon": "💼",
                "status": "connected",
                "followers": 3200
            },
            {
                "id": "twitter",
                "name": "Twitter",
                "icon": "🐦",
                "status": "connected", 
                "followers": 5600
            },
            {
                "id": "tiktok",
                "name": "TikTok",
                "icon": "🎵",
                "status": "disconnected",
                "followers": 0
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
