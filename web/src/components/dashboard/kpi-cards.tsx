"use client";

import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { 
  ArrowUpRight, 
  ArrowDownRight, 
  TrendingUp, 
  MessageSquare, 
  BarChart2, 
  Users,
  Eye,
  MousePointer,
  Heart,
  Share2,
  DollarSign,
  Calendar,
  Clock,
  Target
} from "lucide-react";

export interface KPIData {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down" | "neutral";
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
  description?: string;
  period?: string;
  target?: string;
  status?: "good" | "warning" | "critical";
}

interface KPICardsProps {
  data: KPIData[];
  loading?: boolean;
  error?: boolean;
  onRetry?: () => void;
  className?: string;
}

export function KPICards({ data, loading = false, error = false, onRetry, className }: KPICardsProps) {
  if (loading) {
    return (
      <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6", className)} data-testid="kpi-cards-loading">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i} className="card-premium">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="space-y-2 flex-1">
                  <Skeleton className="h-4 w-3/4" />
                  <Skeleton className="h-8 w-1/2" />
                  <Skeleton className="h-4 w-2/3" />
                </div>
                <Skeleton className="h-12 w-12 rounded-2xl" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6", className)} data-testid="kpi-cards-error">
        <Card className="card-premium lg:col-span-4">
          <CardContent className="p-8 text-center">
            <div className="text-error-500 mb-4">
              <BarChart2 className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">Failed to load KPI data</h3>
            <p className="text-neutral-600 mb-4">There was an issue fetching your performance metrics.</p>
            {onRetry && (
              <button
                onClick={onRetry}
                className="btn-premium"
                data-testid="kpi-retry-button"
                aria-label="Retry loading KPI data"
              >
                Try Again
              </button>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6", className)} data-testid="kpi-cards-empty">
        <Card className="card-premium lg:col-span-4">
          <CardContent className="p-8 text-center">
            <div className="text-neutral-400 mb-4">
              <BarChart2 className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">No data available</h3>
            <p className="text-neutral-600">Start creating content to see your performance metrics.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn("grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6", className)} data-testid="kpi-cards">
      {data.map((kpi, index) => {
        const Icon = kpi.icon;
        const isPositive = kpi.trend === "up";
        const isNegative = kpi.trend === "down";
        
        return (
          <Card 
            key={index} 
            className={cn(
              "card-premium card-premium-hover group",
              kpi.status === "critical" && "border-error-200 bg-error-50/30",
              kpi.status === "warning" && "border-warning-200 bg-warning-50/30"
            )}
            data-testid={`kpi-card-${index}`}
          >
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-sm font-medium text-neutral-600 truncate" data-testid="kpi-title">
                      {kpi.title}
                    </p>
                    {kpi.status && (
                      <Badge 
                        variant="secondary" 
                        className={cn(
                          "text-xs px-2 py-0.5",
                          kpi.status === "good" && "bg-success-100 text-success-700",
                          kpi.status === "warning" && "bg-warning-100 text-warning-700",
                          kpi.status === "critical" && "bg-error-100 text-error-700"
                        )}
                        data-testid="kpi-status-badge"
                      >
                        {kpi.status}
                      </Badge>
                    )}
                  </div>
                  
                  <p className="text-3xl font-bold text-neutral-900 mb-2" data-testid="kpi-value">
                    {kpi.value}
                  </p>
                  
                  <div className="flex items-center gap-2 mb-1">
                    {kpi.trend !== "neutral" && (
                      <>
                        {isPositive ? (
                          <ArrowUpRight className="h-4 w-4 text-success-600" aria-hidden="true" />
                        ) : (
                          <ArrowDownRight className="h-4 w-4 text-error-600" aria-hidden="true" />
                        )}
                        <span 
                          className={cn(
                            "text-sm font-medium",
                            isPositive && "text-success-600",
                            isNegative && "text-error-600"
                          )}
                          data-testid="kpi-change"
                        >
                          {kpi.change}
                        </span>
                      </>
                    )}
                    {kpi.period && (
                      <span className="text-sm text-neutral-500" data-testid="kpi-period">
                        vs {kpi.period}
                      </span>
                    )}
                  </div>
                  
                  {kpi.description && (
                    <p className="text-xs text-neutral-500 truncate" data-testid="kpi-description">
                      {kpi.description}
                    </p>
                  )}
                  
                  {kpi.target && (
                    <div className="mt-2 flex items-center gap-1">
                      <Target className="h-3 w-3 text-neutral-400" aria-hidden="true" />
                      <span className="text-xs text-neutral-500" data-testid="kpi-target">
                        Target: {kpi.target}
                      </span>
                    </div>
                  )}
                </div>
                
                <div className={cn(
                  "p-3 rounded-2xl transition-all duration-200 group-hover:scale-105",
                  kpi.bgColor
                )} data-testid="kpi-icon">
                  <Icon className={cn("h-6 w-6", kpi.color)} aria-hidden="true" />
                </div>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}

// Predefined KPI configurations for common metrics
export const KPI_CONFIGS = {
  posts: {
    title: "Total Posts",
    icon: BarChart2,
    color: "text-brand-600",
    bgColor: "bg-brand-50",
    description: "Content published this month"
  },
  engagements: {
    title: "Engagements",
    icon: MessageSquare,
    color: "text-success-600",
    bgColor: "bg-success-50",
    description: "Total interactions received"
  },
  impressions: {
    title: "Impressions",
    icon: Eye,
    color: "text-warning-600",
    bgColor: "bg-warning-50",
    description: "Total views across platforms"
  },
  conversions: {
    title: "Conversions",
    icon: TrendingUp,
    color: "text-error-600",
    bgColor: "bg-error-50",
    description: "Conversion rate percentage"
  },
  reach: {
    title: "Reach",
    icon: Users,
    color: "text-brand-600",
    bgColor: "bg-brand-50",
    description: "Unique users reached"
  },
  clicks: {
    title: "Clicks",
    icon: MousePointer,
    color: "text-success-600",
    bgColor: "bg-success-50",
    description: "Total clicks generated"
  },
  likes: {
    title: "Likes",
    icon: Heart,
    color: "text-error-600",
    bgColor: "bg-error-50",
    description: "Total likes received"
  },
  shares: {
    title: "Shares",
    icon: Share2,
    color: "text-warning-600",
    bgColor: "bg-warning-50",
    description: "Total shares generated"
  },
  revenue: {
    title: "Revenue",
    icon: DollarSign,
    color: "text-success-600",
    bgColor: "bg-success-50",
    description: "Revenue generated from content"
  },
  scheduled: {
    title: "Scheduled",
    icon: Calendar,
    color: "text-brand-600",
    bgColor: "bg-brand-50",
    description: "Posts scheduled for future"
  },
  avgTime: {
    title: "Avg. Time",
    icon: Clock,
    color: "text-neutral-600",
    bgColor: "bg-neutral-50",
    description: "Average engagement time"
  }
} as const;

// Helper function to create KPI data
export function createKPIData(
  type: keyof typeof KPI_CONFIGS,
  value: string,
  change: string,
  trend: "up" | "down" | "neutral" = "neutral",
  overrides: Partial<KPIData> = {}
): KPIData {
  const config = KPI_CONFIGS[type];
  return {
    ...config,
    value,
    change,
    trend,
    ...overrides
  };
}
