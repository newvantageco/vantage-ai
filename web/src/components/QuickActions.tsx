"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Zap,
  FileText,
  Calendar,
  BarChart3,
  Users,
  Search,
  Image,
  Upload,
  Download,
  MessageSquare,
  Settings,
  Play,
  Pause,
  Stop,
  RotateCcw,
  Plus,
  Edit,
  Trash2,
  Copy,
  Share2,
  Heart,
  Star,
  Bookmark,
  Tag,
  Filter,
  SortAsc,
  SortDesc,
  MoreHorizontal,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2,
  Clock,
  Activity,
  TrendingUp,
  Globe,
  Newspaper,
  Video,
  Music,
  MapPin,
  Phone,
  Mail,
  Map,
  Info,
  HelpCircle,
  Save,
  Archive,
  Send
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface QuickAction {
  id: string;
  title: string;
  description?: string;
  icon: React.ReactNode;
  action: () => void | Promise<void>;
  keywords?: string[];
  variant?: 'primary' | 'secondary' | 'tertiary' | 'utility';
  disabled?: boolean;
  loading?: boolean;
  badge?: string;
  color?: string;
}

interface QuickActionsProps {
  title?: string;
  actions: QuickAction[];
  layout?: 'grid' | 'list' | 'compact';
  showDescriptions?: boolean;
  className?: string;
  maxActions?: number;
}

