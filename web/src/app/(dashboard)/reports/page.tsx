"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { 
  BarChart3, 
  TrendingUp, 
  Eye, 
  Heart,
  MessageCircle,
  Share2,
  Calendar,
  Filter,
  Download,
  RefreshCw,
  Activity,
  Target,
  Zap
} from "lucide-react";
import { RealtimeAnalytics } from "@/components/RealtimeAnalytics";
import { MobileOptimizedCard, MobileStatsCard, mobileClasses } from "@/components/MobileOptimizedCard";
import { apiService } from "@/lib/api";

interface TopPost {
  id: string;
  title: string;
  platform: string;
  published_at: string;
  impressions: number;
  engagement_rate: number;
  total_engagement: number;
}

interface CampaignPerformance {
  id: string;
  name: string;
  posts: number;
  total_reach: number;
  engagement_rate: number;
  status: 'active' | 'completed' | 'paused';
}

export default function ReportsPage() {
  const [topPosts, setTopPosts] = useState<TopPost[]>([]);
  const [campaigns, setCampaigns] = useState<CampaignPerformance[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTopPosts = async () => {
    setLoading(true);
    setError(null);
    
    try {
      // Mock data for now - in real app this would come from API
      const mockTopPosts: TopPost[] = [
        {
          id: '1',
          title: 'Q4 Product Launch Announcement',
          platform: 'linkedin',
          published_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          impressions: 15420,
          engagement_rate: 8.5,
          total_engagement: 1310
        },
        {
          id: '2',
          title: 'Behind the Scenes: Our Development Process',
          platform: 'twitter',
          published_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          impressions: 8920,
          engagement_rate: 12.3,
          total_engagement: 1097
        },
        {
          id: '3',
          title: 'Customer Success Story: TechCorp Integration',
          platform: 'linkedin',
          published_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          impressions: 12300,
          engagement_rate: 6.8,
          total_engagement: 836
        }
      ];
      
      setTopPosts(mockTopPosts);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load top posts');
    } finally {
      setLoading(false);
    }
  };

  const loadCampaigns = async () => {
    try {
      // Mock data for campaigns
      const mockCampaigns: CampaignPerformance[] = [
        {
          id: '1',
          name: 'Q4 Product Launch',
          posts: 12,
          total_reach: 45600,
          engagement_rate: 7.8,
          status: 'active'
        },
        {
          id: '2',
          name: 'Holiday Marketing Campaign',
          posts: 8,
          total_reach: 32100,
          engagement_rate: 9.2,
          status: 'completed'
        },
        {
          id: '3',
          name: 'Brand Awareness Initiative',
          posts: 15,
          total_reach: 67800,
          engagement_rate: 5.4,
          status: 'paused'
        }
      ];
      
      setCampaigns(mockCampaigns);
    } catch (err) {
      console.error('Failed to load campaigns:', err);
    }
  };

  useEffect(() => {
    loadTopPosts();
    loadCampaigns();
  }, []);

  const formatNumber = (num: number) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-700';
      case 'completed': return 'bg-blue-100 text-blue-700';
      case 'paused': return 'bg-yellow-100 text-yellow-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 p-4 sm:p-6">
      <div className="relative z-10 space-y-6 sm:space-y-8">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 sm:p-8 shadow-lg border border-slate-200/50">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
            <div className="space-y-2">
              <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 tracking-tight">
                Analytics & Reports
              </h1>
              <p className="text-slate-600 text-lg">
                Comprehensive insights into your content performance and audience engagement.
              </p>
            </div>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-3">
              <Button 
                variant="outline" 
                onClick={() => { loadTopPosts(); loadCampaigns(); }}
                className="flex items-center space-x-2"
              >
                <RefreshCw className="h-4 w-4" />
                <span>Refresh</span>
              </Button>
              <Button className="bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800">
                <Download className="h-4 w-4 mr-2" />
                Export Report
              </Button>
            </div>
          </div>
        </div>

        {/* Main Content Tabs */}
        <Tabs defaultValue="realtime" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="realtime" className="flex items-center space-x-2">
              <Activity className="h-4 w-4" />
              <span className="hidden sm:inline">Real-time</span>
              <span className="sm:hidden">Live</span>
            </TabsTrigger>
            <TabsTrigger value="top-posts" className="flex items-center space-x-2">
              <TrendingUp className="h-4 w-4" />
              <span className="hidden sm:inline">Top Posts</span>
              <span className="sm:hidden">Top</span>
            </TabsTrigger>
            <TabsTrigger value="campaigns" className="flex items-center space-x-2">
              <Target className="h-4 w-4" />
              <span className="hidden sm:inline">Campaigns</span>
              <span className="sm:hidden">Campaigns</span>
            </TabsTrigger>
          </TabsList>

          {/* Real-time Analytics Tab */}
          <TabsContent value="realtime">
            <RealtimeAnalytics />
          </TabsContent>

          {/* Top Posts Tab */}
          <TabsContent value="top-posts">
            <MobileOptimizedCard
              title="Top Performing Posts"
              description="Your best performing content across all platforms"
            >
              {loading ? (
                <div className="flex items-center justify-center p-8">
                  <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
                </div>
              ) : error ? (
                <div className="flex items-center justify-center p-8 text-red-600">
                  <div className="text-center">
                    <Activity className="h-8 w-8 mx-auto mb-2" />
                    <p className="text-sm">{error}</p>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      onClick={loadTopPosts}
                      className="mt-2"
                    >
                      Retry
                    </Button>
                  </div>
                </div>
              ) : topPosts.length === 0 ? (
                <div className="flex items-center justify-center p-8 text-slate-500">
                  <div className="text-center">
                    <BarChart3 className="h-8 w-8 mx-auto mb-2" />
                    <p className="text-sm">No posts available</p>
                    <p className="text-xs">Start creating content to see performance data</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {topPosts.map((post, index) => (
                    <div key={post.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center space-x-2">
                            <Badge variant="outline" className="text-xs">
                              #{index + 1}
                            </Badge>
                            <Badge variant="outline" className="text-xs capitalize">
                              {post.platform}
                            </Badge>
                            <span className="text-xs text-slate-500">
                              {formatDate(post.published_at)}
                            </span>
                          </div>
                          <h3 className="font-semibold text-slate-900 line-clamp-2">
                            {post.title}
                          </h3>
                          <div className="grid grid-cols-3 gap-4 text-sm">
                            <div className="text-center p-2 bg-white rounded-lg">
                              <div className="font-semibold text-slate-900">
                                {formatNumber(post.impressions)}
                              </div>
                              <div className="text-xs text-slate-600">Impressions</div>
                            </div>
                            <div className="text-center p-2 bg-white rounded-lg">
                              <div className="font-semibold text-slate-900">
                                {post.engagement_rate.toFixed(1)}%
                              </div>
                              <div className="text-xs text-slate-600">Engagement</div>
                            </div>
                            <div className="text-center p-2 bg-white rounded-lg">
                              <div className="font-semibold text-slate-900">
                                {formatNumber(post.total_engagement)}
                              </div>
                              <div className="text-xs text-slate-600">Total</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </MobileOptimizedCard>
          </TabsContent>

          {/* Campaigns Tab */}
          <TabsContent value="campaigns">
            <MobileOptimizedCard
              title="Campaign Performance"
              description="Track the performance of your marketing campaigns"
            >
              {campaigns.length === 0 ? (
                <div className="flex items-center justify-center p-8 text-slate-500">
                  <div className="text-center">
                    <Target className="h-8 w-8 mx-auto mb-2" />
                    <p className="text-sm">No campaigns available</p>
                    <p className="text-xs">Create your first campaign to get started</p>
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  {campaigns.map((campaign) => (
                    <div key={campaign.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex-1 space-y-2">
                          <div className="flex items-center space-x-2">
                            <h3 className="font-semibold text-slate-900">{campaign.name}</h3>
                            <Badge className={`text-xs ${getStatusColor(campaign.status)}`}>
                              {campaign.status}
                            </Badge>
                          </div>
                          <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-sm">
                            <div className="text-center p-2 bg-white rounded-lg">
                              <div className="font-semibold text-slate-900">
                                {campaign.posts}
                              </div>
                              <div className="text-xs text-slate-600">Posts</div>
                            </div>
                            <div className="text-center p-2 bg-white rounded-lg">
                              <div className="font-semibold text-slate-900">
                                {formatNumber(campaign.total_reach)}
                              </div>
                              <div className="text-xs text-slate-600">Reach</div>
                            </div>
                            <div className="text-center p-2 bg-white rounded-lg">
                              <div className="font-semibold text-slate-900">
                                {campaign.engagement_rate.toFixed(1)}%
                              </div>
                              <div className="text-xs text-slate-600">Engagement</div>
                            </div>
                            <div className="text-center p-2 bg-white rounded-lg">
                              <div className="font-semibold text-slate-900">
                                {Math.round(campaign.total_reach * campaign.engagement_rate / 100).toLocaleString()}
                              </div>
                              <div className="text-xs text-slate-600">Total Eng.</div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </MobileOptimizedCard>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}