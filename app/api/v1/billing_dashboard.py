"""
Billing Dashboard API
Provides comprehensive billing dashboard and admin interface
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.db.session import get_db
from app.api.deps import get_current_user, get_admin_user, get_current_user_mock
from app.services.billing_analytics import BillingAnalyticsService
from app.services.billing_service import BillingService

router = APIRouter()


class DashboardResponse(BaseModel):
    """Dashboard response model"""
    revenue: Dict[str, Any]
    subscriptions: Dict[str, Any]
    usage: Dict[str, Any]
    customers: Dict[str, Any]
    plans: Dict[str, Any]
    alerts: List[Dict[str, Any]]


class AdminDashboardResponse(BaseModel):
    """Admin dashboard response model"""
    revenue_analytics: Dict[str, Any]
    customer_analytics: Dict[str, Any]
    plan_analytics: Dict[str, Any]
    usage_analytics: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    health_status: Dict[str, Any]


@router.get("/billing/dashboard", response_model=DashboardResponse)
async def get_billing_dashboard(
    months: int = Query(6, ge=1, le=24, description="Number of months to analyze"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Get billing dashboard for organization"""
    try:
        billing_service = BillingService(db)
        analytics_service = BillingAnalyticsService(db)
        
        # Get organization's usage analytics
        usage_analytics = analytics_service.get_usage_analytics(
            org_id=current_user["org_id"],
            months=months
        )
        
        # Get current subscription and plan
        subscription = billing_service.get_organization_subscription(current_user["org_id"])
        plan = billing_service.get_organization_plan(current_user["org_id"])
        
        # Get current usage
        current_usage = billing_service.get_organization_usage(current_user["org_id"])
        
        # Calculate revenue (for this organization)
        revenue_data = {
            "current_month": current_usage.get("overage", {}).get("amount", 0),
            "total_this_year": 0,  # Would need to calculate from invoices
            "trend": "stable"
        }
        
        # Subscription data
        subscription_data = {
            "status": subscription.status.value if subscription else "none",
            "plan": plan.name if plan else "none",
            "next_billing": subscription.current_period_end.isoformat() if subscription else None,
            "can_upgrade": not subscription or (plan and plan.name in ["starter", "growth"]),
            "can_downgrade": subscription and plan and plan.name == "pro"
        }
        
        # Usage data
        usage_data = {
            "current": current_usage,
            "trends": usage_analytics.get("trends", {}),
            "efficiency": usage_analytics.get("efficiency", {})
        }
        
        # Customer data (for this organization)
        customer_data = {
            "plan_limits": current_usage.get("plan_limits", {}),
            "usage_percentage": current_usage.get("usage_percentage", {}),
            "overage": current_usage.get("overage", {})
        }
        
        # Plan data
        plan_data = {
            "current": {
                "name": plan.name if plan else "none",
                "price": plan.price if plan else 0,
                "features": plan.features if plan else []
            },
            "available": []  # Would get from plans endpoint
        }
        
        # Generate alerts
        alerts = []
        
        # Usage alerts
        for key, percentage in current_usage.get("usage_percentage", {}).items():
            if percentage > 90:
                alerts.append({
                    "type": "warning",
                    "message": f"You're using {percentage:.1f}% of your {key} limit",
                    "action": "Consider upgrading your plan"
                })
            elif percentage > 75:
                alerts.append({
                    "type": "info",
                    "message": f"You're using {percentage:.1f}% of your {key} limit",
                    "action": "Monitor your usage"
                })
        
        # Overage alerts
        if current_usage.get("overage", {}).get("amount", 0) > 0:
            alerts.append({
                "type": "error",
                "message": f"You have ${current_usage['overage']['amount']/100:.2f} in overage charges",
                "action": "Review your usage or upgrade your plan"
            })
        
        # Subscription alerts
        if subscription and subscription.status.value == "past_due":
            alerts.append({
                "type": "error",
                "message": "Your subscription payment is past due",
                "action": "Update your payment method"
            })
        
        return DashboardResponse(
            revenue=revenue_data,
            subscriptions=subscription_data,
            usage=usage_data,
            customers=customer_data,
            plans=plan_data,
            alerts=alerts
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing dashboard: {str(e)}"
        )


