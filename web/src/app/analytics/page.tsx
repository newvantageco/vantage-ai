"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerDescription } from '@/components/ui/drawer';
import { 
  BarChart3, 
  TrendingUp, 
  TrendingDown,
  Users,
  Eye,
  Heart,
  MessageCircle,
  Share2,
  Calendar,
  Download,
  Filter,
  ArrowUpRight,
  ArrowDownRight,
  Activity,
  Target,
  Zap
} from 'lucide-react';
import { LineChart, Line, AreaChart, Area, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { cn } from '@/lib/utils';
import { QuickHelp } from '@/components/tutorials';

// Mock data for KPIs
const kpiData = [
  {
    title: "Total Views",
    value: "2.4M",
    change: "+12.5%",
    trend: "up",
    icon: Eye,
    color: "text-blue-500"
  },
  {
    title: "Engagement Rate",
    value: "68.4%",
    change: "+3.1%",
    trend: "up",
    icon: Heart,
    color: "text-green-500"
  },
  {
    title: "Active Users",
    value: "1.2M",
    change: "+8.2%",
    trend: "up",
    icon: Users,
    color: "text-purple-500"
  },
  {
    title: "Conversion Rate",
    value: "4.2%",
    change: "-1.3%",
    trend: "down",
    icon: Target,
    color: "text-orange-500"
  }
];

// Mock data for charts
const engagementData = [
  { name: 'Jan', views: 4000, engagement: 2400, shares: 1200 },
  { name: 'Feb', views: 3000, engagement: 1398, shares: 980 },
  { name: 'Mar', views: 2000, engagement: 9800, shares: 480 },
  { name: 'Apr', views: 2780, engagement: 3908, shares: 1200 },
  { name: 'May', views: 1890, engagement: 4800, shares: 800 },
  { name: 'Jun', views: 2390, engagement: 3800, shares: 1000 },
  { name: 'Jul', views: 3490, engagement: 4300, shares: 1100 },
];

const platformData = [
  { name: 'Twitter', value: 35, color: '#1DA1F2' },
  { name: 'LinkedIn', value: 25, color: '#0077B5' },
  { name: 'Instagram', value: 20, color: '#E4405F' },
  { name: 'Facebook', value: 15, color: '#1877F2' },
  { name: 'Other', value: 5, color: '#6B7280' },
];

const topContent = [
  {
    id: '1',
    title: 'Q4 Campaign Launch Video',
    platform: 'YouTube',
    views: 125000,
    engagement: 8.5,
    shares: 1200,
    published: '2024-01-15'
  },
  {
    id: '2',
    title: 'AI Trends Blog Post',
    platform: 'Website',
    views: 89000,
    engagement: 12.3,
    shares: 850,
    published: '2024-01-14'
  },
  {
    id: '3',
    title: 'Product Demo on LinkedIn',
    platform: 'LinkedIn',
    views: 67000,
    engagement: 15.2,
    shares: 450,
    published: '2024-01-13'
  },
  {
    id: '4',
    title: 'Twitter Thread: Industry Insights',
    platform: 'Twitter',
    views: 45000,
    engagement: 18.7,
    shares: 320,
    published: '2024-01-12'
  }
];

interface ReportDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  report: any;
}

