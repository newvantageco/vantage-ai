"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

interface MobileOptimizedCardProps {
  title: string;
  description?: string;
  children: React.ReactNode;
  className?: string;
  headerAction?: React.ReactNode;
  mobileActions?: React.ReactNode;
}

export function MobileOptimizedCard({
  title,
  description,
  children,
  className,
  headerAction,
  mobileActions,
}: MobileOptimizedCardProps) {
  return (
    <Card className={cn(
      "border-0 shadow-lg bg-white/80 backdrop-blur-sm",
      "transition-all duration-300 hover:shadow-xl",
      // Mobile optimizations
      "mx-2 sm:mx-0", // Add margin on mobile
      "rounded-xl sm:rounded-2xl", // Smaller radius on mobile
      className
    )}>
      <CardHeader className="pb-4">
        <div className="flex flex-col space-y-2 sm:flex-row sm:items-center sm:justify-between sm:space-y-0">
          <div className="space-y-1">
            <CardTitle className="text-lg sm:text-xl font-bold text-slate-900">
              {title}
            </CardTitle>
            {description && (
              <CardDescription className="text-sm sm:text-base text-slate-600">
                {description}
              </CardDescription>
            )}
          </div>
          {headerAction && (
            <div className="flex-shrink-0">
              {headerAction}
            </div>
          )}
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {children}
        {mobileActions && (
          <div className="flex flex-col space-y-2 sm:hidden">
            {mobileActions}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

interface MobileStatsCardProps {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down" | string;
  icon: React.ReactNode;
  loading?: boolean;
  className?: string;
  color?: string;
}

export function MobileStatsCard({
  title,
  value,
  change,
  trend,
  icon,
  loading = false,
  className,
  color = "from-blue-500 to-blue-600",
}: MobileStatsCardProps) {
  return (
    <Card className={cn(
      "border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm group",
      "mx-1 sm:mx-0", // Smaller margin on mobile
      className
    )}>
      <CardContent className="p-4 sm:p-6">
        <div className="flex items-center justify-between mb-3 sm:mb-4">
          <div className={cn("p-2 sm:p-3 rounded-lg sm:rounded-xl bg-gradient-to-br shadow-lg", color)}>
            <div className="text-white">
              {icon}
            </div>
          </div>
          <div className="flex items-center space-x-1">
            {loading ? (
              <div className="h-4 w-4 bg-slate-200 rounded animate-pulse" />
            ) : (
              <>
                <div className={cn(
                  "h-4 w-4",
                  trend === "up" ? "text-green-500" : "text-red-500",
                  trend === "down" && "rotate-180"
                )}>
                  <svg viewBox="0 0 24 24" fill="currentColor">
                    <path d="M7 14l5-5 5 5z" />
                  </svg>
                </div>
                <span className={cn(
                  "text-xs sm:text-sm font-semibold",
                  trend === "up" ? "text-green-500" : "text-red-500"
                )}>
                  {change}
                </span>
              </>
            )}
          </div>
        </div>
        <div className="space-y-1">
          <h3 className="text-xl sm:text-2xl font-bold text-slate-900">
            {loading ? (
              <div className="h-6 sm:h-8 w-16 sm:w-20 bg-slate-200 rounded animate-pulse" />
            ) : (
              value
            )}
          </h3>
          <p className="text-xs sm:text-sm font-medium text-slate-600">
            {title}
          </p>
        </div>
      </CardContent>
    </Card>
  );
}

interface MobileActionButtonProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  onClick?: () => void;
  variant?: "default" | "secondary" | "outline" | "ghost";
  className?: string;
}

export function MobileActionButton({
  icon,
  title,
  description,
  onClick,
  variant = "ghost",
  className,
}: MobileActionButtonProps) {
  return (
    <Button
      variant={variant}
      onClick={onClick}
      className={cn(
        "w-full justify-start h-auto p-3 sm:p-4 hover:bg-slate-50 transition-all duration-200 group",
        "text-left", // Ensure text alignment
        className
      )}
    >
      <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600 mr-3 group-hover:scale-110 transition-transform duration-200">
        <div className="text-white">
          {icon}
        </div>
      </div>
      <div className="flex-1 min-w-0">
        <div className="font-semibold text-slate-900 text-sm sm:text-base">
          {title}
        </div>
        <div className="text-xs sm:text-sm text-slate-600 truncate">
          {description}
        </div>
      </div>
    </Button>
  );
}

interface MobileTabListProps {
  tabs: Array<{
    value: string;
    label: string;
    icon: React.ReactNode;
  }>;
  value: string;
  onValueChange: (value: string) => void;
  className?: string;
}

export function MobileTabList({
  tabs,
  value,
  onValueChange,
  className,
}: MobileTabListProps) {
  return (
    <div className={cn(
      "grid w-full gap-1 sm:gap-2",
      `grid-cols-${Math.min(tabs.length, 3)}`, // Max 3 columns on mobile
      className
    )}>
      {tabs.map((tab) => (
        <Button
          key={tab.value}
          variant={value === tab.value ? "default" : "outline"}
          onClick={() => onValueChange(tab.value)}
          className={cn(
            "flex flex-col sm:flex-row items-center space-y-1 sm:space-y-0 sm:space-x-2",
            "h-auto py-3 sm:py-2 px-2 sm:px-4",
            "text-xs sm:text-sm",
            value === tab.value
              ? "bg-blue-600 text-white hover:bg-blue-700"
              : "bg-white text-slate-700 hover:bg-slate-50"
          )}
        >
          <div className="h-4 w-4 sm:h-4 sm:w-4">
            {tab.icon}
          </div>
          <span className="hidden sm:inline">{tab.label}</span>
          <span className="sm:hidden text-xs">{tab.label.split(' ')[0]}</span>
        </Button>
      ))}
    </div>
  );
}

// Mobile-specific utility classes
export const mobileClasses = {
  container: "px-2 sm:px-6", // Responsive padding
  grid: "grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4", // Responsive grid
  text: {
    xs: "text-xs sm:text-sm",
    sm: "text-sm sm:text-base", 
    base: "text-base sm:text-lg",
    lg: "text-lg sm:text-xl",
    xl: "text-xl sm:text-2xl",
  },
  spacing: {
    xs: "space-y-2 sm:space-y-4",
    sm: "space-y-3 sm:space-y-6",
    md: "space-y-4 sm:space-y-8",
    lg: "space-y-6 sm:space-y-12",
  },
  padding: {
    xs: "p-2 sm:p-4",
    sm: "p-3 sm:p-6", 
    md: "p-4 sm:p-8",
    lg: "p-6 sm:p-12",
  }
};
