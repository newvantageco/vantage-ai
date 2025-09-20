"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Calendar, 
  Plus, 
  Filter, 
  ChevronLeft, 
  ChevronRight,
  Clock,
  Users,
  Zap,
  CheckCircle2,
  AlertCircle,
  XCircle
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Mock calendar data
const calendarEvents = [
  {
    id: '1',
    title: 'Q4 Campaign Launch',
    date: '2024-01-15',
    time: '10:00 AM',
    duration: '2h',
    type: 'campaign',
    status: 'upcoming',
    attendees: ['John Doe', 'Jane Smith'],
    description: 'Launch of Q4 marketing campaign across all platforms'
  },
  {
    id: '2',
    title: 'Content Review Meeting',
    date: '2024-01-15',
    time: '2:00 PM',
    duration: '1h',
    type: 'meeting',
    status: 'upcoming',
    attendees: ['Mike Johnson', 'Sarah Wilson'],
    description: 'Review and approve content for next week'
  },
  {
    id: '3',
    title: 'Analytics Report Due',
    date: '2024-01-15',
    time: '5:00 PM',
    duration: '30m',
    type: 'deadline',
    status: 'urgent',
    attendees: ['Alex Brown'],
    description: 'Submit monthly analytics report to stakeholders'
  },
  {
    id: '4',
    title: 'AI Model Training',
    date: '2024-01-16',
    time: '8:00 PM',
    duration: '4h',
    type: 'automation',
    status: 'running',
    attendees: [],
    description: 'Automated AI model training process'
  },
  {
    id: '5',
    title: 'Team Standup',
    date: '2024-01-16',
    time: '9:00 AM',
    duration: '30m',
    type: 'meeting',
    status: 'upcoming',
    attendees: ['All Team Members'],
    description: 'Daily team standup meeting'
  },
  {
    id: '6',
    title: 'Client Presentation',
    date: '2024-01-17',
    time: '3:00 PM',
    duration: '1h 30m',
    type: 'presentation',
    status: 'upcoming',
    attendees: ['John Doe', 'Jane Smith', 'Client Team'],
    description: 'Present Q4 results and Q1 strategy to client'
  }
];

const currentDate = new Date();
const currentMonth = currentDate.getMonth();
const currentYear = currentDate.getFullYear();

const monthNames = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];

const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

