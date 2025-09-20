"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";
import {
  Plus,
  Minus,
  Trash2,
  Save,
  X,
  Zap,
  Settings,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  HelpCircle
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { toast } from "react-hot-toast";

interface RuleBuilderProps {
  onSave: (rule: any) => void;
  onCancel: () => void;
  initialRule?: any;
}

interface Condition {
  id: string;
  field: string;
  operator: string;
  value: string | number;
  logicalOperator?: "AND" | "OR";
}

interface Action {
  id: string;
  type: string;
  config: Record<string, any>;
}

const triggerTypes = [
  { value: "post_performance", label: "Post Performance", description: "Trigger when post metrics change" },
  { value: "weekly_brief_generated", label: "Weekly Brief Generated", description: "Trigger when weekly brief is created" },
  { value: "inbox_message_received", label: "Inbox Message Received", description: "Trigger when new message arrives" },
  { value: "campaign_created", label: "Campaign Created", description: "Trigger when new campaign is created" },
  { value: "schedule_posted", label: "Schedule Posted", description: "Trigger when content is scheduled" }
];

const fieldOptions = {
  post_performance: [
    { value: "engagement_rate", label: "Engagement Rate", type: "number" },
    { value: "click_through_rate", label: "Click Through Rate", type: "number" },
    { value: "impressions", label: "Impressions", type: "number" },
    { value: "likes", label: "Likes", type: "number" },
    { value: "comments", label: "Comments", type: "number" },
    { value: "shares", label: "Shares", type: "number" }
  ],
  weekly_brief_generated: [
    { value: "brief_type", label: "Brief Type", type: "select", options: ["performance", "content", "engagement"] },
    { value: "priority", label: "Priority", type: "select", options: ["low", "medium", "high"] }
  ],
  inbox_message_received: [
    { value: "platform", label: "Platform", type: "select", options: ["facebook", "instagram", "linkedin", "twitter"] },
    { value: "message_type", label: "Message Type", type: "select", options: ["comment", "dm", "mention"] },
    { value: "urgency", label: "Urgency", type: "select", options: ["low", "medium", "high"] }
  ],
  campaign_created: [
    { value: "campaign_type", label: "Campaign Type", type: "select", options: ["awareness", "conversion", "engagement"] },
    { value: "budget", label: "Budget", type: "number" },
    { value: "duration_days", label: "Duration (Days)", type: "number" }
  ],
  schedule_posted: [
    { value: "platform", label: "Platform", type: "select", options: ["facebook", "instagram", "linkedin", "twitter"] },
    { value: "content_type", label: "Content Type", type: "select", options: ["text", "image", "video", "carousel"] },
    { value: "scheduled_time", label: "Scheduled Time", type: "time" }
  ]
};

const operators = [
  { value: "eq", label: "Equals", description: "Field equals value" },
  { value: "ne", label: "Not Equals", description: "Field does not equal value" },
  { value: "gt", label: "Greater Than", description: "Field is greater than value" },
  { value: "gte", label: "Greater Than or Equal", description: "Field is greater than or equal to value" },
  { value: "lt", label: "Less Than", description: "Field is less than value" },
  { value: "lte", label: "Less Than or Equal", description: "Field is less than or equal to value" },
  { value: "in", label: "In", description: "Field is in list of values" },
  { value: "not_in", label: "Not In", description: "Field is not in list of values" },
  { value: "contains", label: "Contains", description: "Field contains value" },
  { value: "not_contains", label: "Does Not Contain", description: "Field does not contain value" }
];

const actionTypes = [
  { value: "clone_content_and_reschedule", label: "Clone Content & Reschedule", description: "Create a copy of content and schedule it" },
  { value: "increase_budget_pct", label: "Increase Budget %", description: "Increase advertising budget by percentage" },
  { value: "pause_underperformer", label: "Pause Underperformer", description: "Pause underperforming content or campaigns" },
  { value: "send_notification", label: "Send Notification", description: "Send notification to team members" },
  { value: "pause_campaign", label: "Pause Campaign", description: "Pause a specific campaign" },
  { value: "resume_campaign", label: "Resume Campaign", description: "Resume a paused campaign" }
];

export function RuleBuilder({ onSave, onCancel, initialRule }: RuleBuilderProps) {
  const [step, setStep] = useState(1);
  const [ruleName, setRuleName] = useState(initialRule?.name || "");
  const [ruleDescription, setRuleDescription] = useState(initialRule?.description || "");
  const [trigger, setTrigger] = useState(initialRule?.trigger || "");
  const [conditions, setConditions] = useState<Condition[]>(initialRule?.conditions || []);
  const [actions, setActions] = useState<Action[]>(initialRule?.actions || []);
  const [enabled, setEnabled] = useState(initialRule?.enabled ?? true);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateStep = (stepNumber: number): boolean => {
    const newErrors: Record<string, string> = {};

    if (stepNumber === 1) {
      if (!ruleName.trim()) newErrors.name = "Rule name is required";
      if (!ruleDescription.trim()) newErrors.description = "Rule description is required";
      if (!trigger) newErrors.trigger = "Trigger type is required";
    } else if (stepNumber === 2) {
      if (conditions.length === 0) newErrors.conditions = "At least one condition is required";
      conditions.forEach((condition, index) => {
        if (!condition.field) newErrors[`condition_${index}_field`] = "Field is required";
        if (!condition.operator) newErrors[`condition_${index}_operator`] = "Operator is required";
        if (condition.value === undefined || condition.value === "") newErrors[`condition_${index}_value`] = "Value is required";
      });
    } else if (stepNumber === 3) {
      if (actions.length === 0) newErrors.actions = "At least one action is required";
      actions.forEach((action, index) => {
        if (!action.type) newErrors[`action_${index}_type`] = "Action type is required";
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
    if (validateStep(1) && validateStep(2) && validateStep(3)) {
      const rule = {
        id: initialRule?.id || `rule_${Date.now()}`,
        name: ruleName,
        description: ruleDescription,
        trigger,
        conditions,
        actions,
        enabled,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };
      onSave(rule);
    }
  };

  const addCondition = () => {
    const newCondition: Condition = {
      id: `condition_${Date.now()}`,
      field: "",
      operator: "",
      value: ""
    };
    setConditions([...conditions, newCondition]);
  };

  const updateCondition = (id: string, field: string, value: any) => {
    setConditions(conditions.map(condition => 
      condition.id === id ? { ...condition, [field]: value } : condition
    ));
  };

  const removeCondition = (id: string) => {
    setConditions(conditions.filter(condition => condition.id !== id));
  };

  const addAction = () => {
    const newAction: Action = {
      id: `action_${Date.now()}`,
      type: "",
      config: {}
    };
    setActions([...actions, newAction]);
  };

  const updateAction = (id: string, field: string, value: any) => {
    setActions(actions.map(action => 
      action.id === id ? { ...action, [field]: value } : action
    ));
  };

  const removeAction = (id: string) => {
    setActions(actions.filter(action => action.id !== id));
  };

  const getFieldType = (fieldValue: string) => {
    const field = fieldOptions[trigger as keyof typeof fieldOptions]?.find(f => f.value === fieldValue);
    return field?.type || "text";
  };

  const getFieldOptions = (fieldValue: string) => {
    const field = fieldOptions[trigger as keyof typeof fieldOptions]?.find(f => f.value === fieldValue);
    return (field as any)?.options || [];
  };

  const renderValueInput = (condition: Condition) => {
    const fieldType = getFieldType(condition.field);
    const fieldOptions = getFieldOptions(condition.field);

    if (fieldType === "select") {
      return (
        <Select
          value={condition.value as string}
          onValueChange={(value) => updateCondition(condition.id, "value", value)}
        >
          <SelectTrigger>
            <SelectValue placeholder="Select value" />
          </SelectTrigger>
          <SelectContent>
            {fieldOptions.map((option: string) => (
              <SelectItem key={option} value={option}>
                {option}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      );
    } else if (fieldType === "number") {
      return (
        <Input
          type="number"
          value={condition.value}
          onChange={(e) => updateCondition(condition.id, "value", parseFloat(e.target.value) || 0)}
          placeholder="Enter value"
        />
      );
    } else if (fieldType === "time") {
      return (
        <Input
          type="time"
          value={condition.value}
          onChange={(e) => updateCondition(condition.id, "value", e.target.value)}
        />
      );
    } else {
      return (
        <Input
          type="text"
          value={condition.value}
          onChange={(e) => updateCondition(condition.id, "value", e.target.value)}
          placeholder="Enter value"
        />
      );
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Indicator */}
      <div className="flex items-center space-x-4">
        {[1, 2, 3].map((stepNumber) => (
          <div key={stepNumber} className="flex items-center">
            <div className={cn(
              "flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium",
              step >= stepNumber 
                ? "bg-primary text-primary-foreground" 
                : "bg-muted text-muted-foreground"
            )}>
              {step > stepNumber ? <CheckCircle className="h-4 w-4" /> : stepNumber}
            </div>
            {stepNumber < 3 && (
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
              Set up the basic details for your automation rule
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="rule-name">Rule Name *</Label>
              <Input
                id="rule-name"
                value={ruleName}
                onChange={(e) => setRuleName(e.target.value)}
                placeholder="e.g., Auto-pause underperforming posts"
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
              <Label htmlFor="rule-description">Description *</Label>
              <Textarea
                id="rule-description"
                value={ruleDescription}
                onChange={(e) => setRuleDescription(e.target.value)}
                placeholder="Describe what this rule does..."
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
              <Select value={trigger} onValueChange={setTrigger}>
                <SelectTrigger className={errors.trigger ? "border-red-500" : ""}>
                  <SelectValue placeholder="Select trigger type" />
                </SelectTrigger>
                <SelectContent>
                  {triggerTypes.map((triggerType) => (
                    <SelectItem key={triggerType.value} value={triggerType.value}>
                      <div>
                        <div className="font-medium">{triggerType.label}</div>
                        <div className="text-sm text-muted-foreground">{triggerType.description}</div>
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
              <Switch
                id="enabled"
                checked={enabled}
                onCheckedChange={setEnabled}
              />
              <Label htmlFor="enabled">Enable this rule</Label>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Step 2: Conditions */}
      {step === 2 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <AlertCircle className="h-5 w-5 mr-2" />
              Conditions
            </CardTitle>
            <CardDescription>
              Define when this rule should trigger
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {conditions.map((condition, index) => (
              <div key={condition.id} className="p-4 border rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Condition {index + 1}</h4>
                  {conditions.length > 1 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeCondition(condition.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="space-y-2">
                    <Label>Field</Label>
                    <Select
                      value={condition.field}
                      onValueChange={(value) => updateCondition(condition.id, "field", value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select field" />
                      </SelectTrigger>
                      <SelectContent>
                        {fieldOptions[trigger as keyof typeof fieldOptions]?.map((field) => (
                          <SelectItem key={field.value} value={field.value}>
                            {field.label}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Operator</Label>
                    <Select
                      value={condition.operator}
                      onValueChange={(value) => updateCondition(condition.id, "operator", value)}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select operator" />
                      </SelectTrigger>
                      <SelectContent>
                        {operators.map((operator) => (
                          <SelectItem key={operator.value} value={operator.value}>
                            <div>
                              <div className="font-medium">{operator.label}</div>
                              <div className="text-sm text-muted-foreground">{operator.description}</div>
                            </div>
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>

                  <div className="space-y-2">
                    <Label>Value</Label>
                    {renderValueInput(condition)}
                  </div>
                </div>

                {index < conditions.length - 1 && (
                  <div className="flex items-center space-x-2">
                    <Select
                      value={condition.logicalOperator || "AND"}
                      onValueChange={(value) => updateCondition(condition.id, "logicalOperator", value)}
                    >
                      <SelectTrigger className="w-24">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="AND">AND</SelectItem>
                        <SelectItem value="OR">OR</SelectItem>
                      </SelectContent>
                    </Select>
                    <span className="text-sm text-muted-foreground">next condition</span>
                  </div>
                )}
              </div>
            ))}

            <Button variant="outline" onClick={addCondition} className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Add Condition
            </Button>

            {errors.conditions && (
              <p className="text-sm text-red-500 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.conditions}
              </p>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 3: Actions */}
      {step === 3 && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Zap className="h-5 w-5 mr-2" />
              Actions
            </CardTitle>
            <CardDescription>
              Define what should happen when conditions are met
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {actions.map((action, index) => (
              <div key={action.id} className="p-4 border rounded-lg space-y-4">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">Action {index + 1}</h4>
                  {actions.length > 1 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeAction(action.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>

                <div className="space-y-2">
                  <Label>Action Type</Label>
                  <Select
                    value={action.type}
                    onValueChange={(value) => updateAction(action.id, "type", value)}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select action type" />
                    </SelectTrigger>
                    <SelectContent>
                      {actionTypes.map((actionType) => (
                        <SelectItem key={actionType.value} value={actionType.value}>
                          <div>
                            <div className="font-medium">{actionType.label}</div>
                            <div className="text-sm text-muted-foreground">{actionType.description}</div>
                          </div>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {/* Action-specific configuration would go here */}
                {action.type && (
                  <div className="p-3 bg-muted rounded-lg">
                    <p className="text-sm text-muted-foreground">
                      Configuration options for {actionTypes.find(a => a.value === action.type)?.label} will appear here
                    </p>
                  </div>
                )}
              </div>
            ))}

            <Button variant="outline" onClick={addAction} className="w-full">
              <Plus className="h-4 w-4 mr-2" />
              Add Action
            </Button>

            {errors.actions && (
              <p className="text-sm text-red-500 flex items-center">
                <AlertCircle className="h-4 w-4 mr-1" />
                {errors.actions}
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
          {step < 3 ? (
            <Button onClick={handleNext}>
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button onClick={handleSave}>
              <Save className="h-4 w-4 mr-2" />
              Save Rule
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
