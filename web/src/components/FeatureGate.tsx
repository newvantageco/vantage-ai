/**
 * Feature Gate Component
 * Wraps content that should be gated based on subscription tier
 */

import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Lock, 
  Crown, 
  TrendingUp, 
  Sparkles, 
  ArrowUpRight,
  AlertCircle,
  CheckCircle2
} from 'lucide-react';
import { useFeatureAccess, FeatureType } from '@/hooks/useFeatureAccess';
import { cn } from '@/lib/utils';

interface FeatureGateProps {
  feature: FeatureType;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  showUpgradePrompt?: boolean;
  className?: string;
  requireAccess?: boolean; // If true, shows upgrade prompt instead of fallback
}

export function FeatureGate({ 
  feature, 
  children, 
  fallback, 
  showUpgradePrompt = true,
  className,
  requireAccess = false
}: FeatureGateProps) {
  const { 
    hasFeatureAccess, 
    getFeatureAccess, 
    getUpgradeMessage, 
    getRequiredPlan,
    getUsagePercentage,
    isNearLimit,
    currentPlan
  } = useFeatureAccess();

  const hasAccess = hasFeatureAccess(feature);
  const featureAccess = getFeatureAccess(feature);
  const upgradeMessage = getUpgradeMessage(feature);
  const requiredPlan = getRequiredPlan(feature);
  const usagePercentage = getUsagePercentage(feature);
  const nearLimit = isNearLimit(feature);

  // If user has access and not near limit, show children
  if (hasAccess && !nearLimit) {
    return <>{children}</>;
  }

  // If user has access but is near limit, show warning
  if (hasAccess && nearLimit) {
    return (
      <div className={cn("space-y-2", className)}>
        {children}
        <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center gap-2 text-yellow-800">
            <AlertCircle className="h-4 w-4" />
            <span className="text-sm font-medium">
              You're using {usagePercentage}% of your {feature.replace(/_/g, ' ')} limit
            </span>
          </div>
          <p className="text-xs text-yellow-700 mt-1">
            Consider upgrading to increase your limits.
          </p>
        </div>
      </div>
    );
  }

  // If requireAccess is true, show upgrade prompt instead of fallback
  if (requireAccess) {
    return (
      <div className={cn("space-y-4", className)}>
        {showUpgradePrompt && (
          <FeatureUpgradePrompt 
            feature={feature}
            requiredPlan={requiredPlan}
            upgradeMessage={upgradeMessage}
          />
        )}
      </div>
    );
  }

  // Show fallback content
  return <>{fallback}</>;
}

interface FeatureUpgradePromptProps {
  feature: FeatureType;
  requiredPlan?: string | null;
  upgradeMessage?: string | null;
  className?: string;
}

export function FeatureUpgradePrompt({ 
  feature, 
  requiredPlan, 
  upgradeMessage,
  className 
}: FeatureUpgradePromptProps) {
  const getFeatureIcon = (feature: FeatureType) => {
    switch (feature) {
      case FeatureType.AI_CONTENT_GENERATION:
      case FeatureType.AI_OPTIMIZATION:
        return Sparkles;
      case FeatureType.ADVANCED_ANALYTICS:
      case FeatureType.CUSTOM_REPORTS:
        return TrendingUp;
      case FeatureType.WHITE_LABEL:
      case FeatureType.CUSTOM_BRANDING:
        return Crown;
      default:
        return Lock;
    }
  };

  const getFeatureDisplayName = (feature: FeatureType) => {
    return feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  };

  const getPlanColor = (plan: string) => {
    switch (plan) {
      case 'growth':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'pro':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const Icon = getFeatureIcon(feature);
  const displayName = getFeatureDisplayName(feature);

  return (
    <Card className={cn("border-dashed", className)}>
      <CardContent className="p-6 text-center space-y-4">
        <div className="flex justify-center">
          <div className="p-3 bg-muted rounded-full">
            <Icon className="h-6 w-6 text-muted-foreground" />
          </div>
        </div>
        
        <div className="space-y-2">
          <h3 className="font-semibold text-lg">
            {displayName} Not Available
          </h3>
          
          {upgradeMessage && (
            <p className="text-sm text-muted-foreground">
              {upgradeMessage}
            </p>
          )}
        </div>

        {requiredPlan && (
          <div className="flex justify-center">
            <Badge 
              variant="outline" 
              className={cn("px-3 py-1", getPlanColor(requiredPlan))}
            >
              <Crown className="h-3 w-3 mr-1" />
              {requiredPlan.charAt(0).toUpperCase() + requiredPlan.slice(1)} Plan Required
            </Badge>
          </div>
        )}

        <div className="flex gap-2 justify-center">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => {
              // Navigate to pricing page
              window.location.href = '/pricing';
            }}
          >
            View Plans
          </Button>
          <Button 
            size="sm"
            onClick={() => {
              // Navigate to upgrade page
              window.location.href = '/billing/upgrade';
            }}
          >
            Upgrade Now
            <ArrowUpRight className="h-3 w-3 ml-1" />
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

interface FeatureUsageIndicatorProps {
  feature: FeatureType;
  className?: string;
}

export function FeatureUsageIndicator({ feature, className }: FeatureUsageIndicatorProps) {
  const { 
    getFeatureAccess, 
    getUsagePercentage, 
    isNearLimit,
    isFeatureUnlimited 
  } = useFeatureAccess();

  const featureAccess = getFeatureAccess(feature);
  const usagePercentage = getUsagePercentage(feature);
  const nearLimit = isNearLimit(feature);
  const isUnlimited = isFeatureUnlimited(feature);

  if (!featureAccess || isUnlimited) {
    return null;
  }

  const { currentUsage, limit } = featureAccess;

  return (
    <div className={cn("space-y-2", className)}>
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">
          {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
        </span>
        <span className={cn(
          "font-medium",
          nearLimit ? "text-yellow-600" : "text-muted-foreground"
        )}>
          {currentUsage} / {limit === -1 ? '∞' : limit}
        </span>
      </div>
      
      <div className="w-full bg-muted rounded-full h-2">
        <div 
          className={cn(
            "h-2 rounded-full transition-all",
            nearLimit 
              ? "bg-yellow-500" 
              : "bg-primary"
          )}
          style={{ 
            width: `${Math.min(usagePercentage || 0, 100)}%` 
          }}
        />
      </div>
      
      {nearLimit && (
        <div className="flex items-center gap-1 text-xs text-yellow-600">
          <AlertCircle className="h-3 w-3" />
          <span>Approaching limit</span>
        </div>
      )}
    </div>
  );
}

interface FeatureStatusProps {
  feature: FeatureType;
  className?: string;
}

export function FeatureStatus({ feature, className }: FeatureStatusProps) {
  const { hasFeatureAccess, getFeatureAccess } = useFeatureAccess();
  
  const hasAccess = hasFeatureAccess(feature);
  const featureAccess = getFeatureAccess(feature);

  return (
    <div className={cn("flex items-center gap-2", className)}>
      {hasAccess ? (
        <CheckCircle2 className="h-4 w-4 text-green-500" />
      ) : (
        <Lock className="h-4 w-4 text-muted-foreground" />
      )}
      <span className={cn(
        "text-sm",
        hasAccess ? "text-foreground" : "text-muted-foreground"
      )}>
        {feature.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
      </span>
      {featureAccess?.limit && featureAccess.limit > 0 && (
        <Badge variant="secondary" className="text-xs">
          {featureAccess.limit === -1 ? 'Unlimited' : `Limit: ${featureAccess.limit}`}
        </Badge>
      )}
    </div>
  );
}
