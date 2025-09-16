"use client";

import { useState, useEffect } from "react";
import { Plus, Play, Pause, Settings, History, TestTube } from "lucide-react";

interface Rule {
  id: string;
  name: string;
  description?: string;
  trigger: string;
  condition_json: any;
  action_json: any;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

interface RuleRun {
  id: string;
  rule_id: string;
  status: string;
  last_run_at?: string;
  meta_json?: any;
  started_at?: string;
  completed_at?: string;
  created_at: string;
}

interface RuleFormData {
  name: string;
  description: string;
  trigger: string;
  condition_json: any;
  action_json: any;
  enabled: boolean;
}

const TRIGGER_OPTIONS = [
  { value: "post_performance", label: "Post Performance" },
  { value: "weekly_brief_generated", label: "Weekly Brief Generated" },
  { value: "inbox_message_received", label: "Inbox Message Received" },
  { value: "campaign_created", label: "Campaign Created" },
  { value: "schedule_posted", label: "Schedule Posted" },
];

const ACTION_OPTIONS = [
  { value: "clone_content_and_reschedule", label: "Clone Content & Reschedule" },
  { value: "increase_budget_pct", label: "Increase Budget %" },
  { value: "pause_underperformer", label: "Pause Underperformer" },
  { value: "send_notification", label: "Send Notification" },
  { value: "pause_campaign", label: "Pause Campaign" },
  { value: "resume_campaign", label: "Resume Campaign" },
];

const CONDITION_OPERATORS = [
  { value: "eq", label: "Equals" },
  { value: "gt", label: "Greater Than" },
  { value: "lt", label: "Less Than" },
  { value: "in", label: "In List" },
  { value: "and", label: "And" },
  { value: "or", label: "Or" },
];

export default function AutomationsPage() {
  const [rules, setRules] = useState<Rule[]>([]);
  const [ruleRuns, setRuleRuns] = useState<RuleRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [showTestModal, setShowTestModal] = useState(false);
  const [editingRule, setEditingRule] = useState<Rule | null>(null);
  const [formData, setFormData] = useState<RuleFormData>({
    name: "",
    description: "",
    trigger: "post_performance",
    condition_json: { operator: "eq", field: "engagement_rate", value: 0.01 },
    action_json: { type: "clone_content_and_reschedule", params: {} },
    enabled: true,
  });

  useEffect(() => {
    fetchRules();
    fetchRecentRuns();
  }, []);

  const fetchRules = async () => {
    try {
      const response = await fetch("/api/v1/rules/");
      const data = await response.json();
      setRules(data);
    } catch (error) {
      console.error("Failed to fetch rules:", error);
    } finally {
      setLoading(false);
    }
  };

  const fetchRecentRuns = async () => {
    try {
      const response = await fetch("/api/v1/rules/runs/recent?limit=20");
      const data = await response.json();
      setRuleRuns(data);
    } catch (error) {
      console.error("Failed to fetch rule runs:", error);
    }
  };

  const createRule = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const response = await fetch("/api/v1/rules/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });
      
      if (response.ok) {
        setShowCreateForm(false);
        setFormData({
          name: "",
          description: "",
          trigger: "post_performance",
          condition_json: { operator: "eq", field: "engagement_rate", value: 0.01 },
          action_json: { type: "clone_content_and_reschedule", params: {} },
          enabled: true,
        });
        fetchRules();
      }
    } catch (error) {
      console.error("Failed to create rule:", error);
    }
  };

