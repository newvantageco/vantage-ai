"use client";
import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar as CalendarIcon, Clock, Plus } from "lucide-react";

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

interface CalendarProps {
  orgId: string;
  schedules: Schedule[];
  contentItems: ContentItem[];
  channels: Channel[];
  onScheduleCreate: (data: { contentId: string; channelId: string; scheduledFor: string; }) => Promise<void>;
  onSuggestPosts: () => Promise<void>;
}

export function Calendar({ 
  orgId, 
  schedules, 
  contentItems, 
  channels, 
  onScheduleCreate, 
  onSuggestPosts 
}: CalendarProps) {
  const [showCreateForm, setShowCreateForm] = React.useState(false);
  const [selectedContent, setSelectedContent] = React.useState("");
  const [selectedChannel, setSelectedChannel] = React.useState("");
  const [scheduledFor, setScheduledFor] = React.useState("");

  const handleCreateSchedule = async () => {
    if (!selectedContent || !selectedChannel || !scheduledFor) return;
    
    try {
      await onScheduleCreate({
        contentId: selectedContent,
        channelId: selectedChannel,
        scheduledFor: scheduledFor,
      });
      setShowCreateForm(false);
      setSelectedContent("");
      setSelectedChannel("");
      setScheduledFor("");
    } catch (error) {
      // Error handled by UI state
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">Content Calendar</h2>
          <p className="text-muted-foreground">Schedule and manage your content</p>
        </div>
        <div className="flex gap-2">
          <Button onClick={onSuggestPosts} variant="outline">
            <Plus className="w-4 h-4 mr-2" />
            Suggest Posts
          </Button>
          <Button onClick={() => setShowCreateForm(true)}>
            <CalendarIcon className="w-4 h-4 mr-2" />
            Schedule Content
          </Button>
        </div>
      </div>

      {/* Create Schedule Form */}
      {showCreateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Schedule New Content</CardTitle>
            <CardDescription>Select content and channel to schedule</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2">Content Item</label>
              <select 
                value={selectedContent} 
                onChange={(e) => setSelectedContent(e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="">Select content...</option>
                {contentItems.map((item) => (
                  <option key={item.id} value={item.id}>
                    {item.title || `Content ${item.id.slice(0, 8)}`}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Channel</label>
              <select 
                value={selectedChannel} 
                onChange={(e) => setSelectedChannel(e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                <option value="">Select channel...</option>
                {channels.map((channel) => (
                  <option key={channel.id} value={channel.id}>
                    {channel.provider} - {channel.account_ref || channel.id}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium mb-2">Schedule For</label>
              <input
                type="datetime-local"
                value={scheduledFor}
                onChange={(e) => setScheduledFor(e.target.value)}
                className="w-full p-2 border rounded-md"
              />
            </div>
            
            <div className="flex gap-2">
              <Button onClick={handleCreateSchedule} disabled={!selectedContent || !selectedChannel || !scheduledFor}>
                Schedule
              </Button>
              <Button variant="outline" onClick={() => setShowCreateForm(false)}>
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Schedules List */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Upcoming Schedules
          </CardTitle>
          <CardDescription>
            {schedules.length} scheduled items
          </CardDescription>
        </CardHeader>
        <CardContent>
          {schedules.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <CalendarIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
              <p>No content scheduled yet</p>
              <p className="text-sm">Create your first schedule to get started</p>
            </div>
          ) : (
            <div className="space-y-3">
              {schedules.map((schedule) => {
                const contentItem = contentItems.find(item => item.id === schedule.content_item_id);
                const channel = channels.find(ch => ch.id === schedule.channel_id);
                
                return (
                  <div key={schedule.id} className="flex items-center justify-between p-3 border rounded-lg">
                    <div className="flex-1">
                      <div className="font-medium">
                        {contentItem?.title || `Content ${schedule.content_item_id.slice(0, 8)}`}
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {channel?.provider} - {channel?.account_ref || channel?.id}
                      </div>
                      {schedule.caption && (
                        <div className="text-sm text-muted-foreground/80 mt-1">
                          {schedule.caption}
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium">
                        {new Date(schedule.scheduled_at).toLocaleDateString()}
                      </div>
                      <div className="text-xs text-muted-foreground">
                        {new Date(schedule.scheduled_at).toLocaleTimeString()}
                      </div>
                      <div className={`text-xs px-2 py-1 rounded-full mt-1 ${
                        schedule.status === 'scheduled' ? 'bg-blue-100 text-blue-800' :
                        schedule.status === 'published' ? 'bg-green-100 text-green-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {schedule.status}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

export default Calendar;