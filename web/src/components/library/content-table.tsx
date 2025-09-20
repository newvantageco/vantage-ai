"use client";

import { useState, useMemo } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Skeleton } from "@/components/ui/skeleton";
import { cn } from "@/lib/utils";
import {
  Search,
  Filter,
  Download,
  Trash2,
  Edit,
  Copy,
  Eye,
  Calendar,
  MoreHorizontal,
  Grid3X3,
  List,
  ChevronDown,
  ArrowUpDown,
  X,
  Plus,
  FileText,
  Image,
  Video,
  Link,
  Globe,
  Clock,
  User,
  Tag,
  BarChart2
} from "lucide-react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
  DropdownMenuSeparator,
} from "@/components/ui/dropdown-menu";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { toast } from "react-hot-toast";

interface ContentItem {
  id: string;
  title: string;
  content: string;
  type: "text" | "image" | "video" | "link";
  platforms: string[];
  status: "draft" | "scheduled" | "published" | "archived";
  createdAt: Date;
  updatedAt: Date;
  scheduledDate?: Date;
  publishedDate?: Date;
  author: string;
  tags: string[];
  performance?: {
    impressions: number;
    engagements: number;
    clicks: number;
    reach: number;
  };
  mediaUrl?: string;
  thumbnailUrl?: string;
}

interface ContentTableProps {
  data?: ContentItem[];
  loading?: boolean;
  error?: boolean;
  onItemClick?: (item: ContentItem) => void;
  onItemEdit?: (item: ContentItem) => void;
  onItemDelete?: (itemId: string) => void;
  onItemDuplicate?: (item: ContentItem) => void;
  onItemArchive?: (itemId: string) => void;
  onBulkAction?: (action: string, itemIds: string[]) => void;
  onRetry?: () => void;
  className?: string;
}

const PLATFORM_COLORS = {
  facebook: "bg-blue-500",
  instagram: "bg-pink-500",
  twitter: "bg-sky-500",
  linkedin: "bg-blue-700",
  tiktok: "bg-black",
  youtube: "bg-red-600"
} as const;

const STATUS_COLORS = {
  draft: "bg-neutral-100 text-neutral-700",
  scheduled: "bg-brand-100 text-brand-700",
  published: "bg-success-100 text-success-700",
  archived: "bg-neutral-100 text-neutral-500"
} as const;

const TYPE_ICONS = {
  text: FileText,
  image: Image,
  video: Video,
  link: Link
} as const;

