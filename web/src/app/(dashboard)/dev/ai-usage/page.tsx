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
      console.error("Failed to load budget:", err);
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
      <div className="page-container">
        <h1>AI Usage Monitor</h1>
        <div className="input-group">
          <label>Organization ID</label>
          <input
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
            placeholder="Enter organization ID"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>AI Usage Monitor</h1>
        <div className="input-group">
          <label>Organization ID</label>
          <input
            value={orgId}
            onChange={(e) => setOrgId(e.target.value)}
          />
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {loading && (
        <div className="loading">
          Loading usage statistics...
        </div>
      )}

      {usageStats && (
        <div className="stats-grid">
          <div className="stat-card">
            <h3>Token Usage</h3>
            <div className="stat-value">
              {usageStats.tokens_used.toLocaleString()} / {usageStats.tokens_limit.toLocaleString()}
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${Math.min(usageStats.percentage_used, 100)}%` }}
              />
            </div>
            <div className="stat-percentage">
              {usageStats.percentage_used.toFixed(1)}%
            </div>
          </div>

          <div className="stat-card">
            <h3>Cost Usage</h3>
            <div className="stat-value">
              £{usageStats.cost_gbp_used.toFixed(2)} / £{usageStats.cost_gbp_limit.toFixed(2)}
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${Math.min((usageStats.cost_gbp_used / usageStats.cost_gbp_limit) * 100, 100)}%` }}
              />
            </div>
            <div className="stat-percentage">
              {((usageStats.cost_gbp_used / usageStats.cost_gbp_limit) * 100).toFixed(1)}%
            </div>
          </div>

          <div className="stat-card">
            <h3>Status</h3>
            <div className={`status ${usageStats.is_over_limit ? 'over-limit' : 'within-limit'}`}>
              {usageStats.is_over_limit ? 'Over Limit' : 'Within Limit'}
            </div>
            {usageStats.is_over_limit && (
              <div className="warning-text">
                Non-critical tasks will use open models
              </div>
            )}
          </div>
        </div>
      )}

      {budget && (
        <div className="budget-section">
          <h2>Budget Settings</h2>
          <div className="budget-form">
            <div className="form-group">
              <label>Daily Token Limit</label>
              <input
                type="number"
                value={budget.daily_token_limit}
                onChange={(e) => setBudget({
                  ...budget,
                  daily_token_limit: parseInt(e.target.value) || 0
                })}
              />
            </div>
            <div className="form-group">
              <label>Daily Cost Limit (GBP)</label>
              <input
                type="number"
                step="0.01"
                value={budget.daily_cost_limit_gbp}
                onChange={(e) => setBudget({
                  ...budget,
                  daily_cost_limit_gbp: parseFloat(e.target.value) || 0
                })}
              />
            </div>
            <div className="form-actions">
              <button 
                onClick={() => updateBudget(budget)}
                className="btn-primary"
              >
                Update Budget
              </button>
              <button 
                onClick={resetDailyUsage}
                className="btn-secondary"
              >
                Reset Daily Usage
              </button>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .page-container {
          padding: 24px;
          max-width: 1200px;
          margin: 0 auto;
        }
        
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 32px;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 8px;
        }
        
        .input-group {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .input-group label {
          font-weight: 500;
        }
        
        .input-group input {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
          min-width: 200px;
        }
        
        .error-message {
          padding: 12px;
          margin-bottom: 20px;
          background: #f8d7da;
          color: #721c24;
          border: 1px solid #f5c6cb;
          border-radius: 4px;
        }
        
        .loading {
          padding: 20px;
          text-align: center;
          color: #666;
        }
        
        .stats-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 20px;
          margin-bottom: 32px;
        }
        
        .stat-card {
          padding: 20px;
          background: white;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .stat-card h3 {
          margin: 0 0 16px 0;
          color: #333;
        }
        
        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #495057;
          margin-bottom: 12px;
        }
        
        .progress-bar {
          width: 100%;
          height: 8px;
          background: #e9ecef;
          border-radius: 4px;
          overflow: hidden;
          margin-bottom: 8px;
        }
        
        .progress-fill {
          height: 100%;
          background: #28a745;
          transition: width 0.3s ease;
        }
        
        .stat-percentage {
          font-size: 14px;
          color: #666;
        }
        
        .status {
          padding: 8px 16px;
          border-radius: 20px;
          font-weight: 500;
          text-align: center;
        }
        
        .status.within-limit {
          background: #d4edda;
          color: #155724;
        }
        
        .status.over-limit {
          background: #f8d7da;
          color: #721c24;
        }
        
        .warning-text {
          margin-top: 8px;
          font-size: 12px;
          color: #856404;
        }
        
        .budget-section {
          background: white;
          padding: 24px;
          border: 1px solid #e9ecef;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .budget-section h2 {
          margin: 0 0 20px 0;
          color: #333;
        }
        
        .budget-form {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 20px;
          margin-bottom: 20px;
        }
        
        .form-group {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
        
        .form-group label {
          font-weight: 500;
          color: #333;
        }
        
        .form-group input {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 4px;
        }
        
        .form-actions {
          grid-column: 1 / -1;
          display: flex;
          gap: 12px;
        }
        
        .btn-primary, .btn-secondary {
          padding: 10px 20px;
          border: none;
          border-radius: 4px;
          cursor: pointer;
          font-weight: 500;
        }
        
        .btn-primary {
          background: #007bff;
          color: white;
        }
        
        .btn-primary:hover {
          background: #0056b3;
        }
        
        .btn-secondary {
          background: #6c757d;
          color: white;
        }
        
        .btn-secondary:hover {
          background: #545b62;
        }
      `}</style>
    </div>
  );
}
