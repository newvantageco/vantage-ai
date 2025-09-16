"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { EmptyState } from "@/components/ui/empty-state";
import { DataTable, SortableHeader } from "@/components/ui/data-table";
import { ColumnDef } from "@tanstack/react-table";
import { 
  BarChart3, 
  TrendingUp, 
  Eye, 
  Heart,
  MessageCircle,
  Share2,
  Calendar,
  Filter,
  Download,
  RefreshCw
} from "lucide-react";

interface AnalyticsData {
  id: string;
  post_title: string;
  platform: string;
  published_date: string;
  impressions: number;
  engagements: number;
  engagement_rate: number;
  clicks: number;
  shares: number;
}

interface Summary {
  total_posts: number;
  total_impressions: number;
  total_engagements: number;
  avg_engagement_rate: number;
  period: string;
}

export default function ReportsPage() {
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [dateRange, setDateRange] = useState("30d");

  // Sample columns for the data table
  const columns: ColumnDef<AnalyticsData>[] = [
    {
      accessorKey: "post_title",
      header: ({ column }) => (
        <SortableHeader column={column}>Post Title</SortableHeader>
      ),
      cell: ({ row }) => (
        <div className="max-w-[200px] truncate font-medium">
          {row.getValue("post_title")}
        </div>
      ),
    },
    {
      accessorKey: "platform",
      header: "Platform",
      cell: ({ row }) => (
        <Badge variant="outline" className="capitalize">
          {row.getValue("platform")}
        </Badge>
      ),
    },
    {
      accessorKey: "published_date",
      header: ({ column }) => (
        <SortableHeader column={column}>Published</SortableHeader>
      ),
      cell: ({ row }) => (
        <div className="text-sm">
          {new Date(row.getValue("published_date")).toLocaleDateString()}
        </div>
      ),
    },
    {
      accessorKey: "impressions",
      header: ({ column }) => (
        <SortableHeader column={column}>Impressions</SortableHeader>
      ),
      cell: ({ row }) => (
        <div className="text-right font-mono">
          {(row.getValue("impressions") as number).toLocaleString()}
        </div>
      ),
    },
    {
      accessorKey: "engagements",
      header: ({ column }) => (
        <SortableHeader column={column}>Engagements</SortableHeader>
      ),
      cell: ({ row }) => (
        <div className="text-right font-mono">
          {(row.getValue("engagements") as number).toLocaleString()}
        </div>
      ),
    },
    {
      accessorKey: "engagement_rate",
      header: ({ column }) => (
        <SortableHeader column={column}>Engagement Rate</SortableHeader>
      ),
      cell: ({ row }) => (
        <div className="text-right font-mono">
          {(row.getValue("engagement_rate") as number).toFixed(2)}%
        </div>
      ),
    },
  ];

  useEffect(() => {
    loadAnalytics();
  }, [dateRange]);

  const loadAnalytics = async () => {
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data - in real app this would come from API
      const mockData: AnalyticsData[] = [];
      const mockSummary: Summary = {
        total_posts: 0,
        total_impressions: 0,
        total_engagements: 0,
        avg_engagement_rate: 0,
        period: dateRange
      };
      
      setAnalyticsData(mockData);
      setSummary(mockSummary);
    } catch (error) {
      console.error("Failed to load analytics:", error);
    } finally {
      setLoading(false);
    }
  };

  const stats = [
    {
      title: "Total Posts",
      value: summary?.total_posts || 0,
      icon: <BarChart3 className="h-4 w-4" />,
      change: "+12.5%"
    },
    {
      title: "Total Impressions", 
      value: summary?.total_impressions || 0,
      icon: <Eye className="h-4 w-4" />,
      change: "+8.2%"
    },
    {
      title: "Total Engagements",
      value: summary?.total_engagements || 0,
      icon: <Heart className="h-4 w-4" />,
      change: "+15.3%"
    },
    {
      title: "Avg. Engagement Rate",
      value: `${summary?.avg_engagement_rate?.toFixed(2) || 0}%`,
      icon: <TrendingUp className="h-4 w-4" />,
      change: "+2.1%"
    }
  ];

  if (loading) {
    return (
      <div className="p-6">
        <div className="flex items-center justify-center h-64">
          <RefreshCw className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  // Show empty state when no data
  if (analyticsData.length === 0) {
    return (
      <div className="p-6 space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-muted-foreground mt-1">
              Track your content performance and engagement metrics
            </p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <Filter className="h-4 w-4 mr-2" />
              Filter
            </Button>
            <Button variant="outline">
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
          </div>
        </div>

        <EmptyState
          illustration="analytics"
          title="No analytics data available"
          description="Once you start publishing content, you'll see detailed analytics and performance metrics here. Connect your social channels and publish your first post to get started."
          action={{
            label: "Create First Post",
            onClick: () => alert("Navigate to create post"),
            variant: "default"
          }}
          secondaryAction={{
            label: "Connect Channels",
            onClick: () => alert("Navigate to channels"),
            variant: "outline"
          }}
        />
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground mt-1">
            Track your content performance and engagement metrics
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => loadAnalytics()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
            <Filter className="h-4 w-4 mr-2" />
            Filter
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
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
              <div className="text-2xl font-bold">
                {typeof stat.value === 'number' ? stat.value.toLocaleString() : stat.value}
              </div>
              <div className="flex items-center text-xs text-emerald-600">
                <TrendingUp className="h-3 w-3 mr-1" />
                {stat.change} from last period
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Data Table */}
      <Card>
        <CardHeader>
          <CardTitle>Content Performance</CardTitle>
          <CardDescription>
            Detailed breakdown of your published content performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={columns}
            data={analyticsData}
            searchKey="post_title"
            searchPlaceholder="Search posts..."
            emptyTitle="No posts found"
            emptyDescription="No published posts match your filters"
            emptyAction={
              <Button variant="outline" onClick={() => alert("Navigate to create post")}>
                Create First Post
              </Button>
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}