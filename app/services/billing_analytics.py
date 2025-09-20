"""
Billing Analytics Service
Provides comprehensive analytics and reporting for billing data
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
import logging

from app.models.billing import (
    Subscription, Plan, UsageRecord, BillingEvent, 
    Invoice, OrganizationBilling, BillingHistory
)
from app.models.entities import Organization

logger = logging.getLogger(__name__)


class BillingAnalyticsService:
    """Service for billing analytics and reporting"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_revenue_analytics(self, months: int = 12) -> Dict[str, Any]:
        """
        Get revenue analytics for the specified period
        
        Args:
            months: Number of months to analyze
            
        Returns:
            Dictionary with revenue analytics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30 * months)
        
        # Get all paid invoices in the period
        paid_invoices = self.db.query(Invoice).filter(
            and_(
                Invoice.paid == True,
                Invoice.paid_at >= start_date,
                Invoice.paid_at <= end_date
            )
        ).all()
        
        # Calculate monthly revenue
        monthly_revenue = {}
        total_revenue = 0
        
        for invoice in paid_invoices:
            month_key = invoice.paid_at.strftime("%Y-%m")
            if month_key not in monthly_revenue:
                monthly_revenue[month_key] = 0
            monthly_revenue[month_key] += invoice.amount_paid
            total_revenue += invoice.amount_paid
        
        # Get subscription analytics
        active_subscriptions = self.db.query(Subscription).filter(
            Subscription.status.in_(["active", "trialing"])
        ).count()
        
        canceled_subscriptions = self.db.query(Subscription).filter(
            and_(
                Subscription.status == "canceled",
                Subscription.canceled_at >= start_date
            )
        ).count()
        
        # Calculate MRR (Monthly Recurring Revenue)
        mrr = self._calculate_mrr()
        
        # Calculate churn rate
        churn_rate = self._calculate_churn_rate(months)
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "months": months
            },
            "revenue": {
                "total": total_revenue,
                "monthly": monthly_revenue,
                "mrr": mrr,
                "average_monthly": total_revenue / months if months > 0 else 0
            },
            "subscriptions": {
                "active": active_subscriptions,
                "canceled": canceled_subscriptions,
                "churn_rate": churn_rate
            },
            "growth": self._calculate_growth_metrics(months)
        }
    
    def get_usage_analytics(self, org_id: int, months: int = 6) -> Dict[str, Any]:
        """
        Get usage analytics for an organization
        
        Args:
            org_id: Organization ID
            months: Number of months to analyze
            
        Returns:
            Dictionary with usage analytics
        """
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30 * months)
        
        # Get usage records for the period
        usage_records = self.db.query(UsageRecord).filter(
            and_(
                UsageRecord.organization_id == org_id,
                UsageRecord.period_start >= start_date,
                UsageRecord.period_end <= end_date
            )
        ).order_by(UsageRecord.period_start).all()
        
        # Calculate usage trends
        monthly_usage = {}
        total_usage = {
            "ai_requests": 0,
            "content_posts": 0,
            "overage_charges": 0
        }
        
        for record in usage_records:
            month_key = record.period_start.strftime("%Y-%m")
            if month_key not in monthly_usage:
                monthly_usage[month_key] = {
                    "ai_requests": 0,
                    "content_posts": 0,
                    "overage_charges": 0
                }
            
            monthly_usage[month_key]["ai_requests"] += record.ai_requests_used
            monthly_usage[month_key]["content_posts"] += record.posts_used
            monthly_usage[month_key]["overage_charges"] += record.overage_amount
            
            total_usage["ai_requests"] += record.ai_requests_used
            total_usage["content_posts"] += record.posts_used
            total_usage["overage_charges"] += record.overage_amount
        
        # Calculate usage efficiency
        subscription = self.db.query(Subscription).filter(
            Subscription.organization_id == org_id,
            Subscription.status.in_(["active", "trialing"])
        ).first()
        
        plan_limits = {}
        if subscription and subscription.plan:
            plan = subscription.plan
            plan_limits = {
                "ai_requests": plan.ai_request_limit or 0,
                "content_posts": plan.content_post_limit or 0
            }
        
        # Calculate efficiency metrics
        efficiency = {}
        for key, limit in plan_limits.items():
            if limit > 0:
                used = total_usage.get(key, 0)
                efficiency[key] = {
                    "used": used,
                    "limit": limit,
                    "percentage": min(100, (used / limit) * 100),
                    "efficiency": "high" if (used / limit) > 0.8 else "medium" if (used / limit) > 0.5 else "low"
                }
        
        return {
            "period": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "months": months
            },
            "usage": {
                "total": total_usage,
                "monthly": monthly_usage
            },
            "efficiency": efficiency,
            "trends": self._calculate_usage_trends(usage_records)
        }
    
    def get_plan_analytics(self) -> Dict[str, Any]:
        """
        Get analytics for different subscription plans
        
        Returns:
            Dictionary with plan analytics
        """
        # Get plan distribution
        plan_distribution = self.db.query(
            Plan.name,
            func.count(Subscription.id).label('count')
        ).join(Subscription).filter(
            Subscription.status.in_(["active", "trialing"])
        ).group_by(Plan.name).all()
        
        # Get revenue by plan
        revenue_by_plan = self.db.query(
            Plan.name,
            func.sum(Invoice.amount_paid).label('revenue')
        ).join(Subscription).join(Invoice).filter(
            and_(
                Invoice.paid == True,
                Invoice.paid_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).group_by(Plan.name).all()
        
        # Get churn by plan
        churn_by_plan = self.db.query(
            Plan.name,
            func.count(Subscription.id).label('churned')
        ).join(Subscription).filter(
            and_(
                Subscription.status == "canceled",
                Subscription.canceled_at >= datetime.utcnow() - timedelta(days=30)
            )
        ).group_by(Plan.name).all()
        
        return {
            "distribution": {plan.name: count for plan, count in plan_distribution},
            "revenue": {plan.name: revenue for plan, revenue in revenue_by_plan},
            "churn": {plan.name: churned for plan, churned in churn_by_plan}
        }
    
    def get_customer_analytics(self) -> Dict[str, Any]:
        """
        Get customer analytics and insights
        
        Returns:
            Dictionary with customer analytics
        """
        # Get total customers
        total_customers = self.db.query(Organization).count()
        
        # Get customers with active subscriptions
        active_customers = self.db.query(Organization).join(Subscription).filter(
            Subscription.status.in_(["active", "trialing"])
        ).distinct().count()
        
        # Get new customers this month
        this_month = datetime.utcnow().replace(day=1)
        new_customers = self.db.query(Organization).filter(
            Organization.created_at >= this_month
        ).count()
        
        # Get customer lifetime value
        customer_lifetime_value = self._calculate_customer_lifetime_value()
        
        # Get customer acquisition cost
        customer_acquisition_cost = self._calculate_customer_acquisition_cost()
        
        return {
            "total_customers": total_customers,
            "active_customers": active_customers,
            "new_customers_this_month": new_customers,
            "customer_lifetime_value": customer_lifetime_value,
            "customer_acquisition_cost": customer_acquisition_cost,
            "conversion_rate": self._calculate_conversion_rate()
        }
    
    def _calculate_mrr(self) -> float:
        """Calculate Monthly Recurring Revenue"""
        active_subscriptions = self.db.query(Subscription).filter(
            Subscription.status.in_(["active", "trialing"])
        ).all()
        
        mrr = 0
        for subscription in active_subscriptions:
            if subscription.plan:
                # Convert to monthly if annual
                if subscription.plan.billing_interval == "year":
                    mrr += subscription.plan.price / 12
                else:
                    mrr += subscription.plan.price
        
        return mrr
    
    def _calculate_churn_rate(self, months: int) -> float:
        """Calculate customer churn rate"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30 * months)
        
        # Get customers at start of period
        customers_at_start = self.db.query(Organization).filter(
            Organization.created_at < start_date
        ).count()
        
        # Get customers who churned in period
        churned_customers = self.db.query(Organization).join(Subscription).filter(
            and_(
                Subscription.status == "canceled",
                Subscription.canceled_at >= start_date,
                Subscription.canceled_at <= end_date
            )
        ).distinct().count()
        
        if customers_at_start == 0:
            return 0
        
        return (churned_customers / customers_at_start) * 100
    
    def _calculate_growth_metrics(self, months: int) -> Dict[str, Any]:
        """Calculate growth metrics"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30 * months)
        
        # Revenue growth
        current_month_revenue = self.db.query(func.sum(Invoice.amount_paid)).filter(
            and_(
                Invoice.paid == True,
                Invoice.paid_at >= end_date.replace(day=1),
                Invoice.paid_at <= end_date
            )
        ).scalar() or 0
        
        previous_month_revenue = self.db.query(func.sum(Invoice.amount_paid)).filter(
            and_(
                Invoice.paid == True,
                Invoice.paid_at >= (end_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                Invoice.paid_at < end_date.replace(day=1)
            )
        ).scalar() or 0
        
        revenue_growth = 0
        if previous_month_revenue > 0:
            revenue_growth = ((current_month_revenue - previous_month_revenue) / previous_month_revenue) * 100
        
        # Customer growth
        current_month_customers = self.db.query(Organization).filter(
            Organization.created_at >= end_date.replace(day=1)
        ).count()
        
        previous_month_customers = self.db.query(Organization).filter(
            and_(
                Organization.created_at >= (end_date.replace(day=1) - timedelta(days=1)).replace(day=1),
                Organization.created_at < end_date.replace(day=1)
            )
        ).count()
        
        customer_growth = 0
        if previous_month_customers > 0:
            customer_growth = ((current_month_customers - previous_month_customers) / previous_month_customers) * 100
        
        return {
            "revenue_growth": revenue_growth,
            "customer_growth": customer_growth,
            "current_month_revenue": current_month_revenue,
            "previous_month_revenue": previous_month_revenue,
            "current_month_customers": current_month_customers,
            "previous_month_customers": previous_month_customers
        }
    
    def _calculate_usage_trends(self, usage_records: List[UsageRecord]) -> Dict[str, Any]:
        """Calculate usage trends from records"""
        if len(usage_records) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend for AI requests
        ai_requests = [record.ai_requests_used for record in usage_records]
        ai_trend = self._calculate_trend_direction(ai_requests)
        
        # Calculate trend for content posts
        content_posts = [record.posts_used for record in usage_records]
        content_trend = self._calculate_trend_direction(content_posts)
        
        return {
            "ai_requests": ai_trend,
            "content_posts": content_trend
        }
    
    def _calculate_trend_direction(self, values: List[int]) -> str:
        """Calculate trend direction from a list of values"""
        if len(values) < 2:
            return "stable"
        
        # Simple linear trend calculation
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        first_avg = sum(first_half) / len(first_half)
        second_avg = sum(second_half) / len(second_half)
        
        if second_avg > first_avg * 1.1:
            return "increasing"
        elif second_avg < first_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    def _calculate_customer_lifetime_value(self) -> float:
        """Calculate average customer lifetime value"""
        # Get all customers with at least one paid invoice
        customers_with_revenue = self.db.query(Organization).join(Invoice).filter(
            Invoice.paid == True
        ).distinct().all()
        
        if not customers_with_revenue:
            return 0
        
        total_revenue = 0
        for customer in customers_with_revenue:
            customer_revenue = self.db.query(func.sum(Invoice.amount_paid)).filter(
                and_(
                    Invoice.organization_id == customer.id,
                    Invoice.paid == True
                )
            ).scalar() or 0
            total_revenue += customer_revenue
        
        return total_revenue / len(customers_with_revenue)
    
    def _calculate_customer_acquisition_cost(self) -> float:
        """Calculate customer acquisition cost"""
        # This would typically include marketing spend, but for now return 0
        # In a real implementation, you'd track marketing spend per customer
        return 0
    
    def _calculate_conversion_rate(self) -> float:
        """Calculate conversion rate from trial to paid"""
        # Get total trials
        total_trials = self.db.query(Subscription).filter(
            Subscription.status == "trialing"
        ).count()
        
        # Get trials that converted to paid
        converted_trials = self.db.query(Subscription).filter(
            and_(
                Subscription.status == "active",
                Subscription.trial_start.isnot(None)
            )
        ).count()
        
        if total_trials == 0:
            return 0
        
        return (converted_trials / total_trials) * 100
