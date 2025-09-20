"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Check,
  X,
  Star,
  Zap,
  Crown,
  ArrowRight,
  CreditCard,
  Calendar,
  Users,
  BarChart2,
  Shield,
  Headphones,
  Sparkles,
  Globe,
  Database,
  Lock,
  Clock,
  TrendingUp,
  Target,
  MessageSquare,
  Image,
  Video,
  FileText,
  Settings,
  Download,
  Upload,
  Smartphone,
  Palette,
  Code
} from "lucide-react";
import { toast } from "react-hot-toast";

interface PlanFeature {
  name: string;
  included: boolean;
  limit?: string | number;
  description?: string;
}

interface Plan {
  id: string;
  name: string;
  description: string;
  price: {
    monthly: number;
    yearly: number;
  };
  features: PlanFeature[];
  popular?: boolean;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
  borderColor: string;
  buttonText: string;
  buttonVariant: "default" | "outline" | "secondary";
  cta?: string;
  limitations?: string[];
}

interface PlanCardsProps {
  currentPlan?: string;
  loading?: boolean;
  error?: boolean;
  onPlanSelect?: (planId: string, billing: "monthly" | "yearly") => void;
  onUpgrade?: (planId: string) => void;
  onDowngrade?: (planId: string) => void;
  onContactSales?: () => void;
  onRetry?: () => void;
  className?: string;
}

const PLANS: Plan[] = [
  {
    id: "starter",
    name: "Starter",
    description: "Perfect for individuals and small teams getting started",
    price: {
      monthly: 29,
      yearly: 290
    },
    features: [
      { name: "Content Creation", included: true, limit: "50 posts/month" },
      { name: "Social Media Platforms", included: true, limit: "3 platforms" },
      { name: "Basic Analytics", included: true },
      { name: "AI Content Generation", included: true, limit: "100 generations/month" },
      { name: "Content Scheduling", included: true },
      { name: "Basic Templates", included: true, limit: "10 templates" },
      { name: "Email Support", included: true },
      { name: "Mobile App", included: true },
      { name: "Team Members", included: true, limit: "2 members" },
      { name: "Storage", included: true, limit: "5GB" },
      { name: "Advanced Analytics", included: false },
      { name: "Custom Branding", included: false },
      { name: "Priority Support", included: false },
      { name: "API Access", included: false },
      { name: "White-label", included: false }
    ],
    icon: Zap,
    color: "text-brand-600",
    bgColor: "bg-brand-50",
    borderColor: "border-brand-200",
    buttonText: "Start Free Trial",
    buttonVariant: "outline",
    cta: "7-day free trial, then $29/month"
  },
  {
    id: "growth",
    name: "Growth",
    description: "Ideal for growing businesses and marketing teams",
    price: {
      monthly: 79,
      yearly: 790
    },
    features: [
      { name: "Content Creation", included: true, limit: "200 posts/month" },
      { name: "Social Media Platforms", included: true, limit: "6 platforms" },
      { name: "Advanced Analytics", included: true },
      { name: "AI Content Generation", included: true, limit: "500 generations/month" },
      { name: "Content Scheduling", included: true },
      { name: "Premium Templates", included: true, limit: "50 templates" },
      { name: "Priority Support", included: true },
      { name: "Mobile App", included: true },
      { name: "Team Members", included: true, limit: "10 members" },
      { name: "Storage", included: true, limit: "25GB" },
      { name: "Custom Branding", included: true },
      { name: "Content Calendar", included: true },
      { name: "Bulk Operations", included: true },
      { name: "API Access", included: true },
      { name: "White-label", included: false }
    ],
    popular: true,
    icon: TrendingUp,
    color: "text-success-600",
    bgColor: "bg-success-50",
    borderColor: "border-success-200",
    buttonText: "Upgrade to Growth",
    buttonVariant: "default",
    cta: "Most popular for growing teams"
  },
  {
    id: "pro",
    name: "Pro",
    description: "Advanced features for large teams and agencies",
    price: {
      monthly: 199,
      yearly: 1990
    },
    features: [
      { name: "Content Creation", included: true, limit: "Unlimited" },
      { name: "Social Media Platforms", included: true, limit: "All platforms" },
      { name: "Advanced Analytics", included: true },
      { name: "AI Content Generation", included: true, limit: "Unlimited" },
      { name: "Content Scheduling", included: true },
      { name: "Premium Templates", included: true, limit: "Unlimited" },
      { name: "Priority Support", included: true },
      { name: "Mobile App", included: true },
      { name: "Team Members", included: true, limit: "50 members" },
      { name: "Storage", included: true, limit: "100GB" },
      { name: "Custom Branding", included: true },
      { name: "Content Calendar", included: true },
      { name: "Bulk Operations", included: true },
      { name: "API Access", included: true },
      { name: "White-label", included: true }
    ],
    icon: Crown,
    color: "text-warning-600",
    bgColor: "bg-warning-50",
    borderColor: "border-warning-200",
    buttonText: "Upgrade to Pro",
    buttonVariant: "default",
    cta: "Best for agencies and enterprises"
  }
];

