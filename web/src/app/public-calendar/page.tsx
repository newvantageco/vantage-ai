"use client";
import { useEffect, useState } from "react";
import Calendar from "@/components/Calendar";
import { EmptyState } from "@/components/ui/empty-state";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Calendar as CalendarIcon, Clock } from "lucide-react";

type Schedule = {
  id: string;
  content_item_id: string;
  channel_id: string;
  scheduled_at: string;
  status: string;
  caption?: string;
  channel_name?: string;
};

type ContentItem = {
  id: string;
  title?: string;
  caption?: string;
  status: string;
};

type Channel = {
  id: string;
  provider: string;
  account_ref?: string;
};

type Suggestion = {
  topic: string;
  caption: string;
  hashtags: string[];
};

export default function CalendarDashboardPage() {
  const [orgId, setOrgId] = useState("");
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [contentItems, setContentItems] = useState<ContentItem[]>([]);
  const [channels, setChannels] = useState<Channel[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function loadData() {
    if (!orgId) return;
    
    // Load schedules
    const schedulesResp = await fetch("/api/schedule/due");
    const schedulesData = await schedulesResp.json();
    setSchedules(schedulesData);

    // Load content items (mock for now - would need actual endpoint)
    setContentItems([
      { id: "content1", title: "Product Launch", caption: "Exciting new product coming soon!", status: "draft" },
      { id: "content2", title: "Behind the Scenes", caption: "Take a look at our process", status: "approved" },
    ]);

    // Load channels (mock for now - would need actual endpoint)
    setChannels([
      { id: "channel1", provider: "linkedin", account_ref: "company-page" },
      { id: "channel2", provider: "meta", account_ref: "facebook-page" },
    ]);
  }

  async function handleScheduleCreate(data: {
    contentId: string;
    channelId: string;
    scheduledFor: string;
  }) {
    setMsg(null);
    const payload = [{
      content_id: data.contentId,
      channel_id: data.channelId,
      scheduled_for: data.scheduledFor,
    }];
    const resp = await fetch("/api/schedule/bulk", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await resp.json();
    if (!resp.ok) {
      setMsg(`Error: ${result.detail || "Failed to create schedule"}`);
      return;
    }
    setMsg("Schedule created successfully!");
    await loadData();
  }

  async function handleSuggestPosts() {
    if (!orgId) return;
    
    const fromDate = new Date().toISOString().split('T')[0];
    const toDate = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    
    const resp = await fetch(
      `/api/content/plan/suggestions?from=${fromDate}&to=${toDate}&brand_guide_id=${orgId}`
    );
    const data = await resp.json();
    setSuggestions(data);
    setShowSuggestions(true);
  }

  async function runScheduler() {
    const resp = await fetch("/api/schedule/run", { method: "POST" });
    const data = await resp.json();
    setMsg(`Scheduler processed: ${data.processed} items`);
    await loadData();
  }

  useEffect(() => {
    loadData();
  }, [orgId]);

  if (!orgId) {
    return (
      <div>
        <h1>Calendar</h1>
        <div>
          <label>Org ID</label>
          <input value={orgId} onChange={(e) => setOrgId(e.target.value)} placeholder="Enter organization ID" />
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <div>
          <label>Org ID</label>
          <input value={orgId} onChange={(e) => setOrgId(e.target.value)} />
        </div>
        <button onClick={runScheduler}>Run Scheduler</button>
      </div>
      
      {msg && <div className="message">{msg}</div>}
      
      <Calendar
        orgId={orgId}
        schedules={schedules}
        contentItems={contentItems}
        channels={channels}
        onScheduleCreate={handleScheduleCreate}
        onSuggestPosts={handleSuggestPosts}
      />

      {/* Suggestions Sidebar */}
      {showSuggestions && (
        <div className="suggestions-sidebar">
          <div className="suggestions-header">
            <h3>Suggested Posts</h3>
            <button onClick={() => setShowSuggestions(false)}>×</button>
          </div>
          <div className="suggestions-list">
            {suggestions.map((suggestion, index) => (
              <div key={index} className="suggestion-item">
                <h4>{suggestion.topic}</h4>
                <p>{suggestion.caption}</p>
                <div className="hashtags">
                  {suggestion.hashtags.map((tag, i) => (
                    <span key={i} className="hashtag">#{tag}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <style jsx>{`
        .page-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          padding: 16px;
          background: #f5f5f5;
          border-radius: 8px;
        }
        .page-header label {
          margin-right: 8px;
        }
        .page-header input {
          padding: 8px;
          border: 1px solid #ddd;
          border-radius: 4px;
          margin-right: 16px;
        }
        .page-header button {
          background: #28a745;
          color: white;
          border: none;
          padding: 8px 16px;
          border-radius: 4px;
          cursor: pointer;
        }
        .message {
          padding: 12px;
          margin-bottom: 16px;
          border-radius: 4px;
          background: #d4edda;
          border: 1px solid #c3e6cb;
          color: #155724;
        }
        .suggestions-sidebar {
          position: fixed;
          top: 0;
          right: 0;
          bottom: 0;
          width: 400px;
          background: white;
          box-shadow: -2px 0 8px rgba(0, 0, 0, 0.1);
          z-index: 1000;
          overflow-y: auto;
        }
        .suggestions-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px;
          border-bottom: 1px solid #eee;
        }
        .suggestions-header button {
          background: none;
          border: none;
          font-size: 24px;
          cursor: pointer;
        }
        .suggestions-list {
          padding: 20px;
        }
        .suggestion-item {
          margin-bottom: 20px;
          padding: 16px;
          border: 1px solid #eee;
          border-radius: 8px;
        }
        .suggestion-item h4 {
          margin: 0 0 8px 0;
          color: #333;
        }
        .suggestion-item p {
          margin: 0 0 12px 0;
          color: #666;
          line-height: 1.4;
        }
        .hashtags {
          display: flex;
          flex-wrap: wrap;
          gap: 4px;
        }
        .hashtag {
          background: #e3f2fd;
          color: #1976d2;
          padding: 2px 6px;
          border-radius: 12px;
          font-size: 12px;
        }
      `}</style>
    </div>
  );
}


