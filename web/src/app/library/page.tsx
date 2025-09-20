"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Drawer, DrawerContent, DrawerHeader, DrawerTitle, DrawerDescription } from '@/components/ui/drawer';
import { 
  Library, 
  Search, 
  Filter, 
  Grid3X3, 
  List, 
  Eye,
  Edit,
  Trash2,
  Download,
  Share,
  Calendar,
  Tag,
  FileText,
  Image,
  Video,
  Music,
  Archive,
  Star,
  Clock,
  User
} from 'lucide-react';
import { cn } from '@/lib/utils';

// Mock content data
const contentItems = [
  {
    id: '1',
    title: 'Q4 Campaign Banner',
    type: 'image',
    size: '2.4 MB',
    dimensions: '1920x1080',
    createdAt: '2024-01-15',
    author: 'John Doe',
    tags: ['campaign', 'banner', 'q4'],
    status: 'published',
    thumbnail: '/api/placeholder/300/200'
  },
  {
    id: '2',
    title: 'Product Demo Video',
    type: 'video',
    size: '45.2 MB',
    dimensions: '1920x1080',
    createdAt: '2024-01-14',
    author: 'Jane Smith',
    tags: ['demo', 'product', 'video'],
    status: 'draft',
    thumbnail: '/api/placeholder/300/200'
  },
  {
    id: '3',
    title: 'Blog Post Template',
    type: 'document',
    size: '1.2 MB',
    dimensions: 'A4',
    createdAt: '2024-01-13',
    author: 'Mike Johnson',
    tags: ['template', 'blog', 'content'],
    status: 'published',
    thumbnail: '/api/placeholder/300/200'
  },
  {
    id: '4',
    title: 'Podcast Episode 12',
    type: 'audio',
    size: '28.7 MB',
    dimensions: '44.1kHz',
    createdAt: '2024-01-12',
    author: 'Sarah Wilson',
    tags: ['podcast', 'audio', 'episode'],
    status: 'published',
    thumbnail: '/api/placeholder/300/200'
  },
  {
    id: '5',
    title: 'Social Media Graphics Pack',
    type: 'image',
    size: '15.8 MB',
    dimensions: '1080x1080',
    createdAt: '2024-01-11',
    author: 'Alex Brown',
    tags: ['social', 'graphics', 'pack'],
    status: 'archived',
    thumbnail: '/api/placeholder/300/200'
  },
  {
    id: '6',
    title: 'Tutorial Screenshots',
    type: 'image',
    size: '8.3 MB',
    dimensions: '1920x1080',
    createdAt: '2024-01-10',
    author: 'Chris Davis',
    tags: ['tutorial', 'screenshots', 'guide'],
    status: 'draft',
    thumbnail: '/api/placeholder/300/200'
  }
];

interface ContentDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  content: any;
}

