"use client";

import { useState, useCallback, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Calendar as CalendarIcon,
  Clock,
  Globe,
  Edit,
  Trash2,
  Copy,
  MoreHorizontal,
  Filter,
  Search,
  Grid3X3,
  List,
  Eye,
  EyeOff
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { toast } from "react-hot-toast";

interface CalendarEvent {
  id: string;
  title: string;
  content: string;
  platforms: string[];
  scheduledDate: Date;
  status: "draft" | "scheduled" | "published" | "failed";
  color: string;
  allDay?: boolean;
  recurring?: boolean;
  createdAt: Date;
  updatedAt: Date;
}

interface CalendarBoardProps {
  events?: CalendarEvent[];
  loading?: boolean;
  error?: boolean;
  onEventClick?: (event: CalendarEvent) => void;
  onEventCreate?: (date: Date) => void;
  onEventUpdate?: (event: CalendarEvent) => void;
  onEventDelete?: (eventId: string) => void;
  onEventDuplicate?: (event: CalendarEvent) => void;
  onRetry?: () => void;
  className?: string;
}

const PLATFORM_COLORS = {
  facebook: "bg-blue-500",
  instagram: "bg-pink-500",
  twitter: "bg-sky-500",
  linkedin: "bg-blue-700",
  tiktok: "bg-black",
  youtube: "bg-red-600"
} as const;

const STATUS_COLORS = {
  draft: "bg-neutral-100 text-neutral-700",
  scheduled: "bg-brand-100 text-brand-700",
  published: "bg-success-100 text-success-700",
  failed: "bg-error-100 text-error-700"
} as const;

export function CalendarBoard({
  events = [],
  loading = false,
  error = false,
  onEventClick,
  onEventCreate,
  onEventUpdate,
  onEventDelete,
  onEventDuplicate,
  onRetry,
  className
}: CalendarBoardProps) {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [view, setView] = useState<"month" | "week" | "day">("month");
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [showFilters, setShowFilters] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [platformFilter, setPlatformFilter] = useState<string>("all");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [showCompleted, setShowCompleted] = useState(true);

  // Get calendar data
  const calendarData = useMemo(() => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();
    
    // Create calendar grid
    const days = [];
    
    // Add empty cells for days before month starts
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(new Date(year, month, day));
    }
    
    return {
      days,
      monthName: firstDay.toLocaleDateString('en-US', { month: 'long', year: 'numeric' }),
      firstDay,
      lastDay
    };
  }, [currentDate]);

  // Filter events
  const filteredEvents = useMemo(() => {
    return events.filter(event => {
      const matchesSearch = event.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          event.content.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesPlatform = platformFilter === "all" || event.platforms.includes(platformFilter);
      const matchesStatus = statusFilter === "all" || event.status === statusFilter;
      const matchesCompleted = showCompleted || event.status !== "published";
      
      return matchesSearch && matchesPlatform && matchesStatus && matchesCompleted;
    });
  }, [events, searchQuery, platformFilter, statusFilter, showCompleted]);

  // Get events for a specific date
  const getEventsForDate = useCallback((date: Date) => {
    return filteredEvents.filter(event => {
      const eventDate = new Date(event.scheduledDate);
      return eventDate.toDateString() === date.toDateString();
    });
  }, [filteredEvents]);

  // Navigation
  const goToPreviousMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() - 1, 1));
  };

  const goToNextMonth = () => {
    setCurrentDate(prev => new Date(prev.getFullYear(), prev.getMonth() + 1, 1));
  };

  const goToToday = () => {
    setCurrentDate(new Date());
  };

  // Event handlers
  const handleDateClick = (date: Date) => {
    onEventCreate?.(date);
  };

  const handleEventClick = (event: CalendarEvent) => {
    setSelectedEvent(event);
    onEventClick?.(event);
  };

  const handleEventAction = (action: string, event: CalendarEvent) => {
    switch (action) {
      case "edit":
        onEventUpdate?.(event);
        break;
      case "duplicate":
        onEventDuplicate?.(event);
        toast.success("Event duplicated successfully!");
        break;
      case "delete":
        onEventDelete?.(event.id);
        toast.success("Event deleted successfully!");
        break;
    }
  };

  if (loading) {
    return (
      <div className={cn("space-y-6", className)} data-testid="calendar-loading">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <div className="flex gap-2">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
          </div>
        </div>
        <Card className="card-premium">
          <CardContent className="p-6">
            <Skeleton className="h-96 w-full" />
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("space-y-6", className)} data-testid="calendar-error">
        <Card className="card-premium">
          <CardContent className="p-8 text-center">
            <CalendarIcon className="h-12 w-12 mx-auto mb-4 text-error-500" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">Failed to load calendar</h3>
            <p className="text-neutral-600 mb-4">There was an issue fetching your calendar data.</p>
            {onRetry && (
              <Button onClick={onRetry} className="btn-premium" data-testid="calendar-retry-button">
                Try Again
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)} data-testid="calendar-board">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold text-neutral-900" data-testid="calendar-title">
            {calendarData.monthName}
          </h2>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={goToPreviousMonth}
              data-testid="prev-month-button"
              aria-label="Previous month"
            >
              <ChevronLeft className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={goToNextMonth}
              data-testid="next-month-button"
              aria-label="Next month"
            >
              <ChevronRight className="h-4 w-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={goToToday}
              data-testid="today-button"
            >
              Today
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <Select value={view} onValueChange={(value: "month" | "week" | "day") => setView(value)}>
            <SelectTrigger className="w-32" data-testid="view-select">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="month">Month</SelectItem>
              <SelectItem value="week">Week</SelectItem>
              <SelectItem value="day">Day</SelectItem>
            </SelectContent>
          </Select>

          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            data-testid="filters-button"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onEventCreate?.(new Date())}
            data-testid="create-event-button"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Event
          </Button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card className="card-premium">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
                  <Input
                    placeholder="Search events..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                    data-testid="search-input"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Platform</label>
                <Select value={platformFilter} onValueChange={setPlatformFilter}>
                  <SelectTrigger data-testid="platform-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Platforms</SelectItem>
                    <SelectItem value="facebook">Facebook</SelectItem>
                    <SelectItem value="instagram">Instagram</SelectItem>
                    <SelectItem value="twitter">Twitter</SelectItem>
                    <SelectItem value="linkedin">LinkedIn</SelectItem>
                    <SelectItem value="tiktok">TikTok</SelectItem>
                    <SelectItem value="youtube">YouTube</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Status</label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger data-testid="status-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="scheduled">Scheduled</SelectItem>
                    <SelectItem value="published">Published</SelectItem>
                    <SelectItem value="failed">Failed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setShowCompleted(!showCompleted)}
                  data-testid="toggle-completed-button"
                >
                  {showCompleted ? <EyeOff className="h-4 w-4 mr-2" /> : <Eye className="h-4 w-4 mr-2" />}
                  {showCompleted ? "Hide Completed" : "Show Completed"}
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Calendar Grid */}
      <Card className="card-premium">
        <CardContent className="p-0">
          <div className="grid grid-cols-7 gap-px bg-neutral-200">
            {/* Day headers */}
            {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((day) => (
              <div key={day} className="bg-neutral-50 p-3 text-center text-sm font-medium text-neutral-600">
                {day}
              </div>
            ))}

            {/* Calendar days */}
            {calendarData.days.map((date, index) => {
              const isToday = date && date.toDateString() === new Date().toDateString();
              const isCurrentMonth = date && date.getMonth() === currentDate.getMonth();
              const dayEvents = date ? getEventsForDate(date) : [];

              return (
                <div
                  key={index}
                  className={cn(
                    "min-h-[120px] bg-white p-2 border-r border-b border-neutral-200",
                    !isCurrentMonth && "bg-neutral-50 text-neutral-400",
                    isToday && "bg-brand-50"
                  )}
                  data-testid={`calendar-day-${index}`}
                >
                  {date && (
                    <>
                      <div className="flex items-center justify-between mb-2">
                        <span
                          className={cn(
                            "text-sm font-medium",
                            isToday && "text-brand-600 font-bold"
                          )}
                        >
                          {date.getDate()}
                        </span>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 w-6 p-0 opacity-0 group-hover:opacity-100 transition-opacity"
                          onClick={() => handleDateClick(date)}
                          data-testid={`add-event-${date.getDate()}`}
                          aria-label={`Add event for ${date.toDateString()}`}
                        >
                          <Plus className="h-3 w-3" />
                        </Button>
                      </div>

                      <div className="space-y-1">
                        {dayEvents.slice(0, 3).map((event) => (
                          <div
                            key={event.id}
                            className={cn(
                              "p-1 rounded text-xs cursor-pointer hover:opacity-80 transition-opacity",
                              STATUS_COLORS[event.status]
                            )}
                            onClick={() => handleEventClick(event)}
                            data-testid={`event-${event.id}`}
                          >
                            <div className="flex items-center gap-1 mb-1">
                              <Clock className="h-3 w-3" />
                              <span className="font-medium truncate">{event.title}</span>
                            </div>
                            <div className="flex items-center gap-1">
                              {event.platforms.map((platform) => (
                                <div
                                  key={platform}
                                  className={cn(
                                    "w-2 h-2 rounded-full",
                                    PLATFORM_COLORS[platform as keyof typeof PLATFORM_COLORS]
                                  )}
                                  data-testid={`platform-indicator-${platform}`}
                                />
                              ))}
                            </div>
                          </div>
                        ))}
                        {dayEvents.length > 3 && (
                          <div className="text-xs text-neutral-500 text-center">
                            +{dayEvents.length - 3} more
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

      {/* Event Details Modal */}
      <Dialog open={!!selectedEvent} onOpenChange={() => setSelectedEvent(null)}>
        <DialogContent className="max-w-2xl" data-testid="event-details-modal">
          {selectedEvent && (
            <>
              <DialogHeader>
                <DialogTitle className="flex items-center gap-2">
                  <CalendarIcon className="h-5 w-5" />
                  {selectedEvent.title}
                </DialogTitle>
              </DialogHeader>
              
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <Badge className={STATUS_COLORS[selectedEvent.status]}>
                    {selectedEvent.status}
                  </Badge>
                  <span className="text-sm text-neutral-600">
                    {selectedEvent.scheduledDate.toLocaleDateString()} at{" "}
                    {selectedEvent.scheduledDate.toLocaleTimeString()}
                  </span>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Content</h4>
                  <p className="text-sm text-neutral-600 whitespace-pre-wrap">
                    {selectedEvent.content}
                  </p>
                </div>

                <div>
                  <h4 className="font-medium mb-2">Platforms</h4>
                  <div className="flex gap-2">
                    {selectedEvent.platforms.map((platform) => (
                      <Badge key={platform} variant="outline">
                        <Globe className="h-3 w-3 mr-1" />
                        {platform}
                      </Badge>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4">
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEventAction("edit", selectedEvent)}
                      data-testid="edit-event-button"
                    >
                      <Edit className="h-4 w-4 mr-2" />
                      Edit
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleEventAction("duplicate", selectedEvent)}
                      data-testid="duplicate-event-button"
                    >
                      <Copy className="h-4 w-4 mr-2" />
                      Duplicate
                    </Button>
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm" data-testid="event-menu-button">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={() => handleEventAction("delete", selectedEvent)}
                        className="text-error-600"
                        data-testid="delete-event-button"
                      >
                        <Trash2 className="h-4 w-4 mr-2" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </div>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
