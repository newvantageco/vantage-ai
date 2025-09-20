/**
 * Feature Access Hook
 * Provides feature gating functionality based on subscription tier
 */

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';

export enum FeatureType {
  // Content Creation Features
  AI_CONTENT_GENERATION = 'ai_content_generation',
  CONTENT_TEMPLATES = 'content_templates',
  MEDIA_UPLOAD = 'media_upload',
  BULK_CONTENT_CREATION = 'bulk_content_creation',
  
  // Publishing Features
  MULTI_PLATFORM_PUBLISHING = 'multi_platform_publishing',
  CONTENT_SCHEDULING = 'content_scheduling',
  OPTIMAL_TIMING = 'optimal_timing',
  BULK_PUBLISHING = 'bulk_publishing',
  
  // Analytics Features
  BASIC_ANALYTICS = 'basic_analytics',
  ADVANCED_ANALYTICS = 'advanced_analytics',
  CUSTOM_REPORTS = 'custom_reports',
  REAL_TIME_METRICS = 'real_time_metrics',
  COMPETITIVE_ANALYSIS = 'competitive_analysis',
  
  // AI Features
  AI_OPTIMIZATION = 'ai_optimization',
  PERFORMANCE_PREDICTION = 'performance_prediction',
  CONTENT_VARIATIONS = 'content_variations',
  TREND_ANALYSIS = 'trend_analysis',
  AUDIENCE_INSIGHTS = 'audience_insights',
  
  // Collaboration Features
  TEAM_MANAGEMENT = 'team_management',
  CONTENT_APPROVAL = 'content_approval',
  COMMENTS_FEEDBACK = 'comments_feedback',
  VERSION_CONTROL = 'version_control',
  
  // Automation Features
  AUTOMATION_RULES = 'automation_rules',
  WORKFLOW_AUTOMATION = 'workflow_automation',
  SMART_RECOMMENDATIONS = 'smart_recommendations',
  A_B_TESTING = 'a_b_testing',
  
  // Integration Features
  API_ACCESS = 'api_access',
  WEBHOOK_SUPPORT = 'webhook_support',
  CUSTOM_INTEGRATIONS = 'custom_integrations',
  THIRD_PARTY_CONNECTORS = 'third_party_connectors',
  
  // Branding Features
  CUSTOM_BRANDING = 'custom_branding',
  WHITE_LABEL = 'white_label',
  CUSTOM_DOMAINS = 'custom_domains',
  
  // Support Features
  EMAIL_SUPPORT = 'email_support',
  PRIORITY_SUPPORT = 'priority_support',
  DEDICATED_ACCOUNT_MANAGER = 'dedicated_account_manager',
  PHONE_SUPPORT = 'phone_support',
}

export interface FeatureAccess {
  hasAccess: boolean;
  planRequired?: string;
  limit?: number;
  currentUsage?: number;
  upgradeMessage?: string;
}

export interface SubscriptionInfo {
  plan: string;
  features: Record<string, FeatureAccess>;
  limits: Record<string, number>;
}

