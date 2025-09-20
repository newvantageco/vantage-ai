"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  GitBranch, 
  History, 
  User, 
  Clock, 
  FileText, 
  Image, 
  Video, 
  Music,
  ArrowLeft,
  ArrowRight,
  RotateCcw,
  Download,
  Eye,
  GitCompare,
  Plus,
  Minus,
  AlertCircle,
  CheckCircle2,
  XCircle,
  Calendar,
  Tag,
  MessageSquare,
  Filter,
  Search
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useRelativeTimeHours } from '@/lib/time-utils';

// Types
interface ContentVersion {
  id: number;
  version_number: number;
  title?: string;
  content?: string;
  content_type?: string;
  media_urls?: string[];
  hashtags?: string[];
  mentions?: string[];
  platform_content?: Record<string, any>;
  tags?: string[];
  content_metadata?: Record<string, any>;
  change_summary?: string;
  change_type: 'edit' | 'revert' | 'restore' | 'auto_save';
  is_auto_save: boolean;
  created_at: string;
  created_by: {
    id: number;
    name: string;
    email: string;
    avatar_url?: string;
  };
}

interface VersionDiff {
  type: 'added' | 'removed' | 'modified' | 'unchanged';
  content: string;
  lineNumber?: number;
}

interface VersionControlProps {
  contentId: number;
  versions: ContentVersion[];
  currentVersion: ContentVersion;
  onRestoreVersion: (versionId: number) => void;
  onCompareVersions: (version1Id: number, version2Id: number) => void;
  onCreateVersion: (changeSummary: string, changeType: string) => void;
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

// Change type badges
const changeTypeBadges = {
  edit: { label: 'Edit', color: 'bg-blue-100 text-blue-700', icon: FileText },
  revert: { label: 'Revert', color: 'bg-orange-100 text-orange-700', icon: RotateCcw },
  restore: { label: 'Restore', color: 'bg-green-100 text-green-700', icon: ArrowLeft },
  auto_save: { label: 'Auto Save', color: 'bg-gray-100 text-gray-700', icon: Clock }
};

// Content type icons
const contentTypeIcons = {
  text: FileText,
  image: Image,
  video: Video,
  audio: Music,
  carousel: Image
};

export function VersionControl({ 
  contentId, 
  versions, 
  currentVersion, 
  onRestoreVersion, 
  onCompareVersions, 
  onCreateVersion,
  currentUser 
}: VersionControlProps) {
  const [selectedVersions, setSelectedVersions] = useState<number[]>([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showCompareDialog, setShowCompareDialog] = useState(false);
  const [changeSummary, setChangeSummary] = useState('');
  const [changeType, setChangeType] = useState('edit');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [compareVersion1, setCompareVersion1] = useState<number | null>(null);
  const [compareVersion2, setCompareVersion2] = useState<number | null>(null);

  const filteredVersions = versions.filter(version => {
    const matchesSearch = (version.title || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                         (version.change_summary || '').toLowerCase().includes(searchTerm.toLowerCase()) ||
                         version.created_by.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterType === 'all' || version.change_type === filterType;
    return matchesSearch && matchesFilter;
  });

  const handleSelectVersion = (versionId: number) => {
    if (selectedVersions.includes(versionId)) {
      setSelectedVersions(selectedVersions.filter(id => id !== versionId));
    } else if (selectedVersions.length < 2) {
      setSelectedVersions([...selectedVersions, versionId]);
    }
  };

  const handleCompare = () => {
    if (selectedVersions.length === 2) {
      onCompareVersions(selectedVersions[0], selectedVersions[1]);
      setShowCompareDialog(true);
    }
  };

  const handleCreateVersion = () => {
    if (changeSummary.trim()) {
      onCreateVersion(changeSummary, changeType);
      setChangeSummary('');
      setShowCreateDialog(false);
    }
  };

  const handleRestore = (versionId: number) => {
    onRestoreVersion(versionId);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Version Control</h2>
          <p className="text-muted-foreground">
            Track and manage content versions
          </p>
        </div>
        <div className="flex gap-2">
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button variant="outline">
                <GitBranch className="h-4 w-4 mr-2" />
                Create Version
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Create New Version</DialogTitle>
              </DialogHeader>
              <CreateVersionForm
                changeSummary={changeSummary}
                setChangeSummary={setChangeSummary}
                changeType={changeType}
                setChangeType={setChangeType}
                onSubmit={handleCreateVersion}
              />
            </DialogContent>
          </Dialog>
          {selectedVersions.length === 2 && (
            <Button onClick={handleCompare}>
              <GitCompare className="h-4 w-4 mr-2" />
              Compare Versions
            </Button>
          )}
        </div>
      </div>

      {/* Current Version */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-green-600" />
            Current Version (v{currentVersion.version_number})
          </CardTitle>
        </CardHeader>
        <CardContent>
          <VersionCard version={currentVersion} isCurrent={true} />
        </CardContent>
      </Card>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
                <Input
                  placeholder="Search versions..."
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
                <SelectItem value="edit">Edits</SelectItem>
                <SelectItem value="revert">Reverts</SelectItem>
                <SelectItem value="restore">Restores</SelectItem>
                <SelectItem value="auto_save">Auto Saves</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Version History */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Version History</h3>
          <div className="text-sm text-muted-foreground">
            {selectedVersions.length} of 2 selected for comparison
          </div>
        </div>
        
        {filteredVersions.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <History className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold mb-2">No versions found</h3>
              <p className="text-muted-foreground text-center">
                No versions match your current filters.
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {filteredVersions.map((version) => (
              <VersionCard
                key={version.id}
                version={version}
                isSelected={selectedVersions.includes(version.id)}
                onSelect={() => handleSelectVersion(version.id)}
                onRestore={() => handleRestore(version.id)}
                canSelect={selectedVersions.length < 2 || selectedVersions.includes(version.id)}
              />
            ))}
          </div>
        )}
      </div>

      {/* Compare Dialog */}
      <Dialog open={showCompareDialog} onOpenChange={setShowCompareDialog}>
        <DialogContent className="max-w-6xl">
          <DialogHeader>
            <DialogTitle>Compare Versions</DialogTitle>
          </DialogHeader>
          <VersionComparison
            version1={versions.find(v => v.id === selectedVersions[0])}
            version2={versions.find(v => v.id === selectedVersions[1])}
          />
        </DialogContent>
      </Dialog>
    </div>
  );
}

// Version Card Component
function VersionCard({ 
  version, 
  isCurrent = false, 
  isSelected = false, 
  onSelect, 
  onRestore, 
  canSelect = true 
}: { 
  version: ContentVersion; 
  isCurrent?: boolean; 
  isSelected?: boolean; 
  onSelect?: () => void; 
  onRestore?: () => void; 
  canSelect?: boolean;
}) {
  const ChangeIcon = changeTypeBadges[version.change_type].icon;
  const ContentIcon = contentTypeIcons[version.content_type as keyof typeof contentTypeIcons] || FileText;

  return (
    <Card className={cn(
      "cursor-pointer transition-all",
      isSelected && "ring-2 ring-primary",
      isCurrent && "border-green-200 bg-green-50"
    )}>
      <CardContent className="pt-6">
        <div className="space-y-4">
          {/* Version Header */}
          <div className="flex items-start justify-between">
            <div className="flex items-center space-x-3">
              <div className="flex items-center space-x-2">
                {canSelect && !isCurrent && (
                  <input
                    type="checkbox"
                    checked={isSelected}
                    onChange={onSelect}
                    className="rounded border-gray-300"
                  />
                )}
                <div className="h-10 w-10 rounded-lg bg-muted flex items-center justify-center">
                  <ContentIcon className="h-5 w-5 text-muted-foreground" />
                </div>
              </div>
              <div>
                <div className="flex items-center gap-2">
                  <h4 className="font-semibold">
                    Version {version.version_number}
                    {isCurrent && (
                      <Badge className="ml-2 bg-green-100 text-green-700">
                        <CheckCircle2 className="h-3 w-3 mr-1" />
                        Current
                      </Badge>
                    )}
                  </h4>
                  <Badge className={changeTypeBadges[version.change_type].color}>
                    <ChangeIcon className="h-3 w-3 mr-1" />
                    {changeTypeBadges[version.change_type].label}
                  </Badge>
                  {version.is_auto_save && (
                    <Badge variant="outline" className="text-xs">
                      Auto Save
                    </Badge>
                  )}
                </div>
                <div className="flex items-center gap-4 text-sm text-muted-foreground">
                  <div className="flex items-center gap-1">
                    <User className="h-3 w-3" />
                    {version.created_by.name}
                  </div>
                  <div className="flex items-center gap-1">
                    <Clock className="h-3 w-3" />
                    <RelativeTime timestamp={version.created_at} />
                  </div>
                </div>
              </div>
            </div>
            <div className="flex items-center gap-2">
              {!isCurrent && onRestore && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onRestore}
                >
                  <RotateCcw className="h-4 w-4 mr-2" />
                  Restore
                </Button>
              )}
              <Button variant="outline" size="sm">
                <Eye className="h-4 w-4 mr-2" />
                View
              </Button>
            </div>
          </div>

          {/* Version Content */}
          <div className="space-y-3">
            {version.title && (
              <div>
                <h5 className="font-medium text-sm text-muted-foreground mb-1">Title</h5>
                <p className="text-sm">{version.title}</p>
              </div>
            )}
            
            {version.change_summary && (
              <div>
                <h5 className="font-medium text-sm text-muted-foreground mb-1">Change Summary</h5>
                <p className="text-sm bg-muted p-2 rounded">{version.change_summary}</p>
              </div>
            )}

            {version.content && (
              <div>
                <h5 className="font-medium text-sm text-muted-foreground mb-1">Content</h5>
                <p className="text-sm line-clamp-3">{version.content}</p>
              </div>
            )}

            {/* Tags and Metadata */}
            <div className="flex flex-wrap gap-2">
              {version.tags && version.tags.map((tag, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  <Tag className="h-3 w-3 mr-1" />
                  {tag}
                </Badge>
              ))}
              {version.hashtags && version.hashtags.map((hashtag, index) => (
                <Badge key={index} variant="outline" className="text-xs">
                  #{hashtag}
                </Badge>
              ))}
            </div>

            {/* Media Preview */}
            {version.media_urls && version.media_urls.length > 0 && (
              <div>
                <h5 className="font-medium text-sm text-muted-foreground mb-2">Media</h5>
                <div className="flex gap-2">
                  {version.media_urls.slice(0, 3).map((url, index) => (
                    <div key={index} className="h-16 w-16 rounded bg-muted flex items-center justify-center">
                      <Image className="h-4 w-4 text-muted-foreground" />
                    </div>
                  ))}
                  {version.media_urls.length > 3 && (
                    <div className="h-16 w-16 rounded bg-muted flex items-center justify-center text-xs text-muted-foreground">
                      +{version.media_urls.length - 3}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

// Version Comparison Component
function VersionComparison({ 
  version1, 
  version2 
}: { 
  version1?: ContentVersion; 
  version2?: ContentVersion; 
}) {
  if (!version1 || !version2) return null;

  // Mock diff data - in real implementation, this would come from a diff algorithm
  const diff: VersionDiff[] = [
    { type: 'unchanged', content: 'This is the beginning of the content.', lineNumber: 1 },
    { type: 'removed', content: 'This line was removed in the new version.', lineNumber: 2 },
    { type: 'added', content: 'This line was added in the new version.', lineNumber: 2 },
    { type: 'modified', content: 'This line was modified significantly.', lineNumber: 3 },
    { type: 'unchanged', content: 'This line remained the same.', lineNumber: 4 },
  ];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <h4 className="font-semibold mb-2">Version {version1.version_number}</h4>
          <div className="text-sm text-muted-foreground">
            by {version1.created_by.name} • <RelativeTime timestamp={version1.created_at} />
          </div>
        </div>
        <div>
          <h4 className="font-semibold mb-2">Version {version2.version_number}</h4>
          <div className="text-sm text-muted-foreground">
            by {version2.created_by.name} • <RelativeTime timestamp={version2.created_at} />
          </div>
        </div>
      </div>

      <div className="border rounded-lg overflow-hidden">
        <div className="bg-muted px-4 py-2 text-sm font-medium">Content Differences</div>
        <div className="divide-y">
          {diff.map((line, index) => (
            <div
              key={index}
              className={cn(
                "px-4 py-2 text-sm font-mono",
                line.type === 'added' && "bg-green-50 text-green-800",
                line.type === 'removed' && "bg-red-50 text-red-800",
                line.type === 'modified' && "bg-yellow-50 text-yellow-800",
                line.type === 'unchanged' && "bg-white"
              )}
            >
              <div className="flex items-center gap-2">
                <span className="text-xs text-muted-foreground w-8">
                  {line.lineNumber}
                </span>
                <div className="flex items-center gap-1">
                  {line.type === 'added' && <Plus className="h-3 w-3 text-green-600" />}
                  {line.type === 'removed' && <Minus className="h-3 w-3 text-red-600" />}
                  {line.type === 'modified' && <AlertCircle className="h-3 w-3 text-yellow-600" />}
                </div>
                <span>{line.content}</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// Create Version Form Component
function CreateVersionForm({ 
  changeSummary, 
  setChangeSummary, 
  changeType, 
  setChangeType, 
  onSubmit 
}: { 
  changeSummary: string; 
  setChangeSummary: (summary: string) => void; 
  changeType: string; 
  setChangeType: (type: string) => void; 
  onSubmit: () => void; 
}) {
  return (
    <div className="space-y-4">
      <div>
        <Label htmlFor="changeType">Change Type</Label>
        <Select value={changeType} onValueChange={setChangeType}>
          <SelectTrigger>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="edit">Edit</SelectItem>
            <SelectItem value="revert">Revert</SelectItem>
            <SelectItem value="restore">Restore</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div>
        <Label htmlFor="changeSummary">Change Summary</Label>
        <Textarea
          id="changeSummary"
          placeholder="Describe what changed in this version..."
          value={changeSummary}
          onChange={(e) => setChangeSummary(e.target.value)}
          className="min-h-[100px]"
        />
      </div>
      <div className="flex justify-end gap-2">
        <Button type="button" onClick={onSubmit} disabled={!changeSummary.trim()}>
          <GitBranch className="h-4 w-4 mr-2" />
          Create Version
        </Button>
      </div>
    </div>
  );
}
