"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: "default" | "outline" | "secondary" | "ghost" | "link" | "destructive";
  };
  secondaryAction?: {
    label: string;
    onClick: () => void;
    variant?: "default" | "outline" | "secondary" | "ghost" | "link" | "destructive";
  };
  illustration?: "calendar" | "inbox" | "analytics" | "general";
  className?: string;
}

// Simple SVG illustrations
const illustrations = {
  calendar: (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      className="text-muted-foreground/20"
    >
      <rect x="20" y="30" width="80" height="70" rx="4" stroke="currentColor" strokeWidth="2" fill="none"/>
      <line x1="40" y1="20" x2="40" y2="40" stroke="currentColor" strokeWidth="2"/>
      <line x1="80" y1="20" x2="80" y2="40" stroke="currentColor" strokeWidth="2"/>
      <line x1="20" y1="45" x2="100" y2="45" stroke="currentColor" strokeWidth="2"/>
      <circle cx="35" cy="60" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="50" cy="60" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="65" cy="60" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="80" cy="60" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="35" cy="75" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="50" cy="75" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="65" cy="75" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="35" cy="90" r="3" fill="currentColor" opacity="0.3"/>
      <circle cx="50" cy="90" r="3" fill="currentColor" opacity="0.3"/>
    </svg>
  ),
  inbox: (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      className="text-muted-foreground/20"
    >
      <rect x="25" y="35" width="70" height="50" rx="4" stroke="currentColor" strokeWidth="2" fill="none"/>
      <path d="m25 45 35 25 35-25" stroke="currentColor" strokeWidth="2" fill="none"/>
      <circle cx="85" cy="45" r="8" fill="none" stroke="currentColor" strokeWidth="2"/>
      <circle cx="85" cy="45" r="4" fill="currentColor" opacity="0.3"/>
      <line x1="75" y1="25" x2="95" y2="25" stroke="currentColor" strokeWidth="2" opacity="0.3"/>
      <line x1="75" y1="30" x2="90" y2="30" stroke="currentColor" strokeWidth="2" opacity="0.3"/>
    </svg>
  ),
  analytics: (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      className="text-muted-foreground/20"
    >
      <rect x="20" y="30" width="80" height="60" rx="4" stroke="currentColor" strokeWidth="2" fill="none"/>
      <line x1="30" y1="80" x2="30" y2="60" stroke="currentColor" strokeWidth="4" opacity="0.3"/>
      <line x1="45" y1="80" x2="45" y2="45" stroke="currentColor" strokeWidth="4" opacity="0.3"/>
      <line x1="60" y1="80" x2="60" y2="55" stroke="currentColor" strokeWidth="4" opacity="0.3"/>
      <line x1="75" y1="80" x2="75" y2="40" stroke="currentColor" strokeWidth="4" opacity="0.3"/>
      <line x1="90" y1="80" x2="90" y2="50" stroke="currentColor" strokeWidth="4" opacity="0.3"/>
      <circle cx="75" cy="40" r="3" fill="currentColor"/>
      <circle cx="60" cy="55" r="3" fill="currentColor"/>
      <circle cx="90" cy="50" r="3" fill="currentColor"/>
      <path d="m75 40 15 10" stroke="currentColor" strokeWidth="2"/>
      <path d="m60 55 15-15" stroke="currentColor" strokeWidth="2"/>
    </svg>
  ),
  general: (
    <svg
      width="120"
      height="120"
      viewBox="0 0 120 120"
      fill="none"
      className="text-muted-foreground/20"
    >
      <circle cx="60" cy="60" r="40" stroke="currentColor" strokeWidth="2" fill="none"/>
      <circle cx="60" cy="60" r="20" stroke="currentColor" strokeWidth="2" fill="none" opacity="0.5"/>
      <circle cx="60" cy="60" r="8" fill="currentColor" opacity="0.3"/>
      <line x1="60" y1="20" x2="60" y2="30" stroke="currentColor" strokeWidth="2"/>
      <line x1="60" y1="90" x2="60" y2="100" stroke="currentColor" strokeWidth="2"/>
      <line x1="20" y1="60" x2="30" y2="60" stroke="currentColor" strokeWidth="2"/>
      <line x1="90" y1="60" x2="100" y2="60" stroke="currentColor" strokeWidth="2"/>
    </svg>
  ),
};

export function EmptyState({
  icon,
  title,
  description,
  action,
  secondaryAction,
  illustration = "general",
  className,
}: EmptyStateProps) {
  return (
    <Card className={cn("border-0 bg-transparent shadow-none", className)}>
      <CardContent className="flex flex-col items-center justify-center py-16 px-4">
        <div className="flex flex-col items-center text-center space-y-6 max-w-md">
          {/* Illustration or Icon */}
          <div className="flex items-center justify-center">
            {icon || illustrations[illustration]}
          </div>

          {/* Content */}
          <div className="space-y-2">
            <h3 className="text-xl font-semibold text-foreground">{title}</h3>
            <p className="text-muted-foreground leading-relaxed">{description}</p>
          </div>

          {/* Actions */}
          {(action || secondaryAction) && (
            <div className="flex flex-col sm:flex-row gap-3 pt-2">
              {action && (
                <Button
                  onClick={action.onClick}
                  variant={action.variant || "default"}
                  size="lg"
                >
                  {action.label}
                </Button>
              )}
              {secondaryAction && (
                <Button
                  onClick={secondaryAction.onClick}
                  variant={secondaryAction.variant || "outline"}
                  size="lg"
                >
                  {secondaryAction.label}
                </Button>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