export default function CalendarPage() {
  const [selectedDate, setSelectedDate] = useState(currentDate);
  const [viewMode, setViewMode] = useState<'month' | 'week' | 'day'>('month');
  const [filterType, setFilterType] = useState<'all' | 'campaign' | 'meeting' | 'deadline' | 'automation' | 'presentation'>('all');

  const getDaysInMonth = (date: Date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return days;
  };

  const getEventsForDate = (date: Date) => {
    const dateStr = date.toISOString().split('T')[0];
    return calendarEvents.filter(event => event.date === dateStr);
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'running':
        return <div className="w-2 h-2 bg-green-500 rounded-full pulse-realtime" />;
      case 'urgent':
        return <div className="w-2 h-2 bg-red-500 rounded-full" />;
      case 'upcoming':
        return <div className="w-2 h-2 bg-blue-500 rounded-full" />;
      default:
        return <div className="w-2 h-2 bg-gray-500 rounded-full" />;
    }
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'campaign':
        return 'bg-blue-500/20 text-blue-400 border-blue-500/30';
      case 'meeting':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'deadline':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'automation':
        return 'bg-purple-500/20 text-purple-400 border-purple-500/30';
      case 'presentation':
        return 'bg-orange-500/20 text-orange-400 border-orange-500/30';
      default:
        return 'bg-gray-500/20 text-gray-400 border-gray-500/30';
    }
  };

  const filteredEvents = filterType === 'all' 
    ? calendarEvents 
    : calendarEvents.filter(event => event.type === filterType);

  const days = getDaysInMonth(selectedDate);

  return (
    <div className="h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Calendar</h1>
          <p className="text-muted-foreground">Schedule and manage your events</p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button size="sm">
            <Plus className="h-4 w-4 mr-2" />
            New Event
          </Button>
        </div>
      </div>

      {/* View Controls */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-semibold text-foreground">
            {monthNames[selectedDate.getMonth()]} {selectedDate.getFullYear()}
          </h2>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" onClick={() => setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() - 1, 1))}>
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={() => setSelectedDate(new Date(selectedDate.getFullYear(), selectedDate.getMonth() + 1, 1))}>
              <ChevronRight className="h-4 w-4" />
            </Button>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value as any)}
            className="bg-background border border-border rounded-md px-3 py-2 text-sm"
          >
            <option value="all">All Types</option>
            <option value="campaign">Campaigns</option>
            <option value="meeting">Meetings</option>
            <option value="deadline">Deadlines</option>
            <option value="automation">Automation</option>
            <option value="presentation">Presentations</option>
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar Grid */}
        <div className="lg:col-span-2">
          <Card className="card-lattice">
            <CardContent className="p-6">
              {/* Day Headers */}
              <div className="grid grid-cols-7 gap-1 mb-4">
                {dayNames.map((day) => (
                  <div key={day} className="text-center text-sm font-medium text-muted-foreground py-2">
                    {day}
                  </div>
                ))}
              </div>
              
              {/* Calendar Days */}
              <div className="grid grid-cols-7 gap-1">
                {days.map((day, index) => {
                  const isCurrentMonth = day !== null;
                  const isToday = day && day.toDateString() === new Date().toDateString();
                  const dayEvents = day ? getEventsForDate(day) : [];
                  
                  return (
                    <div
                      key={index}
                      className={cn(
                        "min-h-[100px] p-2 border border-border rounded-lg",
                        isCurrentMonth ? "bg-card" : "bg-muted/50",
                        isToday && "ring-2 ring-primary"
                      )}
                    >
                      {day && (
                        <>
                          <div className="flex items-center justify-between mb-2">
                            <span className={cn(
                              "text-sm font-medium",
                              isToday ? "text-primary" : "text-foreground"
                            )}>
                              {day.getDate()}
                            </span>
                            {dayEvents.length > 0 && (
                              <Badge variant="secondary" className="text-xs">
                                {dayEvents.length}
                              </Badge>
                            )}
                          </div>
                          
                          <div className="space-y-1">
                            {dayEvents.slice(0, 2).map((event) => (
                              <div
                                key={event.id}
                                className={cn(
                                  "text-xs p-1 rounded border",
                                  getTypeColor(event.type)
                                )}
                              >
                                <div className="flex items-center gap-1">
                                  {getStatusIcon(event.status)}
                                  <span className="truncate">{event.title}</span>
                                </div>
                                <div className="text-xs opacity-75">{event.time}</div>
                              </div>
                            ))}
                            {dayEvents.length > 2 && (
                              <div className="text-xs text-muted-foreground">
                                +{dayEvents.length - 2} more
                              </div>
                            )}
                          </div>
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Upcoming Events */}
        <div className="space-y-4">
          <Card className="card-lattice">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Upcoming Events
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {filteredEvents.slice(0, 5).map((event) => (
                <div key={event.id} className="flex items-start gap-3 p-3 rounded-lg bg-muted/50">
                  <div className="flex-shrink-0 mt-1">
                    {getStatusIcon(event.status)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-foreground text-sm truncate">
                      {event.title}
                    </h4>
                    <p className="text-xs text-muted-foreground">
                      {event.date} • {event.time}
                    </p>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="outline" className={cn("text-xs", getTypeColor(event.type))}>
                        {event.type}
                      </Badge>
                      {event.attendees.length > 0 && (
                        <div className="flex items-center gap-1 text-xs text-muted-foreground">
                          <Users className="h-3 w-3" />
                          <span>{event.attendees.length}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>

          {/* Quick Stats */}
          <Card className="card-lattice">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                This Week
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Total Events</span>
                <span className="font-mono text-foreground">{filteredEvents.length}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Meetings</span>
                <span className="font-mono text-foreground">
                  {filteredEvents.filter(e => e.type === 'meeting').length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Deadlines</span>
                <span className="font-mono text-foreground">
                  {filteredEvents.filter(e => e.type === 'deadline').length}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Automation</span>
                <span className="font-mono text-foreground">
                  {filteredEvents.filter(e => e.type === 'automation').length}
                </span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
