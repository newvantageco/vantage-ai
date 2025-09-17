"use client";

import { useRouter } from "next/navigation";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { 
  DashboardIcon,
  ContentIcon,
  AnalyticsIcon,
  MessageIcon,
  CalendarIcon,
  TargetIcon,
  BotIcon,
  SparklesIcon,
  UsersIcon,
  ShieldIcon,
  CreditCardIcon,
  PaletteIcon,
  SettingsIcon,
  RefreshIcon,
  AlertCircleIcon,
  ActivityIcon,
  ClockIcon,
  FileEditIcon,
  TrendingUpIcon,
  TrendingDownIcon
} from "@/components/ui/custom-icons";
import { useRealtimeData } from "@/hooks/useRealtimeData";
import { useDashboardStats, useRecentActivity } from "@/hooks/useRealtimeData";
import { MobileOptimizedCard, MobileStatsCard, MobileActionButton, mobileClasses } from "@/components/MobileOptimizedCard";
import { AIDashboardWidget } from "@/components/AIDashboardWidget";

export default function DashboardPage() {
  const router = useRouter();
  const { stats, loading: statsLoading, error: statsError, refresh: refreshStats } = useDashboardStats();
  const { activity, loading: activityLoading, error: activityError, refresh: refreshActivity } = useRecentActivity();

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatPercentage = (num: number) => {
    const sign = num >= 0 ? '+' : '';
    return `${sign}${num.toFixed(1)}%`;
  };

  const getTimeAgo = (timestamp: string) => {
    const now = new Date();
    const time = new Date(timestamp);
    const diffInMinutes = Math.floor((now.getTime() - time.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const statsData = [
    {
      title: "Total Posts",
      value: stats ? formatNumber(stats.total_posts) : "0",
      change: stats ? formatPercentage(stats.change_percentages?.total_posts ?? 0) : "+0%",
      trend: (stats?.change_percentages?.total_posts ?? 0) >= 0 ? "up" : "down",
      icon: <ContentIcon className="h-6 w-6" />,
      loading: statsLoading,
      color: "from-blue-500 to-blue-600",
    },
    {
      title: "Engagement Rate",
      value: stats ? `${stats.engagement_rate.toFixed(1)}%` : "0%",
      change: stats ? formatPercentage(stats.change_percentages?.engagement_rate ?? 0) : "+0%",
      trend: (stats?.change_percentages?.engagement_rate ?? 0) >= 0 ? "up" : "down",
      icon: <TargetIcon className="h-6 w-6" />,
      loading: statsLoading,
      color: "from-green-500 to-green-600",
    },
    {
      title: "Active Conversations",
      value: stats ? formatNumber(stats.active_conversations) : "0",
      change: stats ? formatPercentage(stats.change_percentages?.active_conversations ?? 0) : "+0%",
      trend: (stats?.change_percentages?.active_conversations ?? 0) >= 0 ? "up" : "down",
      icon: <MessageIcon className="h-6 w-6" />,
      loading: statsLoading,
      color: "from-purple-500 to-purple-600",
    },
    {
      title: "Scheduled Posts",
      value: stats ? formatNumber(stats.scheduled_posts) : "0",
      change: stats ? formatPercentage(stats.change_percentages?.scheduled_posts ?? 0) : "+0%",
      trend: (stats?.change_percentages?.scheduled_posts ?? 0) >= 0 ? "up" : "down",
      icon: <CalendarIcon className="h-6 w-6" />,
      loading: statsLoading,
      color: "from-orange-500 to-orange-600",
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 p-6">
      <div className="relative z-10 space-y-8">
        {/* Header Tile */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/50">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
                Dashboard
              </h1>
              <p className="text-slate-600 text-lg">
                Welcome back! Here's an overview of your content performance and insights.
              </p>
              {statsError && (
                <div className="flex items-center space-x-2 text-red-600 text-sm">
                  <AlertCircle className="h-4 w-4" />
                  <span>Failed to load some data. Click refresh to retry.</span>
                </div>
              )}
            </div>
            <div className="flex space-x-3">
              <Button 
                variant="outline" 
                onClick={() => { refreshStats(); refreshActivity(); }}
                className="border-slate-300 hover:bg-slate-50"
              >
                <RefreshIcon className="h-4 w-4 mr-2" />
                Refresh
              </Button>
              <Button className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800 text-white border-0 rounded-xl px-6 py-3 shadow-lg hover:shadow-xl transition-all duration-200">
                <AnalyticsIcon className="h-5 w-5 mr-2" />
                View Report
              </Button>
            </div>
          </div>
        </div>

        {/* Stats Grid Tiles */}
        <div className={`grid gap-3 sm:gap-6 ${mobileClasses.grid}`}>
          {statsData.map((stat, index) => (
            <MobileStatsCard
              key={index}
              title={stat.title}
              value={stat.value}
              change={stat.change}
              trend={stat.trend}
              icon={stat.icon}
              loading={stat.loading}
              color={stat.color}
            />
          ))}
        </div>

        {/* Main Content Grid */}
        <div className="grid gap-4 sm:gap-6 lg:grid-cols-3">
          {/* Recent Activity Tile */}
          <MobileOptimizedCard
            title="Recent Activity"
            description="Latest updates from your content and conversations"
            className="lg:col-span-2"
            headerAction={
              <Button variant="ghost" className="text-blue-600 hover:text-blue-700 text-sm">
                View all
              </Button>
            }
          >
              <div className="space-y-4">
                {activityLoading ? (
                  // Loading skeleton
                  Array.from({ length: 4 }).map((_, index) => (
                    <div key={index} className="flex items-start space-x-4 p-4 rounded-xl">
                      <div className="w-3 h-3 rounded-full mt-2 flex-shrink-0 bg-slate-200 animate-pulse" />
                      <div className="flex-1 min-w-0 space-y-2">
                        <div className="h-4 w-3/4 bg-slate-200 rounded animate-pulse" />
                        <div className="h-3 w-full bg-slate-200 rounded animate-pulse" />
                        <div className="h-3 w-1/4 bg-slate-200 rounded animate-pulse" />
                      </div>
                    </div>
                  ))
                ) : activityError ? (
                  <div className="flex items-center justify-center p-8 text-red-600">
                    <div className="text-center">
                      <AlertCircleIcon className="h-8 w-8 mx-auto mb-2" />
                      <p className="text-sm">Failed to load activity</p>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={refreshActivity}
                        className="mt-2"
                      >
                        Retry
                      </Button>
                    </div>
                  </div>
                ) : activity.length === 0 ? (
                  <div className="flex items-center justify-center p-8 text-slate-500">
                    <div className="text-center">
                      <ActivityIcon className="h-8 w-8 mx-auto mb-2" />
                      <p className="text-sm">No recent activity</p>
                    </div>
                  </div>
                ) : (
                  activity.map((activity) => (
                    <div key={activity.id} className="flex items-start space-x-4 p-4 rounded-xl hover:bg-slate-50 transition-colors group">
                      <div className={`w-3 h-3 rounded-full mt-2 flex-shrink-0 ${
                        activity.status === 'success' 
                          ? 'bg-green-500' 
                          : activity.status === 'pending'
                          ? 'bg-orange-500'
                          : 'bg-red-500'
                      }`} />
                      <div className="flex-1 min-w-0 space-y-1">
                        <p className="text-sm font-semibold text-slate-900 group-hover:text-slate-700 transition-colors">
                          {activity.title}
                        </p>
                        <p className="text-sm text-slate-600">
                          {activity.description}
                        </p>
                        <p className="text-xs text-slate-500">
                          {getTimeAgo(activity.time)}
                        </p>
                      </div>
                    </div>
                  ))
                )}
              </div>
          </MobileOptimizedCard>

          {/* Quick Actions Tile */}
          <MobileOptimizedCard
            title="Quick Actions"
            description="Common tasks and shortcuts"
          >
            <div className="space-y-2 sm:space-y-3">
              <MobileActionButton
                icon={<FileEditIcon className="h-5 w-5" />}
                title="Create Template"
                description="Design new content templates"
                onClick={() => router.push('/templates')}
              />
              <MobileActionButton
                icon={<CalendarIcon className="h-5 w-5" />}
                title="Schedule Content"
                description="Plan your content calendar"
                onClick={() => router.push('/planning')}
              />
              <MobileActionButton
                icon={<MessageIcon className="h-5 w-5" />}
                title="Check Messages"
                description="Review customer conversations"
                onClick={() => router.push('/inbox')}
              />
              <MobileActionButton
                icon={<AnalyticsIcon className="h-5 w-5" />}
                title="View Analytics"
                description="Analyze performance metrics"
                onClick={() => router.push('/reports')}
              />
            </div>
          </MobileOptimizedCard>
        </div>

        {/* AI Content Generation Section */}
        <div className="grid gap-4 sm:gap-6 lg:grid-cols-2">
          <AIDashboardWidget className="lg:col-span-1" />
          
          {/* AI Insights Card */}
          <MobileOptimizedCard
            title="AI Insights"
            description="Smart recommendations powered by AI"
            className="lg:col-span-1"
          >
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg border border-purple-200">
                <div className="flex items-start space-x-3">
                  <SparklesIcon className="h-5 w-5 text-purple-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-slate-900">Content Performance</h4>
                    <p className="text-sm text-slate-600 mt-1">
                      Your posts perform 23% better on Tuesdays at 2 PM. Consider scheduling more content during this time.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg border border-green-200">
                <div className="flex items-start space-x-3">
                  <TargetIcon className="h-5 w-5 text-green-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-slate-900">Engagement Boost</h4>
                    <p className="text-sm text-slate-600 mt-1">
                      Adding 3-5 hashtags increases engagement by 40%. Try including more relevant hashtags in your next post.
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-orange-50 to-amber-50 rounded-lg border border-orange-200">
                <div className="flex items-start space-x-3">
                  <MessageIcon className="h-5 w-5 text-orange-600 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-slate-900">Audience Growth</h4>
                    <p className="text-sm text-slate-600 mt-1">
                      Your audience is most active between 6-8 PM. Post during these hours for maximum reach.
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </MobileOptimizedCard>
        </div>
      </div>
    </div>
  );
}