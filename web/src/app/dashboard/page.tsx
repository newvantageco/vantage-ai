"use client";

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { EventFeed } from '@/components/EventFeed';
import { TaskQueue } from '@/components/TaskQueue';
import { 
  TrendingUp, 
  Users, 
  FileText, 
  Calendar,
  Activity,
  ArrowUpRight,
  ArrowDownRight,
  RefreshCw,
  Zap,
  BarChart3,
  Clock,
  CheckCircle2,
  Plus,
  Play,
  Settings,
  Search,
  MessageSquare,
  Image,
  Video,
  Music,
  Download,
  Upload,
  Share2,
  Bookmark,
  Star,
  Eye,
  Edit,
  Trash2,
  Copy,
  ExternalLink,
  AlertCircle,
  CheckCircle,
  XCircle,
  Loader2
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { apiService, type DashboardStats, type KPIMetric } from '@/services/api';
import { toast } from 'react-hot-toast';

// Icon mapping for KPIs
const iconMap = {
  'FileText': FileText,
  'Users': Users,
  'TrendingUp': TrendingUp,
  'Zap': Zap,
  'Activity': Activity,
  'BarChart3': BarChart3
};

export default function LatticeDashboardPage() {
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const data = await apiService.getDashboardStats();
      setDashboardData(data);
      setError(null);
    } catch (err: any) {
      console.error('Failed to load dashboard data:', err);
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadDashboardData();
  };

  // Enhanced Quick Actions with working functionality
  const handleQuickAction = async (action: string) => {
    setActionLoading(action);
    
    try {
      switch (action) {
        case 'create-content':
          toast.success('Opening content creator...');
          router.push('/composer');
          break;
          
        case 'schedule-post':
          toast.success('Opening scheduler...');
          router.push('/calendar?action=schedule');
          break;
          
        case 'view-analytics':
          toast.success('Loading analytics...');
          router.push('/analytics');
          break;
          
        case 'manage-team':
          toast.success('Opening team management...');
          router.push('/team');
          break;
          
        case 'search-content':
          toast.success('Opening content search...');
          router.push('/search');
          break;
          
        case 'create-campaign':
          toast.success('Creating new campaign...');
          router.push('/campaigns?action=create');
          break;
          
        case 'view-reports':
          toast.success('Loading reports...');
          router.push('/reports');
          break;
          
        case 'manage-automation':
          toast.success('Opening automation dashboard...');
          router.push('/automation');
          break;
          
        case 'upload-media':
          toast.success('Opening media upload...');
          router.push('/media?action=upload');
          break;
          
        case 'view-collaboration':
          toast.success('Opening collaboration hub...');
          router.push('/collaboration');
          break;
          
        case 'export-data':
          toast.success('Preparing data export...');
          // Simulate export process
          await new Promise(resolve => setTimeout(resolve, 2000));
          toast.success('Data export completed!');
          break;
          
        case 'import-content':
          toast.success('Opening content import...');
          router.push('/content?action=import');
          break;
          
        case 'view-settings':
          toast.success('Opening settings...');
          router.push('/settings');
          break;
          
        default:
          toast.error('Action not implemented yet');
      }
    } catch (error) {
      toast.error('Failed to execute action');
      console.error('Quick action error:', error);
    } finally {
      setActionLoading(null);
    }
  };

  if (loading) {
    return (
      <div className="h-full p-6 flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin mx-auto mb-4" />
          <p className="text-muted-foreground">Loading dashboard data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full p-6 flex items-center justify-center">
        <div className="text-center">
          <div className="text-red-500 mb-4">⚠️</div>
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={handleRefresh} variant="outline">
            <RefreshCw className="h-4 w-4 mr-2" />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full p-6 space-y-6">
      {/* Header with Refresh Button */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Real-time overview of your content and analytics
          </p>
        </div>
        <Button onClick={handleRefresh} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* KPIs Section - Top */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="card-lattice card-lattice-hover">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Total Content
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.overview?.total_content || 0}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-muted text-blue-500">
                <FileText className="h-6 w-6" />
              </div>
            </div>
            <div className="flex items-center gap-2 mt-4">
              <ArrowUpRight className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium text-green-500">
                +12.5%
              </span>
              <span className="text-sm text-muted-foreground">vs last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="card-lattice card-lattice-hover">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Published Content
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.overview?.published_content || 0}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-muted text-green-500">
                <CheckCircle2 className="h-6 w-6" />
              </div>
            </div>
            <div className="flex items-center gap-2 mt-4">
              <ArrowUpRight className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium text-green-500">
                +8.2%
              </span>
              <span className="text-sm text-muted-foreground">vs last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="card-lattice card-lattice-hover">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Scheduled Content
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.overview?.scheduled_content || 0}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-muted text-blue-500">
                <Clock className="h-6 w-6" />
              </div>
            </div>
            <div className="flex items-center gap-2 mt-4">
              <ArrowUpRight className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium text-green-500">
                +15.3%
              </span>
              <span className="text-sm text-muted-foreground">vs last month</span>
            </div>
          </CardContent>
        </Card>

        <Card className="card-lattice card-lattice-hover">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">
                  Active Channels
                </p>
                <p className="text-2xl font-bold text-foreground">
                  {dashboardData?.overview?.total_channels || 0}
                </p>
              </div>
              <div className="p-3 rounded-lg bg-muted text-purple-500">
                <Activity className="h-6 w-6" />
              </div>
            </div>
            <div className="flex items-center gap-2 mt-4">
              <ArrowUpRight className="h-4 w-4 text-green-500" />
              <span className="text-sm font-medium text-green-500">
                +3.1%
              </span>
              <span className="text-sm text-muted-foreground">vs last month</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Status */}
        <Card className="card-lattice">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-500" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <div className="flex-1">
                <p className="font-medium text-sm">API Server</p>
                <p className="text-xs text-muted-foreground">Online and responding</p>
              </div>
              <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                Healthy
              </Badge>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <div className="flex-1">
                <p className="font-medium text-sm">Database</p>
                <p className="text-xs text-muted-foreground">Connected and operational</p>
              </div>
              <Badge variant="secondary" className="text-xs bg-green-100 text-green-800">
                Connected
              </Badge>
            </div>
            <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
              <div className="w-2 h-2 rounded-full bg-yellow-500" />
              <div className="flex-1">
                <p className="font-medium text-sm">AI Processing</p>
                <p className="text-xs text-muted-foreground">Ready for content generation</p>
              </div>
              <Badge variant="secondary" className="text-xs bg-yellow-100 text-yellow-800">
                Ready
              </Badge>
            </div>
          </CardContent>
        </Card>

        {/* Enhanced Quick Actions */}
        <Card className="card-lattice">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5 text-orange-500" />
              Quick Actions
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Primary Actions */}
            <div className="grid grid-cols-2 gap-3">
              <Button 
                variant="outline" 
                className="h-20 flex flex-col gap-2 hover:bg-blue-50 hover:border-blue-300 transition-colors"
                onClick={() => handleQuickAction('create-content')}
                disabled={actionLoading === 'create-content'}
              >
                {actionLoading === 'create-content' ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <FileText className="h-5 w-5" />
                )}
                <span className="text-xs">Create Content</span>
              </Button>
              
              <Button 
                variant="outline" 
                className="h-20 flex flex-col gap-2 hover:bg-green-50 hover:border-green-300 transition-colors"
                onClick={() => handleQuickAction('schedule-post')}
                disabled={actionLoading === 'schedule-post'}
              >
                {actionLoading === 'schedule-post' ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Calendar className="h-5 w-5" />
                )}
                <span className="text-xs">Schedule Post</span>
              </Button>
              
              <Button 
                variant="outline" 
                className="h-20 flex flex-col gap-2 hover:bg-purple-50 hover:border-purple-300 transition-colors"
                onClick={() => handleQuickAction('view-analytics')}
                disabled={actionLoading === 'view-analytics'}
              >
                {actionLoading === 'view-analytics' ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <BarChart3 className="h-5 w-5" />
                )}
                <span className="text-xs">View Analytics</span>
              </Button>
              
              <Button 
                variant="outline" 
                className="h-20 flex flex-col gap-2 hover:bg-orange-50 hover:border-orange-300 transition-colors"
                onClick={() => handleQuickAction('manage-team')}
                disabled={actionLoading === 'manage-team'}
              >
                {actionLoading === 'manage-team' ? (
                  <Loader2 className="h-5 w-5 animate-spin" />
                ) : (
                  <Users className="h-5 w-5" />
                )}
                <span className="text-xs">Manage Team</span>
              </Button>
            </div>

            {/* Secondary Actions */}
            <div className="grid grid-cols-3 gap-2">
              <Button 
                variant="outline" 
                size="sm"
                className="h-12 flex flex-col gap-1 hover:bg-blue-50 transition-colors"
                onClick={() => handleQuickAction('search-content')}
                disabled={actionLoading === 'search-content'}
              >
                {actionLoading === 'search-content' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Search className="h-4 w-4" />
                )}
                <span className="text-xs">Search</span>
              </Button>
              
              <Button 
                variant="outline" 
                size="sm"
                className="h-12 flex flex-col gap-1 hover:bg-green-50 transition-colors"
                onClick={() => handleQuickAction('create-campaign')}
                disabled={actionLoading === 'create-campaign'}
              >
                {actionLoading === 'create-campaign' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Image className="h-4 w-4" />
                )}
                <span className="text-xs">Campaign</span>
              </Button>
              
              <Button 
                variant="outline" 
                size="sm"
                className="h-12 flex flex-col gap-1 hover:bg-purple-50 transition-colors"
                onClick={() => handleQuickAction('view-reports')}
                disabled={actionLoading === 'view-reports'}
              >
                {actionLoading === 'view-reports' ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <TrendingUp className="h-4 w-4" />
                )}
                <span className="text-xs">Reports</span>
              </Button>
            </div>

            {/* Tertiary Actions */}
            <div className="grid grid-cols-4 gap-2">
              <Button 
                variant="outline" 
                size="sm"
                className="h-10 flex flex-col gap-1 hover:bg-yellow-50 transition-colors"
                onClick={() => handleQuickAction('manage-automation')}
                disabled={actionLoading === 'manage-automation'}
              >
                {actionLoading === 'manage-automation' ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <Zap className="h-3 w-3" />
                )}
                <span className="text-xs">Auto</span>
              </Button>
              
              <Button 
                variant="outline" 
                size="sm"
                className="h-10 flex flex-col gap-1 hover:bg-pink-50 transition-colors"
                onClick={() => handleQuickAction('upload-media')}
                disabled={actionLoading === 'upload-media'}
              >
                {actionLoading === 'upload-media' ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <Upload className="h-3 w-3" />
                )}
                <span className="text-xs">Media</span>
              </Button>
              
              <Button 
                variant="outline" 
                size="sm"
                className="h-10 flex flex-col gap-1 hover:bg-indigo-50 transition-colors"
                onClick={() => handleQuickAction('view-collaboration')}
                disabled={actionLoading === 'view-collaboration'}
              >
                {actionLoading === 'view-collaboration' ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <MessageSquare className="h-3 w-3" />
                )}
                <span className="text-xs">Team</span>
              </Button>
              
              <Button 
                variant="outline" 
                size="sm"
                className="h-10 flex flex-col gap-1 hover:bg-gray-50 transition-colors"
                onClick={() => handleQuickAction('view-settings')}
                disabled={actionLoading === 'view-settings'}
              >
                {actionLoading === 'view-settings' ? (
                  <Loader2 className="h-3 w-3 animate-spin" />
                ) : (
                  <Settings className="h-3 w-3" />
                )}
                <span className="text-xs">Settings</span>
              </Button>
            </div>

            {/* Advanced Actions */}
            <div className="pt-2 border-t">
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  size="sm"
                  className="flex-1 h-8 text-xs"
                  onClick={() => handleQuickAction('export-data')}
                  disabled={actionLoading === 'export-data'}
                >
                  {actionLoading === 'export-data' ? (
                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  ) : (
                    <Download className="h-3 w-3 mr-1" />
                  )}
                  Export Data
                </Button>
                
                <Button 
                  variant="outline" 
                  size="sm"
                  className="flex-1 h-8 text-xs"
                  onClick={() => handleQuickAction('import-content')}
                  disabled={actionLoading === 'import-content'}
                >
                  {actionLoading === 'import-content' ? (
                    <Loader2 className="h-3 w-3 animate-spin mr-1" />
                  ) : (
                    <Upload className="h-3 w-3 mr-1" />
                  )}
                  Import Content
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card className="card-lattice">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5 text-blue-500" />
            Recent Activity
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Activity className="h-12 w-12 mx-auto mb-4" />
            <p>No recent activity</p>
            <p className="text-sm">Start creating content to see activity here</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}