const FEATURE_ICONS = {
  "Content Creation": FileText,
  "Social Media Platforms": Globe,
  "Basic Analytics": BarChart2,
  "Advanced Analytics": TrendingUp,
  "AI Content Generation": Sparkles,
  "Content Scheduling": Calendar,
  "Basic Templates": Image,
  "Premium Templates": Video,
  "Email Support": MessageSquare,
  "Priority Support": Headphones,
  "Mobile App": Smartphone,
  "Team Members": Users,
  "Storage": Database,
  "Custom Branding": Palette,
  "Content Calendar": Calendar,
  "Bulk Operations": Settings,
  "API Access": Code,
  "White-label": Lock
} as const;

export function PlanCards({
  currentPlan,
  loading = false,
  error = false,
  onPlanSelect,
  onUpgrade,
  onDowngrade,
  onContactSales,
  onRetry,
  className
}: PlanCardsProps) {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly");
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null);

  const handlePlanSelect = (plan: Plan) => {
    setSelectedPlan(plan.id);
    
    if (currentPlan === plan.id) {
      toast.success("You're already on this plan!");
      return;
    }
    
    if (currentPlan && onUpgrade) {
      onUpgrade(plan.id);
    } else if (onPlanSelect) {
      onPlanSelect(plan.id, billingCycle);
    }
  };

  const getFeatureIcon = (featureName: string) => {
    const Icon = FEATURE_ICONS[featureName as keyof typeof FEATURE_ICONS];
    return Icon || Check;
  };

  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0
    }).format(price);
  };

  const getSavings = (monthlyPrice: number, yearlyPrice: number) => {
    const monthlyTotal = monthlyPrice * 12;
    const savings = monthlyTotal - yearlyPrice;
    const percentage = Math.round((savings / monthlyTotal) * 100);
    return { savings, percentage };
  };

  if (loading) {
    return (
      <div className={cn("space-y-6", className)} data-testid="plan-cards-loading">
        <div className="text-center">
          <Skeleton className="h-8 w-64 mx-auto mb-2" />
          <Skeleton className="h-4 w-96 mx-auto" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {Array.from({ length: 3 }).map((_, i) => (
            <Card key={i} className="card-premium">
              <CardHeader>
                <Skeleton className="h-6 w-32" />
                <Skeleton className="h-4 w-48" />
                <Skeleton className="h-8 w-24" />
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Array.from({ length: 8 }).map((_, j) => (
                    <Skeleton key={j} className="h-4 w-full" />
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("space-y-6", className)} data-testid="plan-cards-error">
        <Card className="card-premium">
          <CardContent className="p-8 text-center">
            <CreditCard className="h-12 w-12 mx-auto mb-4 text-error-500" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">Failed to load plans</h3>
            <p className="text-neutral-600 mb-4">There was an issue fetching available plans.</p>
            {onRetry && (
              <Button onClick={onRetry} className="btn-premium" data-testid="plan-cards-retry-button">
                Try Again
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn("space-y-8", className)} data-testid="plan-cards">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-3xl font-bold text-neutral-900 mb-4">Choose Your Plan</h2>
        <p className="text-lg text-neutral-600 mb-8">
          Select the perfect plan for your content marketing needs
        </p>
        
        {/* Billing Toggle */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <span className={cn(
            "text-sm font-medium transition-colors",
            billingCycle === "monthly" ? "text-neutral-900" : "text-neutral-500"
          )}>
            Monthly
          </span>
          <button
            onClick={() => setBillingCycle(billingCycle === "monthly" ? "yearly" : "monthly")}
            className={cn(
              "relative inline-flex h-6 w-11 items-center rounded-full transition-colors",
              billingCycle === "yearly" ? "bg-brand-500" : "bg-neutral-200"
            )}
            data-testid="billing-toggle"
          >
            <span
              className={cn(
                "inline-block h-4 w-4 transform rounded-full bg-white transition-transform",
                billingCycle === "yearly" ? "translate-x-6" : "translate-x-1"
              )}
            />
          </button>
          <span className={cn(
            "text-sm font-medium transition-colors",
            billingCycle === "yearly" ? "text-neutral-900" : "text-neutral-500"
          )}>
            Yearly
          </span>
          {billingCycle === "yearly" && (
            <Badge className="bg-success-100 text-success-700 border-0">
              Save 17%
            </Badge>
          )}
        </div>
      </div>

      {/* Plan Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {PLANS.map((plan) => {
          const Icon = plan.icon;
          const isCurrentPlan = currentPlan === plan.id;
          const price = billingCycle === "monthly" ? plan.price.monthly : plan.price.yearly;
          const savings = billingCycle === "yearly" ? getSavings(plan.price.monthly, plan.price.yearly) : null;
          
          return (
            <Card
              key={plan.id}
              className={cn(
                "card-premium card-premium-hover relative",
                plan.popular && "ring-2 ring-success-200 shadow-lg",
                isCurrentPlan && "ring-2 ring-brand-200"
              )}
              data-testid={`plan-card-${plan.id}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-success-500 text-white border-0 px-4 py-1">
                    <Star className="h-3 w-3 mr-1" />
                    Most Popular
                  </Badge>
                </div>
              )}
              
              {isCurrentPlan && (
                <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                  <Badge className="bg-brand-500 text-white border-0 px-4 py-1">
                    Current Plan
                  </Badge>
                </div>
              )}

              <CardHeader className="text-center pb-4">
                <div className={cn(
                  "w-12 h-12 rounded-xl flex items-center justify-center mx-auto mb-4",
                  plan.bgColor
                )}>
                  <Icon className={cn("h-6 w-6", plan.color)} />
                </div>
                
                <CardTitle className="text-2xl font-bold">{plan.name}</CardTitle>
                <p className="text-neutral-600">{plan.description}</p>
                
                <div className="mt-4">
                  <div className="flex items-baseline justify-center gap-1">
                    <span className="text-4xl font-bold text-neutral-900">
                      {formatPrice(price)}
                    </span>
                    <span className="text-neutral-500">
                      /{billingCycle === "monthly" ? "month" : "year"}
                    </span>
                  </div>
                  
                  {savings && (
                    <div className="text-sm text-success-600 font-medium mt-1">
                      Save {formatPrice(savings.savings)} ({savings.percentage}% off)
                    </div>
                  )}
                  
                  {plan.cta && (
                    <div className="text-sm text-neutral-500 mt-2">
                      {plan.cta}
                    </div>
                  )}
                </div>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Features */}
                <div className="space-y-3">
                  {plan.features.map((feature, index) => {
                    const FeatureIcon = getFeatureIcon(feature.name);
                    return (
                      <div
                        key={index}
                        className={cn(
                          "flex items-start gap-3",
                          !feature.included && "opacity-50"
                        )}
                        data-testid={`feature-${plan.id}-${index}`}
                      >
                        <div className={cn(
                          "w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5",
                          feature.included ? "bg-success-100" : "bg-neutral-100"
                        )}>
                          {feature.included ? (
                            <Check className="h-3 w-3 text-success-600" />
                          ) : (
                            <X className="h-3 w-3 text-neutral-400" />
                          )}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2">
                            <FeatureIcon className="h-4 w-4 text-neutral-500 flex-shrink-0" />
                            <span className={cn(
                              "text-sm font-medium",
                              feature.included ? "text-neutral-900" : "text-neutral-500"
                            )}>
                              {feature.name}
                            </span>
                          </div>
                          {feature.limit && (
                            <div className="text-xs text-neutral-500 mt-1">
                              {feature.limit}
                            </div>
                          )}
                          {feature.description && (
                            <div className="text-xs text-neutral-500 mt-1">
                              {feature.description}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Action Button */}
                <div className="pt-4">
                  {isCurrentPlan ? (
                    <Button
                      variant="outline"
                      className="w-full"
                      disabled
                      data-testid={`current-plan-button-${plan.id}`}
                    >
                      Current Plan
                    </Button>
                  ) : (
                    <Button
                      variant={plan.buttonVariant}
                      className={cn(
                        "w-full",
                        plan.buttonVariant === "default" && "btn-premium"
                      )}
                      onClick={() => handlePlanSelect(plan)}
                      data-testid={`select-plan-button-${plan.id}`}
                    >
                      {plan.buttonText}
                      <ArrowRight className="h-4 w-4 ml-2" />
                    </Button>
                  )}
                </div>

                {/* Limitations */}
                {plan.limitations && plan.limitations.length > 0 && (
                  <div className="pt-4 border-t border-neutral-200">
                    <div className="text-xs text-neutral-500">
                      <div className="font-medium mb-2">Limitations:</div>
                      <ul className="space-y-1">
                        {plan.limitations.map((limitation, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <X className="h-3 w-3 text-neutral-400 mt-0.5 flex-shrink-0" />
                            <span>{limitation}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Enterprise Plan */}
      <Card className="card-premium">
        <CardContent className="p-8 text-center">
          <div className="max-w-2xl mx-auto">
            <Crown className="h-12 w-12 mx-auto mb-4 text-warning-600" />
            <h3 className="text-2xl font-bold text-neutral-900 mb-2">Enterprise</h3>
            <p className="text-lg text-neutral-600 mb-6">
              Custom solutions for large organizations with specific needs
            </p>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <Shield className="h-8 w-8 mx-auto mb-2 text-brand-600" />
                <h4 className="font-semibold mb-1">Advanced Security</h4>
                <p className="text-sm text-neutral-600">SSO, RBAC, and compliance</p>
              </div>
              <div className="text-center">
                <Headphones className="h-8 w-8 mx-auto mb-2 text-brand-600" />
                <h4 className="font-semibold mb-1">Dedicated Support</h4>
                <p className="text-sm text-neutral-600">24/7 phone and chat support</p>
              </div>
              <div className="text-center">
                <Settings className="h-8 w-8 mx-auto mb-2 text-brand-600" />
                <h4 className="font-semibold mb-1">Custom Features</h4>
                <p className="text-sm text-neutral-600">Tailored to your workflow</p>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button
                variant="outline"
                onClick={onContactSales}
                className="btn-premium-outline"
                data-testid="contact-sales-button"
              >
                Contact Sales
              </Button>
              <Button
                variant="outline"
                onClick={() => window.open("tel:+1-555-0123", "_self")}
                data-testid="call-sales-button"
              >
                Call: +1 (555) 0123
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
