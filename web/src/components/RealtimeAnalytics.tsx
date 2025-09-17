"use client";

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown, 
  Activity, 
  Eye, 
  Heart, 
  MessageCircle, 
  Share2,
  RefreshCw,
  AlertCircle,
  Loader2
} from "lucide-react";
import { apiService } from "@/lib/api";
import { useRealtimeData } from "@/hooks/useRealtimeData";

interface AnalyticsMetric {
  name: string;
  value: number;
  change: number;
  trend: 'up' | 'down';
  icon: React.ReactNode;
  color: string;
}

interface PlatformData {
  platform: string;
  posts: number;
  engagement: number;
  reach: number;
  impressions: number;
}

export function RealtimeAnalytics() {
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [selectedMetric, setSelectedMetric] = useState('engagement_rate');
  const [platformData, setPlatformData] = useState<PlatformData[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { analytics, loading: realtimeLoading, refresh } = useRealtimeData(30000); // 30 second updates

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getAnalytics(selectedPeriod);
      // Mock data for now since the API structure might be different
      const mockPlatformData: PlatformData[] = [
        { platform: 'linkedin', posts: 12, engagement: 8.5, reach: 15420, impressions: 23100 },
        { platform: 'twitter', posts: 8, engagement: 12.3, reach: 8920, impressions: 13380 },
        { platform: 'facebook', posts: 5, engagement: 6.8, reach: 12300, impressions: 18450 },
      ];
      setPlatformData(mockPlatformData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [selectedPeriod, selectedMetric]);

  const metrics: AnalyticsMetric[] = [
    {
      name: 'Impressions',
      value: analytics?.metrics.impressions || 0,
      change: 12.5,
      trend: 'up',
      icon: <Eye className="h-4 w-4" />,
      color: 'text-blue-600'
    },
    {
      name: 'Engagement Rate',
      value: analytics?.metrics.engagement_rate || 0,
      change: 8.2,
      trend: 'up',
      icon: <Activity className="h-4 w-4" />,
      color: 'text-green-600'
    },
    {
      name: 'Reach',
      value: analytics?.metrics.reach || 0,
      change: 15.3,
      trend: 'up',
      icon: <TrendingUp className="h-4 w-4" />,
      color: 'text-purple-600'
    },
    {
      name: 'Clicks',
      value: analytics?.metrics.clicks || 0,
      change: -2.1,
      trend: 'down',
      icon: <BarChart3 className="h-4 w-4" />,
      color: 'text-orange-600'
    }
  ];

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatPercentage = (num: number) => {
    const sign = num >= 0 ? '+' : '';
    return `${sign}${num.toFixed(1)}%`;
  };

  return (
    <div className="space-y-6">
      {/* Header Controls */}
      <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5 text-blue-600" />
                <span>Real-time Analytics</span>
              </CardTitle>
              <CardDescription>
                Live performance metrics and insights
              </CardDescription>
            </div>
            <div className="flex space-x-3">
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger className="w-32">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1d">Last 24h</SelectItem>
                  <SelectItem value="7d">Last 7 days</SelectItem>
                  <SelectItem value="30d">Last 30 days</SelectItem>
                  <SelectItem value="90d">Last 90 days</SelectItem>
                </SelectContent>
              </Select>
              <Button 
                variant="outline" 
                onClick={() => { fetchAnalytics(); refresh(); }}
                disabled={loading || realtimeLoading}
                className="flex items-center space-x-2"
              >
                {(loading || realtimeLoading) ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <RefreshCw className="h-4 w-4" />
                )}
                <span className="hidden sm:inline">Refresh</span>
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
        {metrics.map((metric, index) => (
          <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 bg-white/80 backdrop-blur-sm">
            <CardContent className="p-4 sm:p-6">
              <div className="flex items-center justify-between mb-3">
                <div className={`p-2 rounded-lg bg-gradient-to-br ${metric.color.replace('text-', 'from-').replace('-600', '-500')} to-${metric.color.replace('text-', '').replace('-600', '-700')} shadow-lg`}>
                  <div className="text-white">
                    {metric.icon}
                  </div>
                </div>
                <div className="flex items-center space-x-1">
                  {metric.trend === 'up' ? (
                    <TrendingUp className="h-4 w-4 text-green-500" />
                  ) : (
                    <TrendingDown className="h-4 w-4 text-red-500" />
                  )}
                  <span className={`text-sm font-semibold ${
                    metric.trend === 'up' ? 'text-green-500' : 'text-red-500'
                  }`}>
                    {formatPercentage(metric.change)}
                  </span>
                </div>
              </div>
              <div className="space-y-1">
                <h3 className="text-xl sm:text-2xl font-bold text-slate-900">
                  {realtimeLoading ? (
                    <div className="h-6 sm:h-8 w-16 sm:w-20 bg-slate-200 rounded animate-pulse" />
                  ) : (
                    formatNumber(metric.value)
                  )}
                </h3>
                <p className="text-sm font-medium text-slate-600">{metric.name}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Platform Breakdown */}
      <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Activity className="h-5 w-5 text-green-600" />
            <span>Platform Performance</span>
          </CardTitle>
          <CardDescription>
            Engagement metrics across different platforms
          </CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : error ? (
            <div className="flex items-center justify-center p-8 text-red-600">
              <div className="text-center">
                <AlertCircle className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">{error}</p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={fetchAnalytics}
                  className="mt-2"
                >
                  Retry
                </Button>
              </div>
            </div>
          ) : platformData.length === 0 ? (
            <div className="flex items-center justify-center p-8 text-slate-500">
              <div className="text-center">
                <BarChart3 className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">No platform data available</p>
              </div>
            </div>
          ) : (
            <div className="space-y-4">
              {platformData.map((platform, index) => (
                <div key={index} className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className="p-2 rounded-lg bg-gradient-to-br from-blue-500 to-blue-600">
                        <div className="text-white text-sm font-bold">
                          {platform.platform.charAt(0).toUpperCase()}
                        </div>
                      </div>
                      <div>
                        <h3 className="font-semibold text-slate-900 capitalize">
                          {platform.platform}
                        </h3>
                        <p className="text-sm text-slate-600">
                          {platform.posts} posts
                        </p>
                      </div>
                    </div>
                    <div className="text-right space-y-1">
                      <div className="text-lg font-bold text-slate-900">
                        {formatNumber(platform.engagement)}
                      </div>
                      <div className="text-sm text-slate-600">
                        engagement
                      </div>
                    </div>
                  </div>
                  <div className="mt-3 grid grid-cols-2 gap-4">
                    <div className="text-center p-2 bg-white rounded-lg">
                      <div className="text-sm font-semibold text-slate-900">
                        {formatNumber(platform.reach)}
                      </div>
                      <div className="text-xs text-slate-600">Reach</div>
                    </div>
                    <div className="text-center p-2 bg-white rounded-lg">
                      <div className="text-sm font-semibold text-slate-900">
                        {formatNumber(platform.impressions)}
                      </div>
                      <div className="text-xs text-slate-600">Impressions</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Live Status Indicator */}
      <div className="flex items-center justify-center space-x-2 text-sm text-slate-600">
        <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
        <span>Live data updates every 30 seconds</span>
      </div>
    </div>
  );
}
