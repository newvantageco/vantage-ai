"use client";

import { useEffect, useState } from "react";

type AIUsageStats = {
  tokens_used: number;
  tokens_limit: number;
  cost_gbp_used: number;
  cost_gbp_limit: number;
  percentage_used: number;
  is_over_limit: boolean;
};

type AIBudget = {
  daily_token_limit: number;
  daily_cost_limit_gbp: number;
  tokens_used_today: number;
  cost_gbp_today: number;
  current_date: string;
};

export default function AIUsagePage() {
  const [orgId, setOrgId] = useState("");
  const [usageStats, setUsageStats] = useState<AIUsageStats | null>(null);
  const [budget, setBudget] = useState<AIBudget | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadUsageStats = async () => {
    if (!orgId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`/api/v1/ai/usage?org_id=${orgId}`);
      if (!response.ok) {
        throw new Error(`Failed to load usage stats: ${response.statusText}`);
      }
      const data = await response.json();
      setUsageStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load usage stats");
    } finally {
      setLoading(false);
    }
  };

  const loadBudget = async () => {
    if (!orgId) return;
    
    try {
      const response = await fetch(`/api/v1/ai/budget?org_id=${orgId}`);
      if (!response.ok) {
        throw new Error(`Failed to load budget: ${response.statusText}`);
      }
      const data = await response.json();
      setBudget(data);
    } catch (err) {
      // Error handled by UI state
    }
  };

  const updateBudget = async (newBudget: Partial<AIBudget>) => {
    if (!orgId) return;
    
    try {
      const response = await fetch(`/api/v1/ai/budget`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          org_id: orgId,
          daily_token_limit: newBudget.daily_token_limit,
          daily_cost_limit_gbp: newBudget.daily_cost_limit_gbp,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to update budget: ${response.statusText}`);
      }
      
      await loadBudget();
      await loadUsageStats();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update budget");
    }
  };

  const resetDailyUsage = async () => {
    if (!orgId) return;
    
    try {
      const response = await fetch(`/api/v1/ai/reset-daily`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ org_id: orgId }),
      });
      
      if (!response.ok) {
        throw new Error(`Failed to reset daily usage: ${response.statusText}`);
      }
      
      await loadUsageStats();
      await loadBudget();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to reset daily usage");
    }
  };

  useEffect(() => {
    if (orgId) {
      loadUsageStats();
      loadBudget();
    }
  }, [orgId]);

  if (!orgId) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <h1 className="text-2xl font-semibold mb-8">AI Usage Monitor</h1>
        <div className="flex items-center gap-3">
          <label className="font-medium">Organization ID</label>
          <input
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            placeholder="Enter organization ID"
            className="px-3 py-2 border border-border rounded-md min-w-[200px] input-focus"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="flex justify-between items-center mb-8 p-5 bg-muted rounded-lg">
        <h1 className="text-2xl font-semibold">AI Usage Monitor</h1>
        <div className="flex items-center gap-3">
          <label className="font-medium">Organization ID</label>
          <input
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            className="px-3 py-2 border border-border rounded-md min-w-[200px] input-focus"
          />
        </div>
      </div>

      {error && (
        <div className="p-3 mb-5 bg-destructive/10 text-destructive border border-destructive/20 rounded-md">
          {error}
        </div>
      )}

      {loading && (
        <div className="p-5 text-center text-muted-foreground">
          Loading usage statistics...
        </div>
      )}

      {usageStats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5 mb-8">
          <div className="p-5 bg-card border border-border rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold mb-4 text-card-foreground">Token Usage</h3>
            <div className="text-2xl font-bold text-muted-foreground mb-3">
              {usageStats.tokens_used.toLocaleString()} / {usageStats.tokens_limit.toLocaleString()}
            </div>
            <div className="w-full h-2 bg-muted rounded-full overflow-hidden mb-2">
              <div 
                className="h-full bg-green-500 transition-all duration-300 ease-out" 
                style={{ width: `${Math.min(usageStats.percentage_used, 100)}%` }}
              />
            </div>
            <div className="text-sm text-muted-foreground">
              {usageStats.percentage_used.toFixed(1)}%
            </div>
          </div>

          <div className="p-5 bg-card border border-border rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold mb-4 text-card-foreground">Cost Usage</h3>
            <div className="text-2xl font-bold text-muted-foreground mb-3">
              £{usageStats.cost_gbp_used.toFixed(2)} / £{usageStats.cost_gbp_limit.toFixed(2)}
            </div>
            <div className="w-full h-2 bg-muted rounded-full overflow-hidden mb-2">
              <div 
                className="h-full bg-green-500 transition-all duration-300 ease-out" 
                style={{ width: `${Math.min((usageStats.cost_gbp_used / usageStats.cost_gbp_limit) * 100, 100)}%` }}
              />
            </div>
            <div className="text-sm text-muted-foreground">
              {((usageStats.cost_gbp_used / usageStats.cost_gbp_limit) * 100).toFixed(1)}%
            </div>
          </div>

          <div className="p-5 bg-card border border-border rounded-lg shadow-sm">
            <h3 className="text-lg font-semibold mb-4 text-card-foreground">Status</h3>
            <div className={`px-4 py-2 rounded-full font-medium text-center ${
              usageStats.is_over_limit 
                ? 'bg-destructive/10 text-destructive' 
                : 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400'
            }`}>
              {usageStats.is_over_limit ? 'Over Limit' : 'Within Limit'}
            </div>
            {usageStats.is_over_limit && (
              <div className="mt-2 text-xs text-yellow-600 dark:text-yellow-400">
                Non-critical tasks will use open models
              </div>
            )}
          </div>
        </div>
      )}

      {budget && (
        <div className="bg-card p-6 border border-border rounded-lg shadow-sm">
          <h2 className="text-xl font-semibold mb-5 text-card-foreground">Budget Settings</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-5">
            <div className="flex flex-col gap-2">
              <label className="font-medium text-card-foreground">Daily Token Limit</label>
              <input
                type="number"
                value={budget.daily_token_limit}
                onChange={(e) => setBudget({
                  ...budget,
                  daily_token_limit: parseInt(e.target.value) || 0
                })}
                className="px-3 py-2 border border-border rounded-md input-focus"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="font-medium text-card-foreground">Daily Cost Limit (GBP)</label>
              <input
                type="number"
                step="0.01"
                value={budget.daily_cost_limit_gbp}
                onChange={(e) => setBudget({
                  ...budget,
                  daily_cost_limit_gbp: parseFloat(e.target.value) || 0
                })}
                className="px-3 py-2 border border-border rounded-md input-focus"
              />
            </div>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => updateBudget(budget)}
              className="px-5 py-2 bg-primary text-primary-foreground rounded-md font-medium hover:bg-primary/90 transition-colors"
            >
              Update Budget
            </button>
            <button 
              onClick={resetDailyUsage}
              className="px-5 py-2 bg-secondary text-secondary-foreground rounded-md font-medium hover:bg-secondary/90 transition-colors"
            >
              Reset Daily Usage
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
