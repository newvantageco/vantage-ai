"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { 
  CheckCircle2, 
  XCircle, 
  Clock, 
  User, 
  Calendar,
  MessageSquare,
  Eye,
  ThumbsUp,
  ThumbsDown,
  AlertTriangle,
  FileText,
  Image,
  Video,
  Music
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRelativeTimeHours } from '@/lib/time-utils';

// Types
interface ContentApproval {
  id: number;
  content_id: number;
  requested_by: {
    id: number;
    name: string;
    email: string;
    avatar_url?: string;
  };
  approver?: {
    id: number;
    name: string;
    email: string;
    avatar_url?: string;
  };
  status: 'pending' | 'approved' | 'rejected' | 'cancelled';
  requested_at: string;
  approved_at?: string;
  rejection_reason?: string;
  content: {
    id: number;
    title: string;
    content: string;
    content_type: string;
    thumbnail_url?: string;
    status: string;
  };
}

interface ContentApprovalProps {
  approval: ContentApproval;
  onApprove: (approvalId: number) => void;
  onReject: (approvalId: number, reason: string) => void;
  onViewContent: (contentId: number) => void;
  canApprove?: boolean;
}

// Component for rendering relative time
function RelativeTime({ timestamp }: { timestamp: string }) {
  const relativeTime = useRelativeTimeHours(timestamp, 300000);
  return <span>{relativeTime}</span>;
}

// Status badges
const statusBadges = {
  pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
  approved: { label: 'Approved', color: 'bg-green-100 text-green-700', icon: CheckCircle2 },
  rejected: { label: 'Rejected', color: 'bg-red-100 text-red-700', icon: XCircle },
  cancelled: { label: 'Cancelled', color: 'bg-gray-100 text-gray-700', icon: XCircle }
};

// Content type icons
const contentTypeIcons = {
  text: FileText,
  image: Image,
  video: Video,
  audio: Music,
  carousel: Image
};

