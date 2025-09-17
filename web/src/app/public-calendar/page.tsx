"use client";
import React, { useEffect, useState } from "react";
import { ModernCalendar } from "@/components/ModernCalendar";
import { ModernSidebar } from "@/components/ModernSidebar";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Plus, Calendar as CalendarIcon, Clock, Zap } from "lucide-react";

type Schedule = {
  id: string;
  content_item_id: string;
  channel_id: string;
  scheduled_at: string;
  status: string;
  caption?: string;
  channel_name?: string;
  title?: string;
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
    
    try {
      // Load schedules
      const schedulesResp = await fetch("/api/schedule/due");
      if (!schedulesResp.ok) {
        throw new Error(`Failed to load schedules: ${schedulesResp.status}`);
      }
      const schedulesData = await schedulesResp.json();
      setSchedules(schedulesData);
    } catch (error) {
      console.error("Error loading data:", error);
      setMsg(`Error loading data: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }

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
    
    // Validate input data
    if (!data.contentId || !data.channelId || !data.scheduledFor) {
      setMsg("Error: All fields are required");
      return;
    }
    
    // Validate date format
    const scheduledDate = new Date(data.scheduledFor);
    if (isNaN(scheduledDate.getTime())) {
      setMsg("Error: Invalid date format");
      return;
    }
    
    // Check if date is in the future
    if (scheduledDate <= new Date()) {
      setMsg("Error: Scheduled date must be in the future");
      return;
    }
    
    try {
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
    } catch (error) {
      console.error("Error creating schedule:", error);
      setMsg(`Error: ${error instanceof Error ? error.message : 'Failed to create schedule'}`);
    }
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
      <div className="p-6">
        <h1 className="text-2xl font-semibold mb-4">Calendar</h1>
        <div className="flex items-center gap-3">
          <label className="font-medium">Org ID</label>
          <input 
            value={orgId} 
            onChange={(e: React.ChangeEvent<HTMLInputElement>) => setOrgId(e.target.value)} 
            placeholder="Enter organization ID"
            className="px-3 py-2 border border-border rounded-md input-focus"
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex">
        <ModernSidebar />
        <main className="flex-1 p-6">
          <div className="max-w-7xl mx-auto">
            {/* Header */}
            <div className="mb-8">
              <div className="flex items-center justify-between">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Content Calendar</h1>
                  <p className="text-gray-600 mt-2">
                    Schedule and manage your content across all channels
                  </p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <label className="text-sm font-medium text-gray-700">Org ID:</label>
                    <input 
                      value={orgId} 
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => setOrgId(e.target.value)} 
                      className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
                      placeholder="Enter organization ID"
                    />
                  </div>
                  <Button 
                    onClick={runScheduler}
                    className="bg-green-600 hover:bg-green-700 text-white"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Run Scheduler
                  </Button>
                </div>
              </div>
            </div>

            {/* Status Message */}
            {msg && (
              <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <svg className="h-5 w-5 text-green-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm font-medium text-green-800">{msg}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Modern Calendar Component */}
            <ModernCalendar
              schedules={schedules}
              onDateSelect={(date) => console.log('Date selected:', date)}
              onScheduleCreate={handleScheduleCreate}
              onScheduleEdit={(schedule) => console.log('Edit schedule:', schedule)}
              onScheduleDelete={(scheduleId) => console.log('Delete schedule:', scheduleId)}
            />

            {/* AI Suggestions */}
            <div className="mt-8">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Zap className="h-5 w-5 text-blue-600" />
                    AI Content Suggestions
                  </CardTitle>
                  <CardDescription>
                    Get AI-powered content ideas for your upcoming posts
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <Button 
                    onClick={handleSuggestPosts}
                    variant="outline"
                    className="w-full"
                  >
                    <Zap className="h-4 w-4 mr-2" />
                    Generate Content Ideas
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Suggestions Sidebar */}
            {showSuggestions && (
              <div className="fixed top-0 right-0 bottom-0 w-96 bg-white border-l border-gray-200 shadow-xl z-50 overflow-y-auto">
                <div className="flex justify-between items-center p-6 border-b border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900">AI Content Suggestions</h3>
                  <button 
                    onClick={() => setShowSuggestions(false)}
                    className="text-gray-400 hover:text-gray-600 text-2xl"
                  >
                    ×
                  </button>
                </div>
                <div className="p-6">
                  {suggestions.map((suggestion: Suggestion, index: number) => (
                    <div key={index} className="mb-6 p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                      <h4 className="font-semibold text-gray-900 mb-2">{suggestion.topic}</h4>
                      <p className="text-sm text-gray-600 mb-3 leading-relaxed">
                        {suggestion.caption}
                      </p>
                      <div className="flex flex-wrap gap-2">
                        {suggestion.hashtags.map((tag: string, i: number) => (
                          <span key={i} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                            #{tag}
                          </span>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
}


