"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Plus,
  Play,
  Pause,
  Settings,
  MoreHorizontal,
  Edit,
  Trash2,
  Eye,
  Copy,
  Workflow,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle,
  ArrowRight,
  Zap,
  Send,
  Bell,
  Webhook,
  Brain,
  Timer
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
import { WorkflowStepEditor } from "./workflow-step-editor";
import { toast } from "react-hot-toast";

interface Workflow {
  id: string;
  name: string;
  description: string;
  trigger_type: string;
  trigger_config: Record<string, any>;
  steps: WorkflowStep[];
  status: "draft" | "active" | "paused" | "completed" | "failed";
  enabled: boolean;
  last_run_at?: string;
  run_count: number;
  success_count: number;
  failure_count: number;
  created_at: string;
  updated_at: string;
}

interface WorkflowStep {
  id: string;
  step_type: "condition" | "action" | "delay" | "webhook" | "ai_task" | "notification";
  name: string;
  description: string;
  config: Record<string, any>;
  position: number;
  next_steps: number[];
}

interface WorkflowExecution {
  id: string;
  workflow_id: string;
  status: "success" | "failed" | "running";
  trigger_data?: Record<string, any>;
  execution_data?: Record<string, any>;
  error_message?: string;
  started_at: string;
  completed_at?: string;
  created_at: string;
}

const triggerTypes = [
  { value: "manual", label: "Manual", description: "Triggered manually by users" },
  { value: "scheduled", label: "Scheduled", description: "Triggered on a schedule" },
  { value: "event_based", label: "Event Based", description: "Triggered by system events" },
  { value: "webhook", label: "Webhook", description: "Triggered by external webhooks" }
];

const stepTypes = [
  { 
    value: "condition", 
    label: "Condition", 
    description: "Evaluate conditions and branch workflow",
    icon: AlertCircle,
    color: "bg-blue-100 text-blue-800"
  },
  { 
    value: "action", 
    label: "Action", 
    description: "Execute an action",
    icon: Zap,
    color: "bg-green-100 text-green-800"
  },
  { 
    value: "delay", 
    label: "Delay", 
    description: "Wait for a specified time",
    icon: Timer,
    color: "bg-yellow-100 text-yellow-800"
  },
  { 
    value: "webhook", 
    label: "Webhook", 
    description: "Send data to external webhook",
    icon: Webhook,
    color: "bg-purple-100 text-purple-800"
  },
  { 
    value: "ai_task", 
    label: "AI Task", 
    description: "Execute AI-powered task",
    icon: Brain,
    color: "bg-pink-100 text-pink-800"
  },
  { 
    value: "notification", 
    label: "Notification", 
    description: "Send notification to users",
    icon: Bell,
    color: "bg-orange-100 text-orange-800"
  }
];