export function ContentTable({
  data = [],
  loading = false,
  error = false,
  onItemClick,
  onItemEdit,
  onItemDelete,
  onItemDuplicate,
  onItemArchive,
  onBulkAction,
  onRetry,
  className
}: ContentTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [typeFilter, setTypeFilter] = useState<string>("all");
  const [platformFilter, setPlatformFilter] = useState<string>("all");
  const [sortBy, setSortBy] = useState<string>("updatedAt");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");
  const [viewMode, setViewMode] = useState<"table" | "grid">("table");
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [showFilters, setShowFilters] = useState(false);

  // Filter and sort data
  const filteredData = useMemo(() => {
    let filtered = data.filter(item => {
      const matchesSearch = item.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.content.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          item.tags.some(tag => tag.toLowerCase().includes(searchQuery.toLowerCase()));
      const matchesStatus = statusFilter === "all" || item.status === statusFilter;
      const matchesType = typeFilter === "all" || item.type === typeFilter;
      const matchesPlatform = platformFilter === "all" || item.platforms.includes(platformFilter);
      
      return matchesSearch && matchesStatus && matchesType && matchesPlatform;
    });

    // Sort data
    filtered.sort((a, b) => {
      let aValue: any = a[sortBy as keyof ContentItem];
      let bValue: any = b[sortBy as keyof ContentItem];
      
      if (sortBy === "createdAt" || sortBy === "updatedAt" || sortBy === "scheduledDate" || sortBy === "publishedDate") {
        aValue = new Date(aValue).getTime();
        bValue = new Date(bValue).getTime();
      }
      
      if (sortOrder === "asc") {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

    return filtered;
  }, [data, searchQuery, statusFilter, typeFilter, platformFilter, sortBy, sortOrder]);

  // Selection handlers
  const handleSelectAll = (checked: boolean) => {
    if (checked) {
      setSelectedItems(filteredData.map(item => item.id));
    } else {
      setSelectedItems([]);
    }
  };

  const handleSelectItem = (itemId: string, checked: boolean) => {
    if (checked) {
      setSelectedItems(prev => [...prev, itemId]);
    } else {
      setSelectedItems(prev => prev.filter(id => id !== itemId));
    }
  };

  // Bulk actions
  const handleBulkAction = (action: string) => {
    if (selectedItems.length === 0) {
      toast.error("Please select items first");
      return;
    }
    
    onBulkAction?.(action, selectedItems);
    
    switch (action) {
      case "delete":
        toast.success(`${selectedItems.length} items deleted`);
        break;
      case "archive":
        toast.success(`${selectedItems.length} items archived`);
        break;
      case "export":
        toast.success(`Exporting ${selectedItems.length} items`);
        break;
    }
    
    setSelectedItems([]);
  };

  // Sort handlers
  const handleSort = (column: string) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortBy(column);
      setSortOrder("asc");
    }
  };

  // Format date
  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  // Format number
  const formatNumber = (num: number) => {
    if (num >= 1000000) {
      return (num / 1000000).toFixed(1) + 'M';
    } else if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'K';
    }
    return num.toString();
  };

  if (loading) {
    return (
      <div className={cn("space-y-6", className)} data-testid="content-table-loading">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <div className="flex gap-2">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
          </div>
        </div>
        <Card className="card-premium">
          <CardContent className="p-6">
            <div className="space-y-4">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex items-center space-x-4">
                  <Skeleton className="h-4 w-4" />
                  <Skeleton className="h-4 w-32" />
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-20" />
                  <Skeleton className="h-4 w-16" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className={cn("space-y-6", className)} data-testid="content-table-error">
        <Card className="card-premium">
          <CardContent className="p-8 text-center">
            <FileText className="h-12 w-12 mx-auto mb-4 text-error-500" />
            <h3 className="text-lg font-semibold text-neutral-900 mb-2">Failed to load content</h3>
            <p className="text-neutral-600 mb-4">There was an issue fetching your content library.</p>
            {onRetry && (
              <Button onClick={onRetry} className="btn-premium" data-testid="content-table-retry-button">
                Try Again
              </Button>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className={cn("space-y-6", className)} data-testid="content-table">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-bold text-neutral-900">Content Library</h2>
          <p className="text-neutral-600">
            {filteredData.length} {filteredData.length === 1 ? 'item' : 'items'}
            {selectedItems.length > 0 && ` • ${selectedItems.length} selected`}
          </p>
        </div>

        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            data-testid="filters-button"
          >
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </Button>

          <div className="flex items-center border rounded-lg">
            <Button
              variant={viewMode === "table" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("table")}
              data-testid="table-view-button"
            >
              <List className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === "grid" ? "default" : "ghost"}
              size="sm"
              onClick={() => setViewMode("grid")}
              data-testid="grid-view-button"
            >
              <Grid3X3 className="h-4 w-4" />
            </Button>
          </div>

          <Button
            variant="outline"
            size="sm"
            onClick={() => onItemClick?.({} as ContentItem)}
            data-testid="create-content-button"
          >
            <Plus className="h-4 w-4 mr-2" />
            New Content
          </Button>
        </div>
      </div>

      {/* Filters */}
      {showFilters && (
        <Card className="card-premium">
          <CardContent className="p-4">
            <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              <div>
                <label className="text-sm font-medium mb-2 block">Search</label>
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
                  <Input
                    placeholder="Search content..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="pl-10"
                    data-testid="search-input"
                  />
                </div>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Status</label>
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger data-testid="status-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Status</SelectItem>
                    <SelectItem value="draft">Draft</SelectItem>
                    <SelectItem value="scheduled">Scheduled</SelectItem>
                    <SelectItem value="published">Published</SelectItem>
                    <SelectItem value="archived">Archived</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Type</label>
                <Select value={typeFilter} onValueChange={setTypeFilter}>
                  <SelectTrigger data-testid="type-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Types</SelectItem>
                    <SelectItem value="text">Text</SelectItem>
                    <SelectItem value="image">Image</SelectItem>
                    <SelectItem value="video">Video</SelectItem>
                    <SelectItem value="link">Link</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <label className="text-sm font-medium mb-2 block">Platform</label>
                <Select value={platformFilter} onValueChange={setPlatformFilter}>
                  <SelectTrigger data-testid="platform-filter">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Platforms</SelectItem>
                    <SelectItem value="facebook">Facebook</SelectItem>
                    <SelectItem value="instagram">Instagram</SelectItem>
                    <SelectItem value="twitter">Twitter</SelectItem>
                    <SelectItem value="linkedin">LinkedIn</SelectItem>
                    <SelectItem value="tiktok">TikTok</SelectItem>
                    <SelectItem value="youtube">YouTube</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-end">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {
                    setSearchQuery("");
                    setStatusFilter("all");
                    setTypeFilter("all");
                    setPlatformFilter("all");
                  }}
                  data-testid="clear-filters-button"
                >
                  <X className="h-4 w-4 mr-2" />
                  Clear
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Bulk Actions */}
      {selectedItems.length > 0 && (
        <Card className="card-premium">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <span className="text-sm font-medium">
                  {selectedItems.length} item{selectedItems.length === 1 ? '' : 's'} selected
                </span>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleBulkAction("export")}
                    data-testid="bulk-export-button"
                  >
                    <Download className="h-4 w-4 mr-2" />
                    Export
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleBulkAction("archive")}
                    data-testid="bulk-archive-button"
                  >
                    Archive
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleBulkAction("delete")}
                    data-testid="bulk-delete-button"
                    className="text-error-600 hover:text-error-700"
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Delete
                  </Button>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSelectedItems([])}
                data-testid="clear-selection-button"
              >
                Clear Selection
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Content Table/Grid */}
      <Card className="card-premium">
        <CardContent className="p-0">
          {viewMode === "table" ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-12">
                    <Checkbox
                      checked={selectedItems.length === filteredData.length && filteredData.length > 0}
                      onCheckedChange={handleSelectAll}
                      data-testid="select-all-checkbox"
                    />
                  </TableHead>
                  <TableHead>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleSort("title")}
                      className="h-auto p-0 font-medium"
                      data-testid="sort-title-button"
                    >
                      Title
                      <ArrowUpDown className="h-4 w-4 ml-2" />
                    </Button>
                  </TableHead>
                  <TableHead>Type</TableHead>
                  <TableHead>Platforms</TableHead>
                  <TableHead>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleSort("status")}
                      className="h-auto p-0 font-medium"
                      data-testid="sort-status-button"
                    >
                      Status
                      <ArrowUpDown className="h-4 w-4 ml-2" />
                    </Button>
                  </TableHead>
                  <TableHead>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleSort("updatedAt")}
                      className="h-auto p-0 font-medium"
                      data-testid="sort-updated-button"
                    >
                      Updated
                      <ArrowUpDown className="h-4 w-4 ml-2" />
                    </Button>
                  </TableHead>
                  <TableHead>Performance</TableHead>
                  <TableHead className="w-12"></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredData.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                      <FileText className="h-8 w-8 mx-auto mb-2" />
                      <p>No content found</p>
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredData.map((item) => {
                    const TypeIcon = TYPE_ICONS[item.type];
                    return (
                      <TableRow key={item.id} className="hover:bg-neutral-50">
                        <TableCell>
                          <Checkbox
                            checked={selectedItems.includes(item.id)}
                            onCheckedChange={(checked) => handleSelectItem(item.id, checked as boolean)}
                            data-testid={`select-item-${item.id}`}
                          />
                        </TableCell>
                        <TableCell>
                          <div className="flex items-center gap-3">
                            <TypeIcon className="h-4 w-4 text-neutral-500" />
                            <div>
                              <div className="font-medium">{item.title}</div>
                              <div className="text-sm text-neutral-500 truncate max-w-xs">
                                {item.content.substring(0, 100)}...
                              </div>
                            </div>
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">
                            {item.type}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-1">
                            {item.platforms.map((platform) => (
                              <div
                                key={platform}
                                className={cn(
                                  "w-2 h-2 rounded-full",
                                  PLATFORM_COLORS[platform as keyof typeof PLATFORM_COLORS]
                                )}
                                data-testid={`platform-${platform}`}
                                title={platform}
                              />
                            ))}
                          </div>
                        </TableCell>
                        <TableCell>
                          <Badge className={STATUS_COLORS[item.status]}>
                            {item.status}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="text-sm">
                            <div>{formatDate(item.updatedAt)}</div>
                            <div className="text-neutral-500">by {item.author}</div>
                          </div>
                        </TableCell>
                        <TableCell>
                          {item.performance ? (
                            <div className="text-sm">
                              <div className="flex items-center gap-4">
                                <span>{formatNumber(item.performance.impressions)} views</span>
                                <span>{formatNumber(item.performance.engagements)} engagements</span>
                              </div>
                            </div>
                          ) : (
                            <span className="text-neutral-400">-</span>
                          )}
                        </TableCell>
                        <TableCell>
                          <DropdownMenu>
                            <DropdownMenuTrigger asChild>
                              <Button variant="ghost" size="sm" data-testid={`item-menu-${item.id}`}>
                                <MoreHorizontal className="h-4 w-4" />
                              </Button>
                            </DropdownMenuTrigger>
                            <DropdownMenuContent align="end">
                              <DropdownMenuItem
                                onClick={() => onItemClick?.(item)}
                                data-testid={`view-item-${item.id}`}
                              >
                                <Eye className="h-4 w-4 mr-2" />
                                View
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => onItemEdit?.(item)}
                                data-testid={`edit-item-${item.id}`}
                              >
                                <Edit className="h-4 w-4 mr-2" />
                                Edit
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => onItemDuplicate?.(item)}
                                data-testid={`duplicate-item-${item.id}`}
                              >
                                <Copy className="h-4 w-4 mr-2" />
                                Duplicate
                              </DropdownMenuItem>
                              <DropdownMenuSeparator />
                              <DropdownMenuItem
                                onClick={() => onItemArchive?.(item.id)}
                                data-testid={`archive-item-${item.id}`}
                              >
                                Archive
                              </DropdownMenuItem>
                              <DropdownMenuItem
                                onClick={() => onItemDelete?.(item.id)}
                                className="text-error-600"
                                data-testid={`delete-item-${item.id}`}
                              >
                                <Trash2 className="h-4 w-4 mr-2" />
                                Delete
                              </DropdownMenuItem>
                            </DropdownMenuContent>
                          </DropdownMenu>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 p-6">
              {filteredData.length === 0 ? (
                <div className="col-span-full text-center py-8 text-muted-foreground">
                  <FileText className="h-8 w-8 mx-auto mb-2" />
                  <p>No content found</p>
                </div>
              ) : (
                filteredData.map((item) => {
                  const TypeIcon = TYPE_ICONS[item.type];
                  return (
                    <Card key={item.id} className="card-premium-hover">
                      <CardContent className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <TypeIcon className="h-4 w-4 text-neutral-500" />
                            <Badge className={STATUS_COLORS[item.status]}>
                              {item.status}
                            </Badge>
                          </div>
                          <Checkbox
                            checked={selectedItems.includes(item.id)}
                            onCheckedChange={(checked) => handleSelectItem(item.id, checked as boolean)}
                            data-testid={`select-item-${item.id}`}
                          />
                        </div>
                        
                        <h3 className="font-medium mb-2 line-clamp-2">{item.title}</h3>
                        <p className="text-sm text-neutral-600 mb-3 line-clamp-3">
                          {item.content}
                        </p>
                        
                        <div className="flex items-center justify-between">
                          <div className="flex gap-1">
                            {item.platforms.map((platform) => (
                              <div
                                key={platform}
                                className={cn(
                                  "w-2 h-2 rounded-full",
                                  PLATFORM_COLORS[platform as keyof typeof PLATFORM_COLORS]
                                )}
                                title={platform}
                              />
                            ))}
                          </div>
                          <div className="text-xs text-neutral-500">
                            {formatDate(item.updatedAt)}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })
              )}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