// Mock subscription data - in real app, this would come from API
const MOCK_SUBSCRIPTION_DATA: Record<string, SubscriptionInfo> = {
  starter: {
    plan: 'starter',
    features: {
      [FeatureType.AI_CONTENT_GENERATION]: { hasAccess: true, limit: 200, currentUsage: 45 },
      [FeatureType.CONTENT_TEMPLATES]: { hasAccess: true, limit: 10, currentUsage: 3 },
      [FeatureType.MEDIA_UPLOAD]: { hasAccess: true, limit: 5, currentUsage: 1.2 },
      [FeatureType.BULK_CONTENT_CREATION]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Bulk content creation is available in Growth plan and above.' },
      [FeatureType.MULTI_PLATFORM_PUBLISHING]: { hasAccess: true, limit: 3, currentUsage: 2 },
      [FeatureType.CONTENT_SCHEDULING]: { hasAccess: true, limit: 50, currentUsage: 23 },
      [FeatureType.OPTIMAL_TIMING]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Optimal timing recommendations are available in Growth plan and above.' },
      [FeatureType.BULK_PUBLISHING]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Bulk publishing is available in Growth plan and above.' },
      [FeatureType.BASIC_ANALYTICS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.ADVANCED_ANALYTICS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Advanced analytics are available in Growth plan and above.' },
      [FeatureType.CUSTOM_REPORTS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Custom reports are available in Growth plan and above.' },
      [FeatureType.REAL_TIME_METRICS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Real-time metrics are available in Growth plan and above.' },
      [FeatureType.COMPETITIVE_ANALYSIS]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Competitive analysis is available in Pro plan.' },
      [FeatureType.AI_OPTIMIZATION]: { hasAccess: true, limit: 50, currentUsage: 12 },
      [FeatureType.PERFORMANCE_PREDICTION]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Performance prediction is available in Growth plan and above.' },
      [FeatureType.CONTENT_VARIATIONS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Content variations are available in Growth plan and above.' },
      [FeatureType.TREND_ANALYSIS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Trend analysis is available in Growth plan and above.' },
      [FeatureType.AUDIENCE_INSIGHTS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Audience insights are available in Growth plan and above.' },
      [FeatureType.TEAM_MANAGEMENT]: { hasAccess: true, limit: 2, currentUsage: 1 },
      [FeatureType.CONTENT_APPROVAL]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Content approval workflows are available in Growth plan and above.' },
      [FeatureType.COMMENTS_FEEDBACK]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Comments and feedback are available in Growth plan and above.' },
      [FeatureType.VERSION_CONTROL]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Version control is available in Growth plan and above.' },
      [FeatureType.AUTOMATION_RULES]: { hasAccess: true, limit: 3, currentUsage: 1 },
      [FeatureType.WORKFLOW_AUTOMATION]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Workflow automation is available in Growth plan and above.' },
      [FeatureType.SMART_RECOMMENDATIONS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Smart recommendations are available in Growth plan and above.' },
      [FeatureType.A_B_TESTING]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'A/B testing is available in Growth plan and above.' },
      [FeatureType.API_ACCESS]: { hasAccess: true, limit: 1000, currentUsage: 234 },
      [FeatureType.WEBHOOK_SUPPORT]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Webhook support is available in Growth plan and above.' },
      [FeatureType.CUSTOM_INTEGRATIONS]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Custom integrations are available in Growth plan and above.' },
      [FeatureType.THIRD_PARTY_CONNECTORS]: { hasAccess: true, limit: 3, currentUsage: 2 },
      [FeatureType.CUSTOM_BRANDING]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Custom branding is available in Growth plan and above.' },
      [FeatureType.WHITE_LABEL]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'White-label options are available in Pro plan.' },
      [FeatureType.CUSTOM_DOMAINS]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Custom domains are available in Pro plan.' },
      [FeatureType.EMAIL_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.PRIORITY_SUPPORT]: { hasAccess: false, planRequired: 'growth', upgradeMessage: 'Priority support is available in Growth plan and above.' },
      [FeatureType.DEDICATED_ACCOUNT_MANAGER]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Dedicated account manager is available in Pro plan.' },
      [FeatureType.PHONE_SUPPORT]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Phone support is available in Pro plan.' },
    },
    limits: {
      posts_per_month: 50,
      channels: 3,
      users: 2,
      campaigns: 5,
      content_items: 100,
      ai_generations: 200,
      storage_gb: 5,
      templates: 10,
      api_calls_per_month: 1000,
      automation_rules: 3,
      integrations: 3,
    }
  },
  growth: {
    plan: 'growth',
    features: {
      [FeatureType.AI_CONTENT_GENERATION]: { hasAccess: true, limit: 1000, currentUsage: 234 },
      [FeatureType.CONTENT_TEMPLATES]: { hasAccess: true, limit: 50, currentUsage: 12 },
      [FeatureType.MEDIA_UPLOAD]: { hasAccess: true, limit: 25, currentUsage: 8.5 },
      [FeatureType.BULK_CONTENT_CREATION]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.MULTI_PLATFORM_PUBLISHING]: { hasAccess: true, limit: 6, currentUsage: 4 },
      [FeatureType.CONTENT_SCHEDULING]: { hasAccess: true, limit: 200, currentUsage: 89 },
      [FeatureType.OPTIMAL_TIMING]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.BULK_PUBLISHING]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.BASIC_ANALYTICS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.ADVANCED_ANALYTICS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.CUSTOM_REPORTS]: { hasAccess: true, limit: 10, currentUsage: 3 },
      [FeatureType.REAL_TIME_METRICS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.COMPETITIVE_ANALYSIS]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Competitive analysis is available in Pro plan.' },
      [FeatureType.AI_OPTIMIZATION]: { hasAccess: true, limit: 200, currentUsage: 45 },
      [FeatureType.PERFORMANCE_PREDICTION]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.CONTENT_VARIATIONS]: { hasAccess: true, limit: 50, currentUsage: 12 },
      [FeatureType.TREND_ANALYSIS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.AUDIENCE_INSIGHTS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.TEAM_MANAGEMENT]: { hasAccess: true, limit: 10, currentUsage: 4 },
      [FeatureType.CONTENT_APPROVAL]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.COMMENTS_FEEDBACK]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.VERSION_CONTROL]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.AUTOMATION_RULES]: { hasAccess: true, limit: 10, currentUsage: 3 },
      [FeatureType.WORKFLOW_AUTOMATION]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.SMART_RECOMMENDATIONS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.A_B_TESTING]: { hasAccess: true, limit: 5, currentUsage: 2 },
      [FeatureType.API_ACCESS]: { hasAccess: true, limit: 10000, currentUsage: 2345 },
      [FeatureType.WEBHOOK_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.CUSTOM_INTEGRATIONS]: { hasAccess: true, limit: 2, currentUsage: 1 },
      [FeatureType.THIRD_PARTY_CONNECTORS]: { hasAccess: true, limit: 6, currentUsage: 4 },
      [FeatureType.CUSTOM_BRANDING]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.WHITE_LABEL]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'White-label options are available in Pro plan.' },
      [FeatureType.CUSTOM_DOMAINS]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Custom domains are available in Pro plan.' },
      [FeatureType.EMAIL_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.PRIORITY_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.DEDICATED_ACCOUNT_MANAGER]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Dedicated account manager is available in Pro plan.' },
      [FeatureType.PHONE_SUPPORT]: { hasAccess: false, planRequired: 'pro', upgradeMessage: 'Phone support is available in Pro plan.' },
    },
    limits: {
      posts_per_month: 200,
      channels: 6,
      users: 10,
      campaigns: 20,
      content_items: 500,
      ai_generations: 1000,
      storage_gb: 25,
      templates: 50,
      api_calls_per_month: 10000,
      automation_rules: 10,
      integrations: 6,
    }
  },
  pro: {
    plan: 'pro',
    features: {
      [FeatureType.AI_CONTENT_GENERATION]: { hasAccess: true, limit: -1, currentUsage: 1234 },
      [FeatureType.CONTENT_TEMPLATES]: { hasAccess: true, limit: -1, currentUsage: 45 },
      [FeatureType.MEDIA_UPLOAD]: { hasAccess: true, limit: 100, currentUsage: 23.5 },
      [FeatureType.BULK_CONTENT_CREATION]: { hasAccess: true, limit: -1, currentUsage: 12 },
      [FeatureType.MULTI_PLATFORM_PUBLISHING]: { hasAccess: true, limit: -1, currentUsage: 8 },
      [FeatureType.CONTENT_SCHEDULING]: { hasAccess: true, limit: -1, currentUsage: 456 },
      [FeatureType.OPTIMAL_TIMING]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.BULK_PUBLISHING]: { hasAccess: true, limit: -1, currentUsage: 23 },
      [FeatureType.BASIC_ANALYTICS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.ADVANCED_ANALYTICS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.CUSTOM_REPORTS]: { hasAccess: true, limit: -1, currentUsage: 15 },
      [FeatureType.REAL_TIME_METRICS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.COMPETITIVE_ANALYSIS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.AI_OPTIMIZATION]: { hasAccess: true, limit: -1, currentUsage: 234 },
      [FeatureType.PERFORMANCE_PREDICTION]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.CONTENT_VARIATIONS]: { hasAccess: true, limit: -1, currentUsage: 67 },
      [FeatureType.TREND_ANALYSIS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.AUDIENCE_INSIGHTS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.TEAM_MANAGEMENT]: { hasAccess: true, limit: 50, currentUsage: 12 },
      [FeatureType.CONTENT_APPROVAL]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.COMMENTS_FEEDBACK]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.VERSION_CONTROL]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.AUTOMATION_RULES]: { hasAccess: true, limit: -1, currentUsage: 15 },
      [FeatureType.WORKFLOW_AUTOMATION]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.SMART_RECOMMENDATIONS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.A_B_TESTING]: { hasAccess: true, limit: -1, currentUsage: 8 },
      [FeatureType.API_ACCESS]: { hasAccess: true, limit: -1, currentUsage: 12345 },
      [FeatureType.WEBHOOK_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.CUSTOM_INTEGRATIONS]: { hasAccess: true, limit: -1, currentUsage: 5 },
      [FeatureType.THIRD_PARTY_CONNECTORS]: { hasAccess: true, limit: -1, currentUsage: 12 },
      [FeatureType.CUSTOM_BRANDING]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.WHITE_LABEL]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.CUSTOM_DOMAINS]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.EMAIL_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.PRIORITY_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.DEDICATED_ACCOUNT_MANAGER]: { hasAccess: true, limit: 1, currentUsage: 1 },
      [FeatureType.PHONE_SUPPORT]: { hasAccess: true, limit: 1, currentUsage: 1 },
    },
    limits: {
      posts_per_month: -1,
      channels: -1,
      users: 50,
      campaigns: -1,
      content_items: -1,
      ai_generations: -1,
      storage_gb: 100,
      templates: -1,
      api_calls_per_month: -1,
      automation_rules: -1,
      integrations: -1,
    }
  }
};

