"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Activity, 
  CheckCircle2, 
  AlertCircle, 
  XCircle, 
  Clock,
  RefreshCw,
  Filter
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { eventEngine, SystemEvent } from '@/lib/engines/event-engine';
import { useRelativeTime } from '@/lib/time-utils';

// Component for rendering relative time that prevents hydration issues
function RelativeTime({ timestamp }: { timestamp: Date }) {
  const relativeTime = useRelativeTime(timestamp, 30000); // Update every 30 seconds
  return <span className="text-xs text-muted-foreground">{relativeTime}</span>;
}

interface EventFeedProps {
  className?: string;
  maxEvents?: number;
  autoRefresh?: boolean;
  refreshInterval?: number;
}

export function EventFeed({ 
  className, 
  maxEvents = 50, 
  autoRefresh = true, 
  refreshInterval = 5000 
}: EventFeedProps) {
  const [events, setEvents] = useState<SystemEvent[]>([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState<'all' | 'success' | 'warning' | 'error' | 'info'>('all');

  const fetchEvents = async () => {
    setLoading(true);
    try {
      // Get events from the real-time engine
      const engineEvents = eventEngine.getEvents(maxEvents);
      setEvents(engineEvents);
    } catch (error) {
      console.error('Failed to fetch events:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Subscribe to real-time events
    const unsubscribe = eventEngine.subscribe((event) => {
      setEvents(prev => [event, ...prev].slice(0, maxEvents));
    });

    // Load initial events
    fetchEvents();
    
    if (autoRefresh) {
      const interval = setInterval(fetchEvents, refreshInterval);
      return () => {
        clearInterval(interval);
        unsubscribe();
      };
    }

    return unsubscribe;
  }, [autoRefresh, refreshInterval, maxEvents]);

  const getEventIcon = (type: SystemEvent['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle2 className="h-4 w-4 text-green-500" />;
      case 'warning':
        return <AlertCircle className="h-4 w-4 text-yellow-500" />;
      case 'error':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'info':
        return <Activity className="h-4 w-4 text-blue-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getEventBadgeVariant = (type: SystemEvent['type']) => {
    switch (type) {
      case 'success':
        return 'default';
      case 'warning':
        return 'secondary';
      case 'error':
        return 'destructive';
      case 'info':
        return 'outline';
      default:
        return 'default';
    }
  };

  // Removed formatTimestamp function - now using formatRelativeTime from time-utils

  const filteredEvents = filter === 'all' 
    ? events 
    : events.filter(event => event.type === filter);

  return (
    <Card className={cn("h-full", className)}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-4">
        <CardTitle className="text-lg font-semibold">Event Feed</CardTitle>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setFilter(filter === 'all' ? 'success' : 'all')}
            className="h-8"
          >
            <Filter className="h-4 w-4 mr-1" />
            {filter === 'all' ? 'All' : 'Filter'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchEvents}
            disabled={loading}
            className="h-8"
          >
            <RefreshCw className={cn("h-4 w-4", loading && "animate-spin")} />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="p-0">
        <div className="event-feed">
          {filteredEvents.length === 0 ? (
            <div className="flex items-center justify-center p-8 text-muted-foreground">
              <div className="text-center">
                <Activity className="h-8 w-8 mx-auto mb-2" />
                <p className="text-sm">No events to display</p>
              </div>
            </div>
          ) : (
            filteredEvents.map((event) => (
              <div key={event.id} className="event-item">
                <div className="flex-shrink-0">
                  {getEventIcon(event.type)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <h4 className="font-medium text-foreground truncate">
                      {event.title || 'Untitled Event'}
                    </h4>
                    <Badge variant={getEventBadgeVariant(event.type)} className="text-xs">
                      {event.type || 'unknown'}
                    </Badge>
                  </div>
                  <p className="text-muted-foreground text-sm mb-2">
                    {event.description || 'No description available'}
                  </p>
                  <div className="flex items-center justify-between">
                    <span className="text-xs text-muted-foreground font-mono">
                      {event.source || 'Unknown'}
                    </span>
                    {event.timestamp ? (
                      <RelativeTime timestamp={event.timestamp} />
                    ) : (
                      <span className="text-xs text-muted-foreground">Unknown time</span>
                    )}
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