  const updateRule = async (ruleId: string, updates: Partial<RuleFormData>) => {
    try {
      const response = await fetch(`/api/v1/rules/${ruleId}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updates),
      });
      
      if (response.ok) {
        fetchRules();
      }
    } catch (error) {
      console.error("Failed to update rule:", error);
    }
  };

  const deleteRule = async (ruleId: string) => {
    if (!confirm("Are you sure you want to delete this rule?")) return;
    
    try {
      const response = await fetch(`/api/v1/rules/${ruleId}`, {
        method: "DELETE",
      });
      
      if (response.ok) {
        fetchRules();
      }
    } catch (error) {
      console.error("Failed to delete rule:", error);
    }
  };

  const testRule = async () => {
    try {
      const response = await fetch("/api/v1/rules/test", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          trigger: formData.trigger,
          payload: { engagement_rate: 0.005, impressions: 1000 },
        }),
      });
      
      const result = await response.json();
      alert(`Condition met: ${result.condition_met}\nAction preview: ${JSON.stringify(result.action_preview)}`);
    } catch (error) {
      console.error("Failed to test rule:", error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "success": return "text-green-600 bg-green-100";
      case "failed": return "text-red-600 bg-red-100";
      case "running": return "text-blue-600 bg-blue-100";
      case "pending": return "text-yellow-600 bg-yellow-100";
      default: return "text-gray-600 bg-gray-100";
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Automations</h1>
          <p className="text-gray-600">Create rules to automate your marketing actions</p>
        </div>
        <button
          onClick={() => setShowCreateForm(true)}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          <Plus className="w-4 h-4 mr-2" />
          Create Rule
        </button>
      </div>

      {/* Rules List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Active Rules</h2>
        </div>
        <div className="divide-y">
          {rules.map((rule) => (
            <div key={rule.id} className="px-6 py-4 flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <h3 className="font-medium text-gray-900">{rule.name}</h3>
                  <span className={`px-2 py-1 text-xs rounded-full ${
                    rule.enabled ? "bg-green-100 text-green-800" : "bg-gray-100 text-gray-800"
                  }`}>
                    {rule.enabled ? "Enabled" : "Disabled"}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{rule.description}</p>
                <div className="flex items-center space-x-4 mt-2 text-sm text-gray-500">
                  <span>Trigger: {TRIGGER_OPTIONS.find(t => t.value === rule.trigger)?.label}</span>
                  <span>Action: {ACTION_OPTIONS.find(a => a.value === rule.action_json?.type)?.label}</span>
                </div>
              </div>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => updateRule(rule.id, { enabled: !rule.enabled })}
                  className={`p-2 rounded-lg ${
                    rule.enabled ? "text-red-600 hover:bg-red-50" : "text-green-600 hover:bg-green-50"
                  }`}
                >
                  {rule.enabled ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                <button
                  onClick={() => setEditingRule(rule)}
                  className="p-2 text-gray-600 hover:bg-gray-50 rounded-lg"
                >
                  <Settings className="w-4 h-4" />
                </button>
                <button
                  onClick={() => deleteRule(rule.id)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
          {rules.length === 0 && (
            <div className="px-6 py-8 text-center text-gray-500">
              No rules created yet. Create your first automation rule to get started.
            </div>
          )}
        </div>
      </div>

      {/* Recent Runs */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold">Recent Rule Runs</h2>
        </div>
        <div className="divide-y">
          {ruleRuns.map((run) => (
            <div key={run.id} className="px-6 py-3 flex items-center justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3">
                  <span className={`px-2 py-1 text-xs rounded-full ${getStatusColor(run.status)}`}>
                    {run.status}
                  </span>
                  <span className="text-sm text-gray-600">
                    {new Date(run.created_at).toLocaleString()}
                  </span>
                </div>
                {run.meta_json && (
                  <p className="text-sm text-gray-500 mt-1">
                    {JSON.stringify(run.meta_json)}
                  </p>
                )}
              </div>
            </div>
          ))}
          {ruleRuns.length === 0 && (
            <div className="px-6 py-8 text-center text-gray-500">
              No rule runs yet.
            </div>
          )}
        </div>
      </div>

      {/* Create Rule Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-4">Create Automation Rule</h2>
            <form onSubmit={createRule} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Rule Name
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Trigger
                </label>
                <select
                  value={formData.trigger}
                  onChange={(e) => setFormData({ ...formData, trigger: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {TRIGGER_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Condition
                </label>
                <div className="grid grid-cols-3 gap-2">
                  <select
                    value={formData.condition_json.operator}
                    onChange={(e) => setFormData({
                      ...formData,
                      condition_json: { ...formData.condition_json, operator: e.target.value }
                    })}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    {CONDITION_OPERATORS.map((op) => (
                      <option key={op.value} value={op.value}>
                        {op.label}
                      </option>
                    ))}
                  </select>
                  <input
                    type="text"
                    placeholder="Field (e.g., engagement_rate)"
                    value={formData.condition_json.field}
                    onChange={(e) => setFormData({
                      ...formData,
                      condition_json: { ...formData.condition_json, field: e.target.value }
                    })}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                  <input
                    type="text"
                    placeholder="Value"
                    value={formData.condition_json.value}
                    onChange={(e) => setFormData({
                      ...formData,
                      condition_json: { ...formData.condition_json, value: e.target.value }
                    })}
                    className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Action
                </label>
                <select
                  value={formData.action_json.type}
                  onChange={(e) => setFormData({
                    ...formData,
                    action_json: { ...formData.action_json, type: e.target.value }
                  })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {ACTION_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </div>

              <div className="flex items-center space-x-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                    className="mr-2"
                  />
                  <span className="text-sm text-gray-700">Enable rule</span>
                </label>
              </div>

              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  Cancel
                </button>
                <button
                  type="button"
                  onClick={testRule}
                  className="flex items-center px-4 py-2 text-blue-600 bg-blue-100 rounded-lg hover:bg-blue-200"
                >
                  <TestTube className="w-4 h-4 mr-2" />
                  Test Rule
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Create Rule
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
