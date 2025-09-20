"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Zap,
  Workflow,
  Lightbulb,
  TestTube,
  Play,
  Pause,
  Settings,
  BarChart3,
  TrendingUp,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Plus,
  MoreHorizontal,
  RefreshCw,
  Eye,
  Edit,
  Trash2
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import { AutomationRules } from "./automation-rules";
import { WorkflowBuilder } from "./workflow-builder";
import { SmartRecommendations } from "./smart-recommendations";
import { ABTesting } from "./ab-testing";
import { toast } from "react-hot-toast";

interface AutomationStats {
  total_rules: number;
  active_rules: number;
  total_workflows: number;
  active_workflows: number;
  pending_recommendations: number;
  active_ab_tests: number;
  recent_rule_runs: Array<{
    id: string;
    rule_name: string;
    status: "success" | "failed" | "running";
    executed_at: string;
  }>;
  recent_workflow_executions: Array<{
    id: string;
    workflow_name: string;
    status: "success" | "failed" | "running";
    executed_at: string;
  }>;
  top_recommendations: Array<{
    id: string;
    title: string;
    type: string;
    confidence_score: number;
    priority: number;
  }>;
}

export function AutomationDashboard({ className }: { className?: string }) {
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState<AutomationStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchStats = async () => {
    try {
      setRefreshing(true);
      // Mock data - replace with actual API call
      const mockStats: AutomationStats = {
        total_rules: 12,
        active_rules: 8,
        total_workflows: 5,
        active_workflows: 3,
        pending_recommendations: 7,
        active_ab_tests: 2,
        recent_rule_runs: [
          {
            id: "1",
            rule_name: "Auto-pause underperforming posts",
            status: "success",
            executed_at: "2024-01-15T10:30:00Z"
          },
          {
            id: "2",
            rule_name: "Increase budget for high performers",
            status: "success",
            executed_at: "2024-01-15T09:15:00Z"
          },
          {
            id: "3",
            rule_name: "Send weekly report",
            status: "running",
            executed_at: "2024-01-15T08:00:00Z"
          }
        ],
        recent_workflow_executions: [
          {
            id: "1",
            workflow_name: "Content approval workflow",
            status: "success",
            executed_at: "2024-01-15T11:00:00Z"
          },
          {
            id: "2",
            workflow_name: "Campaign launch sequence",
            status: "failed",
            executed_at: "2024-01-15T10:45:00Z"
          }
        ],
        top_recommendations: [
          {
            id: "1",
            title: "Post at 2 PM for better engagement",
            type: "posting_time",
            confidence_score: 0.85,
            priority: 1
          },
          {
            id: "2",
            title: "Use #marketing hashtag more often",
            type: "hashtag_suggestion",
            confidence_score: 0.72,
            priority: 2
          },
          {
            id: "3",
            title: "Optimize content length to 150-200 words",
            type: "content_optimization",
            confidence_score: 0.68,
            priority: 3
          }
        ]
      };
      
      setStats(mockStats);
    } catch (error) {
      console.error("Failed to fetch automation stats:", error);
      toast.error("Failed to load automation data");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success":
        return "text-green-600 bg-green-50";
      case "failed":
        return "text-red-600 bg-red-50";
      case "running":
        return "text-blue-600 bg-blue-50";
      default:
        return "text-gray-600 bg-gray-50";
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  if (loading) {
    return (
      <div className={cn("space-y-6", className)}>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="pb-2">
                <Skeleton className="h-4 w-24" />
                <Skeleton className="h-8 w-16" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-32" />
              </CardContent>
            </Card>
          ))}
        </div>
        <Card>
          <CardHeader>
            <Skeleton className="h-6 w-48" />
          </CardHeader>
          <CardContent>
            <Skeleton className="h-32 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Automation</h1>
          <p className="text-muted-foreground">
            Manage rules, workflows, recommendations, and A/B tests
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchStats}
            disabled={refreshing}
          >
            <RefreshCw className={cn("h-4 w-4 mr-2", refreshing && "animate-spin")} />
            Refresh
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            Create Rule
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Automation Rules</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_rules || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.active_rules || 0} active
            </p>
            <div className="mt-2">
              <Progress 
                value={stats ? (stats.active_rules / stats.total_rules) * 100 : 0} 
                className="h-2" 
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Workflows</CardTitle>
            <Workflow className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.total_workflows || 0}</div>
            <p className="text-xs text-muted-foreground">
              {stats?.active_workflows || 0} running
            </p>
            <div className="mt-2">
              <Progress 
                value={stats ? (stats.active_workflows / stats.total_workflows) * 100 : 0} 
                className="h-2" 
              />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Recommendations</CardTitle>
            <Lightbulb className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.pending_recommendations || 0}</div>
            <p className="text-xs text-muted-foreground">
              Pending review
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">A/B Tests</CardTitle>
            <TestTube className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats?.active_ab_tests || 0}</div>
            <p className="text-xs text-muted-foreground">
              Currently running
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="rules">Rules</TabsTrigger>
          <TabsTrigger value="workflows">Workflows</TabsTrigger>
          <TabsTrigger value="recommendations">Recommendations</TabsTrigger>
          <TabsTrigger value="ab-tests">A/B Tests</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="h-5 w-5 mr-2" />
                  Recent Activity
                </CardTitle>
                <CardDescription>
                  Latest rule executions and workflow runs
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium mb-2">Rule Executions</h4>
                  <div className="space-y-2">
                    {stats?.recent_rule_runs.slice(0, 3).map((run) => (
                      <div key={run.id} className="flex items-center justify-between p-2 rounded-lg border">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(run.status)}
                          <span className="text-sm font-medium">{run.rule_name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(run.status)}>
                            {run.status}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatTimeAgo(run.executed_at)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="text-sm font-medium mb-2">Workflow Executions</h4>
                  <div className="space-y-2">
                    {stats?.recent_workflow_executions.slice(0, 3).map((execution) => (
                      <div key={execution.id} className="flex items-center justify-between p-2 rounded-lg border">
                        <div className="flex items-center space-x-2">
                          {getStatusIcon(execution.status)}
                          <span className="text-sm font-medium">{execution.workflow_name}</span>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Badge className={getStatusColor(execution.status)}>
                            {execution.status}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatTimeAgo(execution.executed_at)}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Top Recommendations */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="h-5 w-5 mr-2" />
                  Top Recommendations
                </CardTitle>
                <CardDescription>
                  AI-powered suggestions for optimization
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {stats?.top_recommendations.map((rec) => (
                  <div key={rec.id} className="p-3 rounded-lg border">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <h4 className="text-sm font-medium">{rec.title}</h4>
                        <p className="text-xs text-muted-foreground capitalize">
                          {rec.type.replace('_', ' ')}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-xs">
                          {Math.round(rec.confidence_score * 100)}% confidence
                        </Badge>
                        <Badge variant="secondary" className="text-xs">
                          Priority {rec.priority}
                        </Badge>
                      </div>
                    </div>
                    <div className="mt-2">
                      <Progress value={rec.confidence_score * 100} className="h-1" />
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="rules">
          <AutomationRules />
        </TabsContent>

        <TabsContent value="workflows">
          <WorkflowBuilder />
        </TabsContent>

        <TabsContent value="recommendations">
          <SmartRecommendations />
        </TabsContent>

        <TabsContent value="ab-tests">
          <ABTesting />
        </TabsContent>
      </Tabs>
    </div>
  );
}