export function ContentApprovalCard({ 
  approval, 
  onApprove, 
  onReject, 
  onViewContent, 
  canApprove = false 
}: ContentApprovalProps) {
  const [showRejectDialog, setShowRejectDialog] = useState(false);
  const [rejectionReason, setRejectionReason] = useState('');
  const [showContentPreview, setShowContentPreview] = useState(false);

  const StatusIcon = statusBadges[approval.status].icon;
  const ContentIcon = contentTypeIcons[approval.content.content_type as keyof typeof contentTypeIcons] || FileText;

  const handleReject = () => {
    if (rejectionReason.trim()) {
      onReject(approval.id, rejectionReason);
      setShowRejectDialog(false);
      setRejectionReason('');
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between">
          <div className="flex items-center space-x-3">
            <div className="relative">
              {approval.requested_by.avatar_url ? (
                <img
                  src={approval.requested_by.avatar_url}
                  alt={approval.requested_by.name}
                  className="h-10 w-10 rounded-full object-cover"
                />
              ) : (
                <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center">
                  <User className="h-5 w-5 text-muted-foreground" />
                </div>
              )}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h3 className="font-semibold">{approval.requested_by.name}</h3>
                <Badge className={statusBadges[approval.status].color}>
                  <StatusIcon className="h-3 w-3 mr-1" />
                  {statusBadges[approval.status].label}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">
                Requested approval for content
              </p>
              <p className="text-xs text-muted-foreground">
                <RelativeTime timestamp={approval.requested_at} />
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowContentPreview(true)}
            >
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
            {canApprove && approval.status === 'pending' && (
              <>
                <Button
                  size="sm"
                  onClick={() => onApprove(approval.id)}
                  className="bg-green-600 hover:bg-green-700"
                >
                  <ThumbsUp className="h-4 w-4 mr-2" />
                  Approve
                </Button>
                <Dialog open={showRejectDialog} onOpenChange={setShowRejectDialog}>
                  <DialogTrigger asChild>
                    <Button
                      variant="destructive"
                      size="sm"
                    >
                      <ThumbsDown className="h-4 w-4 mr-2" />
                      Reject
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Reject Content</DialogTitle>
                    </DialogHeader>
                    <div className="space-y-4">
                      <div>
                        <label className="text-sm font-medium">Reason for rejection</label>
                        <Textarea
                          value={rejectionReason}
                          onChange={(e) => setRejectionReason(e.target.value)}
                          placeholder="Please provide a reason for rejecting this content..."
                          className="mt-1"
                        />
                      </div>
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          onClick={() => setShowRejectDialog(false)}
                        >
                          Cancel
                        </Button>
                        <Button
                          variant="destructive"
                          onClick={handleReject}
                          disabled={!rejectionReason.trim()}
                        >
                          Reject Content
                        </Button>
                      </div>
                    </div>
                  </DialogContent>
                </Dialog>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      
      <CardContent className="pt-0">
        <div className="space-y-4">
          {/* Content Preview */}
          <div className="border rounded-lg p-4 bg-muted/50">
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <div className="h-12 w-12 rounded-lg bg-muted flex items-center justify-center">
                  <ContentIcon className="h-6 w-6 text-muted-foreground" />
                </div>
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h4 className="font-medium truncate">{approval.content.title}</h4>
                  <Badge variant="outline" className="text-xs">
                    {approval.content.content_type}
                  </Badge>
                  <Badge variant="outline" className="text-xs">
                    {approval.content.status}
                  </Badge>
                </div>
                <p className="text-sm text-muted-foreground line-clamp-2">
                  {approval.content.content}
                </p>
                {approval.content.thumbnail_url && (
                  <div className="mt-2">
                    <img
                      src={approval.content.thumbnail_url}
                      alt="Content thumbnail"
                      className="h-20 w-20 rounded object-cover"
                    />
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Approval Details */}
          {approval.status !== 'pending' && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Status:</span>
                <div className="flex items-center gap-2">
                  <StatusIcon className="h-4 w-4" />
                  <span className="font-medium">{statusBadges[approval.status].label}</span>
                </div>
              </div>
              {approval.approver && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Approved by:</span>
                  <span className="font-medium">{approval.approver.name}</span>
                </div>
              )}
              {approval.approved_at && (
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">Approved at:</span>
                  <span className="font-medium">
                    <RelativeTime timestamp={approval.approved_at} />
                  </span>
                </div>
              )}
              {approval.rejection_reason && (
                <div className="space-y-1">
                  <span className="text-sm text-muted-foreground">Rejection reason:</span>
                  <p className="text-sm bg-red-50 border border-red-200 rounded p-2">
                    {approval.rejection_reason}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

// Content Approval List Component
interface ContentApprovalListProps {
  approvals: ContentApproval[];
  onApprove: (approvalId: number) => void;
  onReject: (approvalId: number, reason: string) => void;
  onViewContent: (contentId: number) => void;
  canApprove?: boolean;
  loading?: boolean;
}

export function ContentApprovalList({ 
  approvals, 
  onApprove, 
  onReject, 
  onViewContent, 
  canApprove = false,
  loading = false 
}: ContentApprovalListProps) {
  if (loading) {
    return (
      <div className="space-y-4">
        {[...Array(3)].map((_, i) => (
          <Card key={i} className="w-full">
            <CardHeader>
              <div className="flex items-center space-x-3">
                <div className="h-10 w-10 rounded-full bg-muted animate-pulse" />
                <div className="space-y-2">
                  <div className="h-4 w-32 bg-muted animate-pulse rounded" />
                  <div className="h-3 w-24 bg-muted animate-pulse rounded" />
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="h-4 w-full bg-muted animate-pulse rounded" />
                <div className="h-4 w-3/4 bg-muted animate-pulse rounded" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (approvals.length === 0) {
    return (
      <Card className="w-full">
        <CardContent className="flex flex-col items-center justify-center py-12">
          <CheckCircle2 className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No pending approvals</h3>
          <p className="text-muted-foreground text-center">
            All content has been reviewed and approved.
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {approvals.map((approval) => (
        <ContentApprovalCard
          key={approval.id}
          approval={approval}
          onApprove={onApprove}
          onReject={onReject}
          onViewContent={onViewContent}
          canApprove={canApprove}
        />
      ))}
    </div>
  );
}
