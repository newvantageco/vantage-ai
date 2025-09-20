"""
Feature Gating Service
Controls access to features based on subscription tiers
"""

from __future__ import annotations

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from app.models.billing import PlanTier
from app.services.limits import LimitsService, LimitType


class FeatureType(str, Enum):
    # Content Creation Features
    AI_CONTENT_GENERATION = "ai_content_generation"
    CONTENT_TEMPLATES = "content_templates"
    MEDIA_UPLOAD = "media_upload"
    BULK_CONTENT_CREATION = "bulk_content_creation"
    
    # Publishing Features
    MULTI_PLATFORM_PUBLISHING = "multi_platform_publishing"
    CONTENT_SCHEDULING = "content_scheduling"
    OPTIMAL_TIMING = "optimal_timing"
    BULK_PUBLISHING = "bulk_publishing"
    
    # Analytics Features
    BASIC_ANALYTICS = "basic_analytics"
    ADVANCED_ANALYTICS = "advanced_analytics"
    CUSTOM_REPORTS = "custom_reports"
    REAL_TIME_METRICS = "real_time_metrics"
    COMPETITIVE_ANALYSIS = "competitive_analysis"
    
    # AI Features
    AI_OPTIMIZATION = "ai_optimization"
    PERFORMANCE_PREDICTION = "performance_prediction"
    CONTENT_VARIATIONS = "content_variations"
    TREND_ANALYSIS = "trend_analysis"
    AUDIENCE_INSIGHTS = "audience_insights"
    
    # Collaboration Features
    TEAM_MANAGEMENT = "team_management"
    CONTENT_APPROVAL = "content_approval"
    COMMENTS_FEEDBACK = "comments_feedback"
    VERSION_CONTROL = "version_control"
    
    # Automation Features
    AUTOMATION_RULES = "automation_rules"
    WORKFLOW_AUTOMATION = "workflow_automation"
    SMART_RECOMMENDATIONS = "smart_recommendations"
    A_B_TESTING = "a_b_testing"
    
    # Integration Features
    API_ACCESS = "api_access"
    WEBHOOK_SUPPORT = "webhook_support"
    CUSTOM_INTEGRATIONS = "custom_integrations"
    THIRD_PARTY_CONNECTORS = "third_party_connectors"
    
    # Branding Features
    CUSTOM_BRANDING = "custom_branding"
    WHITE_LABEL = "white_label"
    CUSTOM_DOMAINS = "custom_domains"
    
    # Support Features
    EMAIL_SUPPORT = "email_support"
    PRIORITY_SUPPORT = "priority_support"
    DEDICATED_ACCOUNT_MANAGER = "dedicated_account_manager"
    PHONE_SUPPORT = "phone_support"


@dataclass
class FeatureAccess:
    """Feature access information"""
    has_access: bool
    plan_required: Optional[PlanTier] = None
    limit: Optional[int] = None
    current_usage: Optional[int] = None
    upgrade_message: Optional[str] = None


