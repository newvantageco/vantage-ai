"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Plus,
  Minus,
  Trash2,
  Save,
  X,
  ArrowRight,
  Settings,
  AlertCircle,
  CheckCircle,
  Zap,
  Timer,
  Webhook,
  Brain,
  Bell,
  Play,
  Pause
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "react-hot-toast";

interface WorkflowStepEditorProps {
  onSave: (workflow: any) => void;
  onCancel: () => void;
  initialWorkflow?: any;
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

export function WorkflowStepEditor({ onSave, onCancel, initialWorkflow }: WorkflowStepEditorProps) {
  const [step, setStep] = useState(1);
  const [workflowName, setWorkflowName] = useState(initialWorkflow?.name || "");
  const [workflowDescription, setWorkflowDescription] = useState(initialWorkflow?.description || "");
  const [triggerType, setTriggerType] = useState(initialWorkflow?.trigger_type || "");
  const [triggerConfig, setTriggerConfig] = useState(initialWorkflow?.trigger_config || {});
  const [steps, setSteps] = useState<WorkflowStep[]>(initialWorkflow?.steps || []);
  const [enabled, setEnabled] = useState(initialWorkflow?.enabled ?? true);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateStep = (stepNumber: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (stepNumber === 1) {
      if (!workflowName.trim()) newErrors.name = "Workflow name is required";
      if (!workflowDescription.trim()) newErrors.description = "Workflow description is required";
      if (!triggerType) newErrors.trigger = "Trigger type is required";
    } else if (stepNumber === 2) {
      if (steps.length === 0) newErrors.steps = "At least one step is required";
      steps.forEach((step, index) => {
        if (!step.name.trim()) newErrors[`step_${index}_name`] = "Step name is required";
        if (!step.step_type) newErrors[`step_${index}_type`] = "Step type is required";
      });
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep(step + 1);
    }
  };

  const handlePrevious = () => {
    setStep(step - 1);
  };

  const handleSave = () => {
    if (validateStep(1) && validateStep(2)) {
      const workflow = {
        id: initialWorkflow?.id || `workflow_${Date.now()}`,
        name: workflowName,
        description: workflowDescription,
        trigger_type: triggerType,
        trigger_config: triggerConfig,
        steps,
        enabled,
        status: "draft",
        run_count: 0,
        success_count: 0,
        failure_count: 0,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      onSave(workflow);
    }
  };

  const addStep = () => {
    const newStep: WorkflowStep = {
      id: `step_${Date.now()}`,
      step_type: "action",
      name: "",
      description: "",
      config: {},
      position: steps.length,
      next_steps: []
    };
    setSteps([...steps, newStep]);
  };

  const updateStep = (id: string, field: string, value: any) => {
    setSteps(steps.map(step => 
      step.id === id ? { ...step, [field]: value } : step
    ));
  };

  const removeStep = (id: string) => {
    setSteps(steps.filter(step => step.id !== id));
  };

  const moveStep = (id: string, direction: "up" | "down") => {
    const index = steps.findIndex(step => step.id === id);
    if (index === -1) return;

    const newSteps = [...steps];
    if (direction === "up" && index > 0) {
      [newSteps[index], newSteps[index - 1]] = [newSteps[index - 1], newSteps[index]];
      // Update positions
      newSteps[index].position = index;
      newSteps[index - 1].position = index - 1;
    } else if (direction === "down" && index < steps.length - 1) {
      [newSteps[index], newSteps[index + 1]] = [newSteps[index + 1], newSteps[index]];
      // Update positions
      newSteps[index].position = index;
      newSteps[index + 1].position = index + 1;
    }
    setSteps(newSteps);
  };

  const renderStepConfiguration = (step: WorkflowStep) => {
    switch (step.step_type) {
      case "condition":
        return (
          <div className="space-y-4">
            <div>
              <Label>Condition Logic</Label>
              <Textarea
                placeholder="Enter condition logic (e.g., engagement_rate > 0.05)"
                value={step.config.condition || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, condition: e.target.value })}
              />
            </div>
            <div>
              <Label>True Next Steps</Label>
              <Input
                placeholder="Comma-separated step positions (e.g., 1, 2)"
                value={step.config.true_steps || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, true_steps: e.target.value })}
              />
            </div>
            <div>
              <Label>False Next Steps</Label>
              <Input
                placeholder="Comma-separated step positions (e.g., 3)"
                value={step.config.false_steps || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, false_steps: e.target.value })}
              />
            </div>
          </div>
        );
      
      case "action":
        return (
          <div className="space-y-4">
            <div>
              <Label>Action Type</Label>
              <Select
                value={step.config.action_type || ""}
                onValueChange={(value) => updateStep(step.id, "config", { ...step.config, action_type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select action type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="publish_content">Publish Content</SelectItem>
                  <SelectItem value="schedule_content">Schedule Content</SelectItem>
                  <SelectItem value="pause_campaign">Pause Campaign</SelectItem>
                  <SelectItem value="resume_campaign">Resume Campaign</SelectItem>
                  <SelectItem value="send_email">Send Email</SelectItem>
                  <SelectItem value="update_budget">Update Budget</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Action Parameters</Label>
              <Textarea
                placeholder="Enter action parameters as JSON"
                value={step.config.parameters || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, parameters: e.target.value })}
              />
            </div>
          </div>
        );
      
      case "delay":
        return (
          <div className="space-y-4">
            <div>
              <Label>Delay Duration</Label>
              <div className="flex space-x-2">
                <Input
                  type="number"
                  placeholder="Duration"
                  value={step.config.duration || ""}
                  onChange={(e) => updateStep(step.id, "config", { ...step.config, duration: e.target.value })}
                />
                <Select
                  value={step.config.duration_unit || "minutes"}
                  onValueChange={(value) => updateStep(step.id, "config", { ...step.config, duration_unit: value })}
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="seconds">Seconds</SelectItem>
                    <SelectItem value="minutes">Minutes</SelectItem>
                    <SelectItem value="hours">Hours</SelectItem>
                    <SelectItem value="days">Days</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </div>
        );
      
      case "webhook":
        return (
          <div className="space-y-4">
            <div>
              <Label>Webhook URL</Label>
              <Input
                placeholder="https://example.com/webhook"
                value={step.config.url || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, url: e.target.value })}
              />
            </div>
            <div>
              <Label>HTTP Method</Label>
              <Select
                value={step.config.method || "POST"}
                onValueChange={(value) => updateStep(step.id, "config", { ...step.config, method: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="GET">GET</SelectItem>
                  <SelectItem value="POST">POST</SelectItem>
                  <SelectItem value="PUT">PUT</SelectItem>
                  <SelectItem value="PATCH">PATCH</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Headers</Label>
              <Textarea
                placeholder='{"Authorization": "Bearer token", "Content-Type": "application/json"}'
                value={step.config.headers || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, headers: e.target.value })}
              />
            </div>
          </div>
        );
      
      case "ai_task":
        return (
          <div className="space-y-4">
            <div>
              <Label>AI Task Type</Label>
              <Select
                value={step.config.task_type || ""}
                onValueChange={(value) => updateStep(step.id, "config", { ...step.config, task_type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select AI task type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="generate_content">Generate Content</SelectItem>
                  <SelectItem value="analyze_sentiment">Analyze Sentiment</SelectItem>
                  <SelectItem value="extract_keywords">Extract Keywords</SelectItem>
                  <SelectItem value="translate_text">Translate Text</SelectItem>
                  <SelectItem value="summarize_text">Summarize Text</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>AI Model</Label>
              <Select
                value={step.config.model || "gpt-4"}
                onValueChange={(value) => updateStep(step.id, "config", { ...step.config, model: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="gpt-4">GPT-4</SelectItem>
                  <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                  <SelectItem value="claude-3">Claude 3</SelectItem>
                  <SelectItem value="claude-2">Claude 2</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Task Parameters</Label>
              <Textarea
                placeholder="Enter task parameters as JSON"
                value={step.config.parameters || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, parameters: e.target.value })}
              />
            </div>
          </div>
        );
      
      case "notification":
        return (
          <div className="space-y-4">
            <div>
              <Label>Notification Type</Label>
              <Select
                value={step.config.notification_type || ""}
                onValueChange={(value) => updateStep(step.id, "config", { ...step.config, notification_type: value })}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select notification type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="email">Email</SelectItem>
                  <SelectItem value="slack">Slack</SelectItem>
                  <SelectItem value="teams">Microsoft Teams</SelectItem>
                  <SelectItem value="discord">Discord</SelectItem>
                  <SelectItem value="webhook">Webhook</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div>
              <Label>Recipients</Label>
              <Input
                placeholder="Comma-separated emails or user IDs"
                value={step.config.recipients || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, recipients: e.target.value })}
              />
            </div>
            <div>
              <Label>Message Template</Label>
              <Textarea
                placeholder="Enter message template with variables like {{workflow_name}}"
                value={step.config.template || ""}
                onChange={(e) => updateStep(step.id, "config", { ...step.config, template: e.target.value })}
              />
            </div>
          </div>
        );
      
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center space-x-4">
        {[1, 2].map((stepNumber) => (
          <div key={stepNumber} className="flex items-center">
            <div className={cn(
              "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium",
              step >= stepNumber 
                ? "bg-primary text-primary-foreground" 
                : "bg-muted text-muted-foreground"
            )}>
              {step > stepNumber ? <CheckCircle className="h-4 w-4" /> : stepNumber}
            </div>
            {stepNumber < 2 && (
              <ArrowRight className="h-4 w-4 mx-2 text-muted-foreground" />
            )}
          </div>
        ))}
      </div>

      {/* Step 1: Basic Information */}
      {step === 1 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Settings className="h-5 w-5 mr-2" />
              Basic Information
            </CardTitle>
            <CardDescription>
              Set up the basic details for your workflow
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="workflow-name">Workflow Name *</Label>
              <Input
                id="workflow-name"
                value={workflowName}
                onChange={(e) => setWorkflowName(e.target.value)}
                placeholder="e.g., Content Approval Workflow"
                className={errors.name ? "border-red-500" : ""}
              />
              {errors.name && (
                <p className="text-sm text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.name}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="workflow-description">Description *</Label>
              <Textarea
                id="workflow-description"
                value={workflowDescription}
                onChange={(e) => setWorkflowDescription(e.target.value)}
                placeholder="Describe what this workflow does..."
                className={errors.description ? "border-red-500" : ""}
              />
              {errors.description && (
                <p className="text-sm text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.description}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="trigger">Trigger Type *</Label>
              <Select value={triggerType} onValueChange={setTriggerType}>
                <SelectTrigger className={errors.trigger ? "border-red-500" : ""}>
                  <SelectValue placeholder="Select trigger type" />
                </SelectTrigger>
                <SelectContent>
                  {triggerTypes.map((trigger) => (
                    <SelectItem key={trigger.value} value={trigger.value}>
                      <div>
                        <div className="font-medium">{trigger.label}</div>
                        <div className="text-sm text-muted-foreground">{trigger.description}</div>
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.trigger && (
                <p className="text-sm text-red-500 flex items-center">
                  <AlertCircle className="h-4 w-4 mr-1" />
                  {errors.trigger}
                </p>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="enabled"
                checked={enabled}
                onChange={(e) => setEnabled(e.target.checked)}
                className="rounded"
              />
              <Label htmlFor="enabled">Enable this workflow</Label>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Workflow Steps */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Zap className="h-5 w-5 mr-2" />
              Workflow Steps
            </CardTitle>
            <CardDescription>
              Define the steps in your workflow
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {steps.map((step, index) => {
              const stepType = stepTypes.find(t => t.value === step.step_type);
              const Icon = stepType?.icon || AlertCircle;
              
              return (
                <div key={step.id} className="p-4 border rounded-lg space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-3">
                      <div className={cn("p-2 rounded-lg", stepType?.color || "bg-gray-100")}>
                        <Icon className="h-4 w-4" />
                      </div>
                      <div>
                        <h4 className="font-medium">Step {index + 1}</h4>
                        <p className="text-sm text-muted-foreground">
                          {stepType?.label || "Unknown Step Type"}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      {index > 0 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => moveStep(step.id, "up")}
                        >
                          ↑
                        </Button>
                      )}
                      {index < steps.length - 1 && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => moveStep(step.id, "down")}
                        >
                          ↓
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeStep(step.id)}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Step Name</Label>
                      <Input
                        value={step.name}
                        onChange={(e) => updateStep(step.id, "name", e.target.value)}
                        placeholder="Enter step name"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>Step Type</Label>
                      <Select
                        value={step.step_type}
                        onValueChange={(value) => updateStep(step.id, "step_type", value)}
                      >
                        <SelectTrigger>
                          <SelectValue placeholder="Select step type" />
                        </SelectTrigger>
                        <SelectContent>
                          {stepTypes.map((type) => (
                            <SelectItem key={type.value} value={type.value}>
                              <div className="flex items-center space-x-2">
                                <type.icon className="h-4 w-4" />
                                <span>{type.label}</span>
                              </div>
                            </SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Label>Description</Label>
                    <Textarea
                      value={step.description}
                      onChange={(e) => updateStep(step.id, "description", e.target.value)}
                      placeholder="Describe what this step does..."
                    />
                  </div>

                  {renderStepConfiguration(step)}
                </div>
              );
            })}

            <Button variant="outline" onClick={addStep} className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Add Step
            </Button>

            {errors.steps && (
              <p className="text-sm text-red-500 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.steps}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {step > 1 && (
            <Button variant="outline" onClick={handlePrevious}>
              Previous
            </Button>
          )}
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={onCancel}>
            <X className="h-4 w-4 mr-2" />
            Cancel
          </Button>
          {step < 2 ? (
            <Button onClick={handleNext}>
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              Save Workflow
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
