"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Calendar, 
  Clock, 
  TrendingUp, 
  Sparkles, 
  BarChart3,
  Target,
  Zap,
  CheckCircle,
  AlertCircle,
  Loader2
} from "lucide-react";
import { AIContentGenerator } from "@/components/AIContentGenerator";
import { apiService } from "@/lib/api";

interface TimeSlot {
  key: string;
  when: string;
  engagement_score?: number;
  optimal: boolean;
}

interface ContentPlan {
  id: string;
  title: string;
  content: string;
  platform: string;
  scheduled_at?: string;
  status: 'draft' | 'scheduled' | 'published';
  engagement_prediction?: number;
}

export default function PlanningPage() {
  const [channel, setChannel] = useState("linkedin");
  const [orgId, setOrgId] = useState("demo-org");
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([]);
  const [contentPlans, setContentPlans] = useState<ContentPlan[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchTimeSlots = async () => {
    if (!orgId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await apiService.getAnalyticsMetrics('timeslot', 'engagement_rate', '7d');
      // Mock data for now since the API might not be fully implemented
      const mockTimeSlots: TimeSlot[] = [
        { key: "09:00", when: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), engagement_score: 8.5, optimal: true },
        { key: "14:00", when: new Date(Date.now() + 2 * 24 * 60 * 60 * 1000).toISOString(), engagement_score: 7.8, optimal: true },
        { key: "18:00", when: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), engagement_score: 6.2, optimal: false },
        { key: "12:00", when: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString(), engagement_score: 5.9, optimal: false },
        { key: "16:00", when: new Date(Date.now() + 5 * 24 * 60 * 60 * 1000).toISOString(), engagement_score: 7.1, optimal: true },
      ];
      setTimeSlots(mockTimeSlots);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch time slots');
    } finally {
      setLoading(false);
    }
  };

  const fetchContentPlans = async () => {
    try {
      const response = await apiService.getContentItems(orgId);
      setContentPlans(response.data);
    } catch (err) {
      console.error('Failed to fetch content plans:', err);
    }
  };

  useEffect(() => {
    fetchTimeSlots();
    fetchContentPlans();
  }, [orgId, channel]);

  const handleContentGenerated = (content: string, type: string) => {
    // Add the generated content to the content plans
    const newPlan: ContentPlan = {
      id: `plan-${Date.now()}`,
      title: `Generated ${type}`,
      content,
      platform: channel,
      scheduled_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
      status: 'draft',
      engagement_prediction: Math.random() * 10 + 5, // Mock prediction
    };
    setContentPlans(prev => [newPlan, ...prev]);
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const getEngagementColor = (score?: number) => {
    if (!score) return 'text-slate-500';
    if (score >= 8) return 'text-green-600';
    if (score >= 6) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 p-6">
      <div className="relative z-10 space-y-8">
        {/* Header */}
        <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 shadow-lg border border-slate-200/50">
          <div className="flex items-center justify-between">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
                Content Planning
              </h1>
              <p className="text-slate-600 text-lg">
                Plan, create, and schedule your content with AI-powered insights.
              </p>
            </div>
            <div className="flex space-x-3">
              <Button 
                variant="outline" 
                onClick={() => { fetchTimeSlots(); fetchContentPlans(); }}
                className="border-slate-300 hover:bg-slate-50"
              >
                <Loader2 className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </div>

        {/* Configuration */}
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Target className="h-5 w-5 text-blue-600" />
              <span>Configuration</span>
            </CardTitle>
            <CardDescription>
              Set your organization and platform preferences
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="org-id">Organization ID</Label>
                <Input
                  id="org-id"
                  placeholder="Enter organization ID"
                  value={orgId}
                  onChange={(e) => setOrgId(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="platform">Platform</Label>
                <Select value={channel} onValueChange={setChannel}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select platform" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="linkedin">LinkedIn</SelectItem>
                    <SelectItem value="meta">Meta (Facebook/Instagram)</SelectItem>
                    <SelectItem value="twitter">Twitter</SelectItem>
                    <SelectItem value="tiktok">TikTok</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Content Tabs */}
        <Tabs defaultValue="ai-generator" className="space-y-6">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="ai-generator" className="flex items-center space-x-2">
              <Sparkles className="h-4 w-4" />
              <span>AI Generator</span>
            </TabsTrigger>
            <TabsTrigger value="optimal-times" className="flex items-center space-x-2">
              <Clock className="h-4 w-4" />
              <span>Optimal Times</span>
            </TabsTrigger>
            <TabsTrigger value="content-plans" className="flex items-center space-x-2">
              <Calendar className="h-4 w-4" />
              <span>Content Plans</span>
            </TabsTrigger>
          </TabsList>

          {/* AI Content Generator Tab */}
          <TabsContent value="ai-generator">
            <AIContentGenerator onContentGenerated={handleContentGenerated} />
          </TabsContent>

          {/* Optimal Times Tab */}
          <TabsContent value="optimal-times">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <TrendingUp className="h-5 w-5 text-green-600" />
                  <span>Optimal Posting Times</span>
                </CardTitle>
                <CardDescription>
                  AI-powered recommendations for the best times to post on {channel}
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
                        onClick={fetchTimeSlots}
                        className="mt-2"
                      >
                        Retry
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {timeSlots.map((slot, index) => (
                      <div 
                        key={index} 
                        className={`p-4 rounded-xl border-2 transition-all duration-200 ${
                          slot.optimal 
                            ? 'border-green-200 bg-green-50 hover:bg-green-100' 
                            : 'border-slate-200 bg-slate-50 hover:bg-slate-100'
                        }`}
                      >
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <div className={`p-2 rounded-lg ${
                              slot.optimal 
                                ? 'bg-green-100 text-green-600' 
                                : 'bg-slate-100 text-slate-600'
                            }`}>
                              <Clock className="h-4 w-4" />
                            </div>
                            <div>
                              <h3 className="font-semibold text-slate-900">
                                {slot.key} - {formatDateTime(slot.when)}
                              </h3>
                              <p className="text-sm text-slate-600">
                                {slot.optimal ? 'Optimal posting time' : 'Good posting time'}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            {slot.optimal && (
                              <Badge variant="secondary" className="bg-green-100 text-green-700">
                                <Zap className="h-3 w-3 mr-1" />
                                Optimal
                              </Badge>
                            )}
                            <div className={`text-sm font-semibold ${getEngagementColor(slot.engagement_score)}`}>
                              {slot.engagement_score?.toFixed(1) || 'N/A'} score
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Content Plans Tab */}
          <TabsContent value="content-plans">
            <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Calendar className="h-5 w-5 text-blue-600" />
                  <span>Content Plans</span>
                </CardTitle>
                <CardDescription>
                  Your scheduled and planned content
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {contentPlans.length === 0 ? (
                    <div className="flex items-center justify-center p-8 text-slate-500">
                      <div className="text-center">
                        <Calendar className="h-8 w-8 mx-auto mb-2" />
                        <p className="text-sm">No content plans yet</p>
                        <p className="text-xs">Generate some content using the AI Generator tab</p>
                      </div>
                    </div>
                  ) : (
                    contentPlans.map((plan) => (
                      <div key={plan.id} className="p-4 rounded-xl border border-slate-200 bg-slate-50 hover:bg-slate-100 transition-colors">
                        <div className="flex items-start justify-between">
                          <div className="flex-1 space-y-2">
                            <div className="flex items-center space-x-2">
                              <h3 className="font-semibold text-slate-900">{plan.title}</h3>
                              <Badge variant="outline" className="text-xs">
                                {plan.platform}
                              </Badge>
                              <Badge 
                                variant={plan.status === 'published' ? 'default' : 'secondary'}
                                className="text-xs"
                              >
                                {plan.status}
                              </Badge>
                            </div>
                            <p className="text-sm text-slate-600 line-clamp-2">
                              {plan.content}
                            </p>
                            <div className="flex items-center space-x-4 text-xs text-slate-500">
                              <span>Scheduled: {plan.scheduled_at ? formatDateTime(plan.scheduled_at) : 'Not scheduled'}</span>
                              {plan.engagement_prediction && (
                                <span className="flex items-center space-x-1">
                                  <BarChart3 className="h-3 w-3" />
                                  <span>Predicted: {plan.engagement_prediction.toFixed(1)}/10</span>
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex space-x-2">
                            <Button variant="outline" size="sm">
                              Edit
                            </Button>
                            <Button variant="outline" size="sm">
                              Schedule
                            </Button>
                          </div>
                        </div>
                      </div>
                    ))
                  )}
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}