export function WorkflowBuilder() {
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [showWorkflowEditor, setShowWorkflowEditor] = useState(false);
  const [showStepEditor, setShowStepEditor] = useState(false);
  const [editingStep, setEditingStep] = useState<WorkflowStep | null>(null);
  const [workflowExecutions, setWorkflowExecutions] = useState<WorkflowExecution[]>([]);

  const fetchWorkflows = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockWorkflows: Workflow[] = [
        {
          id: "1",
          name: "Content Approval Workflow",
          description: "Automated content review and approval process",
          trigger_type: "manual",
          trigger_config: {},
          steps: [
            {
              id: "step_1",
              step_type: "condition",
              name: "Check Content Quality",
              description: "Evaluate content against quality criteria",
              config: { criteria: ["grammar", "brand_guidelines", "engagement_potential"] },
              position: 0,
              next_steps: [1, 2]
            },
            {
              id: "step_2",
              step_type: "action",
              name: "Approve Content",
              description: "Mark content as approved",
              config: { action: "approve" },
              position: 1,
              next_steps: [3]
            },
            {
              id: "step_3",
              step_type: "notification",
              name: "Send Rejection Notice",
              description: "Notify creator of rejection",
              config: { recipients: ["creator"], template: "rejection" },
              position: 2,
              next_steps: []
            },
            {
              id: "step_4",
              step_type: "action",
              name: "Schedule Content",
              description: "Schedule approved content for publishing",
              config: { action: "schedule" },
              position: 3,
              next_steps: []
            }
          ],
          status: "active",
          enabled: true,
          last_run_at: "2024-01-15T11:00:00Z",
          run_count: 25,
          success_count: 23,
          failure_count: 2,
          created_at: "2024-01-01T00:00:00Z",
          updated_at: "2024-01-15T11:00:00Z"
        },
        {
          id: "2",
          name: "Campaign Launch Sequence",
          description: "Automated campaign setup and launch process",
          trigger_type: "event_based",
          trigger_config: { event: "campaign_created" },
          steps: [
            {
              id: "step_1",
              step_type: "ai_task",
              name: "Generate Ad Copy",
              description: "Use AI to generate ad copy variations",
              config: { model: "gpt-4", variations: 3 },
              position: 0,
              next_steps: [1]
            },
            {
              id: "step_2",
              step_type: "delay",
              name: "Wait for Review",
              description: "Wait 24 hours for manual review",
              config: { duration: "24h" },
              position: 1,
              next_steps: [2]
            },
            {
              id: "step_3",
              step_type: "action",
              name: "Launch Campaign",
              description: "Activate the campaign",
              config: { action: "launch" },
              position: 2,
              next_steps: []
            }
          ],
          status: "paused",
          enabled: false,
          run_count: 8,
          success_count: 6,
          failure_count: 2,
          created_at: "2024-01-05T00:00:00Z",
          updated_at: "2024-01-14T00:00:00Z"
        }
      ];
      
      setWorkflows(mockWorkflows);
    } catch (error) {
      console.error("Failed to fetch workflows:", error);
      toast.error("Failed to load workflows");
    } finally {
      setLoading(false);
    }
  };

  const fetchWorkflowExecutions = async (workflowId: string) => {
    try {
      // Mock data - replace with actual API call
      const mockExecutions: WorkflowExecution[] = [
        {
          id: "1",
          workflow_id: workflowId,
          status: "success",
          trigger_data: { user_id: "123", content_id: "456" },
          execution_data: { steps_completed: 4, duration_ms: 2500 },
          started_at: "2024-01-15T11:00:00Z",
          completed_at: "2024-01-15T11:00:02Z",
          created_at: "2024-01-15T11:00:00Z"
        },
        {
          id: "2",
          workflow_id: workflowId,
          status: "failed",
          trigger_data: { user_id: "123", content_id: "789" },
          error_message: "Failed to connect to AI service",
          started_at: "2024-01-15T10:30:00Z",
          completed_at: "2024-01-15T10:30:05Z",
          created_at: "2024-01-15T10:30:00Z"
        }
      ];
      
      setWorkflowExecutions(mockExecutions);
    } catch (error) {
      console.error("Failed to fetch workflow executions:", error);
      toast.error("Failed to load execution history");
    }
  };

  useEffect(() => {
    fetchWorkflows();
  }, []);

  const toggleWorkflow = async (workflowId: string, enabled: boolean) => {
    try {
      setWorkflows(prev => prev.map(workflow => 
        workflow.id === workflowId ? { ...workflow, enabled } : workflow
      ));
      toast.success(`Workflow ${enabled ? 'enabled' : 'disabled'} successfully`);
    } catch (error) {
      console.error("Failed to toggle workflow:", error);
      toast.error("Failed to update workflow");
    }
  };

  const deleteWorkflow = async (workflowId: string) => {
    try {
      setWorkflows(prev => prev.filter(workflow => workflow.id !== workflowId));
      toast.success("Workflow deleted successfully");
    } catch (error) {
      console.error("Failed to delete workflow:", error);
      toast.error("Failed to delete workflow");
    }
  };

  const executeWorkflow = async (workflowId: string) => {
    try {
      // Mock API call - replace with actual implementation
      toast.success("Workflow execution started");
    } catch (error) {
      console.error("Failed to execute workflow:", error);
      toast.error("Failed to execute workflow");
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

  const renderWorkflowVisualization = (workflow: Workflow) => {
    const sortedSteps = [...workflow.steps].sort((a, b) => a.position - b.position);
    
    return (
      <div className="space-y-4">
        {sortedSteps.map((step, index) => {
          const stepType = stepTypes.find(t => t.value === step.step_type);
          const Icon = stepType?.icon || AlertCircle;
          
          return (
            <div key={step.id} className="flex items-center">
              <div className={cn(
                "flex items-center space-x-3 p-3 rounded-lg border-2 border-dashed",
                stepType?.color || "bg-gray-100 text-gray-800"
              )}>
                <Icon className="h-5 w-5" />
                <div>
                  <h4 className="font-medium">{step.name}</h4>
                  <p className="text-sm opacity-75">{step.description}</p>
                </div>
              </div>
              
              {index < sortedSteps.length - 1 && (
                <ArrowRight className="h-4 w-4 mx-4 text-muted-foreground" />
              )}
            </div>
          );
        })}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {Array.from({ length: 4 }).map((_, i) => (
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
          <h2 className="text-2xl font-bold tracking-tight">Workflows</h2>
          <p className="text-muted-foreground">
            Create and manage automated workflows with visual flow builder
          </p>
        </div>
        <Dialog open={showWorkflowEditor} onOpenChange={setShowWorkflowEditor}>
          <DialogTrigger asChild>
            <Button>
              <Plus className="h-4 w-4 mr-2" />
              Create Workflow
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-4xl">
            <DialogHeader>
              <DialogTitle>Create Workflow</DialogTitle>
              <DialogDescription>
                Build automated workflows with visual flow builder
              </DialogDescription>
            </DialogHeader>
            <WorkflowStepEditor
              onSave={(workflow) => {
                setWorkflows(prev => [workflow, ...prev]);
                setShowWorkflowEditor(false);
                toast.success("Workflow created successfully");
              }}
              onCancel={() => setShowWorkflowEditor(false)}
            />
          </DialogContent>
        </Dialog>
      </div>

      {/* Workflows Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {workflows.map((workflow) => (
          <Card key={workflow.id} className="relative">
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="space-y-1">
                  <CardTitle className="text-lg">{workflow.name}</CardTitle>
                  <CardDescription className="line-clamp-2">
                    {workflow.description}
                  </CardDescription>
                  <div className="flex items-center space-x-2">
                    <Badge variant="outline">
                      {triggerTypes.find(t => t.value === workflow.trigger_type)?.label || workflow.trigger_type}
                    </Badge>
                    <Badge className={workflow.enabled ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"}>
                      {workflow.enabled ? "Active" : "Inactive"}
                    </Badge>
                  </div>
                </div>
                <DropdownMenu>
                  <DropdownMenuTrigger asChild>
                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </DropdownMenuTrigger>
                  <DropdownMenuContent align="end">
                    <DropdownMenuItem onClick={() => executeWorkflow(workflow.id)}>
                      <Play className="h-4 w-4 mr-2" />
                      Execute Now
                    </DropdownMenuItem>
                    <DropdownMenuItem onClick={() => {
                      setSelectedWorkflow(workflow);
                      fetchWorkflowExecutions(workflow.id);
                    }}>
                      <Eye className="h-4 w-4 mr-2" />
                      View Details
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Edit className="h-4 w-4 mr-2" />
                      Edit Workflow
                    </DropdownMenuItem>
                    <DropdownMenuItem>
                      <Copy className="h-4 w-4 mr-2" />
                      Duplicate
                    </DropdownMenuItem>
                    <DropdownMenuSeparator />
                    <DropdownMenuItem 
                      onClick={() => toggleWorkflow(workflow.id, !workflow.enabled)}
                    >
                      {workflow.enabled ? (
                        <>
                          <Pause className="h-4 w-4 mr-2" />
                          Disable
                        </>
                      ) : (
                        <>
                          <Play className="h-4 w-4 mr-2" />
                          Enable
                        </>
                      )}
                    </DropdownMenuItem>
                    <DropdownMenuItem 
                      onClick={() => deleteWorkflow(workflow.id)}
                      className="text-red-600"
                    >
                      <Trash2 className="h-4 w-4 mr-2" />
                      Delete Workflow
                    </DropdownMenuItem>
                  </DropdownMenuContent>
                </DropdownMenu>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Workflow Visualization */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium">Workflow Steps</h4>
                <div className="max-h-32 overflow-y-auto">
                  {renderWorkflowVisualization(workflow)}
                </div>
              </div>

              {/* Statistics */}
              <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                <div className="text-center">
                  <div className="text-2xl font-bold">{workflow.run_count}</div>
                  <div className="text-xs text-muted-foreground">Total Runs</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    {workflow.run_count > 0 ? Math.round((workflow.success_count / workflow.run_count) * 100) : 0}%
                  </div>
                  <div className="text-xs text-muted-foreground">Success Rate</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{workflow.steps.length}</div>
                  <div className="text-xs text-muted-foreground">Steps</div>
                </div>
              </div>

              {workflow.last_run_at && (
                <div className="text-xs text-muted-foreground">
                  Last run: {formatTimeAgo(workflow.last_run_at)}
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {workflows.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Workflow className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No workflows found</h3>
            <p className="text-muted-foreground text-center mb-4">
              Get started by creating your first workflow
            </p>
            <Button onClick={() => setShowWorkflowEditor(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Your First Workflow
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Workflow Details Dialog */}
      <Dialog open={!!selectedWorkflow} onOpenChange={() => setSelectedWorkflow(null)}>
        <DialogContent className="max-w-4xl">
          <DialogHeader>
            <DialogTitle>{selectedWorkflow?.name}</DialogTitle>
            <DialogDescription>
              {selectedWorkflow?.description}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-6">
            {/* Workflow Visualization */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Workflow Flow</h3>
              {selectedWorkflow && renderWorkflowVisualization(selectedWorkflow)}
            </div>

            {/* Execution History */}
            <div>
              <h3 className="text-lg font-semibold mb-4">Execution History</h3>
              <div className="space-y-2">
                {workflowExecutions.map((execution) => (
                  <div key={execution.id} className="flex items-center justify-between p-3 rounded-lg border">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(execution.status)}
                      <div>
                        <p className="text-sm font-medium">
                          {formatTimeAgo(execution.started_at)}
                        </p>
                        {execution.execution_data && (
                          <p className="text-xs text-muted-foreground">
                            Duration: {execution.execution_data.duration_ms}ms
                          </p>
                        )}
                        {execution.error_message && (
                          <p className="text-xs text-red-600">
                            Error: {execution.error_message}
                          </p>
                        )}
                      </div>
                    </div>
                    <Badge className={getStatusColor(execution.status)}>
                      {execution.status}
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
