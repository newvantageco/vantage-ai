"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  TestTube,
  Plus,
  Play,
  Pause,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  Copy,
  BarChart3,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  XCircle,
  Clock,
  AlertCircle,
  Target,
  Users,
  Zap,
  Calendar,
  Settings
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ABTestBuilder } from "./ab-test-builder";
import { toast } from "react-hot-toast";

interface ABTest {
  id: string;
  name: string;
  description: string;
  hypothesis: string;
  test_type: string;
  traffic_allocation: number;
  minimum_sample_size: number;
  significance_level: number;
  status: "draft" | "running" | "paused" | "completed" | "cancelled";
  enabled: boolean;
  start_date?: string;
  end_date?: string;
  planned_duration_days: number;
  winner_variant_id?: string;
  confidence_level?: number;
  p_value?: number;
  created_at: string;
  updated_at: string;
  variants: ABTestVariant[];
}

interface ABTestVariant {
  id: string;
  ab_test_id: string;
  name: string;
  description?: string;
  variant_data: Record<string, any>;
  traffic_percentage: number;
  status: "active" | "winner" | "loser" | "paused";
  impressions: number;
  clicks: number;
  conversions: number;
  engagement_rate: number;
  conversion_rate: number;
  created_at: string;
  updated_at: string;
}

interface ABTestResult {
  id: string;
  ab_test_id: string;
  variant_id: string;
  metric_name: string;
  metric_value: number;
  sample_size: number;
  confidence_interval_lower?: number;
  confidence_interval_upper?: number;
  p_value?: number;
  measured_at: string;
  created_at: string;
}

const testTypes = [
  { value: "content", label: "Content", description: "Test different content variations" },
  { value: "timing", label: "Timing", description: "Test different posting times" },
  { value: "audience", label: "Audience", description: "Test different audience segments" },
  { value: "creative", label: "Creative", description: "Test different creative elements" },
  { value: "landing_page", label: "Landing Page", description: "Test different landing pages" },
  { value: "cta", label: "Call-to-Action", description: "Test different CTA buttons" }
];

const statusLabels = {
  draft: "Draft",
  running: "Running",
  paused: "Paused",
  completed: "Completed",
  cancelled: "Cancelled"
};

const statusColors = {
  draft: "bg-gray-100 text-gray-800",
  running: "bg-green-100 text-green-800",
  paused: "bg-yellow-100 text-yellow-800",
  completed: "bg-blue-100 text-blue-800",
  cancelled: "bg-red-100 text-red-800"
};

const variantStatusColors = {
  active: "bg-blue-100 text-blue-800",
  winner: "bg-green-100 text-green-800",
  loser: "bg-red-100 text-red-800",
  paused: "bg-yellow-100 text-yellow-800"
};

