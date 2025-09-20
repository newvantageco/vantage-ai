"use client";

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { 
  Users, 
  UserPlus, 
  Settings, 
  MoreHorizontal, 
  Mail, 
  Shield, 
  Clock, 
  CheckCircle2, 
  XCircle,
  AlertTriangle,
  Search,
  Filter,
  Download,
  Upload,
  Trash2,
  Edit,
  Eye,
  UserCheck,
  UserX,
  Crown,
  UserCog,
  Activity,
  Bell,
  MessageSquare,
  ThumbsUp,
  ThumbsDown,
  Star,
  GitBranch,
  History
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRelativeTimeHours } from '@/lib/time-utils';

// Types
interface TeamMember {
  id: number;
  email: string;
  first_name?: string;
  last_name?: string;
  role: 'owner' | 'admin' | 'editor' | 'analyst';
  is_active: boolean;
  last_login_at?: string;
  created_at: string;
  avatar_url?: string;
}

interface TeamInvitation {
  id: number;
  email: string;
  role: 'owner' | 'admin' | 'editor' | 'analyst';
  status: 'pending' | 'accepted' | 'expired' | 'cancelled';
  invited_by: string;
  created_at: string;
  expires_at: string;
}

interface TeamStats {
  total_members: number;
  active_members: number;
  pending_invitations: number;
  role_breakdown: Record<string, number>;
}

// Component for rendering relative time
function RelativeTime({ timestamp }: { timestamp: string }) {
  const relativeTime = useRelativeTimeHours(timestamp, 300000);
  return <span>{relativeTime}</span>;
}

// Role badges
const roleBadges = {
  owner: { label: 'Owner', color: 'bg-purple-100 text-purple-700', icon: Crown },
  admin: { label: 'Admin', color: 'bg-blue-100 text-blue-700', icon: Shield },
  editor: { label: 'Editor', color: 'bg-green-100 text-green-700', icon: Edit },
  analyst: { label: 'Analyst', color: 'bg-orange-100 text-orange-700', icon: Activity }
};

// Status badges
const statusBadges = {
  active: { label: 'Active', color: 'bg-green-100 text-green-700', icon: CheckCircle2 },
  inactive: { label: 'Inactive', color: 'bg-gray-100 text-gray-700', icon: XCircle },
  pending: { label: 'Pending', color: 'bg-yellow-100 text-yellow-700', icon: Clock },
  accepted: { label: 'Accepted', color: 'bg-green-100 text-green-700', icon: CheckCircle2 },
  expired: { label: 'Expired', color: 'bg-red-100 text-red-700', icon: AlertTriangle },
  cancelled: { label: 'Cancelled', color: 'bg-red-100 text-red-700', icon: XCircle }
};

