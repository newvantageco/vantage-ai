"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Plus,
  Search,
  Filter,
  MoreHorizontal,
  Play,
  Pause,
  Edit,
  Trash2,
  Eye,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  Zap,
  Settings,
  BarChart3
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
import { RuleBuilder } from "./rule-builder";
import { toast } from "react-hot-toast";

interface AutomationRule {
  id: string;
  name: string;
  description: string;
  trigger: string;
  condition: string;
  action: string;
  enabled: boolean;
  last_run?: string;
  run_count: number;
  success_count: number;
  failure_count: number;
  created_at: string;
  updated_at: string;
}

interface RuleRun {
  id: string;
  rule_id: string;
  status: "success" | "failed" | "running";
  executed_at: string;
  duration?: number;
  error_message?: string;
}

export function AutomationRules() {
  const [rules, setRules] = useState<AutomationRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterTrigger, setFilterTrigger] = useState<string>("all");
  const [selectedRule, setSelectedRule] = useState<AutomationRule | null>(null);
  const [showRuleBuilder, setShowRuleBuilder] = useState(false);
  const [showRuleDetails, setShowRuleDetails] = useState(false);
  const [ruleRuns, setRuleRuns] = useState<RuleRun[]>([]);

  const triggerTypes = [
    { value: "post_performance", label: "Post Performance" },
    { value: "weekly_brief_generated", label: "Weekly Brief Generated" },
    { value: "inbox_message_received", label: "Inbox Message Received" },
    { value: "campaign_created", label: "Campaign Created" },
    { value: "schedule_posted", label: "Schedule Posted" }
  ];

  const actionTypes = [
    { value: "clone_content_and_reschedule", label: "Clone Content & Reschedule" },
    { value: "increase_budget_pct", label: "Increase Budget %" },
    { value: "pause_underperformer", label: "Pause Underperformer" },
    { value: "send_notification", label: "Send Notification" },
    { value: "pause_campaign", label: "Pause Campaign" },
    { value: "resume_campaign", label: "Resume Campaign" }
  ];

  const fetchRules = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockRules: AutomationRule[] = [
        {
          id: "1",
          name: "Auto-pause underperforming posts",
          description: "Automatically pause posts with engagement rate below 2%",
          trigger: "post_performance",
          condition: "engagement_rate < 0.02",
          action: "pause_underperformer",
          enabled: true,
          last_run: "2024-01-15T10:30:00Z",
          run_count: 45,
          success_count: 42,
          failure_count: 3,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-15T10:30:00Z"
        },
        {
          id: "2",
          name: "Increase budget for high performers",
          description: "Increase ad budget by 20% for posts with engagement above 5%",
          trigger: "post_performance",
          condition: "engagement_rate > 0.05",
          action: "increase_budget_pct",
          enabled: true,
          last_run: "2024-01-15T09:15:00Z",
          run_count: 23,
          success_count: 20,
          failure_count: 3,
          created_at: "2024-01-05T00:00:00Z",
          updated_at: "2024-01-15T09:15:00Z"
        },
        {
          id: "3",
          name: "Send weekly report",
          description: "Send weekly performance report every Monday at 9 AM",
          trigger: "weekly_brief_generated",
          condition: "day_of_week == 'monday'",
          action: "send_notification",
          enabled: false,
          run_count: 12,
          success_count: 10,
          failure_count: 2,
          created_at: "2024-01-10T00:00:00Z",
          updated_at: "2024-01-14T00:00:00Z"
        }
      ];
      
      setRules(mockRules);
    } catch (error) {
      console.error("Failed to fetch rules:", error);
      toast.error("Failed to load automation rules");
    } finally {
      setLoading(false);
    }
  };

  const fetchRuleRuns = async (ruleId: string) => {
    try {
      // Mock data - replace with actual API call
      const mockRuns: RuleRun[] = [
        {
          id: "1",
          rule_id: ruleId,
          status: "success",
          executed_at: "2024-01-15T10:30:00Z",
          duration: 150
        },
        {
          id: "2",
          rule_id: ruleId,
          status: "success",
          executed_at: "2024-01-15T09:15:00Z",
          duration: 200
        },
        {
          id: "3",
          rule_id: ruleId,
          status: "failed",
          executed_at: "2024-01-15T08:00:00Z",
          duration: 300,
          error_message: "Failed to connect to external API"
        }
      ];
      
      setRuleRuns(mockRuns);
    } catch (error) {
      console.error("Failed to fetch rule runs:", error);
      toast.error("Failed to load rule execution history");
    }
  };

  useEffect(() => {
    fetchRules();
  }, []);

  const toggleRule = async (ruleId: string, enabled: boolean) => {
    try {
      // Mock API call - replace with actual implementation
      setRules(prev => prev.map(rule => 
        rule.id === ruleId ? { ...rule, enabled } : rule
      ));
      toast.success(`Rule ${enabled ? 'enabled' : 'disabled'} successfully`);
    } catch (error) {
      console.error("Failed to toggle rule:", error);
      toast.error("Failed to update rule");
    }
  };

  const deleteRule = async (ruleId: string) => {
    try {
      // Mock API call - replace with actual implementation
      setRules(prev => prev.filter(rule => rule.id !== ruleId));
      toast.success("Rule deleted successfully");
    } catch (error) {
      console.error("Failed to delete rule:", error);
      toast.error("Failed to delete rule");
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "failed":
        return <XCircle className="h-4 w-4 text-red-500" />;
      case "running":
        return <Clock className="h-4 w-4 text-blue-500 animate-spin" />;
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

  const filteredRules = rules.filter(rule => {
    const matchesSearch = rule.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rule.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = filterStatus === "all" || 
                         (filterStatus === "enabled" && rule.enabled) ||
                         (filterStatus === "disabled" && !rule.enabled);
    const matchesTrigger = filterTrigger === "all" || rule.trigger === filterTrigger;
    
    return matchesSearch && matchesStatus && matchesTrigger;
  });

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
                <Skeleton className="h-4 w-1/2" />
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
          <h2 className="text-2xl font-bold tracking-tight">Automation Rules</h2>
          <p className="text-muted-foreground">
            Create and manage automated actions based on triggers and conditions
          </p>
        </div>
        <Dialog open={showRuleBuilder} onOpenChange={setShowRuleBuilder}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Rule
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>Create Automation Rule</DialogTitle>
              <DialogDescription>
                Set up automated actions that trigger based on specific conditions
              </DialogDescription>
            </DialogHeader>
            <RuleBuilder
              onSave={(rule) => {
                setRules(prev => [rule, ...prev]);
                setShowRuleBuilder(false);
                toast.success("Rule created successfully");
              }}
              onCancel={() => setShowRuleBuilder(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search rules..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            <SelectItem value="enabled">Enabled</SelectItem>
            <SelectItem value="disabled">Disabled</SelectItem>
          </SelectContent>
        </Select>
        <Select value={filterTrigger} onValueChange={setFilterTrigger}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Trigger" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Triggers</SelectItem>
            {triggerTypes.map((trigger) => (
              <SelectItem key={trigger.value} value={trigger.value}>
                {trigger.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Rules Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredRules.map((rule) => (
          <Card key={rule.id} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{rule.name}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {rule.description}
                  </CardDescription>
                </div>
                <div className="flex items-center space-x-2">
                  <Switch
                    checked={rule.enabled}
                    onCheckedChange={(enabled) => toggleRule(rule.id, enabled)}
                  />
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => {
                        setSelectedRule(rule);
                        fetchRuleRuns(rule.id);
                        setShowRuleDetails(true);
                      }}>
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </DropdownMenuItem>
                      <DropdownMenuItem>
                        <Edit className="h-4 w-4 mr-2" />
                        Edit Rule
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => deleteRule(rule.id)}
                        className="text-red-600"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete Rule
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Trigger:</span>
                  <Badge variant="outline">
                    {triggerTypes.find(t => t.value === rule.trigger)?.label || rule.trigger}
                  </Badge>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Action:</span>
                  <Badge variant="outline">
                    {actionTypes.find(a => a.value === rule.action)?.label || rule.action}
                  </Badge>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Executions:</span>
                  <span className="font-medium">{rule.run_count}</span>
                </div>
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Success Rate:</span>
                  <span className="font-medium">
                    {rule.run_count > 0 ? Math.round((rule.success_count / rule.run_count) * 100) : 0}%
                  </span>
                </div>
                {rule.last_run && (
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Last Run:</span>
                    <span className="font-medium">{formatTimeAgo(rule.last_run)}</span>
                  </div>
                )}
              </div>

              <div className="pt-2 border-t">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Status</span>
                  <Badge className={rule.enabled ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                    {rule.enabled ? "Active" : "Inactive"}
                  </Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {filteredRules.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Zap className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No rules found</h3>
            <p className="text-muted-foreground text-center mb-4">
              {searchTerm || filterStatus !== "all" || filterTrigger !== "all"
                ? "No rules match your current filters"
                : "Get started by creating your first automation rule"
              }
            </p>
            <Button onClick={() => setShowRuleBuilder(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Rule
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Rule Details Dialog */}
      <Dialog open={showRuleDetails} onOpenChange={setShowRuleDetails}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{selectedRule?.name}</DialogTitle>
            <DialogDescription>
              {selectedRule?.description}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* Rule Configuration */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Trigger</CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge variant="outline">
                    {triggerTypes.find(t => t.value === selectedRule?.trigger)?.label || selectedRule?.trigger}
                  </Badge>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Action</CardTitle>
                </CardHeader>
                <CardContent>
                  <Badge variant="outline">
                    {actionTypes.find(a => a.value === selectedRule?.action)?.label || selectedRule?.action}
                  </Badge>
                </CardContent>
              </Card>
            </div>

            {/* Execution History */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Execution History</h3>
              <div className="space-y-2">
                {ruleRuns.map((run) => (
                  <div key={run.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(run.status)}
                      <div>
                        <p className="text-sm font-medium">
                          {formatTimeAgo(run.executed_at)}
                        </p>
                        {run.duration && (
                          <p className="text-xs text-muted-foreground">
                            Duration: {run.duration}ms
                          </p>
                        )}
                        {run.error_message && (
                          <p className="text-xs text-red-600">
                            Error: {run.error_message}
                          </p>
                        )}
                      </div>
                    </div>
                    <Badge className={getStatusColor(run.status)}>
                      {run.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
