"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerDescription } from '@/components/ui/drawer';
import { 
  Zap, 
  Activity, 
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Play,
  Pause,
  Square,
  RefreshCw,
  Eye,
  Settings,
  Database,
  Cloud,
  Cpu,
  HardDrive
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRelativeTimeMinutes } from '@/lib/time-utils';

// Component for rendering relative time that prevents hydration issues
function RelativeTime({ timestamp }: { timestamp: string }) {
  const relativeTime = useRelativeTimeMinutes(timestamp, 30000); // Update every 30 seconds
  return <span className="text-xs text-muted-foreground">{relativeTime}</span>;
}

// Mock data for connectors
const connectors = [
  {
    id: '1',
    name: 'Twitter API',
    status: 'connected',
    type: 'social_media',
    lastSync: '2 minutes ago',
    health: 98,
    icon: Database
  },
  {
    id: '2',
    name: 'LinkedIn API',
    status: 'connected',
    type: 'social_media',
    lastSync: '5 minutes ago',
    health: 95,
    icon: Database
  },
  {
    id: '3',
    name: 'Analytics Service',
    status: 'warning',
    type: 'analytics',
    lastSync: '15 minutes ago',
    health: 78,
    icon: Activity
  },
  {
    id: '4',
    name: 'AI Processing',
    status: 'connected',
    type: 'ai',
    lastSync: '1 minute ago',
    health: 92,
    icon: Cpu
  },
  {
    id: '5',
    name: 'Content Storage',
    status: 'error',
    type: 'storage',
    lastSync: '1 hour ago',
    health: 45,
    icon: HardDrive
  }
];

// Mock data for tasks
const tasks = [
  {
    id: '1',
    name: 'Content Generation Pipeline',
    status: 'running',
    progress: 75,
    priority: 'high',
    duration: '2h 15m',
    type: 'ai_processing'
  },
  {
    id: '2',
    name: 'Analytics Data Sync',
    status: 'pending',
    progress: 0,
    priority: 'medium',
    duration: '0m',
    type: 'data_sync'
  },
  {
    id: '3',
    name: 'Social Media Posting',
    status: 'completed',
    progress: 100,
    priority: 'low',
    duration: '45m',
    type: 'automation'
  },
  {
    id: '4',
    name: 'Model Training',
    status: 'failed',
    progress: 30,
    priority: 'urgent',
    duration: '1h 30m',
    type: 'ai_training'
  }
];

// Mock data for event timeline
const events = [
  {
    id: '1',
    timestamp: new Date().toISOString(),
    type: 'success',
    title: 'Content Published',
    description: 'Q4 campaign post published to Twitter',
    source: 'Twitter API'
  },
  {
    id: '2',
    timestamp: new Date(Date.now() - 300000).toISOString(),
    type: 'warning',
    title: 'High Memory Usage',
    description: 'AI processing service using 85% memory',
    source: 'System Monitor'
  },
  {
    id: '3',
    timestamp: new Date(Date.now() - 600000).toISOString(),
    type: 'error',
    title: 'API Rate Limit',
    description: 'LinkedIn API rate limit exceeded',
    source: 'LinkedIn API'
  },
  {
    id: '4',
    timestamp: new Date(Date.now() - 900000).toISOString(),
    type: 'info',
    title: 'Backup Completed',
    description: 'Daily backup completed successfully',
    source: 'Backup Service'
  }
];

interface EntityDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  entity: any;
}

