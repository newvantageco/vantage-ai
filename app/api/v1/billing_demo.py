"""
Billing Demo API
Provides mock billing data for demonstration without database dependency
"""

from fastapi import APIRouter
from typing import Dict, Any
from datetime import datetime, timedelta

router = APIRouter()


@router.get("/billing/demo/status")
async def get_demo_billing_status():
    """Get mock billing status for demonstration"""
    return {
        "has_subscription": True,
        "plan": {
            "id": 1,
            "name": "growth",
            "display_name": "Growth Plan",
            "description": "Perfect for growing businesses",
            "price": 7900,  # $79.00
            "currency": "USD",
            "billing_interval": "month",
            "features": [
                "AI Content Generation",
                "Advanced Analytics", 
                "Team Collaboration",
                "Content Scheduling",
                "Multi-platform Publishing"
            ],
            "limits": {
                "ai_requests": 1000,
                "ai_tokens": 100000,
                "content_posts": 200,
                "team_members": 10,
                "integrations": 5
            }
        },
        "subscription": {
            "id": 1,
            "status": "active",
            "current_period_start": (datetime.utcnow() - timedelta(days=15)).isoformat(),
            "current_period_end": (datetime.utcnow() + timedelta(days=15)).isoformat(),
            "canceled_at": None
        },
        "usage": {
            "month": datetime.utcnow().strftime("%Y-%m"),
            "ai_requests": 450,
            "content_posts": 85,
            "team_members": 3,
            "integrations": 2,
            "plan_limits": {
                "ai_requests": 1000,
                "ai_tokens": 100000,
                "content_posts": 200,
                "team_members": 10,
                "integrations": 5
            },
            "usage_percentage": {
                "ai_requests": 45.0,
                "content_posts": 42.5,
                "team_members": 30.0,
                "integrations": 40.0
            },
            "overage": {
                "posts": 0,
                "ai_requests": 0,
                "amount": 0
            }
        },
        "can_upgrade": True,
        "can_downgrade": False
    }


@router.get("/billing/demo/dashboard")
async def get_demo_dashboard():
    """Get mock billing dashboard data"""
    return {
        "revenue": {
            "current_month": 7900,
            "total_this_year": 94800,
            "trend": "increasing"
        },
        "subscriptions": {
            "status": "active",
            "plan": "growth",
            "next_billing": (datetime.utcnow() + timedelta(days=15)).isoformat(),
            "can_upgrade": True,
            "can_downgrade": False
        },
        "usage": {
            "current": {
                "month": datetime.utcnow().strftime("%Y-%m"),
                "ai_requests": 450,
                "content_posts": 85,
                "team_members": 3,
                "integrations": 2,
                "plan_limits": {
                    "ai_requests": 1000,
                    "ai_tokens": 100000,
                    "content_posts": 200,
                    "team_members": 10,
                    "integrations": 5
                },
                "usage_percentage": {
                    "ai_requests": 45.0,
                    "content_posts": 42.5,
                    "team_members": 30.0,
                    "integrations": 40.0
                },
                "overage": {
                    "posts": 0,
                    "ai_requests": 0,
                    "amount": 0
                }
            },
            "trends": {
                "ai_requests": "increasing",
                "content_posts": "stable"
            },
            "efficiency": {
                "ai_requests": {
                    "used": 450,
                    "limit": 1000,
                    "percentage": 45.0,
                    "efficiency": "medium"
                },
                "content_posts": {
                    "used": 85,
                    "limit": 200,
                    "percentage": 42.5,
                    "efficiency": "medium"
                }
            }
        },
        "customers": {
            "plan_limits": {
                "ai_requests": 1000,
                "ai_tokens": 100000,
                "content_posts": 200,
                "team_members": 10,
                "integrations": 5
            },
            "usage_percentage": {
                "ai_requests": 45.0,
                "content_posts": 42.5,
                "team_members": 30.0,
                "integrations": 40.0
            },
            "overage": {
                "posts": 0,
                "ai_requests": 0,
                "amount": 0
            }
        },
        "plans": {
            "current": {
                "name": "growth",
                "price": 7900,
                "features": [
                    "AI Content Generation",
                    "Advanced Analytics", 
                    "Team Collaboration",
                    "Content Scheduling",
                    "Multi-platform Publishing"
                ]
            },
            "available": []
        },
        "alerts": [
            {
                "type": "info",
                "message": "You're using 45% of your AI requests limit",
                "action": "Monitor your usage"
            }
        ]
    }


@router.get("/billing/demo/alerts")
async def get_demo_alerts():
    """Get mock billing alerts"""
    return {
        "alerts": [
            {
                "type": "info",
                "severity": "medium",
                "message": "You're using 45% of your AI requests limit",
                "action": "Monitor your usage",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "type": "success",
                "severity": "low",
                "message": "Your subscription is active and up to date",
                "action": "Continue using the service",
                "created_at": datetime.utcnow().isoformat()
            }
        ],
        "total": 2,
        "unread": 1
    }


@router.get("/billing/demo/analytics")
async def get_demo_analytics():
    """Get mock billing analytics"""
    return {
        "months": ["2024-07", "2024-08", "2024-09", "2024-10", "2024-11", "2024-12"],
        "total_usage": {
            "ai_requests": 2700,
            "content_posts": 510,
            "overage_charges": 0
        },
        "trends": {
            "ai_requests": [300, 350, 400, 450, 500, 450],
            "content_posts": [60, 70, 80, 85, 90, 85],
            "overage_charges": [0, 0, 0, 0, 0, 0]
        }
    }
