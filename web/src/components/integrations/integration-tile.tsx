"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import { useRelativeTimeMinutes } from "@/lib/time-utils";

// Component for rendering relative time that prevents hydration issues
function RelativeTime({ timestamp }: { timestamp: Date }) {
  const relativeTime = useRelativeTimeMinutes(timestamp, 60000); // Update every minute
  return <span>{relativeTime}</span>;
}

import {
  Check,
  X,
  ExternalLink,
  Settings,
  AlertCircle,
  Clock,
  RefreshCw,
  MoreHorizontal,
  Zap,
  Shield,
  Users,
  BarChart2,
  Calendar,
  MessageSquare,
  Image,
  Video,
  FileText,
  Globe,
  Smartphone,
  Monitor,
  Database,
  Lock,
  Key,
  Link,
  Download,
  Upload,
  Trash2,
  Edit,
  Eye,
  EyeOff
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { toast } from "react-hot-toast";

interface IntegrationScope {
  name: string;
  description: string;
  required: boolean;
  granted: boolean;
}

interface Integration {
  id: string;
  name: string;
  description: string;
  category: "social" | "analytics" | "design" | "automation" | "storage" | "other";
  status: "connected" | "disconnected" | "error" | "pending" | "expired";
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  bgColor: string;
  connectedAt?: Date;
  lastSync?: Date;
  scopes: IntegrationScope[];
  features: string[];
  limitations?: string[];
  setupRequired?: boolean;
  requiresReauth?: boolean;
  errorMessage?: string;
  isPopular?: boolean;
  isNew?: boolean;
  isBeta?: boolean;
}

interface IntegrationTileProps {
  integration: Integration;
  loading?: boolean;
  onConnect?: (integrationId: string) => void;
  onDisconnect?: (integrationId: string) => void;
  onReconnect?: (integrationId: string) => void;
  onConfigure?: (integrationId: string) => void;
  onRefresh?: (integrationId: string) => void;
  onViewDetails?: (integrationId: string) => void;
  className?: string;
}

const CATEGORY_ICONS = {
  social: Globe,
  analytics: BarChart2,
  design: Image,
  automation: Zap,
  storage: Database,
  other: Settings
} as const;

const STATUS_COLORS = {
  connected: "bg-success-100 text-success-700",
  disconnected: "bg-neutral-100 text-neutral-700",
  error: "bg-error-100 text-error-700",
  pending: "bg-warning-100 text-warning-700",
  expired: "bg-error-100 text-error-700"
} as const;

const STATUS_ICONS = {
  connected: Check,
  disconnected: X,
  error: AlertCircle,
  pending: Clock,
  expired: AlertCircle
} as const;

export function IntegrationTile({
  integration,
  loading = false,
  onConnect,
  onDisconnect,
  onReconnect,
  onConfigure,
  onRefresh,
  onViewDetails,
  className
}: IntegrationTileProps) {
  const [isConnecting, setIsConnecting] = useState(false);
  const [showScopes, setShowScopes] = useState(false);

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      await onConnect?.(integration.id);
      toast.success(`${integration.name} connected successfully!`);
    } catch (error) {
      toast.error(`Failed to connect ${integration.name}`);
    } finally {
      setIsConnecting(false);
    }
  };

  const handleDisconnect = () => {
    onDisconnect?.(integration.id);
    toast.success(`${integration.name} disconnected`);
  };

  const handleReconnect = () => {
    onReconnect?.(integration.id);
    toast.success(`Reconnecting to ${integration.name}...`);
  };

  const handleConfigure = () => {
    onConfigure?.(integration.id);
  };

  const handleRefresh = () => {
    onRefresh?.(integration.id);
    toast.success(`${integration.name} data refreshed`);
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  // Removed getTimeAgo function - now using formatRelativeTimeMinutes from time-utils

  const StatusIcon = STATUS_ICONS[integration.status];
  const CategoryIcon = CATEGORY_ICONS[integration.category];

  if (loading) {
    return (
      <Card className={cn("card-premium", className)} data-testid="integration-tile-loading">
        <CardHeader>
          <div className="flex items-center gap-3">
            <Skeleton className="h-10 w-10 rounded-xl" />
            <div className="flex-1">
              <Skeleton className="h-5 w-32 mb-2" />
              <Skeleton className="h-4 w-48" />
            </div>
            <Skeleton className="h-6 w-16" />
          </div>
        </CardHeader>
        <CardContent>
          <Skeleton className="h-4 w-full mb-2" />
          <Skeleton className="h-4 w-3/4" />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className={cn("card-premium card-premium-hover group", className)} data-testid={`integration-tile-${integration.id}`}>
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center gap-3">
            <div className={cn(
              "w-10 h-10 rounded-xl flex items-center justify-center",
              integration.bgColor
            )}>
              <integration.icon className={cn("h-5 w-5", integration.color)} />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <CardTitle className="text-lg font-semibold truncate">
                  {integration.name}
                </CardTitle>
                {integration.isPopular && (
                  <Badge className="bg-brand-100 text-brand-700 border-0 text-xs">
                    Popular
                  </Badge>
                )}
                {integration.isNew && (
                  <Badge className="bg-success-100 text-success-700 border-0 text-xs">
                    New
                  </Badge>
                )}
                {integration.isBeta && (
                  <Badge className="bg-warning-100 text-warning-700 border-0 text-xs">
                    Beta
                  </Badge>
                )}
              </div>
              <p className="text-sm text-neutral-600 line-clamp-2">
                {integration.description}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <Badge className={STATUS_COLORS[integration.status]}>
              <StatusIcon className="h-3 w-3 mr-1" />
              {integration.status}
            </Badge>
            
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => onViewDetails?.(integration.id)}
                  data-testid={`view-details-${integration.id}`}
                >
                  <Eye className="h-4 w-4 mr-2" />
                  View Details
                </DropdownMenuItem>
                {integration.status === "connected" && (
                  <>
                    <DropdownMenuItem
                      onClick={handleConfigure}
                      data-testid={`configure-${integration.id}`}
                    >
                      <Settings className="h-4 w-4 mr-2" />
                      Configure
                    </DropdownMenuItem>
                    <DropdownMenuItem
                      onClick={handleRefresh}
                      data-testid={`refresh-${integration.id}`}
                    >
                      <RefreshCw className="h-4 w-4 mr-2" />
                      Refresh Data
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem
                      onClick={handleDisconnect}
                      className="text-error-600"
                      data-testid={`disconnect-${integration.id}`}
                    >
                      <X className="h-4 w-4 mr-2" />
                      Disconnect
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Status Details */}
        {integration.status === "connected" && (
          <div className="space-y-2">
            {integration.connectedAt && (
              <div className="flex items-center gap-2 text-sm text-neutral-600">
                <Check className="h-4 w-4 text-success-600" />
                <span>Connected {formatDate(integration.connectedAt)}</span>
              </div>
            )}
            {integration.lastSync && (
              <div className="flex items-center gap-2 text-sm text-neutral-600">
                <RefreshCw className="h-4 w-4 text-neutral-400" />
                <span>Last sync: <RelativeTime timestamp={integration.lastSync} /></span>
              </div>
            )}
          </div>
        )}

        {integration.status === "error" && integration.errorMessage && (
          <div className="flex items-start gap-2 p-3 bg-error-50 rounded-lg">
            <AlertCircle className="h-4 w-4 text-error-600 mt-0.5 flex-shrink-0" />
            <div className="text-sm text-error-700">
              <div className="font-medium">Connection Error</div>
              <div className="text-xs mt-1">{integration.errorMessage}</div>
            </div>
          </div>
        )}

        {/* Features */}
        <div className="space-y-2">
          <div className="text-sm font-medium text-neutral-700">Features</div>
          <div className="flex flex-wrap gap-1">
            {integration.features.slice(0, 3).map((feature, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {feature}
              </Badge>
            ))}
            {integration.features.length > 3 && (
              <Badge variant="outline" className="text-xs">
                +{integration.features.length - 3} more
              </Badge>
            )}
          </div>
        </div>

        {/* Scopes */}
        {integration.scopes.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="text-sm font-medium text-neutral-700">Permissions</div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setShowScopes(!showScopes)}
                className="h-6 text-xs"
                data-testid={`toggle-scopes-${integration.id}`}
              >
                {showScopes ? <EyeOff className="h-3 w-3" /> : <Eye className="h-3 w-3" />}
                {showScopes ? "Hide" : "Show"}
              </Button>
            </div>
            
            {showScopes && (
              <div className="space-y-2">
                {integration.scopes.map((scope, index) => (
                  <div key={index} className="flex items-start gap-2 text-xs">
                    <div className={cn(
                      "w-4 h-4 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5",
                      scope.granted ? "bg-success-100" : "bg-neutral-100"
                    )}>
                      {scope.granted ? (
                        <Check className="h-2 w-2 text-success-600" />
                      ) : (
                        <X className="h-2 w-2 text-neutral-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="font-medium">{scope.name}</div>
                      <div className="text-neutral-500">{scope.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Limitations */}
        {integration.limitations && integration.limitations.length > 0 && (
          <div className="space-y-2">
            <div className="text-sm font-medium text-neutral-700">Limitations</div>
            <div className="space-y-1">
              {integration.limitations.map((limitation, index) => (
                <div key={index} className="flex items-start gap-2 text-xs text-neutral-600">
                  <X className="h-3 w-3 text-neutral-400 mt-0.5 flex-shrink-0" />
                  <span>{limitation}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="pt-2">
          {integration.status === "connected" ? (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleConfigure}
                className="flex-1"
                data-testid={`configure-button-${integration.id}`}
              >
                <Settings className="h-4 w-4 mr-2" />
                Configure
              </Button>
              {integration.requiresReauth && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleReconnect}
                  data-testid={`reconnect-button-${integration.id}`}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              )}
            </div>
          ) : integration.status === "error" ? (
            <div className="flex items-center gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleReconnect}
                className="flex-1"
                data-testid={`reconnect-button-${integration.id}`}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Reconnect
              </Button>
            </div>
          ) : (
            <Button
              onClick={handleConnect}
              disabled={isConnecting}
              className="w-full btn-premium"
              data-testid={`connect-button-${integration.id}`}
            >
              {isConnecting ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Connecting...
                </>
              ) : (
                <>
                  <Link className="h-4 w-4 mr-2" />
                  Connect {integration.name}
                </>
              )}
            </Button>
          )}
        </div>

        {/* Setup Required */}
        {integration.setupRequired && (
          <div className="flex items-center gap-2 p-2 bg-warning-50 rounded-lg">
            <AlertCircle className="h-4 w-4 text-warning-600" />
            <span className="text-sm text-warning-700">
              Additional setup required after connection
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