export function ABTesting() {
  const [abTests, setABTests] = useState<ABTest[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTest, setSelectedTest] = useState<ABTest | null>(null);
  const [showTestBuilder, setShowTestBuilder] = useState(false);
  const [showTestDetails, setShowTestDetails] = useState(false);
  const [testResults, setTestResults] = useState<ABTestResult[]>([]);
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterType, setFilterType] = useState<string>("all");

  const fetchABTests = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockABTests: ABTest[] = [
        {
          id: "1",
          name: "Headline A/B Test",
          description: "Test different headline variations for better engagement",
          hypothesis: "Shorter headlines will increase click-through rates by 15%",
          test_type: "content",
          traffic_allocation: 0.5,
          minimum_sample_size: 1000,
          significance_level: 0.05,
          status: "running",
          enabled: true,
          start_date: "2024-01-10T00:00:00Z",
          planned_duration_days: 14,
          created_at: "2024-01-10T00:00:00Z",
          updated_at: "2024-01-15T00:00:00Z",
          variants: [
            {
              id: "variant_1",
              ab_test_id: "1",
              name: "Control - Long Headline",
              description: "Original long headline version",
              variant_data: { headline: "Discover the Amazing Benefits of Our Revolutionary Product" },
              traffic_percentage: 0.5,
              status: "active",
              impressions: 1250,
              clicks: 125,
              conversions: 25,
              engagement_rate: 0.10,
              conversion_rate: 0.20,
              created_at: "2024-01-10T00:00:00Z",
              updated_at: "2024-01-15T00:00:00Z"
            },
            {
              id: "variant_2",
              ab_test_id: "1",
              name: "Test - Short Headline",
              description: "New short headline version",
              variant_data: { headline: "Revolutionary Product - Try Now!" },
              traffic_percentage: 0.5,
              status: "active",
              impressions: 1180,
              clicks: 142,
              conversions: 32,
              engagement_rate: 0.12,
              conversion_rate: 0.23,
              created_at: "2024-01-10T00:00:00Z",
              updated_at: "2024-01-15T00:00:00Z"
            }
          ]
        },
        {
          id: "2",
          name: "Posting Time Test",
          description: "Test optimal posting times for maximum engagement",
          hypothesis: "Morning posts will generate 20% more engagement than afternoon posts",
          test_type: "timing",
          traffic_allocation: 0.5,
          minimum_sample_size: 500,
          significance_level: 0.05,
          status: "completed",
          enabled: false,
          start_date: "2024-01-01T00:00:00Z",
          end_date: "2024-01-08T00:00:00Z",
          planned_duration_days: 7,
          winner_variant_id: "variant_3",
          confidence_level: 0.95,
          p_value: 0.02,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-08T00:00:00Z",
          variants: [
            {
              id: "variant_3",
              ab_test_id: "2",
              name: "Morning Posts",
              description: "Posts published at 9 AM",
              variant_data: { posting_time: "09:00" },
              traffic_percentage: 0.5,
              status: "winner",
              impressions: 800,
              clicks: 120,
              conversions: 30,
              engagement_rate: 0.15,
              conversion_rate: 0.25,
              created_at: "2024-01-01T00:00:00Z",
              updated_at: "2024-01-08T00:00:00Z"
            },
            {
              id: "variant_4",
              ab_test_id: "2",
              name: "Afternoon Posts",
              description: "Posts published at 2 PM",
              variant_data: { posting_time: "14:00" },
              traffic_percentage: 0.5,
              status: "loser",
              impressions: 750,
              clicks: 90,
              conversions: 18,
              engagement_rate: 0.12,
              conversion_rate: 0.20,
              created_at: "2024-01-01T00:00:00Z",
              updated_at: "2024-01-08T00:00:00Z"
            }
          ]
        },
        {
          id: "3",
          name: "CTA Button Color Test",
          description: "Test different CTA button colors for better conversion",
          hypothesis: "Red buttons will increase conversions by 10% compared to blue buttons",
          test_type: "cta",
          traffic_allocation: 0.5,
          minimum_sample_size: 800,
          significance_level: 0.05,
          status: "draft",
          enabled: false,
          planned_duration_days: 10,
          created_at: "2024-01-14T00:00:00Z",
          updated_at: "2024-01-14T00:00:00Z",
          variants: [
            {
              id: "variant_5",
              ab_test_id: "3",
              name: "Control - Blue Button",
              description: "Original blue CTA button",
              variant_data: { button_color: "#3B82F6", button_text: "Get Started" },
              traffic_percentage: 0.5,
              status: "active",
              impressions: 0,
              clicks: 0,
              conversions: 0,
              engagement_rate: 0,
              conversion_rate: 0,
              created_at: "2024-01-14T00:00:00Z",
              updated_at: "2024-01-14T00:00:00Z"
            },
            {
              id: "variant_6",
              ab_test_id: "3",
              name: "Test - Red Button",
              description: "New red CTA button",
              variant_data: { button_color: "#EF4444", button_text: "Get Started" },
              traffic_percentage: 0.5,
              status: "active",
              impressions: 0,
              clicks: 0,
              conversions: 0,
              engagement_rate: 0,
              conversion_rate: 0,
              created_at: "2024-01-14T00:00:00Z",
              updated_at: "2024-01-14T00:00:00Z"
            }
          ]
        }
      ];
      
      setABTests(mockABTests);
    } catch (error) {
      console.error("Failed to fetch A/B tests:", error);
      toast.error("Failed to load A/B tests");
    } finally {
      setLoading(false);
    }
  };

  const fetchTestResults = async (testId: string) => {
    try {
      // Mock data - replace with actual API call
      const mockResults: ABTestResult[] = [
        {
          id: "result_1",
          ab_test_id: testId,
          variant_id: "variant_1",
          metric_name: "conversion_rate",
          metric_value: 0.20,
          sample_size: 1250,
          confidence_interval_lower: 0.17,
          confidence_interval_upper: 0.23,
          p_value: 0.03,
          measured_at: "2024-01-15T00:00:00Z",
          created_at: "2024-01-15T00:00:00Z"
        },
        {
          id: "result_2",
          ab_test_id: testId,
          variant_id: "variant_2",
          metric_name: "conversion_rate",
          metric_value: 0.23,
          sample_size: 1180,
          confidence_interval_lower: 0.20,
          confidence_interval_upper: 0.26,
          p_value: 0.03,
          measured_at: "2024-01-15T00:00:00Z",
          created_at: "2024-01-15T00:00:00Z"
        }
      ];
      
      setTestResults(mockResults);
    } catch (error) {
      console.error("Failed to fetch test results:", error);
      toast.error("Failed to load test results");
    }
  };

  const startTest = async (testId: string) => {
    try {
      setABTests(prev => prev.map(test => 
        test.id === testId 
          ? { 
              ...test, 
              status: "running" as const, 
              enabled: true,
              start_date: new Date().toISOString(),
              end_date: new Date(Date.now() + test.planned_duration_days * 24 * 60 * 60 * 1000).toISOString()
            } 
          : test
      ));
      toast.success("A/B test started successfully");
    } catch (error) {
      console.error("Failed to start test:", error);
      toast.error("Failed to start A/B test");
    }
  };

  const stopTest = async (testId: string) => {
    try {
      setABTests(prev => prev.map(test => 
        test.id === testId 
          ? { 
              ...test, 
              status: "completed" as const, 
              enabled: false,
              end_date: new Date().toISOString()
            } 
          : test
      ));
      toast.success("A/B test stopped successfully");
    } catch (error) {
      console.error("Failed to stop test:", error);
      toast.error("Failed to stop A/B test");
    }
  };

  const deleteTest = async (testId: string) => {
    try {
      setABTests(prev => prev.filter(test => test.id !== testId));
      toast.success("A/B test deleted successfully");
    } catch (error) {
      console.error("Failed to delete test:", error);
      toast.error("Failed to delete A/B test");
    }
  };

  useEffect(() => {
    fetchABTests();
  }, []);

  const filteredTests = abTests.filter(test => {
    const matchesStatus = filterStatus === "all" || test.status === filterStatus;
    const matchesType = filterType === "all" || test.test_type === filterType;
    return matchesStatus && matchesType;
  });

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const calculateTestProgress = (test: ABTest) => {
    if (!test.start_date) return 0;
    
    const startDate = new Date(test.start_date);
    const endDate = test.end_date ? new Date(test.end_date) : new Date(Date.now());
    const totalDuration = test.planned_duration_days * 24 * 60 * 60 * 1000;
    const elapsed = endDate.getTime() - startDate.getTime();
    
    return Math.min((elapsed / totalDuration) * 100, 100);
  };

  const getTestTypeIcon = (type: string) => {
    switch (type) {
      case "content":
        return <Target className="h-5 w-5" />;
      case "timing":
        return <Clock className="h-5 w-5" />;
      case "audience":
        return <Users className="h-5 w-5" />;
      case "creative":
        return <Zap className="h-5 w-5" />;
      case "landing_page":
        return <BarChart3 className="h-5 w-5" />;
      case "cta":
        return <Target className="h-5 w-5" />;
      default:
        return <TestTube className="h-5 w-5" />;
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-32 w-full" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">A/B Testing</h2>
          <p className="text-muted-foreground">
            Test different variations to optimize your content and campaigns
          </p>
        </div>
        <Dialog open={showTestBuilder} onOpenChange={setShowTestBuilder}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create A/B Test
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>Create A/B Test</DialogTitle>
              <DialogDescription>
                Set up a new A/B test to compare different variations
              </DialogDescription>
            </DialogHeader>
            <ABTestBuilder
              onSave={(test) => {
                setABTests(prev => [test, ...prev]);
                setShowTestBuilder(false);
                toast.success("A/B test created successfully");
              }}
              onCancel={() => setShowTestBuilder(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            {Object.entries(statusLabels).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Test Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {testTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* A/B Tests Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredTests.map((test) => (
          <Card key={test.id} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    {getTestTypeIcon(test.test_type)}
                    <Badge className={statusColors[test.status]}>
                      {statusLabels[test.status]}
                    </Badge>
                  </div>
                  <CardTitle className="text-lg">{test.name}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {test.description}
                  </CardDescription>
                  <div className="text-sm text-muted-foreground">
                    <strong>Hypothesis:</strong> {test.hypothesis}
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    {test.status === "draft" && (
                      <DropdownMenuItem onClick={() => startTest(test.id)}>
                        <Play className="h-4 w-4 mr-2" />
                        Start Test
                      </DropdownMenuItem>
                    )}
                    {test.status === "running" && (
                      <DropdownMenuItem onClick={() => stopTest(test.id)}>
                        <Pause className="h-4 w-4 mr-2" />
                        Stop Test
                      </DropdownMenuItem>
                    )}
                    <DropdownMenuItem onClick={() => {
                      setSelectedTest(test);
                      fetchTestResults(test.id);
                      setShowTestDetails(true);
                    }}>
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit Test
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Copy className="h-4 w-4 mr-2" />
                      Duplicate
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem 
                      onClick={() => deleteTest(test.id)}
                      className="text-red-600"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Test
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Test Progress */}
              {test.status === "running" && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Progress</span>
                    <span className="font-medium">{Math.round(calculateTestProgress(test))}%</span>
                  </div>
                  <Progress value={calculateTestProgress(test)} className="h-2" />
                </div>
              )}

              {/* Variants */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Variants ({test.variants.length})</h4>
                <div className="space-y-1">
                  {test.variants.map((variant) => (
                    <div key={variant.id} className="flex items-center justify-between p-2 rounded border">
                      <div className="flex items-center space-x-2">
                        <div className={cn(
                          "w-2 h-2 rounded-full",
                          variant.status === "winner" ? "bg-green-500" :
                          variant.status === "loser" ? "bg-red-500" :
                          variant.status === "paused" ? "bg-yellow-500" : "bg-blue-500"
                        )} />
                        <span className="text-sm font-medium">{variant.name}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge className={variantStatusColors[variant.status]}>
                          {variant.status}
                        </Badge>
                        {variant.impressions > 0 && (
                          <span className="text-xs text-muted-foreground">
                            {variant.conversion_rate.toFixed(1)}%
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Test Stats */}
              <div className="grid grid-cols-2 gap-4 pt-2 border-t">
                <div className="text-center">
                  <div className="text-lg font-bold">
                    {test.variants.reduce((sum, v) => sum + v.impressions, 0).toLocaleString()}
                  </div>
                  <div className="text-xs text-muted-foreground">Total Impressions</div>
                </div>
                <div className="text-center">
                  <div className="text-lg font-bold">
                    {test.variants.reduce((sum, v) => sum + v.conversions, 0)}
                  </div>
                  <div className="text-xs text-muted-foreground">Total Conversions</div>
                </div>
              </div>

              {/* Test Results */}
              {test.status === "completed" && test.winner_variant_id && (
                <div className="p-3 bg-green-50 rounded-lg">
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <span className="text-sm font-medium text-green-800">Test Completed</span>
                  </div>
                  <p className="text-xs text-green-700 mt-1">
                    Winner: {test.variants.find(v => v.id === test.winner_variant_id)?.name}
                    {test.confidence_level && ` (${Math.round(test.confidence_level * 100)}% confidence)`}
                  </p>
                </div>
              )}

              {/* Timestamps */}
              <div className="pt-2 border-t space-y-1">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>Created</span>
                  <span>{formatTimeAgo(test.created_at)}</span>
                </div>
                {test.start_date && (
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Started</span>
                    <span>{formatTimeAgo(test.start_date)}</span>
                  </div>
                )}
                {test.end_date && (
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Ended</span>
                    <span>{formatTimeAgo(test.end_date)}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredTests.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <TestTube className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No A/B tests found</h3>
            <p className="text-muted-foreground text-center mb-4">
              {filterStatus !== "all" || filterType !== "all"
                ? "No tests match your current filters"
                : "Get started by creating your first A/B test"
              }
            </p>
            <Button onClick={() => setShowTestBuilder(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Your First A/B Test
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Test Details Dialog */}
      <Dialog open={showTestDetails} onOpenChange={setShowTestDetails}>
        <DialogContent className="max-w-6xl">
          <DialogHeader>
            <DialogTitle>{selectedTest?.name}</DialogTitle>
            <DialogDescription>
              {selectedTest?.description}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* Test Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Test Type</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    {getTestTypeIcon(selectedTest?.test_type || "")}
                    <span>{testTypes.find(t => t.value === selectedTest?.test_type)?.label}</span>
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Traffic Allocation</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {selectedTest ? Math.round(selectedTest.traffic_allocation * 100) : 0}%
                  </div>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Significance Level</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">
                    {selectedTest ? Math.round(selectedTest.significance_level * 100) : 0}%
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Variants Performance */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Variants Performance</h3>
              <div className="space-y-4">
                {selectedTest?.variants.map((variant) => (
                  <Card key={variant.id}>
                    <CardContent className="p-4">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <h4 className="font-medium">{variant.name}</h4>
                          {variant.description && (
                            <p className="text-sm text-muted-foreground">{variant.description}</p>
                          )}
                        </div>
                        <Badge className={variantStatusColors[variant.status]}>
                          {variant.status}
                        </Badge>
                      </div>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="text-center">
                          <div className="text-2xl font-bold">{variant.impressions.toLocaleString()}</div>
                          <div className="text-xs text-muted-foreground">Impressions</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">{variant.clicks}</div>
                          <div className="text-xs text-muted-foreground">Clicks</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">{variant.conversions}</div>
                          <div className="text-xs text-muted-foreground">Conversions</div>
                        </div>
                        <div className="text-center">
                          <div className="text-2xl font-bold">
                            {variant.conversion_rate.toFixed(1)}%
                          </div>
                          <div className="text-xs text-muted-foreground">Conversion Rate</div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>

            {/* Test Results */}
            {testResults.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-4">Statistical Results</h3>
                <div className="space-y-2">
                  {testResults.map((result) => (
                    <div key={result.id} className="flex items-center justify-between p-3 rounded-lg border">
                      <div>
                        <p className="text-sm font-medium">{result.metric_name}</p>
                        <p className="text-xs text-muted-foreground">
                          Sample size: {result.sample_size}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-lg font-bold">{result.metric_value.toFixed(3)}</p>
                        {result.p_value && (
                          <p className="text-xs text-muted-foreground">
                            p-value: {result.p_value.toFixed(3)}
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
