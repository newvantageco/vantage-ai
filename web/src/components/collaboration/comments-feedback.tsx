"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  MessageSquare, 
  ThumbsUp, 
  ThumbsDown, 
  Star, 
  User, 
  Reply, 
  CheckCircle2, 
  XCircle,
  AlertTriangle,
  Heart,
  Flag,
  MoreHorizontal,
  Send,
  Smile,
  AtSign,
  Tag,
  Filter,
  Search,
  Plus,
  Minus
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRelativeTimeHours } from '@/lib/time-utils';

// Types
interface Comment {
  id: number;
  content: string;
  comment_type: 'comment' | 'suggestion' | 'question' | 'feedback';
  is_resolved: boolean;
  resolved_at?: string;
  resolved_by?: {
    id: number;
    name: string;
    avatar_url?: string;
  };
  mentioned_user_ids: number[];
  tags: string[];
  created_at: string;
  updated_at: string;
  user: {
    id: number;
    name: string;
    email: string;
    avatar_url?: string;
  };
  replies?: Comment[];
}

interface Feedback {
  id: number;
  feedback_type: 'like' | 'dislike' | 'suggestion' | 'issue';
  rating?: number;
  comment?: string;
  is_anonymous: boolean;
  categories: string[];
  is_acknowledged: boolean;
  acknowledged_by?: {
    id: number;
    name: string;
    avatar_url?: string;
  };
  acknowledged_at?: string;
  created_at: string;
  user: {
    id: number;
    name: string;
    email: string;
    avatar_url?: string;
  };
}

interface CommentsFeedbackProps {
  contentId: number;
  comments: Comment[];
  feedback: Feedback[];
  onAddComment: (content: string, type: string, parentId?: number) => void;
  onAddFeedback: (type: string, rating?: number, comment?: string) => void;
  onResolveComment: (commentId: number) => void;
  onAcknowledgeFeedback: (feedbackId: number) => void;
  currentUser: {
    id: number;
    name: string;
    email: string;
    avatar_url?: string;
  };
}

// Component for rendering relative time
function RelativeTime({ timestamp }: { timestamp: string }) {
  const relativeTime = useRelativeTimeHours(timestamp, 300000);
  return <span>{relativeTime}</span>;
}

// Comment type badges
const commentTypeBadges = {
  comment: { label: 'Comment', color: 'bg-blue-100 text-blue-700', icon: MessageSquare },
  suggestion: { label: 'Suggestion', color: 'bg-green-100 text-green-700', icon: ThumbsUp },
  question: { label: 'Question', color: 'bg-yellow-100 text-yellow-700', icon: AlertTriangle },
  feedback: { label: 'Feedback', color: 'bg-purple-100 text-purple-700', icon: Heart }
};

// Feedback type badges
const feedbackTypeBadges = {
  like: { label: 'Like', color: 'bg-green-100 text-green-700', icon: ThumbsUp },
  dislike: { label: 'Dislike', color: 'bg-red-100 text-red-700', icon: ThumbsDown },
  suggestion: { label: 'Suggestion', color: 'bg-blue-100 text-blue-700', icon: MessageSquare },
  issue: { label: 'Issue', color: 'bg-orange-100 text-orange-700', icon: Flag }
};

