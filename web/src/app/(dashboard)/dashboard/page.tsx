"use client";

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  BarChart3, 
  MessageSquare, 
  Calendar, 
  FileText, 
  TrendingUp,
  Users,
  Clock,
  Activity
} from "lucide-react";

export default function DashboardPage() {
  const stats = [
    {
      title: "Total Posts",
      value: "1,234",
      change: "+12.5%",
      trend: "up",
      icon: <FileText className="h-4 w-4" />,
    },
    {
      title: "Engagement Rate",
      value: "8.2%",
      change: "+2.1%",
      trend: "up", 
      icon: <Activity className="h-4 w-4" />,
    },
    {
      title: "Active Conversations",
      value: "47",
      change: "+5",
      trend: "up",
      icon: <MessageSquare className="h-4 w-4" />,
    },
    {
      title: "Scheduled Posts",
      value: "23",
      change: "+8",
      trend: "up",
      icon: <Clock className="h-4 w-4" />,
    },
  ];

  const recentActivity = [
    {
      id: "1",
      title: "Instagram post published",
      description: "Summer collection showcase went live",
      time: "5 minutes ago",
      status: "success",
    },
    {
      id: "2", 
      title: "New message received",
      description: "Customer inquiry about product availability",
      time: "12 minutes ago",
      status: "info",
    },
    {
      id: "3",
      title: "Template created",
      description: "Holiday promotion template ready",
      time: "1 hour ago", 
      status: "success",
    },
    {
      id: "4",
      title: "Campaign scheduled",
      description: "Back to school campaign set for next week",
      time: "2 hours ago",
      status: "info",
    },
  ];

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Welcome back! Here's an overview of your content performance.
          </p>
        </div>
        <Button>
          <BarChart3 className="h-4 w-4 mr-2" />
          View Full Report
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat, index) => (
          <Card key={index}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              {stat.icon}
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <div className="flex items-center text-xs text-muted-foreground">
                <TrendingUp className="h-3 w-3 mr-1 text-emerald-500" />
                <span className="text-emerald-500">{stat.change}</span>
                <span className="ml-1">from last month</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Recent Activity */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest updates from your content and conversations
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentActivity.map((activity) => (
                <div key={activity.id} className="flex items-start space-x-3">
                  <div className={`w-2 h-2 rounded-full mt-2 ${
                    activity.status === 'success' ? 'bg-emerald-500' : 'bg-blue-500'
                  }`} />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">
                      {activity.title}
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {activity.description}
                    </p>
                    <p className="text-xs text-muted-foreground mt-1">
                      {activity.time}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>
              Common tasks and shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full justify-start" variant="ghost">
              <FileText className="h-4 w-4 mr-2" />
              Create New Template
            </Button>
            <Button className="w-full justify-start" variant="ghost">
              <Calendar className="h-4 w-4 mr-2" />
              Schedule Content
            </Button>
            <Button className="w-full justify-start" variant="ghost">
              <MessageSquare className="h-4 w-4 mr-2" />
              Check Messages
            </Button>
            <Button className="w-full justify-start" variant="ghost">
              <BarChart3 className="h-4 w-4 mr-2" />
              View Analytics
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
