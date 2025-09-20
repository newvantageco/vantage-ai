"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Users, 
  CheckCircle2, 
  MessageSquare, 
  GitBranch, 
  Bell,
  Activity,
  Clock,
  AlertTriangle,
  TrendingUp,
  BarChart3,
  Settings,
  Plus,
  Filter,
  Search
} from 'lucide-react';
import { ContentApprovalList } from '@/components/collaboration/content-approval';
import { CommentsFeedback } from '@/components/collaboration/comments-feedback';
import { VersionControl } from '@/components/collaboration/version-control';
import { useRelativeTimeHours } from '@/lib/time-utils';

// Types
interface CollaborationStats {
  pending_approvals: number;
  total_comments: number;
  unresolved_comments: number;
  total_versions: number;
  recent_activity: number;
  team_members: number;
}

interface RecentActivity {
  id: number;
  type: 'approval' | 'comment' | 'version' | 'feedback';
  title: string;
  description: string;
  user: string;
  timestamp: string;
  status?: string;
}

// Component for rendering relative time
function RelativeTime({ timestamp }: { timestamp: string }) {
  const relativeTime = useRelativeTimeHours(timestamp, 300000);
  return <span>{relativeTime}</span>;
}

export default function CollaborationPage() {
  const [stats, setStats] = useState<CollaborationStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedContentId, setSelectedContentId] = useState<number | null>(null);

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockStats: CollaborationStats = {
      pending_approvals: 5,
      total_comments: 23,
      unresolved_comments: 8,
      total_versions: 47,
      recent_activity: 12,
      team_members: 8
    };

    const mockActivity: RecentActivity[] = [
      {
        id: 1,
        type: 'approval',
        title: 'Content approval requested',
        description: 'John Doe requested approval for "Summer Campaign Post"',
        user: 'John Doe',
        timestamp: '2024-01-15T10:30:00Z',
        status: 'pending'
      },
      {
        id: 2,
        type: 'comment',
        title: 'New comment added',
        description: 'Sarah Wilson commented on "Product Launch Video"',
        user: 'Sarah Wilson',
        timestamp: '2024-01-15T09:15:00Z'
      },
      {
        id: 3,
        type: 'version',
        title: 'Version created',
        description: 'Mike Johnson created version 3 of "Brand Guidelines"',
        user: 'Mike Johnson',
        timestamp: '2024-01-15T08:45:00Z'
      },
      {
        id: 4,
        type: 'feedback',
        title: 'Feedback provided',
        description: 'Lisa Chen provided feedback on "Social Media Strategy"',
        user: 'Lisa Chen',
        timestamp: '2024-01-15T07:20:00Z'
      },
      {
        id: 5,
        type: 'approval',
        title: 'Content approved',
        description: 'Admin approved "Holiday Campaign Banner"',
        user: 'Admin',
        timestamp: '2024-01-14T16:30:00Z',
        status: 'approved'
      }
    ];

    setStats(mockStats);
    setRecentActivity(mockActivity);
    setLoading(false);
  }, []);

  const handleApprove = (approvalId: number) => {
    // TODO: Implement API call
    console.log('Approving:', approvalId);
  };

  const handleReject = (approvalId: number, reason: string) => {
    // TODO: Implement API call
    console.log('Rejecting:', approvalId, reason);
  };

  const handleViewContent = (contentId: number) => {
    setSelectedContentId(contentId);
  };

  const handleAddComment = (content: string, type: string, parentId?: number) => {
    // TODO: Implement API call
    console.log('Adding comment:', { content, type, parentId });
  };

  const handleAddFeedback = (type: string, rating?: number, comment?: string) => {
    // TODO: Implement API call
    console.log('Adding feedback:', { type, rating, comment });
  };

  const handleResolveComment = (commentId: number) => {
    // TODO: Implement API call
    console.log('Resolving comment:', commentId);
  };

  const handleAcknowledgeFeedback = (feedbackId: number) => {
    // TODO: Implement API call
    console.log('Acknowledging feedback:', feedbackId);
  };

  const handleRestoreVersion = (versionId: number) => {
    // TODO: Implement API call
    console.log('Restoring version:', versionId);
  };

  const handleCompareVersions = (version1Id: number, version2Id: number) => {
    // TODO: Implement API call
    console.log('Comparing versions:', version1Id, version2Id);
  };

  const handleCreateVersion = (changeSummary: string, changeType: string) => {
    // TODO: Implement API call
    console.log('Creating version:', { changeSummary, changeType });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Team Collaboration</h1>
          <p className="text-muted-foreground">
            Manage content approvals, comments, feedback, and version control
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            New Content
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Approvals</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pending_approvals}</div>
              <p className="text-xs text-muted-foreground">
                Awaiting review
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Comments</CardTitle>
              <MessageSquare className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_comments}</div>
              <p className="text-xs text-muted-foreground">
                {stats.unresolved_comments} unresolved
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Versions</CardTitle>
              <GitBranch className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_versions}</div>
              <p className="text-xs text-muted-foreground">
                Total versions
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Team Members</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.team_members}</div>
              <p className="text-xs text-muted-foreground">
                Active collaborators
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Recent Activity</CardTitle>
              <Activity className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.recent_activity}</div>
              <p className="text-xs text-muted-foreground">
                Last 24 hours
              </p>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Notifications</CardTitle>
              <Bell className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">3</div>
              <p className="text-xs text-muted-foreground">
                Unread notifications
              </p>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Tabs defaultValue="approvals" className="space-y-4">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="approvals">Content Approvals</TabsTrigger>
          <TabsTrigger value="comments">Comments & Feedback</TabsTrigger>
          <TabsTrigger value="versions">Version Control</TabsTrigger>
          <TabsTrigger value="activity">Activity Feed</TabsTrigger>
        </TabsList>

        <TabsContent value="approvals" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Content Approvals</CardTitle>
            </CardHeader>
            <CardContent>
              <ContentApprovalList
                approvals={[]} // Mock data - replace with actual API call
                onApprove={handleApprove}
                onReject={handleReject}
                onViewContent={handleViewContent}
                canApprove={true}
                loading={false}
              />
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="comments" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Comments & Feedback</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedContentId ? (
                <CommentsFeedback
                  contentId={selectedContentId}
                  comments={[]} // Mock data - replace with actual API call
                  feedback={[]} // Mock data - replace with actual API call
                  onAddComment={handleAddComment}
                  onAddFeedback={handleAddFeedback}
                  onResolveComment={handleResolveComment}
                  onAcknowledgeFeedback={handleAcknowledgeFeedback}
                  currentUser={{
                    id: 1,
                    name: 'Current User',
                    email: 'user@company.com',
                    avatar_url: undefined
                  }}
                />
              ) : (
                <div className="text-center py-12">
                  <MessageSquare className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Select Content to View Comments</h3>
                  <p className="text-muted-foreground">
                    Choose a content item to view and manage comments and feedback.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="versions" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Version Control</CardTitle>
            </CardHeader>
            <CardContent>
              {selectedContentId ? (
                <VersionControl
                  contentId={selectedContentId}
                  versions={[]} // Mock data - replace with actual API call
                  currentVersion={{
                    id: 1,
                    version_number: 1,
                    title: 'Sample Content',
                    content: 'This is sample content for version control.',
                    content_type: 'text',
                    change_type: 'edit',
                    is_auto_save: false,
                    created_at: '2024-01-15T10:00:00Z',
                    created_by: {
                      id: 1,
                      name: 'John Doe',
                      email: 'john@company.com'
                    }
                  }}
                  onRestoreVersion={handleRestoreVersion}
                  onCompareVersions={handleCompareVersions}
                  onCreateVersion={handleCreateVersion}
                  currentUser={{
                    id: 1,
                    name: 'Current User',
                    email: 'user@company.com',
                    avatar_url: undefined
                  }}
                />
              ) : (
                <div className="text-center py-12">
                  <GitBranch className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Select Content to View Versions</h3>
                  <p className="text-muted-foreground">
                    Choose a content item to view and manage version history.
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivity.map((activity) => {
                  const getActivityIcon = (type: string) => {
                    switch (type) {
                      case 'approval':
                        return <CheckCircle2 className="h-4 w-4" />;
                      case 'comment':
                        return <MessageSquare className="h-4 w-4" />;
                      case 'version':
                        return <GitBranch className="h-4 w-4" />;
                      case 'feedback':
                        return <Activity className="h-4 w-4" />;
                      default:
                        return <Activity className="h-4 w-4" />;
                    }
                  };

                  const getActivityColor = (type: string) => {
                    switch (type) {
                      case 'approval':
                        return 'bg-blue-100 text-blue-700';
                      case 'comment':
                        return 'bg-green-100 text-green-700';
                      case 'version':
                        return 'bg-purple-100 text-purple-700';
                      case 'feedback':
                        return 'bg-orange-100 text-orange-700';
                      default:
                        return 'bg-gray-100 text-gray-700';
                    }
                  };

                  return (
                    <div key={activity.id} className="flex items-start space-x-4">
                      <div className={`h-8 w-8 rounded-full flex items-center justify-center ${getActivityColor(activity.type)}`}>
                        {getActivityIcon(activity.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <h4 className="text-sm font-medium">{activity.title}</h4>
                          {activity.status && (
                            <Badge variant="outline" className="text-xs">
                              {activity.status}
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground">{activity.description}</p>
                        <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                          <span>by {activity.user}</span>
                          <span>•</span>
                          <span><RelativeTime timestamp={activity.timestamp} /></span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