class FeatureGatingService:
    """Service for controlling feature access based on subscription tiers"""
    
    # Feature access matrix by plan
    FEATURE_ACCESS = {
        PlanTier.STARTER: {
            # Content Creation
            FeatureType.AI_CONTENT_GENERATION: {"limit": 200},
            FeatureType.CONTENT_TEMPLATES: {"limit": 10},
            FeatureType.MEDIA_UPLOAD: {"limit": 5},  # GB
            FeatureType.BULK_CONTENT_CREATION: {"limit": 0},  # Not available
            
            # Publishing
            FeatureType.MULTI_PLATFORM_PUBLISHING: {"limit": 3},  # platforms
            FeatureType.CONTENT_SCHEDULING: {"limit": 50},  # posts per month
            FeatureType.OPTIMAL_TIMING: {"limit": 0},  # Not available
            FeatureType.BULK_PUBLISHING: {"limit": 0},  # Not available
            
            # Analytics
            FeatureType.BASIC_ANALYTICS: {"limit": 1},
            FeatureType.ADVANCED_ANALYTICS: {"limit": 0},  # Not available
            FeatureType.CUSTOM_REPORTS: {"limit": 0},  # Not available
            FeatureType.REAL_TIME_METRICS: {"limit": 0},  # Not available
            FeatureType.COMPETITIVE_ANALYSIS: {"limit": 0},  # Not available
            
            # AI Features
            FeatureType.AI_OPTIMIZATION: {"limit": 50},  # per month
            FeatureType.PERFORMANCE_PREDICTION: {"limit": 0},  # Not available
            FeatureType.CONTENT_VARIATIONS: {"limit": 0},  # Not available
            FeatureType.TREND_ANALYSIS: {"limit": 0},  # Not available
            FeatureType.AUDIENCE_INSIGHTS: {"limit": 0},  # Not available
            
            # Collaboration
            FeatureType.TEAM_MANAGEMENT: {"limit": 2},  # members
            FeatureType.CONTENT_APPROVAL: {"limit": 0},  # Not available
            FeatureType.COMMENTS_FEEDBACK: {"limit": 0},  # Not available
            FeatureType.VERSION_CONTROL: {"limit": 0},  # Not available
            
            # Automation
            FeatureType.AUTOMATION_RULES: {"limit": 3},
            FeatureType.WORKFLOW_AUTOMATION: {"limit": 0},  # Not available
            FeatureType.SMART_RECOMMENDATIONS: {"limit": 0},  # Not available
            FeatureType.A_B_TESTING: {"limit": 0},  # Not available
            
            # Integrations
            FeatureType.API_ACCESS: {"limit": 1000},  # calls per month
            FeatureType.WEBHOOK_SUPPORT: {"limit": 0},  # Not available
            FeatureType.CUSTOM_INTEGRATIONS: {"limit": 0},  # Not available
            FeatureType.THIRD_PARTY_CONNECTORS: {"limit": 3},
            
            # Branding
            FeatureType.CUSTOM_BRANDING: {"limit": 0},  # Not available
            FeatureType.WHITE_LABEL: {"limit": 0},  # Not available
            FeatureType.CUSTOM_DOMAINS: {"limit": 0},  # Not available
            
            # Support
            FeatureType.EMAIL_SUPPORT: {"limit": 1},
            FeatureType.PRIORITY_SUPPORT: {"limit": 0},  # Not available
            FeatureType.DEDICATED_ACCOUNT_MANAGER: {"limit": 0},  # Not available
            FeatureType.PHONE_SUPPORT: {"limit": 0},  # Not available
        },
        
        PlanTier.GROWTH: {
            # Content Creation
            FeatureType.AI_CONTENT_GENERATION: {"limit": 1000},
            FeatureType.CONTENT_TEMPLATES: {"limit": 50},
            FeatureType.MEDIA_UPLOAD: {"limit": 25},  # GB
            FeatureType.BULK_CONTENT_CREATION: {"limit": 1},
            
            # Publishing
            FeatureType.MULTI_PLATFORM_PUBLISHING: {"limit": 6},  # platforms
            FeatureType.CONTENT_SCHEDULING: {"limit": 200},  # posts per month
            FeatureType.OPTIMAL_TIMING: {"limit": 1},
            FeatureType.BULK_PUBLISHING: {"limit": 1},
            
            # Analytics
            FeatureType.BASIC_ANALYTICS: {"limit": 1},
            FeatureType.ADVANCED_ANALYTICS: {"limit": 1},
            FeatureType.CUSTOM_REPORTS: {"limit": 10},
            FeatureType.REAL_TIME_METRICS: {"limit": 1},
            FeatureType.COMPETITIVE_ANALYSIS: {"limit": 0},  # Not available
            
            # AI Features
            FeatureType.AI_OPTIMIZATION: {"limit": 200},  # per month
            FeatureType.PERFORMANCE_PREDICTION: {"limit": 1},
            FeatureType.CONTENT_VARIATIONS: {"limit": 50},  # per month
            FeatureType.TREND_ANALYSIS: {"limit": 1},
            FeatureType.AUDIENCE_INSIGHTS: {"limit": 1},
            
            # Collaboration
            FeatureType.TEAM_MANAGEMENT: {"limit": 10},  # members
            FeatureType.CONTENT_APPROVAL: {"limit": 1},
            FeatureType.COMMENTS_FEEDBACK: {"limit": 1},
            FeatureType.VERSION_CONTROL: {"limit": 1},
            
            # Automation
            FeatureType.AUTOMATION_RULES: {"limit": 10},
            FeatureType.WORKFLOW_AUTOMATION: {"limit": 1},
            FeatureType.SMART_RECOMMENDATIONS: {"limit": 1},
            FeatureType.A_B_TESTING: {"limit": 5},  # tests per month
            
            # Integrations
            FeatureType.API_ACCESS: {"limit": 10000},  # calls per month
            FeatureType.WEBHOOK_SUPPORT: {"limit": 1},
            FeatureType.CUSTOM_INTEGRATIONS: {"limit": 2},
            FeatureType.THIRD_PARTY_CONNECTORS: {"limit": 6},
            
            # Branding
            FeatureType.CUSTOM_BRANDING: {"limit": 1},
            FeatureType.WHITE_LABEL: {"limit": 0},  # Not available
            FeatureType.CUSTOM_DOMAINS: {"limit": 0},  # Not available
            
            # Support
            FeatureType.EMAIL_SUPPORT: {"limit": 1},
            FeatureType.PRIORITY_SUPPORT: {"limit": 1},
            FeatureType.DEDICATED_ACCOUNT_MANAGER: {"limit": 0},  # Not available
            FeatureType.PHONE_SUPPORT: {"limit": 0},  # Not available
        },
        
        PlanTier.PRO: {
            # Content Creation
            FeatureType.AI_CONTENT_GENERATION: {"limit": -1},  # Unlimited
            FeatureType.CONTENT_TEMPLATES: {"limit": -1},  # Unlimited
            FeatureType.MEDIA_UPLOAD: {"limit": 100},  # GB
            FeatureType.BULK_CONTENT_CREATION: {"limit": -1},  # Unlimited
            
            # Publishing
            FeatureType.MULTI_PLATFORM_PUBLISHING: {"limit": -1},  # Unlimited
            FeatureType.CONTENT_SCHEDULING: {"limit": -1},  # Unlimited
            FeatureType.OPTIMAL_TIMING: {"limit": 1},
            FeatureType.BULK_PUBLISHING: {"limit": -1},  # Unlimited
            
            # Analytics
            FeatureType.BASIC_ANALYTICS: {"limit": 1},
            FeatureType.ADVANCED_ANALYTICS: {"limit": 1},
            FeatureType.CUSTOM_REPORTS: {"limit": -1},  # Unlimited
            FeatureType.REAL_TIME_METRICS: {"limit": 1},
            FeatureType.COMPETITIVE_ANALYSIS: {"limit": 1},
            
            # AI Features
            FeatureType.AI_OPTIMIZATION: {"limit": -1},  # Unlimited
            FeatureType.PERFORMANCE_PREDICTION: {"limit": 1},
            FeatureType.CONTENT_VARIATIONS: {"limit": -1},  # Unlimited
            FeatureType.TREND_ANALYSIS: {"limit": 1},
            FeatureType.AUDIENCE_INSIGHTS: {"limit": 1},
            
            # Collaboration
            FeatureType.TEAM_MANAGEMENT: {"limit": 50},  # members
            FeatureType.CONTENT_APPROVAL: {"limit": 1},
            FeatureType.COMMENTS_FEEDBACK: {"limit": 1},
            FeatureType.VERSION_CONTROL: {"limit": 1},
            
            # Automation
            FeatureType.AUTOMATION_RULES: {"limit": -1},  # Unlimited
            FeatureType.WORKFLOW_AUTOMATION: {"limit": 1},
            FeatureType.SMART_RECOMMENDATIONS: {"limit": 1},
            FeatureType.A_B_TESTING: {"limit": -1},  # Unlimited
            
            # Integrations
            FeatureType.API_ACCESS: {"limit": -1},  # Unlimited
            FeatureType.WEBHOOK_SUPPORT: {"limit": 1},
            FeatureType.CUSTOM_INTEGRATIONS: {"limit": -1},  # Unlimited
            FeatureType.THIRD_PARTY_CONNECTORS: {"limit": -1},  # Unlimited
            
            # Branding
            FeatureType.CUSTOM_BRANDING: {"limit": 1},
            FeatureType.WHITE_LABEL: {"limit": 1},
            FeatureType.CUSTOM_DOMAINS: {"limit": 1},
            
            # Support
            FeatureType.EMAIL_SUPPORT: {"limit": 1},
            FeatureType.PRIORITY_SUPPORT: {"limit": 1},
            FeatureType.DEDICATED_ACCOUNT_MANAGER: {"limit": 1},
            FeatureType.PHONE_SUPPORT: {"limit": 1},
        }
    }
    
    def __init__(self, limits_service: LimitsService):
        self.limits_service = limits_service
    
    def check_feature_access(
        self, 
        org_id: str, 
        feature: FeatureType, 
        current_usage: Optional[int] = None
    ) -> FeatureAccess:
        """Check if organization has access to a specific feature"""
        plan = self.limits_service.get_organization_plan(org_id)
        feature_config = self.FEATURE_ACCESS.get(plan, {}).get(feature)
        
        if not feature_config:
            return FeatureAccess(
                has_access=False,
                plan_required=PlanTier.PRO,
                upgrade_message=f"Feature '{feature.value}' is not available in your current plan. Upgrade to Pro for access."
            )
        
        limit = feature_config.get("limit", 0)
        
        # If limit is -1, feature is unlimited
        if limit == -1:
            return FeatureAccess(
                has_access=True,
                limit=limit,
                current_usage=current_usage or 0
            )
        
        # If limit is 0, feature is not available
        if limit == 0:
            return FeatureAccess(
                has_access=False,
                plan_required=self._get_next_plan_with_feature(feature),
                upgrade_message=f"Feature '{feature.value}' is not available in your current plan. Upgrade to access this feature."
            )
        
        # Check if within limit
        if current_usage is None:
            # Get current usage from limits service
            current_usage = self._get_current_usage(org_id, feature)
        
        has_access = current_usage < limit
        
        return FeatureAccess(
            has_access=has_access,
            limit=limit,
            current_usage=current_usage,
            upgrade_message=f"You've reached the limit for '{feature.value}' ({current_usage}/{limit}). Upgrade to increase your limits." if not has_access else None
        )
    
    def get_available_features(self, org_id: str) -> List[FeatureType]:
        """Get list of features available to organization"""
        plan = self.limits_service.get_organization_plan(org_id)
        available_features = []
        
        for feature, config in self.FEATURE_ACCESS.get(plan, {}).items():
            if config.get("limit", 0) > 0 or config.get("limit", 0) == -1:
                available_features.append(feature)
        
        return available_features
    
    def get_feature_limits(self, org_id: str) -> Dict[FeatureType, Dict[str, Any]]:
        """Get all feature limits for organization"""
        plan = self.limits_service.get_organization_plan(org_id)
        return self.FEATURE_ACCESS.get(plan, {})
    
    def _get_next_plan_with_feature(self, feature: FeatureType) -> PlanTier:
        """Get the next plan that includes this feature"""
        for plan in [PlanTier.GROWTH, PlanTier.PRO]:
            if self.FEATURE_ACCESS.get(plan, {}).get(feature, {}).get("limit", 0) > 0:
                return plan
        return PlanTier.PRO
    
    def _get_current_usage(self, org_id: str, feature: FeatureType) -> int:
        """Get current usage for a feature"""
        # Map feature types to limit types for usage checking
        feature_to_limit_map = {
            FeatureType.AI_CONTENT_GENERATION: LimitType.AI_GENERATIONS,
            FeatureType.CONTENT_SCHEDULING: LimitType.POSTS_PER_MONTH,
            FeatureType.TEAM_MANAGEMENT: LimitType.USERS,
            FeatureType.MULTI_PLATFORM_PUBLISHING: LimitType.CHANNELS,
            FeatureType.API_ACCESS: LimitType.API_CALLS_PER_MONTH,
        }
        
        limit_type = feature_to_limit_map.get(feature)
        if limit_type:
            result = self.limits_service.check_limit(org_id, limit_type)
            return result.current
        
        return 0
