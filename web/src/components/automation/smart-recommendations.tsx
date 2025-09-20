"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Lightbulb,
  Search,
  Filter,
  MoreHorizontal,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
  Target,
  Hash,
  Users,
  DollarSign,
  RefreshCw,
  Eye,
  ThumbsUp,
  ThumbsDown,
  Star,
  AlertCircle,
  Zap,
  BarChart3
} from "lucide-react";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { toast } from "react-hot-toast";

interface Recommendation {
  id: string;
  type: "content_optimization" | "posting_time" | "hashtag_suggestion" | "audience_targeting" | "budget_allocation" | "content_variation";
  title: string;
  description: string;
  confidence_score: number;
  priority: number;
  status: "pending" | "accepted" | "rejected" | "implemented" | "expired";
  data: Record<string, any>;
  implementation_data?: Record<string, any>;
  content_id?: string;
  campaign_id?: string;
  created_at: string;
  updated_at: string;
  expires_at?: string;
}

const recommendationTypes = [
  { 
    value: "content_optimization", 
    label: "Content Optimization", 
    icon: TrendingUp,
    color: "bg-blue-100 text-blue-800"
  },
  { 
    value: "posting_time", 
    label: "Posting Time", 
    icon: Clock,
    color: "bg-green-100 text-green-800"
  },
  { 
    value: "hashtag_suggestion", 
    label: "Hashtag Suggestion", 
    icon: Hash,
    color: "bg-purple-100 text-purple-800"
  },
  { 
    value: "audience_targeting", 
    label: "Audience Targeting", 
    icon: Users,
    color: "bg-orange-100 text-orange-800"
  },
  { 
    value: "budget_allocation", 
    label: "Budget Allocation", 
    icon: DollarSign,
    color: "bg-yellow-100 text-yellow-800"
  },
  { 
    value: "content_variation", 
    label: "Content Variation", 
    icon: Target,
    color: "bg-pink-100 text-pink-800"
  }
];

const priorityLabels = {
  1: "Critical",
  2: "High",
  3: "Medium",
  4: "Low",
  5: "Info"
};

const statusLabels = {
  pending: "Pending Review",
  accepted: "Accepted",
  rejected: "Rejected",
  implemented: "Implemented",
  expired: "Expired"
};

const statusColors = {
  pending: "bg-yellow-100 text-yellow-800",
  accepted: "bg-green-100 text-green-800",
  rejected: "bg-red-100 text-red-800",
  implemented: "bg-blue-100 text-blue-800",
  expired: "bg-gray-100 text-gray-800"
};