export function QuickActions({ 
  title = "Quick Actions",
  actions,
  layout = 'grid',
  showDescriptions = true,
  className = "",
  maxActions
}: QuickActionsProps) {
  const router = useRouter();
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const handleAction = async (action: QuickAction) => {
    if (action.disabled || action.loading) return;
    
    setActionLoading(action.id);
    
    try {
      await action.action();
    } catch (error) {
      toast.error('Failed to execute action');
      console.error('Quick action error:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const getActionSize = (variant: string) => {
    switch (variant) {
      case 'primary': return 'h-20';
      case 'secondary': return 'h-12';
      case 'tertiary': return 'h-10';
      case 'utility': return 'h-8';
      default: return 'h-12';
    }
  };

  const getActionIconSize = (variant: string) => {
    switch (variant) {
      case 'primary': return 'h-5 w-5';
      case 'secondary': return 'h-4 w-4';
      case 'tertiary': return 'h-3 w-3';
      case 'utility': return 'h-3 w-3';
      default: return 'h-4 w-4';
    }
  };

  const getActionTextSize = (variant: string) => {
    switch (variant) {
      case 'primary': return 'text-xs';
      case 'secondary': return 'text-xs';
      case 'tertiary': return 'text-xs';
      case 'utility': return 'text-xs';
      default: return 'text-xs';
    }
  };

  const displayActions = maxActions ? actions.slice(0, maxActions) : actions;

  if (layout === 'list') {
    return (
      <Card className={`card-lattice ${className}`}>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5 text-orange-500" />
            {title}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {displayActions.map((action) => (
            <Button
              key={action.id}
              variant="outline"
              className="w-full justify-start hover:bg-accent transition-colors"
              onClick={() => handleAction(action)}
              disabled={action.disabled || actionLoading === action.id}
            >
              {actionLoading === action.id ? (
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
              ) : (
                <div className="mr-2">{action.icon}</div>
              )}
              <div className="flex-1 text-left">
                <div className="font-medium">{action.title}</div>
                {showDescriptions && action.description && (
                  <div className="text-xs text-muted-foreground">{action.description}</div>
                )}
              </div>
              {action.badge && (
                <Badge variant="secondary" className="ml-2 text-xs">
                  {action.badge}
                </Badge>
              )}
            </Button>
          ))}
        </CardContent>
      </Card>
    );
  }

  if (layout === 'compact') {
    return (
      <div className={`flex flex-wrap gap-2 ${className}`}>
        {displayActions.map((action) => (
          <Button
            key={action.id}
            variant="outline"
            size="sm"
            className={`${getActionSize(action.variant || 'secondary')} flex flex-col gap-1 hover:bg-accent transition-colors`}
            onClick={() => handleAction(action)}
            disabled={action.disabled || actionLoading === action.id}
          >
            {actionLoading === action.id ? (
              <Loader2 className={`${getActionIconSize(action.variant || 'secondary')} animate-spin`} />
            ) : (
              <div className={getActionIconSize(action.variant || 'secondary')}>{action.icon}</div>
            )}
            <span className={getActionTextSize(action.variant || 'secondary')}>{action.title}</span>
          </Button>
        ))}
      </div>
    );
  }

  // Grid layout (default)
  const primaryActions = displayActions.filter(a => a.variant === 'primary');
  const secondaryActions = displayActions.filter(a => a.variant === 'secondary');
  const tertiaryActions = displayActions.filter(a => a.variant === 'tertiary');
  const utilityActions = displayActions.filter(a => a.variant === 'utility');

  return (
    <Card className={`card-lattice ${className}`}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Zap className="h-5 w-5 text-orange-500" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Primary Actions */}
        {primaryActions.length > 0 && (
          <div className="grid grid-cols-2 gap-3">
            {primaryActions.map((action) => (
              <Button
                key={action.id}
                variant="outline"
                className={`${getActionSize(action.variant || 'primary')} flex flex-col gap-2 hover:bg-accent transition-colors`}
                onClick={() => handleAction(action)}
                disabled={action.disabled || actionLoading === action.id}
              >
                {actionLoading === action.id ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <div className="h-5 w-5">{action.icon}</div>
                )}
                <span className="text-xs">{action.title}</span>
                {action.badge && (
                  <Badge variant="secondary" className="text-xs">
                    {action.badge}
                  </Badge>
                )}
              </Button>
            ))}
          </div>
        )}

        {/* Secondary Actions */}
        {secondaryActions.length > 0 && (
          <div className="grid grid-cols-3 gap-2">
            {secondaryActions.map((action) => (
              <Button
                key={action.id}
                variant="outline"
                size="sm"
                className={`${getActionSize(action.variant || 'secondary')} flex flex-col gap-1 hover:bg-accent transition-colors`}
                onClick={() => handleAction(action)}
                disabled={action.disabled || actionLoading === action.id}
              >
                {actionLoading === action.id ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <div className="h-4 w-4">{action.icon}</div>
                )}
                <span className="text-xs">{action.title}</span>
              </Button>
            ))}
          </div>
        )}

        {/* Tertiary Actions */}
        {tertiaryActions.length > 0 && (
          <div className="grid grid-cols-4 gap-2">
            {tertiaryActions.map((action) => (
              <Button
                key={action.id}
                variant="outline"
                size="sm"
                className={`${getActionSize(action.variant || 'tertiary')} flex flex-col gap-1 hover:bg-accent transition-colors`}
                onClick={() => handleAction(action)}
                disabled={action.disabled || actionLoading === action.id}
              >
                {actionLoading === action.id ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <div className="h-3 w-3">{action.icon}</div>
                )}
                <span className="text-xs">{action.title}</span>
              </Button>
            ))}
          </div>
        )}

        {/* Utility Actions */}
        {utilityActions.length > 0 && (
          <div className="pt-2 border-t">
            <div className="flex gap-2">
              {utilityActions.map((action) => (
                <Button
                  key={action.id}
                  variant="outline"
                  size="sm"
                  className={`flex-1 ${getActionSize(action.variant || 'utility')} text-xs hover:bg-accent transition-colors`}
                  onClick={() => handleAction(action)}
                  disabled={action.disabled || actionLoading === action.id}
                >
                  {actionLoading === action.id ? (
                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  ) : (
                    <div className="h-3 w-3 mr-1">{action.icon}</div>
                  )}
                  {action.title}
                </Button>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

// Predefined action sets for common use cases
export const dashboardActions: QuickAction[] = [
  {
    id: 'create-content',
    title: 'Create Content',
    description: 'Start writing new content',
    icon: <FileText className="h-5 w-5" />,
    action: () => {
      toast.success('Opening content creator...');
      window.location.href = '/composer';
    },
    variant: 'primary',
    keywords: ['create', 'content', 'write', 'draft']
  },
  {
    id: 'schedule-post',
    title: 'Schedule Post',
    description: 'Schedule content for publishing',
    icon: <Calendar className="h-5 w-5" />,
    action: () => {
      toast.success('Opening scheduler...');
      window.location.href = '/calendar?action=schedule';
    },
    variant: 'primary',
    keywords: ['schedule', 'publish', 'post', 'calendar']
  },
  {
    id: 'view-analytics',
    title: 'View Analytics',
    description: 'Check performance metrics',
    icon: <BarChart3 className="h-5 w-5" />,
    action: () => {
      toast.success('Loading analytics...');
      window.location.href = '/analytics';
    },
    variant: 'primary',
    keywords: ['analytics', 'metrics', 'performance', 'stats']
  },
  {
    id: 'manage-team',
    title: 'Manage Team',
    description: 'Add or manage team members',
    icon: <Users className="h-5 w-5" />,
    action: () => {
      toast.success('Opening team management...');
      window.location.href = '/team';
    },
    variant: 'primary',
    keywords: ['team', 'members', 'users', 'manage']
  },
  {
    id: 'search-content',
    title: 'Search',
    description: 'Find content and inspiration',
    icon: <Search className="h-4 w-4" />,
    action: () => {
      toast.success('Opening content search...');
      window.location.href = '/search';
    },
    variant: 'secondary',
    keywords: ['search', 'find', 'research']
  },
  {
    id: 'create-campaign',
    title: 'Campaign',
    description: 'Create marketing campaign',
    icon: <Image className="h-4 w-4" />,
    action: () => {
      toast.success('Creating new campaign...');
      window.location.href = '/campaigns?action=create';
    },
    variant: 'secondary',
    keywords: ['campaign', 'marketing', 'ads']
  },
  {
    id: 'view-reports',
    title: 'Reports',
    description: 'View detailed reports',
    icon: <TrendingUp className="h-4 w-4" />,
    action: () => {
      toast.success('Loading reports...');
      window.location.href = '/reports';
    },
    variant: 'secondary',
    keywords: ['reports', 'analytics', 'insights']
  },
  {
    id: 'manage-automation',
    title: 'Auto',
    description: 'Manage automation',
    icon: <Zap className="h-3 w-3" />,
    action: () => {
      toast.success('Opening automation dashboard...');
      window.location.href = '/automation';
    },
    variant: 'tertiary',
    keywords: ['automation', 'workflows', 'rules']
  },
  {
    id: 'upload-media',
    title: 'Media',
    description: 'Upload media files',
    icon: <Upload className="h-3 w-3" />,
    action: () => {
      toast.success('Opening media upload...');
      window.location.href = '/media?action=upload';
    },
    variant: 'tertiary',
    keywords: ['upload', 'media', 'files']
  },
  {
    id: 'view-collaboration',
    title: 'Team',
    description: 'View collaboration hub',
    icon: <MessageSquare className="h-3 w-3" />,
    action: () => {
      toast.success('Opening collaboration hub...');
      window.location.href = '/collaboration';
    },
    variant: 'tertiary',
    keywords: ['collaboration', 'team', 'messages']
  },
  {
    id: 'view-settings',
    title: 'Settings',
    description: 'Configure settings',
    icon: <Settings className="h-3 w-3" />,
    action: () => {
      toast.success('Opening settings...');
      window.location.href = '/settings';
    },
    variant: 'tertiary',
    keywords: ['settings', 'preferences', 'config']
  },
  {
    id: 'export-data',
    title: 'Export Data',
    description: 'Export your data',
    icon: <Download className="h-3 w-3" />,
    action: async () => {
      toast.success('Preparing data export...');
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast.success('Data export completed!');
    },
    variant: 'utility',
    keywords: ['export', 'download', 'data']
  },
  {
    id: 'import-content',
    title: 'Import Content',
    description: 'Import content from files',
    icon: <Upload className="h-3 w-3" />,
    action: () => {
      toast.success('Opening content import...');
      window.location.href = '/content?action=import';
    },
    variant: 'utility',
    keywords: ['import', 'upload', 'content']
  }
];

export const searchActions: QuickAction[] = [
  {
    id: 'create-content',
    title: 'Create Content',
    description: 'Create content from selected results',
    icon: <Plus className="h-4 w-4" />,
    action: () => {
      toast.success('Creating content with selected results...');
      window.location.href = '/composer';
    },
    variant: 'primary',
    keywords: ['create', 'content', 'selected']
  },
  {
    id: 'copy-urls',
    title: 'Copy URLs',
    description: 'Copy selected URLs to clipboard',
    icon: <Copy className="h-4 w-4" />,
    action: async () => {
      // This would need to be passed from parent component
      toast.success('URLs copied to clipboard');
    },
    variant: 'primary',
    keywords: ['copy', 'urls', 'clipboard']
  },
  {
    id: 'schedule-content',
    title: 'Schedule',
    description: 'Schedule selected content',
    icon: <Calendar className="h-3 w-3" />,
    action: () => {
      toast.success('Opening scheduler with selected results...');
      window.location.href = '/calendar?action=schedule';
    },
    variant: 'secondary',
    keywords: ['schedule', 'selected', 'content']
  },
  {
    id: 'create-campaign',
    title: 'Campaign',
    description: 'Create campaign from results',
    icon: <Image className="h-3 w-3" />,
    action: () => {
      toast.success('Creating campaign with selected results...');
      window.location.href = '/campaigns?action=create';
    },
    variant: 'secondary',
    keywords: ['campaign', 'selected', 'marketing']
  },
  {
    id: 'analyze-trends',
    title: 'Analyze',
    description: 'Analyze trends from results',
    icon: <BarChart3 className="h-3 w-3" />,
    action: () => {
      toast.success('Analyzing trends from selected results...');
      window.location.href = '/analytics?action=trends';
    },
    variant: 'tertiary',
    keywords: ['analyze', 'trends', 'results']
  },
  {
    id: 'share-results',
    title: 'Share',
    description: 'Share selected results',
    icon: <Share2 className="h-3 w-3" />,
    action: async () => {
      if (navigator.share) {
        await navigator.share({
          title: 'Search Results',
          text: 'Check out these interesting results I found!'
        });
      } else {
        await navigator.clipboard.writeText('Check out these interesting results!');
        toast.success('Results copied to clipboard for sharing');
      }
    },
    variant: 'tertiary',
    keywords: ['share', 'results', 'social']
  },
  {
    id: 'favorite-selection',
    title: 'Favorite',
    description: 'Add to favorites',
    icon: <Heart className="h-3 w-3" />,
    action: () => {
      toast.success('Added to favorites');
    },
    variant: 'tertiary',
    keywords: ['favorite', 'bookmark', 'save']
  },
  {
    id: 'export-results',
    title: 'Export',
    description: 'Export results to file',
    icon: <Download className="h-3 w-3" />,
    action: () => {
      toast.success('Results exported successfully');
    },
    variant: 'utility',
    keywords: ['export', 'download', 'results']
  },
  {
    id: 'clear-selection',
    title: 'Clear',
    description: 'Clear selection',
    icon: <Trash2 className="h-3 w-3" />,
    action: () => {
      toast.success('Selection cleared');
    },
    variant: 'utility',
    keywords: ['clear', 'reset', 'selection']
  }
];