@router.get("/billing/admin/dashboard", response_model=AdminDashboardResponse)
async def get_admin_billing_dashboard(
    months: int = Query(12, ge=1, le=24, description="Number of months to analyze"),
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_admin_user)
):
    """Get admin billing dashboard with system-wide analytics"""
    try:
        analytics_service = BillingAnalyticsService(db)
        
        # Get comprehensive analytics
        revenue_analytics = analytics_service.get_revenue_analytics(months)
        customer_analytics = analytics_service.get_customer_analytics()
        plan_analytics = analytics_service.get_plan_analytics()
        
        # Get usage analytics for all organizations
        usage_analytics = {
            "total_ai_requests": 0,
            "total_content_posts": 0,
            "total_overage_charges": 0,
            "top_users": []  # Would implement top users by usage
        }
        
        # Generate admin alerts
        alerts = []
        
        # Revenue alerts
        if revenue_analytics.get("revenue", {}).get("mrr", 0) < 1000:
            alerts.append({
                "type": "warning",
                "message": "MRR is below $1000",
                "action": "Focus on customer acquisition"
            })
        
        # Churn alerts
        churn_rate = revenue_analytics.get("subscriptions", {}).get("churn_rate", 0)
        if churn_rate > 5:
            alerts.append({
                "type": "error",
                "message": f"Churn rate is {churn_rate:.1f}%",
                "action": "Investigate customer satisfaction"
            })
        
        # Growth alerts
        growth = revenue_analytics.get("growth", {})
        if growth.get("revenue_growth", 0) < 0:
            alerts.append({
                "type": "warning",
                "message": "Revenue growth is negative",
                "action": "Review pricing and marketing strategy"
            })
        
        # Health status
        health_status = {
            "stripe_connected": True,  # Would check actual Stripe connection
            "database_connected": True,  # Would check database connection
            "webhook_processing": True,  # Would check webhook processing
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return AdminDashboardResponse(
            revenue_analytics=revenue_analytics,
            customer_analytics=customer_analytics,
            plan_analytics=plan_analytics,
            usage_analytics=usage_analytics,
            alerts=alerts,
            health_status=health_status
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get admin billing dashboard: {str(e)}"
        )


@router.get("/billing/dashboard/export")
async def export_billing_data(
    format: str = Query("csv", description="Export format (csv, json)"),
    months: int = Query(6, ge=1, le=24, description="Number of months to export"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Export billing data for the organization"""
    try:
        analytics_service = BillingAnalyticsService(db)
        
        # Get usage analytics
        usage_analytics = analytics_service.get_usage_analytics(
            org_id=current_user["org_id"],
            months=months
        )
        
        if format.lower() == "csv":
            # Generate CSV data
            csv_data = "Month,AI Requests,Content Posts,Overage Charges\n"
            for month, data in usage_analytics.get("usage", {}).get("monthly", {}).items():
                csv_data += f"{month},{data['ai_requests']},{data['content_posts']},{data['overage_charges']}\n"
            
            return {
                "data": csv_data,
                "format": "csv",
                "filename": f"billing_data_{datetime.utcnow().strftime('%Y%m%d')}.csv"
            }
        
        elif format.lower() == "json":
            return {
                "data": usage_analytics,
                "format": "json",
                "filename": f"billing_data_{datetime.utcnow().strftime('%Y%m%d')}.json"
            }
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported format. Use 'csv' or 'json'"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export billing data: {str(e)}"
        )


@router.get("/billing/dashboard/alerts")
async def get_billing_alerts(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user_mock)
):
    """Get billing alerts for the organization"""
    try:
        billing_service = BillingService(db)
        
        # Get current usage and subscription
        current_usage = billing_service.get_organization_usage(current_user["org_id"])
        subscription = billing_service.get_organization_subscription(current_user["org_id"])
        
        alerts = []
        
        # Usage alerts
        for key, percentage in current_usage.get("usage_percentage", {}).items():
            if percentage > 90:
                alerts.append({
                    "type": "warning",
                    "severity": "high",
                    "message": f"You're using {percentage:.1f}% of your {key} limit",
                    "action": "Consider upgrading your plan",
                    "created_at": datetime.utcnow().isoformat()
                })
            elif percentage > 75:
                alerts.append({
                    "type": "info",
                    "severity": "medium",
                    "message": f"You're using {percentage:.1f}% of your {key} limit",
                    "action": "Monitor your usage",
                    "created_at": datetime.utcnow().isoformat()
                })
        
        # Overage alerts
        overage_amount = current_usage.get("overage", {}).get("amount", 0)
        if overage_amount > 0:
            alerts.append({
                "type": "error",
                "severity": "high",
                "message": f"You have ${overage_amount/100:.2f} in overage charges",
                "action": "Review your usage or upgrade your plan",
                "created_at": datetime.utcnow().isoformat()
            })
        
        # Subscription alerts
        if subscription:
            if subscription.status.value == "past_due":
                alerts.append({
                    "type": "error",
                    "severity": "high",
                    "message": "Your subscription payment is past due",
                    "action": "Update your payment method",
                    "created_at": datetime.utcnow().isoformat()
                })
            elif subscription.status.value == "trialing":
                days_left = (subscription.trial_end - datetime.utcnow()).days if subscription.trial_end else 0
                if days_left <= 3:
                    alerts.append({
                        "type": "warning",
                        "severity": "medium",
                        "message": f"Your trial ends in {days_left} days",
                        "action": "Subscribe to continue using the service",
                        "created_at": datetime.utcnow().isoformat()
                    })
        
        return {
            "alerts": alerts,
            "total": len(alerts),
            "unread": len([a for a in alerts if a["severity"] in ["high", "medium"]])
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get billing alerts: {str(e)}"
        )