export function SmartRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");
  const [filterType, setFilterType] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [filterPriority, setFilterPriority] = useState<string>("all");
  const [generating, setGenerating] = useState(false);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      // Mock data - replace with actual API call
      const mockRecommendations: Recommendation[] = [
        {
          id: "1",
          type: "posting_time",
          title: "Post at 2 PM for better engagement",
          description: "Your content performs best at 2 PM with 15% higher engagement rate compared to other times.",
          confidence_score: 0.85,
          priority: 1,
          status: "pending",
          data: {
            best_hours: [14, 15, 16],
            engagement_rates: { 14: 0.12, 15: 0.15, 16: 0.13 },
            recommended_schedule: "Post between 2:00-3:00 PM"
          },
          created_at: "2024-01-15T10:00:00Z",
          updated_at: "2024-01-15T10:00:00Z",
          expires_at: "2024-01-22T10:00:00Z"
        },
        {
          id: "2",
          type: "hashtag_suggestion",
          title: "Use #marketing hashtag more often",
          description: "Posts with #marketing hashtag show 25% higher reach and engagement.",
          confidence_score: 0.72,
          priority: 2,
          status: "accepted",
          data: {
            top_hashtags: [
              { tag: "#marketing", engagement_rate: 0.18 },
              { tag: "#socialmedia", engagement_rate: 0.15 },
              { tag: "#content", engagement_rate: 0.12 }
            ],
            recommended_hashtags: ["#marketing", "#socialmedia", "#content", "#digital", "#strategy"]
          },
          implementation_data: {
            implemented_at: "2024-01-15T11:00:00Z",
            implemented_by: "user_123"
          },
          created_at: "2024-01-14T09:00:00Z",
          updated_at: "2024-01-15T11:00:00Z"
        },
        {
          id: "3",
          type: "content_optimization",
          title: "Optimize content length to 150-200 words",
          description: "Your top-performing posts average 175 words with 20% higher engagement.",
          confidence_score: 0.68,
          priority: 3,
          status: "implemented",
          data: {
            avg_engagement: 0.08,
            sample_size: 45,
            recommended_actions: [
              "Maintain content length between 150-200 words",
              "Use similar tone and style",
              "Include 2-3 relevant hashtags"
            ]
          },
          implementation_data: {
            implemented_at: "2024-01-13T14:00:00Z",
            implemented_by: "user_123",
            results: { engagement_increase: 0.15 }
          },
          created_at: "2024-01-13T08:00:00Z",
          updated_at: "2024-01-13T14:00:00Z"
        },
        {
          id: "4",
          type: "audience_targeting",
          title: "Focus on 25-34 age group",
          description: "Your 25-34 age group shows 30% higher engagement and conversion rates.",
          confidence_score: 0.78,
          priority: 2,
          status: "pending",
          data: {
            top_demographics: [
              { segment: "25-34", engagement_rate: 0.12 },
              { segment: "35-44", engagement_rate: 0.09 },
              { segment: "18-24", engagement_rate: 0.08 }
            ],
            recommended_focus: "25-34"
          },
          created_at: "2024-01-15T08:00:00Z",
          updated_at: "2024-01-15T08:00:00Z",
          expires_at: "2024-01-29T08:00:00Z"
        },
        {
          id: "5",
          type: "budget_allocation",
          title: "Increase Facebook ad budget by 20%",
          description: "Facebook ads show 40% better ROI compared to other platforms.",
          confidence_score: 0.65,
          priority: 3,
          status: "rejected",
          data: {
            platform_performance: {
              facebook: { roi: 2.4, cost_per_click: 0.85 },
              instagram: { roi: 1.8, cost_per_click: 1.20 },
              linkedin: { roi: 1.5, cost_per_click: 2.10 }
            },
            recommended_allocation: { facebook: 0.6, instagram: 0.3, linkedin: 0.1 }
          },
          created_at: "2024-01-12T16:00:00Z",
          updated_at: "2024-01-14T10:00:00Z"
        }
      ];
      
      setRecommendations(mockRecommendations);
    } catch (error) {
      console.error("Failed to fetch recommendations:", error);
      toast.error("Failed to load recommendations");
    } finally {
      setLoading(false);
    }
  };

  const generateRecommendations = async () => {
    try {
      setGenerating(true);
      // Mock API call - replace with actual implementation
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Add new mock recommendations
      const newRecommendations: Recommendation[] = [
        {
          id: `new_${Date.now()}`,
          type: "content_variation",
          title: "Try video content format",
          description: "Video posts show 35% higher engagement in your industry.",
          confidence_score: 0.71,
          priority: 2,
          status: "pending",
          data: {
            format_performance: {
              video: { engagement_rate: 0.15 },
              image: { engagement_rate: 0.11 },
              text: { engagement_rate: 0.08 }
            }
          },
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
          expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString()
        }
      ];
      
      setRecommendations(prev => [...newRecommendations, ...prev]);
      toast.success("New recommendations generated successfully");
    } catch (error) {
      console.error("Failed to generate recommendations:", error);
      toast.error("Failed to generate recommendations");
    } finally {
      setGenerating(false);
    }
  };

  const updateRecommendationStatus = async (id: string, status: Recommendation["status"]) => {
    try {
      setRecommendations(prev => prev.map(rec => 
        rec.id === id ? { ...rec, status, updated_at: new Date().toISOString() } : rec
      ));
      toast.success(`Recommendation ${status} successfully`);
    } catch (error) {
      console.error("Failed to update recommendation:", error);
      toast.error("Failed to update recommendation");
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, []);

  const filteredRecommendations = recommendations.filter(rec => {
    const matchesSearch = rec.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         rec.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesType = filterType === "all" || rec.type === filterType;
    const matchesStatus = filterStatus === "all" || rec.status === filterStatus;
    const matchesPriority = filterPriority === "all" || rec.priority.toString() === filterPriority;
    
    return matchesSearch && matchesType && matchesStatus && matchesPriority;
  });

  const getTypeIcon = (type: Recommendation["type"]) => {
    const typeConfig = recommendationTypes.find(t => t.value === type);
    const Icon = typeConfig?.icon || Lightbulb;
    return <Icon className="h-5 w-5" />;
  };

  const getTypeColor = (type: Recommendation["type"]) => {
    const typeConfig = recommendationTypes.find(t => t.value === type);
    return typeConfig?.color || "bg-gray-100 text-gray-800";
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 1) return "Just now";
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const isExpired = (expiresAt?: string) => {
    if (!expiresAt) return false;
    return new Date(expiresAt) < new Date();
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-10 w-32" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {Array.from({ length: 6 }).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-full" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-1/2" />
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Smart Recommendations</h2>
          <p className="text-muted-foreground">
            AI-powered suggestions to optimize your content and campaigns
          </p>
        </div>
        <Button onClick={generateRecommendations} disabled={generating}>
          <RefreshCw className={cn("h-4 w-4 mr-2", generating && "animate-spin")} />
          {generating ? "Generating..." : "Generate New"}
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center space-x-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search recommendations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>
        <Select value={filterType} onValueChange={setFilterType}>
          <SelectTrigger className="w-48">
            <SelectValue placeholder="Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Types</SelectItem>
            {recommendationTypes.map((type) => (
              <SelectItem key={type.value} value={type.value}>
                {type.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-40">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Status</SelectItem>
            {Object.entries(statusLabels).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={filterPriority} onValueChange={setFilterPriority}>
          <SelectTrigger className="w-32">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Priority</SelectItem>
            {Object.entries(priorityLabels).map(([value, label]) => (
              <SelectItem key={value} value={value}>
                {label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Recommendations Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredRecommendations.map((rec) => {
          const typeConfig = recommendationTypes.find(t => t.value === rec.type);
          const expired = isExpired(rec.expires_at);
          
          return (
            <Card key={rec.id} className={cn("relative", expired && "opacity-60")}>
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between">
                  <div className="space-y-2">
                    <div className="flex items-center space-x-2">
                      <div className={cn("p-2 rounded-lg", getTypeColor(rec.type))}>
                        {getTypeIcon(rec.type)}
                      </div>
                      <Badge className={getTypeColor(rec.type)}>
                        {typeConfig?.label || rec.type}
                      </Badge>
                    </div>
                    <CardTitle className="text-lg line-clamp-2">{rec.title}</CardTitle>
                    <CardDescription className="line-clamp-3">
                      {rec.description}
                    </CardDescription>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="sm">
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem onClick={() => updateRecommendationStatus(rec.id, "accepted")}>
                        <ThumbsUp className="h-4 w-4 mr-2" />
                        Accept
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => updateRecommendationStatus(rec.id, "rejected")}>
                        <ThumbsDown className="h-4 w-4 mr-2" />
                        Reject
                      </DropdownMenuItem>
                      <DropdownMenuItem onClick={() => updateRecommendationStatus(rec.id, "implemented")}>
                        <CheckCircle className="h-4 w-4 mr-2" />
                        Mark Implemented
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem>
                        <Eye className="h-4 w-4 mr-2" />
                        View Details
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                {/* Confidence Score */}
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground">Confidence</span>
                    <span className="font-medium">{Math.round(rec.confidence_score * 100)}%</span>
                  </div>
                  <Progress value={rec.confidence_score * 100} className="h-2" />
                </div>

                {/* Priority and Status */}
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Star className="h-4 w-4 text-yellow-500" />
                    <span className="text-sm font-medium">
                      {priorityLabels[rec.priority as keyof typeof priorityLabels]}
                    </span>
                  </div>
                  <Badge className={statusColors[rec.status]}>
                    {statusLabels[rec.status]}
                  </Badge>
                </div>

                {/* Additional Data */}
                {rec.data && Object.keys(rec.data).length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-medium">Key Insights:</h4>
                    <div className="space-y-1">
                      {Object.entries(rec.data).slice(0, 2).map(([key, value]) => (
                        <div key={key} className="text-xs text-muted-foreground">
                          <span className="font-medium">{key.replace(/_/g, ' ')}:</span>{" "}
                          {typeof value === 'object' ? JSON.stringify(value).slice(0, 50) + '...' : String(value)}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Timestamps */}
                <div className="pt-2 border-t space-y-1">
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>Created</span>
                    <span>{formatTimeAgo(rec.created_at)}</span>
                  </div>
                  {rec.expires_at && (
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Expires</span>
                      <span className={expired ? "text-red-500" : ""}>
                        {expired ? "Expired" : formatTimeAgo(rec.expires_at)}
                      </span>
                    </div>
                  )}
                  {rec.implementation_data && (
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>Implemented</span>
                      <span>{formatTimeAgo(rec.implementation_data.implemented_at)}</span>
                    </div>
                  )}
                </div>

                {/* Action Buttons */}
                {rec.status === "pending" && !expired && (
                  <div className="flex space-x-2">
                    <Button 
                      size="sm" 
                      className="flex-1"
                      onClick={() => updateRecommendationStatus(rec.id, "accepted")}
                    >
                      <ThumbsUp className="h-4 w-4 mr-1" />
                      Accept
                    </Button>
                    <Button 
                      size="sm" 
                      variant="outline"
                      className="flex-1"
                      onClick={() => updateRecommendationStatus(rec.id, "rejected")}
                    >
                      <ThumbsDown className="h-4 w-4 mr-1" />
                      Reject
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          );
        })}
      </div>

      {filteredRecommendations.length === 0 && (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Lightbulb className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No recommendations found</h3>
            <p className="text-muted-foreground text-center mb-4">
              {searchTerm || filterType !== "all" || filterStatus !== "all" || filterPriority !== "all"
                ? "No recommendations match your current filters"
                : "Generate your first AI-powered recommendations"
              }
            </p>
            <Button onClick={generateRecommendations} disabled={generating}>
              <RefreshCw className={cn("h-4 w-4 mr-2", generating && "animate-spin")} />
              {generating ? "Generating..." : "Generate Recommendations"}
            </Button>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