function ContentDrawer({ isOpen, onClose, content }: ContentDrawerProps) {
  if (!content) return null;

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'image':
        return <Image className="h-5 w-5" />;
      case 'video':
        return <Video className="h-5 w-5" />;
      case 'audio':
        return <Music className="h-5 w-5" />;
      case 'document':
        return <FileText className="h-5 w-5" />;
      default:
        return <FileText className="h-5 w-5" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'text-green-500';
      case 'draft':
        return 'text-yellow-500';
      case 'archived':
        return 'text-gray-500';
      default:
        return 'text-muted-foreground';
    }
  };

  return (
    <Drawer open={isOpen} onOpenChange={onClose}>
      <DrawerContent className="h-[80vh]">
        <DrawerHeader>
          <DrawerTitle className="flex items-center gap-2">
            {getTypeIcon(content.type)}
            {content.title}
          </DrawerTitle>
          <DrawerDescription>
            {content.type} • {content.size} • {content.dimensions}
          </DrawerDescription>
        </DrawerHeader>
        <div className="px-4 pb-4 space-y-6">
          {/* Content Preview */}
          <div className="aspect-video bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              {getTypeIcon(content.type)}
              <p className="text-sm text-muted-foreground mt-2">Content Preview</p>
            </div>
          </div>

          {/* Content Details */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="font-medium text-sm text-muted-foreground mb-2">Status</h4>
              <Badge variant={content.status === 'published' ? 'default' : 'secondary'}>
                {content.status}
              </Badge>
            </div>
            <div>
              <h4 className="font-medium text-sm text-muted-foreground mb-2">Size</h4>
              <p className="text-sm font-mono">{content.size}</p>
            </div>
            <div>
              <h4 className="font-medium text-sm text-muted-foreground mb-2">Created</h4>
              <p className="text-sm font-mono">{content.createdAt}</p>
            </div>
            <div>
              <h4 className="font-medium text-sm text-muted-foreground mb-2">Author</h4>
              <p className="text-sm">{content.author}</p>
            </div>
          </div>

          {/* Tags */}
          <div>
            <h4 className="font-medium text-sm text-muted-foreground mb-2">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {content.tags.map((tag: string, index: number) => (
                <Badge key={index} variant="outline" className="text-xs">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>

          {/* Actions */}
          <div className="space-y-2">
            <Button variant="outline" size="sm" className="w-full">
              <Eye className="h-4 w-4 mr-2" />
              Preview
            </Button>
            <Button variant="outline" size="sm" className="w-full">
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
            <Button variant="outline" size="sm" className="w-full">
              <Download className="h-4 w-4 mr-2" />
              Download
            </Button>
            <Button variant="outline" size="sm" className="w-full">
              <Share className="h-4 w-4 mr-2" />
              Share
            </Button>
            <Button variant="outline" size="sm" className="w-full text-red-500 hover:text-red-700">
              <Trash2 className="h-4 w-4 mr-2" />
              Delete
            </Button>
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}

export default function LibraryPage() {
  const [selectedContent, setSelectedContent] = useState<any>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<'all' | 'published' | 'draft' | 'archived'>('all');

  const handleContentClick = (content: any) => {
    setSelectedContent(content);
    setDrawerOpen(true);
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'image':
        return <Image className="h-5 w-5 text-blue-500" />;
      case 'video':
        return <Video className="h-5 w-5 text-purple-500" />;
      case 'audio':
        return <Music className="h-5 w-5 text-green-500" />;
      case 'document':
        return <FileText className="h-5 w-5 text-orange-500" />;
      default:
        return <FileText className="h-5 w-5 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'published':
        return 'text-green-500';
      case 'draft':
        return 'text-yellow-500';
      case 'archived':
        return 'text-gray-500';
      default:
        return 'text-muted-foreground';
    }
  };

  const filteredContent = contentItems.filter(item => {
    const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesFilter = filterStatus === 'all' || item.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  return (
    <div className="h-full p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-foreground">Library</h1>
            <p className="text-muted-foreground">Manage your content assets</p>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant={viewMode === 'grid' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('grid')}
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value as any)}
            className="bg-background border border-border rounded-md px-3 py-2 text-sm"
          >
            <option value="all">All Status</option>
            <option value="published">Published</option>
            <option value="draft">Draft</option>
            <option value="archived">Archived</option>
          </select>
        </div>
      </div>

      {/* Content Grid/List */}
      {viewMode === 'grid' ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredContent.map((item) => (
            <Card
              key={item.id}
              className="card-lattice card-lattice-hover cursor-pointer"
              onClick={() => handleContentClick(item)}
            >
              <CardContent className="p-4">
                <div className="aspect-video bg-muted rounded-lg mb-3 flex items-center justify-center">
                  <div className="text-center">
                    {getTypeIcon(item.type)}
                    <p className="text-xs text-muted-foreground mt-1">{item.type}</p>
                  </div>
                </div>
                <div className="space-y-2">
                  <h3 className="font-medium text-foreground truncate">{item.title}</h3>
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <span className="font-mono">{item.size}</span>
                    <span className={getStatusColor(item.status)}>{item.status}</span>
                  </div>
                  <div className="flex items-center gap-1 text-xs text-muted-foreground">
                    <Calendar className="h-3 w-3" />
                    <span>{item.createdAt}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {item.tags.slice(0, 2).map((tag: string, index: number) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {item.tags.length > 2 && (
                      <Badge variant="outline" className="text-xs">
                        +{item.tags.length - 2}
                      </Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-2">
          {filteredContent.map((item) => (
            <Card
              key={item.id}
              className="card-lattice card-lattice-hover cursor-pointer"
              onClick={() => handleContentClick(item)}
            >
              <CardContent className="p-4">
                <div className="flex items-center gap-4">
                  <div className="w-16 h-16 bg-muted rounded-lg flex items-center justify-center flex-shrink-0">
                    {getTypeIcon(item.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium text-foreground truncate">{item.title}</h3>
                      <Badge variant={item.status === 'published' ? 'default' : 'secondary'}>
                        {item.status}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mt-1">
                      {item.type} • {item.size} • {item.dimensions}
                    </p>
                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <div className="flex items-center gap-1">
                        <User className="h-3 w-3" />
                        <span>{item.author}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        <span>{item.createdAt}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {item.tags.slice(0, 3).map((tag: string, index: number) => (
                      <Badge key={index} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {item.tags.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{item.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Content Drawer */}
      <ContentDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        content={selectedContent}
      />
    </div>
  );
}