export function useFeatureAccess() {
  const { user } = useAuth();
  const [subscriptionInfo, setSubscriptionInfo] = useState<SubscriptionInfo | null>(null);
  const [loading, setLoading] = useState(true);

  // Mock current plan - in real app, this would come from user context
  const currentPlan = user?.subscription?.plan || 'starter';

  useEffect(() => {
    // Simulate API call
    const fetchSubscriptionInfo = async () => {
      setLoading(true);
      try {
        // In real app, this would be an API call
        await new Promise(resolve => setTimeout(resolve, 500));
        setSubscriptionInfo(MOCK_SUBSCRIPTION_DATA[currentPlan]);
      } catch (error) {
        console.error('Failed to fetch subscription info:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSubscriptionInfo();
  }, [currentPlan]);

  const hasFeatureAccess = useCallback((feature: FeatureType): boolean => {
    if (!subscriptionInfo) return false;
    return subscriptionInfo.features[feature]?.hasAccess || false;
  }, [subscriptionInfo]);

  const getFeatureAccess = useCallback((feature: FeatureType): FeatureAccess | null => {
    if (!subscriptionInfo) return null;
    return subscriptionInfo.features[feature] || null;
  }, [subscriptionInfo]);

  const getFeatureLimit = useCallback((feature: FeatureType): number | null => {
    const access = getFeatureAccess(feature);
    return access?.limit || null;
  }, [getFeatureAccess]);

  const getFeatureUsage = useCallback((feature: FeatureType): number | null => {
    const access = getFeatureAccess(feature);
    return access?.currentUsage || null;
  }, [getFeatureAccess]);

  const isFeatureUnlimited = useCallback((feature: FeatureType): boolean => {
    const limit = getFeatureLimit(feature);
    return limit === -1;
  }, [getFeatureLimit]);

  const getUpgradeMessage = useCallback((feature: FeatureType): string | null => {
    const access = getFeatureAccess(feature);
    return access?.upgradeMessage || null;
  }, [getFeatureAccess]);

  const getRequiredPlan = useCallback((feature: FeatureType): string | null => {
    const access = getFeatureAccess(feature);
    return access?.planRequired || null;
  }, [getFeatureAccess]);

  const getUsagePercentage = useCallback((feature: FeatureType): number | null => {
    const limit = getFeatureLimit(feature);
    const usage = getFeatureUsage(feature);
    
    if (limit === null || usage === null || limit === -1) return null;
    
    return Math.round((usage / limit) * 100);
  }, [getFeatureLimit, getFeatureUsage]);

  const isNearLimit = useCallback((feature: FeatureType, threshold: number = 80): boolean => {
    const percentage = getUsagePercentage(feature);
    return percentage !== null && percentage >= threshold;
  }, [getUsagePercentage]);

  return {
    subscriptionInfo,
    loading,
    currentPlan,
    hasFeatureAccess,
    getFeatureAccess,
    getFeatureLimit,
    getFeatureUsage,
    isFeatureUnlimited,
    getUpgradeMessage,
    getRequiredPlan,
    getUsagePercentage,
    isNearLimit,
  };
}