function EntityDrawer({ isOpen, onClose, entity }: EntityDrawerProps) {
  if (!entity) return null;

  return (
    <Drawer open={isOpen} onOpenChange={onClose}>
      <DrawerContent className="h-[80vh]">
        <DrawerHeader>
          <DrawerTitle className="flex items-center gap-2">
            <entity.icon className="h-5 w-5" />
            {entity.name}
          </DrawerTitle>
          <DrawerDescription>
            {entity.type} • {entity.status}
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 pb-4 space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-sm text-muted-foreground mb-2">Status</h4>
              <Badge variant={entity.status === 'connected' ? 'default' : 'destructive'}>
                {entity.status}
              </Badge>
            </div>
            <div>
              <h4 className="font-medium text-sm text-muted-foreground mb-2">Health</h4>
              <p className="text-sm font-mono">{entity.health}%</p>
            </div>
          </div>
          
          <div>
            <h4 className="font-medium text-sm text-muted-foreground mb-2">Last Sync</h4>
            <p className="text-sm font-mono">{entity.lastSync}</p>
          </div>
          
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full">
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh Connection
            </Button>
            <Button variant="outline" size="sm" className="w-full">
              <Settings className="h-4 w-4 mr-2" />
              Configure
            </Button>
            <Button variant="outline" size="sm" className="w-full">
              <Eye className="h-4 w-4 mr-2" />
              View Logs
            </Button>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}

export default function OpsBoardPage() {
  const [selectedEntity, setSelectedEntity] = useState<any>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);

  const handleEntityClick = (entity: any) => {
    setSelectedEntity(entity);
    setDrawerOpen(true);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'connected':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'connected':
        return 'text-green-500';
      case 'warning':
        return 'text-yellow-500';
      case 'error':
        return 'text-red-500';
      default:
        return 'text-muted-foreground';
    }
  };

  const getTaskStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <Play className="h-4 w-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-muted-foreground" />;
      default:
        return <Pause className="h-4 w-4 text-yellow-500" />;
    }
  };

  // Removed formatTimestamp function - now using formatRelativeTimeMinutes from time-utils

  return (
    <div className="h-full p-6">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-foreground">Ops Board</h1>
        <p className="text-muted-foreground">Monitor system health, tasks, and events</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-12rem)]">
        {/* Connectors Column */}
        <Card className="card-lattice">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Connectors
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {connectors.map((connector) => (
              <div
                key={connector.id}
                className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted/80 cursor-pointer transition-colors"
                onClick={() => handleEntityClick(connector)}
              >
                <div className="flex-shrink-0">
                  {getStatusIcon(connector.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground truncate">
                      {connector.name}
                    </h4>
                    <Badge variant={connector.status === 'connected' ? 'default' : 'destructive'}>
                      {connector.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {connector.type} • {connector.lastSync}
                  </p>
                  <div className="flex items-center gap-2 mt-1">
                    <div className="flex-1 bg-muted rounded-full h-1">
                      <div 
                        className={cn(
                          "h-1 rounded-full",
                          connector.health > 80 ? "bg-green-500" : 
                          connector.health > 60 ? "bg-yellow-500" : "bg-red-500"
                        )}
                        style={{ width: `${connector.health}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-muted-foreground">
                      {connector.health}%
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Tasks Column */}
        <Card className="card-lattice">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="h-5 w-5" />
              Tasks
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {tasks.map((task) => (
              <div key={task.id} className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <div className="flex-shrink-0">
                  {getTaskStatusIcon(task.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <h4 className="font-medium text-foreground truncate">
                      {task.name}
                    </h4>
                    <Badge variant={task.priority === 'urgent' ? 'destructive' : 'secondary'}>
                      {task.priority}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    {task.type} • {task.duration}
                  </p>
                  {task.status === 'running' && (
                    <div className="mt-2">
                      <div className="flex justify-between text-xs text-muted-foreground mb-1">
                        <span>Progress</span>
                        <span>{task.progress}%</span>
                      </div>
                      <div className="w-full bg-muted rounded-full h-1">
                        <div 
                          className="bg-blue-500 h-1 rounded-full transition-all duration-300"
                          style={{ width: `${task.progress}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </CardContent>
        </Card>

        {/* Event Timeline Column */}
        <Card className="card-lattice">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Event Timeline
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3 max-h-96 overflow-y-auto">
            {events.map((event) => (
              <div key={event.id} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                <div className="flex-shrink-0 mt-1">
                  {getStatusIcon(event.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-foreground text-sm">
                    {event.title}
                  </h4>
                  <p className="text-sm text-muted-foreground mt-1">
                    {event.description}
                  </p>
                  <div className="flex items-center justify-between mt-2">
                    <span className="text-xs font-mono text-muted-foreground">
                      {event.source}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      <RelativeTime timestamp={event.timestamp} />
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      {/* Entity Drawer */}
      <EntityDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        entity={selectedEntity}
      />
    </div>
  );
}