export default function TeamPage() {
  const [members, setMembers] = useState<TeamMember[]>([]);
  const [invitations, setInvitations] = useState<TeamInvitation[]>([]);
  const [stats, setStats] = useState<TeamStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedRole, setSelectedRole] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [showInviteDialog, setShowInviteDialog] = useState(false);
  const [showSettingsDialog, setShowSettingsDialog] = useState(false);

  // Mock data - replace with actual API calls
  useEffect(() => {
    const mockMembers: TeamMember[] = [
      {
        id: 1,
        email: 'john.doe@company.com',
        first_name: 'John',
        last_name: 'Doe',
        role: 'owner',
        is_active: true,
        last_login_at: '2024-01-15T10:30:00Z',
        created_at: '2023-12-01T09:00:00Z',
        avatar_url: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=32&h=32&fit=crop&crop=face'
      },
      {
        id: 2,
        email: 'jane.smith@company.com',
        first_name: 'Jane',
        last_name: 'Smith',
        role: 'admin',
        is_active: true,
        last_login_at: '2024-01-15T08:45:00Z',
        created_at: '2023-12-05T14:20:00Z',
        avatar_url: 'https://images.unsplash.com/photo-1494790108755-2616b612b786?w=32&h=32&fit=crop&crop=face'
      },
      {
        id: 3,
        email: 'mike.wilson@company.com',
        first_name: 'Mike',
        last_name: 'Wilson',
        role: 'editor',
        is_active: true,
        last_login_at: '2024-01-14T16:20:00Z',
        created_at: '2023-12-10T11:15:00Z'
      },
      {
        id: 4,
        email: 'sarah.jones@company.com',
        first_name: 'Sarah',
        last_name: 'Jones',
        role: 'analyst',
        is_active: false,
        last_login_at: '2024-01-10T09:30:00Z',
        created_at: '2023-12-15T13:45:00Z'
      }
    ];

    const mockInvitations: TeamInvitation[] = [
      {
        id: 1,
        email: 'new.user@company.com',
        role: 'editor',
        status: 'pending',
        invited_by: 'John Doe',
        created_at: '2024-01-14T10:00:00Z',
        expires_at: '2024-01-21T10:00:00Z'
      }
    ];

    const mockStats: TeamStats = {
      total_members: 4,
      active_members: 3,
      pending_invitations: 1,
      role_breakdown: {
        owner: 1,
        admin: 1,
        editor: 1,
        analyst: 1
      }
    };

    setMembers(mockMembers);
    setInvitations(mockInvitations);
    setStats(mockStats);
    setLoading(false);
  }, []);

  const filteredMembers = members.filter(member => {
    const matchesSearch = member.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         `${member.first_name} ${member.last_name}`.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = selectedRole === 'all' || member.role === selectedRole;
    const matchesStatus = selectedStatus === 'all' || 
                         (selectedStatus === 'active' && member.is_active) ||
                         (selectedStatus === 'inactive' && !member.is_active);
    
    return matchesSearch && matchesRole && matchesStatus;
  });

  const handleInviteUser = (email: string, role: string) => {
    // TODO: Implement API call
    console.log('Inviting user:', { email, role });
    setShowInviteDialog(false);
  };

  const handleUpdateRole = (memberId: number, newRole: string) => {
    // TODO: Implement API call
    console.log('Updating role:', { memberId, newRole });
  };

  const handleToggleActive = (memberId: number) => {
    // TODO: Implement API call
    console.log('Toggling active status:', memberId);
  };

  const handleResendInvitation = (invitationId: number) => {
    // TODO: Implement API call
    console.log('Resending invitation:', invitationId);
  };

  const handleCancelInvitation = (invitationId: number) => {
    // TODO: Implement API call
    console.log('Cancelling invitation:', invitationId);
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
          <h1 className="text-3xl font-bold tracking-tight">Team Management</h1>
          <p className="text-muted-foreground">
            Manage team members, roles, and permissions
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => setShowSettingsDialog(true)}>
            <Settings className="h-4 w-4 mr-2" />
            Settings
          </Button>
          <Dialog open={showInviteDialog} onOpenChange={setShowInviteDialog}>
            <DialogTrigger asChild>
              <Button>
                <UserPlus className="h-4 w-4 mr-2" />
                Invite Member
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Invite Team Member</DialogTitle>
              </DialogHeader>
              <InviteUserForm onSubmit={handleInviteUser} />
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Members</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.total_members}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Members</CardTitle>
              <UserCheck className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.active_members}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Pending Invitations</CardTitle>
              <Clock className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stats.pending_invitations}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Role Distribution</CardTitle>
              <Shield className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="space-y-1">
                {Object.entries(stats.role_breakdown).map(([role, count]) => (
                  <div key={role} className="flex justify-between text-sm">
                    <span className="capitalize">{role}</span>
                    <span className="font-medium">{count}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Main Content */}
      <Tabs defaultValue="members" className="space-y-4">
        <TabsList>
          <TabsTrigger value="members">Team Members</TabsTrigger>
          <TabsTrigger value="invitations">Invitations</TabsTrigger>
          <TabsTrigger value="activity">Activity</TabsTrigger>
        </TabsList>

        <TabsContent value="members" className="space-y-4">
          {/* Filters */}
          <Card>
            <CardContent className="pt-6">
              <div className="flex flex-col sm:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                    <Input
                      placeholder="Search members..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                </div>
                <Select value={selectedRole} onValueChange={setSelectedRole}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by role" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Roles</SelectItem>
                    <SelectItem value="owner">Owner</SelectItem>
                    <SelectItem value="admin">Admin</SelectItem>
                    <SelectItem value="editor">Editor</SelectItem>
                    <SelectItem value="analyst">Analyst</SelectItem>
                  </SelectContent>
                </Select>
                <Select value={selectedStatus} onValueChange={setSelectedStatus}>
                  <SelectTrigger className="w-[180px]">
                    <SelectValue placeholder="Filter by status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="active">Active</SelectItem>
                    <SelectItem value="inactive">Inactive</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </CardContent>
          </Card>

          {/* Members List */}
          <div className="space-y-4">
            {filteredMembers.map((member) => {
              const RoleIcon = roleBadges[member.role].icon;
              const StatusIcon = member.is_active ? statusBadges.active.icon : statusBadges.inactive.icon;
              
              return (
                <Card key={member.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="relative">
                          {member.avatar_url ? (
                            <img
                              src={member.avatar_url}
                              alt={`${member.first_name} ${member.last_name}`}
                              className="h-12 w-12 rounded-full object-cover"
                            />
                          ) : (
                            <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                              <Users className="h-6 w-6 text-muted-foreground" />
                            </div>
                          )}
                          <div className={cn(
                            "absolute -bottom-1 -right-1 h-4 w-4 rounded-full border-2 border-background",
                            member.is_active ? "bg-green-500" : "bg-gray-400"
                          )} />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">
                              {member.first_name} {member.last_name}
                            </h3>
                            <Badge className={roleBadges[member.role].color}>
                              <RoleIcon className="h-3 w-3 mr-1" />
                              {roleBadges[member.role].label}
                            </Badge>
                            <Badge className={member.is_active ? statusBadges.active.color : statusBadges.inactive.color}>
                              <StatusIcon className="h-3 w-3 mr-1" />
                              {member.is_active ? statusBadges.active.label : statusBadges.inactive.label}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">{member.email}</p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                            <span>Joined <RelativeTime timestamp={member.created_at} /></span>
                            {member.last_login_at && (
                              <span>Last active <RelativeTime timestamp={member.last_login_at} /></span>
                            )}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Select
                          value={member.role}
                          onValueChange={(value) => handleUpdateRole(member.id, value)}
                        >
                          <SelectTrigger className="w-[120px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="owner">Owner</SelectItem>
                            <SelectItem value="admin">Admin</SelectItem>
                            <SelectItem value="editor">Editor</SelectItem>
                            <SelectItem value="analyst">Analyst</SelectItem>
                          </SelectContent>
                        </Select>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleToggleActive(member.id)}
                        >
                          {member.is_active ? (
                            <UserX className="h-4 w-4" />
                          ) : (
                            <UserCheck className="h-4 w-4" />
                          )}
                        </Button>
                        <Button variant="outline" size="sm">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="invitations" className="space-y-4">
          <div className="space-y-4">
            {invitations.map((invitation) => {
              const StatusIcon = statusBadges[invitation.status].icon;
              
              return (
                <Card key={invitation.id}>
                  <CardContent className="pt-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
                          <Mail className="h-6 w-6 text-muted-foreground" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <h3 className="font-semibold">{invitation.email}</h3>
                            <Badge className={roleBadges[invitation.role].color}>
                              {roleBadges[invitation.role].label}
                            </Badge>
                            <Badge className={statusBadges[invitation.status].color}>
                              <StatusIcon className="h-3 w-3 mr-1" />
                              {statusBadges[invitation.status].label}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground">
                            Invited by {invitation.invited_by}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-muted-foreground mt-1">
                            <span>Sent <RelativeTime timestamp={invitation.created_at} /></span>
                            <span>Expires <RelativeTime timestamp={invitation.expires_at} /></span>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {invitation.status === 'pending' && (
                          <>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleResendInvitation(invitation.id)}
                            >
                              Resend
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() => handleCancelInvitation(invitation.id)}
                            >
                              Cancel
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center space-x-4">
                  <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center">
                    <UserPlus className="h-4 w-4 text-blue-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">New member invited</p>
                    <p className="text-xs text-muted-foreground">
                      John Doe invited new.user@company.com as Editor
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <RelativeTime timestamp="2024-01-14T10:00:00Z" />
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="h-8 w-8 rounded-full bg-green-100 flex items-center justify-center">
                    <UserCheck className="h-4 w-4 text-green-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Member activated</p>
                    <p className="text-xs text-muted-foreground">
                      Sarah Jones was activated by John Doe
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <RelativeTime timestamp="2024-01-13T15:30:00Z" />
                    </p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="h-8 w-8 rounded-full bg-orange-100 flex items-center justify-center">
                    <Shield className="h-4 w-4 text-orange-600" />
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium">Role updated</p>
                    <p className="text-xs text-muted-foreground">
                      Mike Wilson's role changed from Analyst to Editor
                    </p>
                    <p className="text-xs text-muted-foreground">
                      <RelativeTime timestamp="2024-01-12T09:15:00Z" />
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

// Invite User Form Component
function InviteUserForm({ onSubmit }: { onSubmit: (email: string, role: string) => void }) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('editor');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(email, role);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label htmlFor="email">Email Address</Label>
        <Input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="user@company.com"
          required
        />
      </div>
      <div>
        <Label htmlFor="role">Role</Label>
        <Select value={role} onValueChange={setRole}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="owner">Owner</SelectItem>
            <SelectItem value="admin">Admin</SelectItem>
            <SelectItem value="editor">Editor</SelectItem>
            <SelectItem value="analyst">Analyst</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="flex justify-end gap-2">
        <Button type="submit">Send Invitation</Button>
      </div>
    </form>
  );
}
