"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { 
  Play, 
  Pause, 
  Square, 
  RefreshCw, 
  Clock,
  CheckCircle2,
  AlertCircle,
  XCircle,
  Loader2,
  Eye,
  MoreHorizontal
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { taskQueueEngine, Task } from '@/lib/engines/task-queue-engine';

interface TaskQueueProps {
  className?: string;
  maxTasks?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function TaskQueue({ 
  className, 
  maxTasks = 20, 
  autoRefresh = true, 
  refreshInterval = 3000 
}: TaskQueueProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchTasks = async () => {
    setLoading(true);
    try {
      // Get tasks from the real-time engine
      const engineTasks = taskQueueEngine.getTasks();
      setTasks(engineTasks.slice(0, maxTasks));
    } catch (error) {
      console.error('Failed to fetch tasks:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Subscribe to real-time task updates
    const unsubscribe = taskQueueEngine.subscribe((task) => {
      setTasks(prev => {
        const updated = prev.map(t => t.id === task.id ? task : t);
        if (!prev.find(t => t.id === task.id)) {
          updated.unshift(task);
        }
        return updated.slice(0, maxTasks);
      });
    });

    // Load initial tasks
    fetchTasks();
    
    if (autoRefresh) {
      const interval = setInterval(fetchTasks, refreshInterval);
      return () => {
        clearInterval(interval);
        unsubscribe();
      };
    }

    return unsubscribe;
  }, [autoRefresh, refreshInterval, maxTasks]);

  const getTaskIcon = (status: Task['status']) => {
    switch (status) {
      case 'running':
        return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'completed':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'cancelled':
        return <XCircle className="h-4 w-4 text-gray-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-muted-foreground" />;
      default:
        return <Play className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusBadgeVariant = (status: Task['status']) => {
    switch (status) {
      case 'running':
        return 'default';
      case 'completed':
        return 'secondary';
      case 'failed':
        return 'destructive';
      case 'cancelled':
        return 'outline';
      case 'pending':
        return 'secondary';
      default:
        return 'secondary';
    }
  };

  const getPriorityColor = (priority: Task['priority']) => {
    switch (priority) {
      case 'urgent':
        return 'text-red-500';
      case 'high':
        return 'text-orange-500';
      case 'normal':
        return 'text-yellow-500';
      case 'low':
        return 'text-green-500';
      default:
        return 'text-muted-foreground';
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`;
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
  };

  const getElapsedTime = (startedAt: Date) => {
    const now = new Date();
    const diffInSeconds = Math.floor((now.getTime() - startedAt.getTime()) / 1000);
    return formatDuration(diffInSeconds);
  };

  const handleTaskAction = (taskId: string, action: 'start' | 'pause' | 'stop' | 'retry') => {
    switch (action) {
      case 'retry':
        taskQueueEngine.retryTask(taskId);
        break;
      case 'stop':
        taskQueueEngine.cancelTask(taskId);
        break;
      default:
        // Other actions would be handled by the engine
        break;
    }
  };

  const runningTasks = tasks.filter(task => task.status === 'running');
  const completedTasks = tasks.filter(task => task.status === 'completed');
  const failedTasks = tasks.filter(task => task.status === 'failed');

  return (
    <Card className={cn("h-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold">Task Queue</CardTitle>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <div className="w-2 h-2 bg-blue-500 rounded-full pulse-realtime" />
            {runningTasks.length} running
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchTasks}
            disabled={loading}
            className="h-8"
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="task-queue">
          {tasks.length === 0 ? (
            <div className="flex items-center justify-center p-8 text-muted-foreground">
              <div className="text-center">
                <Play className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">No tasks in queue</p>
              </div>
            </div>
          ) : (
            tasks.map((task) => (
              <div key={task.id} className="task-item">
                <div className="flex-shrink-0">
                  {getTaskIcon(task.status)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-foreground truncate">
                      {task.name || 'Unnamed Task'}
                    </h4>
                    <div className="flex items-center gap-2">
                      <Badge variant={getStatusBadgeVariant(task.status)} className="text-xs">
                        {task.status || 'unknown'}
                      </Badge>
                      <span className={cn("text-xs font-mono", getPriorityColor(task.priority))}>
                        {task.priority || 'normal'}
                      </span>
                    </div>
                  </div>
                  
                  {task.status === 'running' && (
                    <div className="mb-2">
                      <Progress value={task.progress || 0} className="h-2" />
                      <div className="flex justify-between text-xs text-muted-foreground mt-1">
                        <span>{task.progress || 0}% complete</span>
                        {task.startedAt && (
                          <span>Running for {getElapsedTime(task.startedAt)}</span>
                        )}
                      </div>
                    </div>
                  )}
                  
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span className="font-mono">{task.category?.replace('_', ' ') || 'Unknown'}</span>
                    <div className="flex items-center gap-2">
                      {task.status === 'running' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleTaskAction(task.id, 'pause')}
                          className="h-6 px-2"
                        >
                          <Pause className="h-3 w-3" />
                        </Button>
                      )}
                      {task.status === 'cancelled' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleTaskAction(task.id, 'start')}
                          className="h-6 px-2"
                        >
                          <Play className="h-3 w-3" />
                        </Button>
                      )}
                      {task.status === 'failed' && (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleTaskAction(task.id, 'retry')}
                          className="h-6 px-2"
                        >
                          <RefreshCw className="h-3 w-3" />
                        </Button>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        className="h-6 px-2"
                      >
                        <Eye className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
}
