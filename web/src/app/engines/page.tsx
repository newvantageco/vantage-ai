"use client";

import React from 'react';
import { SystemInitializer } from '@/components/SystemInitializer';
import { EventFeed } from '@/components/EventFeed';
import { TaskQueue } from '@/components/TaskQueue';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  Activity, 
  Database, 
  Brain, 
  BarChart3, 
  FileText,
  Zap,
  Code,
  Server,
  Cpu
} from 'lucide-react';

export default function EnginesPage() {
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Engine Control Center</h1>
          <p className="text-muted-foreground mt-2">
            Real-time monitoring and control of all VANTAGE AI engines and services
          </p>
        </div>
        <Badge className="status-success text-sm px-3 py-1">
          <Zap className="h-3 w-3 mr-1" />
          Live System
        </Badge>
      </div>

      {/* System Status */}
      <SystemInitializer />

      {/* Live Engines Display */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Event Feed - Real-time */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-500" />
              Live Event Feed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <EventFeed maxEvents={8} />
          </CardContent>
        </Card>

        {/* Task Queue - Real-time */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-blue-500" />
              Live Task Queue
            </CardTitle>
          </CardHeader>
          <CardContent>
            <TaskQueue maxTasks={8} />
          </CardContent>
        </Card>
      </div>

      {/* Engine Details */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5 text-green-500" />
              Event Engine
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium">Real-time Features:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• WebSocket event streaming</li>
                <li>• Event categorization & filtering</li>
                <li>• Automatic cleanup & retention</li>
                <li>• Event statistics & analytics</li>
              </ul>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span>Status:</span>
                <Badge className="status-success">Active</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5 text-blue-500" />
              Task Queue Engine
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium">Background Processing:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Priority-based scheduling</li>
                <li>• Retry logic with backoff</li>
                <li>• Task dependencies & chaining</li>
                <li>• Real-time progress tracking</li>
              </ul>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span>Status:</span>
                <Badge className="status-success">Active</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5 text-purple-500" />
              Analytics Engine
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium">Live Metrics:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Real-time metric collection</li>
                <li>• Chart data management</li>
                <li>• Trend analysis & detection</li>
                <li>• Performance monitoring</li>
              </ul>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span>Status:</span>
                <Badge className="status-success">Active</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-orange-500" />
              Content Engine
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium">Content Management:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• CRUD operations</li>
                <li>• Template-based generation</li>
                <li>• Multi-platform publishing</li>
                <li>• Content scheduling</li>
              </ul>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span>Status:</span>
                <Badge className="status-success">Active</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="h-5 w-5 text-cyan-500" />
              AI Engine
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium">AI Integration:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• Multi-provider support</li>
                <li>• Content generation & analysis</li>
                <li>• Sentiment analysis</li>
                <li>• Platform optimization</li>
              </ul>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span>Status:</span>
                <Badge className="status-warning">Demo Mode</Badge>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Server className="h-5 w-5 text-red-500" />
              Backend Integration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <h4 className="font-medium">API Services:</h4>
              <ul className="text-sm text-muted-foreground space-y-1">
                <li>• REST API client</li>
                <li>• WebSocket manager</li>
                <li>• Data synchronization</li>
                <li>• Error handling & retries</li>
              </ul>
            </div>
            <div className="pt-2 border-t">
              <div className="flex justify-between text-sm">
                <span>Status:</span>
                <Badge className="status-info">Ready</Badge>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Code Examples */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Code className="h-5 w-5" />
            How to Use the Real Engines
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium mb-2">1. Event Engine Usage:</h4>
              <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`import { eventEngine } from '@/lib/engines/event-engine';

// Subscribe to real-time events
const unsubscribe = eventEngine.subscribe((event) => {
  console.log('New event:', event);
});

// Add custom event
eventEngine.addEvent({
  type: 'success',
  category: 'content',
  title: 'Content Published',
  description: 'New blog post published',
  source: 'Publisher',
  severity: 'low'
});`}
              </pre>
            </div>

            <div>
              <h4 className="font-medium mb-2">2. Task Queue Engine Usage:</h4>
              <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`import { taskQueueEngine } from '@/lib/engines/task-queue-engine';

// Create a real task
const taskId = taskQueueEngine.createTask({
  name: 'Generate AI Content',
  category: 'ai',
  priority: 'high',
  maxRetries: 3
});

// Subscribe to task updates
taskQueueEngine.subscribe((task) => {
  console.log('Task updated:', task);
});`}
              </pre>
            </div>

            <div>
              <h4 className="font-medium mb-2">3. Backend Integration Usage:</h4>
              <pre className="bg-muted p-3 rounded text-sm overflow-x-auto">
{`import { backendIntegration } from '@/lib/api/backend-integration';

// Create content via API
const content = await backendIntegration.createContent({
  title: 'My Post',
  content: 'Content here...'
});

// Publish to platforms
await backendIntegration.publishContent(
  content.id, 
  ['twitter', 'linkedin']
);`}
              </pre>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