export function CommentsFeedback({ 
  contentId, 
  comments, 
  feedback, 
  onAddComment, 
  onAddFeedback, 
  onResolveComment, 
  onAcknowledgeFeedback,
  currentUser 
}: CommentsFeedbackProps) {
  const [activeTab, setActiveTab] = useState('comments');
  const [showCommentDialog, setShowCommentDialog] = useState(false);
  const [showFeedbackDialog, setShowFeedbackDialog] = useState(false);
  const [commentType, setCommentType] = useState('comment');
  const [feedbackType, setFeedbackType] = useState('like');
  const [rating, setRating] = useState(5);
  const [commentContent, setCommentContent] = useState('');
  const [feedbackContent, setFeedbackContent] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');

  const handleAddComment = () => {
    if (commentContent.trim()) {
      onAddComment(commentContent, commentType);
      setCommentContent('');
      setShowCommentDialog(false);
    }
  };

  const handleAddFeedback = () => {
    onAddFeedback(feedbackType, rating, feedbackContent);
    setFeedbackContent('');
    setShowFeedbackDialog(false);
  };

  const filteredComments = comments.filter(comment => {
    const matchesSearch = comment.content.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         comment.user.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || comment.comment_type === filterType;
    return matchesSearch && matchesFilter;
  });

  const filteredFeedback = feedback.filter(fb => {
    const matchesSearch = (fb.comment || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                         fb.user.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || fb.feedback_type === filterType;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Comments & Feedback</h2>
        <div className="flex gap-2">
          <Dialog open={showCommentDialog} onOpenChange={setShowCommentDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <MessageSquare className="h-4 w-4 mr-2" />
                Add Comment
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Comment</DialogTitle>
              </DialogHeader>
              <AddCommentForm
                content={commentContent}
                setContent={setCommentContent}
                type={commentType}
                setType={setCommentType}
                onSubmit={handleAddComment}
              />
            </DialogContent>
          </Dialog>
          <Dialog open={showFeedbackDialog} onOpenChange={setShowFeedbackDialog}>
            <DialogTrigger asChild>
              <Button>
                <Heart className="h-4 w-4 mr-2" />
                Add Feedback
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add Feedback</DialogTitle>
              </DialogHeader>
              <AddFeedbackForm
                content={feedbackContent}
                setContent={setFeedbackContent}
                type={feedbackType}
                setType={setFeedbackType}
                rating={rating}
                setRating={setRating}
                onSubmit={handleAddFeedback}
              />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search comments and feedback..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={filterType} onValueChange={setFilterType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="comment">Comments</SelectItem>
                <SelectItem value="suggestion">Suggestions</SelectItem>
                <SelectItem value="question">Questions</SelectItem>
                <SelectItem value="feedback">Feedback</SelectItem>
                <SelectItem value="like">Likes</SelectItem>
                <SelectItem value="dislike">Dislikes</SelectItem>
                <SelectItem value="issue">Issues</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="comments">
            Comments ({comments.length})
          </TabsTrigger>
          <TabsTrigger value="feedback">
            Feedback ({feedback.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="comments" className="space-y-4">
          {filteredComments.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No comments yet</h3>
                <p className="text-muted-foreground text-center">
                  Be the first to leave a comment on this content.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredComments.map((comment) => (
                <CommentCard
                  key={comment.id}
                  comment={comment}
                  onResolve={onResolveComment}
                  currentUser={currentUser}
                />
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="feedback" className="space-y-4">
          {filteredFeedback.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Heart className="h-12 w-12 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No feedback yet</h3>
                <p className="text-muted-foreground text-center">
                  Be the first to provide feedback on this content.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {filteredFeedback.map((fb) => (
                <FeedbackCard
                  key={fb.id}
                  feedback={fb}
                  onAcknowledge={onAcknowledgeFeedback}
                  currentUser={currentUser}
                />
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Comment Card Component
function CommentCard({ 
  comment, 
  onResolve, 
  currentUser 
}: { 
  comment: Comment; 
  onResolve: (commentId: number) => void; 
  currentUser: any;
}) {
  const [showReplies, setShowReplies] = useState(false);
  const [replyContent, setReplyContent] = useState('');
  const [showReplyForm, setShowReplyForm] = useState(false);

  const TypeIcon = commentTypeBadges[comment.comment_type].icon;
  const canResolve = currentUser.id === comment.user.id || currentUser.role === 'admin' || currentUser.role === 'owner';

  const handleReply = () => {
    if (replyContent.trim()) {
      // TODO: Implement reply functionality
      console.log('Replying to comment:', comment.id, replyContent);
      setReplyContent('');
      setShowReplyForm(false);
    }
  };

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Comment Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                {comment.user.avatar_url ? (
                  <img
                    src={comment.user.avatar_url}
                    alt={comment.user.name}
                    className="h-8 w-8 rounded-full object-cover"
                  />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                    <User className="h-4 w-4 text-muted-foreground" />
                  </div>
                )}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">{comment.user.name}</h4>
                  <Badge className={commentTypeBadges[comment.comment_type].color}>
                    <TypeIcon className="h-3 w-3 mr-1" />
                    {commentTypeBadges[comment.comment_type].label}
                  </Badge>
                  {comment.is_resolved && (
                    <Badge className="bg-green-100 text-green-700">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Resolved
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  <RelativeTime timestamp={comment.created_at} />
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {canResolve && !comment.is_resolved && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onResolve(comment.id)}
                >
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Resolve
                </Button>
              )}
              <Button
                variant="outline"
                size="sm"
                onClick={() => setShowReplyForm(!showReplyForm)}
              >
                <Reply className="h-4 w-4 mr-2" />
                Reply
              </Button>
            </div>
          </div>

          {/* Comment Content */}
          <div className="pl-11">
            <p className="text-sm whitespace-pre-wrap">{comment.content}</p>
            
            {/* Tags */}
            {comment.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {comment.tags.map((tag, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    <Tag className="h-3 w-3 mr-1" />
                    {tag}
                  </Badge>
                ))}
              </div>
            )}

            {/* Mentions */}
            {comment.mentioned_user_ids.length > 0 && (
              <div className="flex items-center gap-1 mt-2">
                <AtSign className="h-3 w-3 text-muted-foreground" />
                <span className="text-xs text-muted-foreground">
                  Mentioned {comment.mentioned_user_ids.length} user(s)
                </span>
              </div>
            )}

            {/* Reply Form */}
            {showReplyForm && (
              <div className="mt-4 space-y-2">
                <Textarea
                  placeholder="Write a reply..."
                  value={replyContent}
                  onChange={(e) => setReplyContent(e.target.value)}
                  className="min-h-[80px]"
                />
                <div className="flex justify-end gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setShowReplyForm(false)}
                  >
                    Cancel
                  </Button>
                  <Button
                    size="sm"
                    onClick={handleReply}
                    disabled={!replyContent.trim()}
                  >
                    <Send className="h-4 w-4 mr-2" />
                    Reply
                  </Button>
                </div>
              </div>
            )}

            {/* Replies */}
            {comment.replies && comment.replies.length > 0 && (
              <div className="mt-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setShowReplies(!showReplies)}
                  className="p-0 h-auto text-muted-foreground"
                >
                  {showReplies ? (
                    <Minus className="h-4 w-4 mr-1" />
                  ) : (
                    <Plus className="h-4 w-4 mr-1" />
                  )}
                  {comment.replies.length} {comment.replies.length === 1 ? 'reply' : 'replies'}
                </Button>
                {showReplies && (
                  <div className="mt-2 space-y-2 pl-4 border-l-2 border-muted">
                    {comment.replies.map((reply) => (
                      <div key={reply.id} className="space-y-2">
                        <div className="flex items-center space-x-2">
                          <div className="h-6 w-6 rounded-full bg-muted flex items-center justify-center">
                            <User className="h-3 w-3 text-muted-foreground" />
                          </div>
                          <span className="text-sm font-medium">{reply.user.name}</span>
                          <span className="text-xs text-muted-foreground">
                            <RelativeTime timestamp={reply.created_at} />
                          </span>
                        </div>
                        <p className="text-sm text-muted-foreground pl-8">
                          {reply.content}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Feedback Card Component
function FeedbackCard({ 
  feedback, 
  onAcknowledge, 
  currentUser 
}: { 
  feedback: Feedback; 
  onAcknowledge: (feedbackId: number) => void; 
  currentUser: any;
}) {
  const TypeIcon = feedbackTypeBadges[feedback.feedback_type].icon;
  const canAcknowledge = currentUser.role === 'admin' || currentUser.role === 'owner';

  return (
    <Card>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Feedback Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="relative">
                {feedback.is_anonymous ? (
                  <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                    <User className="h-4 w-4 text-muted-foreground" />
                  </div>
                ) : feedback.user.avatar_url ? (
                  <img
                    src={feedback.user.avatar_url}
                    alt={feedback.user.name}
                    className="h-8 w-8 rounded-full object-cover"
                  />
                ) : (
                  <div className="h-8 w-8 rounded-full bg-muted flex items-center justify-center">
                    <User className="h-4 w-4 text-muted-foreground" />
                  </div>
                )}
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-medium">
                    {feedback.is_anonymous ? 'Anonymous' : feedback.user.name}
                  </h4>
                  <Badge className={feedbackTypeBadges[feedback.feedback_type].color}>
                    <TypeIcon className="h-3 w-3 mr-1" />
                    {feedbackTypeBadges[feedback.feedback_type].label}
                  </Badge>
                  {feedback.rating && (
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <Star
                          key={i}
                          className={cn(
                            "h-3 w-3",
                            i < feedback.rating! ? "text-yellow-400 fill-current" : "text-gray-300"
                          )}
                        />
                      ))}
                    </div>
                  )}
                  {feedback.is_acknowledged && (
                    <Badge className="bg-green-100 text-green-700">
                      <CheckCircle2 className="h-3 w-3 mr-1" />
                      Acknowledged
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  <RelativeTime timestamp={feedback.created_at} />
                </p>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {canAcknowledge && !feedback.is_acknowledged && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onAcknowledge(feedback.id)}
                >
                  <CheckCircle2 className="h-4 w-4 mr-2" />
                  Acknowledge
                </Button>
              )}
            </div>
          </div>

          {/* Feedback Content */}
          <div className="pl-11">
            {feedback.comment && (
              <p className="text-sm whitespace-pre-wrap">{feedback.comment}</p>
            )}
            
            {/* Categories */}
            {feedback.categories.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-2">
                {feedback.categories.map((category, index) => (
                  <Badge key={index} variant="outline" className="text-xs">
                    {category}
                  </Badge>
                ))}
              </div>
            )}

            {/* Acknowledgment Info */}
            {feedback.is_acknowledged && feedback.acknowledged_by && (
              <div className="mt-2 text-xs text-muted-foreground">
                Acknowledged by {feedback.acknowledged_by.name} on{' '}
                <RelativeTime timestamp={feedback.acknowledged_at!} />
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Add Comment Form Component
function AddCommentForm({ 
  content, 
  setContent, 
  type, 
  setType, 
  onSubmit 
}: { 
  content: string; 
  setContent: (content: string) => void; 
  type: string; 
  setType: (type: string) => void; 
  onSubmit: () => void; 
}) {
  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="type">Type</Label>
        <Select value={type} onValueChange={setType}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="comment">Comment</SelectItem>
            <SelectItem value="suggestion">Suggestion</SelectItem>
            <SelectItem value="question">Question</SelectItem>
            <SelectItem value="feedback">Feedback</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="content">Content</Label>
        <Textarea
          id="content"
          placeholder="Write your comment..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="min-h-[100px]"
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" onClick={onSubmit} disabled={!content.trim()}>
          <Send className="h-4 w-4 mr-2" />
          Post Comment
        </Button>
      </div>
    </div>
  );
}

// Add Feedback Form Component
function AddFeedbackForm({ 
  content, 
  setContent, 
  type, 
  setType, 
  rating, 
  setRating, 
  onSubmit 
}: { 
  content: string; 
  setContent: (content: string) => void; 
  type: string; 
  setType: (type: string) => void; 
  rating: number; 
  setRating: (rating: number) => void; 
  onSubmit: () => void; 
}) {
  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="type">Type</Label>
        <Select value={type} onValueChange={setType}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="like">Like</SelectItem>
            <SelectItem value="dislike">Dislike</SelectItem>
            <SelectItem value="suggestion">Suggestion</SelectItem>
            <SelectItem value="issue">Issue</SelectItem>
          </SelectContent>
        </Select>
      </div>
      {(type === 'like' || type === 'dislike') && (
        <div>
          <Label>Rating</Label>
          <div className="flex items-center gap-1">
            {[...Array(5)].map((_, i) => (
              <button
                key={i}
                type="button"
                onClick={() => setRating(i + 1)}
                className="p-1"
              >
                <Star
                  className={cn(
                    "h-5 w-5",
                    i < rating ? "text-yellow-400 fill-current" : "text-gray-300"
                  )}
                />
              </button>
            ))}
          </div>
        </div>
      )}
      <div>
        <Label htmlFor="content">Comment (Optional)</Label>
        <Textarea
          id="content"
          placeholder="Add a comment with your feedback..."
          value={content}
          onChange={(e) => setContent(e.target.value)}
          className="min-h-[80px]"
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" onClick={onSubmit}>
          <Heart className="h-4 w-4 mr-2" />
          Submit Feedback
        </Button>
      </div>
    </div>
  );
}