function ReportDrawer({ isOpen, onClose, report }: ReportDrawerProps) {
  if (!report) return null;

  return (
    <Drawer open={isOpen} onOpenChange={onClose}>
      <DrawerContent className="h-[80vh]">
        <DrawerHeader>
          <DrawerTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            {report.title}
          </DrawerTitle>
          <DrawerDescription>
            Detailed analytics report • {report.platform} • {report.published}
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 pb-4 space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Eye className="h-4 w-4 text-blue-500" />
                <span className="text-sm font-medium">Views</span>
              </div>
              <p className="text-2xl font-bold">{report.views.toLocaleString()}</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Heart className="h-4 w-4 text-red-500" />
                <span className="text-sm font-medium">Engagement</span>
              </div>
              <p className="text-2xl font-bold">{report.engagement}%</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Share2 className="h-4 w-4 text-green-500" />
                <span className="text-sm font-medium">Shares</span>
              </div>
              <p className="text-2xl font-bold">{report.shares.toLocaleString()}</p>
            </div>
            <div className="p-4 bg-muted rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-purple-500" />
                <span className="text-sm font-medium">CTR</span>
              </div>
              <p className="text-2xl font-bold">{(report.engagement * 0.8).toFixed(1)}%</p>
            </div>
          </div>

          {/* Performance Chart */}
          <div className="h-64">
            <h4 className="font-medium mb-4">Performance Over Time</h4>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={engagementData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Area type="monotone" dataKey="views" stackId="1" stroke="#8884d8" fill="#8884d8" />
              </AreaChart>
            </ResponsiveContainer>
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
            <Button variant="outline" size="sm" className="w-full">
              <Share2 className="h-4 w-4 mr-2" />
              Share Report
            </Button>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}

export default function AnalyticsPage() {
  const [selectedReport, setSelectedReport] = useState<any>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [timeRange, setTimeRange] = useState<'7d' | '30d' | '90d' | '1y'>('30d');

  const handleReportClick = (report: any) => {
    setSelectedReport(report);
    setDrawerOpen(true);
  };

  return (
    <div className="h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Analytics</h1>
          <p className="text-muted-foreground">Track performance and insights</p>
        </div>
        <div className="flex items-center gap-2">
          <QuickHelp context="analytics" />
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value as any)}
            className="bg-background border border-border rounded-md px-3 py-2 text-sm"
          >
            <option value="7d">Last 7 days</option>
            <option value="30d">Last 30 days</option>
            <option value="90d">Last 90 days</option>
            <option value="1y">Last year</option>
          </select>
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiData.map((kpi, index) => (
          <Card key={index} className="card-lattice card-lattice-hover">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">
                    {kpi.title}
                  </p>
                  <p className="text-2xl font-bold text-foreground">
                    {kpi.value}
                  </p>
                </div>
                <div className={cn("p-3 rounded-lg bg-muted", kpi.color)}>
                  <kpi.icon className="h-6 w-6" />
                </div>
              </div>
              <div className="flex items-center gap-2 mt-4">
                {kpi.trend === 'up' ? (
                  <ArrowUpRight className="h-4 w-4 text-green-500" />
                ) : (
                  <ArrowDownRight className="h-4 w-4 text-red-500" />
                )}
                <span className={cn(
                  "text-sm font-medium",
                  kpi.trend === 'up' ? "text-green-500" : "text-red-500"
                )}>
                  {kpi.change}
                </span>
                <span className="text-sm text-muted-foreground">vs last period</span>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Engagement Trend */}
        <Card className="card-lattice">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Engagement Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={engagementData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="views" stroke="#8884d8" strokeWidth={2} />
                  <Line type="monotone" dataKey="engagement" stroke="#82ca9d" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>

        {/* Platform Distribution */}
        <Card className="card-lattice">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Platform Distribution
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-80">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={platformData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {platformData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Content Performance */}
      <Card className="card-lattice">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Top Performing Content
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {topContent.map((content) => (
              <div
                key={content.id}
                className="flex items-center gap-4 p-4 rounded-lg bg-muted/50 hover:bg-muted/80 cursor-pointer transition-colors"
                onClick={() => handleReportClick(content)}
              >
                <div className="w-12 h-12 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="h-6 w-6 text-muted-foreground" />
                </div>
                <div className="flex-1 min-w-0">
                  <h4 className="font-medium text-foreground truncate">{content.title}</h4>
                  <p className="text-sm text-muted-foreground">
                    {content.platform} • Published {content.published}
                  </p>
                </div>
                <div className="grid grid-cols-3 gap-6 text-sm">
                  <div className="text-center">
                    <p className="font-mono text-foreground">{content.views.toLocaleString()}</p>
                    <p className="text-xs text-muted-foreground">Views</p>
                  </div>
                  <div className="text-center">
                    <p className="font-mono text-foreground">{content.engagement}%</p>
                    <p className="text-xs text-muted-foreground">Engagement</p>
                  </div>
                  <div className="text-center">
                    <p className="font-mono text-foreground">{content.shares.toLocaleString()}</p>
                    <p className="text-xs text-muted-foreground">Shares</p>
                  </div>
                </div>
                <Button variant="ghost" size="sm">
                  <ArrowUpRight className="h-4 w-4" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Report Drawer */}
      <ReportDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        report={selectedReport}
      />
    </div>
  );
}