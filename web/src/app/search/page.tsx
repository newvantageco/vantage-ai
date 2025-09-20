"use client";

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Search, 
  Globe, 
  Newspaper, 
  Image, 
  Video, 
  MapPin,
  ExternalLink,
  Loader2,
  CheckCircle2,
  XCircle,
  RefreshCw,
  Plus,
  Bookmark,
  Share2,
  Download,
  Upload,
  FileText,
  Calendar,
  BarChart3,
  Users,
  Zap,
  Settings,
  MessageSquare,
  Copy,
  Save,
  Trash2,
  Edit,
  Eye,
  Star,
  Heart,
  Tag,
  Filter,
  SortAsc,
  SortDesc,
  MoreHorizontal,
  Play,
  Pause,
  Stop,
  RotateCcw,
  Archive,
  Send,
  Mail,
  Phone,
  Map,
  Clock,
  AlertCircle,
  CheckCircle,
  Info,
  HelpCircle
} from 'lucide-react';
import { apiService, type BraveSearchResponse, type BraveSearchResult } from '@/services/api';
import { toast } from 'react-hot-toast';
import BraveSearchComponent from '@/components/BraveSearchComponent';

export default function SearchPage() {
  const router = useRouter();
  const [selectedResults, setSelectedResults] = useState<BraveSearchResult[]>([]);
  const [savedSearches, setSavedSearches] = useState<string[]>([]);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [favoriteResults, setFavoriteResults] = useState<string[]>([]);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);

  const handleResultSelect = (result: BraveSearchResult) => {
    setSelectedResults(prev => {
      const exists = prev.some(r => r.url === result.url);
      if (exists) {
        toast.error('Result already selected');
        return prev;
      }
      toast.success('Result added to selection');
      return [...prev, result];
    });
  };

  const handleRemoveResult = (url: string) => {
    setSelectedResults(prev => prev.filter(r => r.url !== url));
    toast.success('Result removed from selection');
  };

  const handleSaveSearch = (query: string) => {
    if (!savedSearches.includes(query)) {
      setSavedSearches(prev => [...prev, query]);
      toast.success('Search saved');
    } else {
      toast.error('Search already saved');
    }
  };

  const handleCreateContent = () => {
    if (selectedResults.length === 0) {
      toast.error('Please select some results first');
      return;
    }
    // Navigate to content creation with selected results
    toast.success(`Creating content with ${selectedResults.length} selected results`);
    router.push('/composer?selectedResults=' + encodeURIComponent(JSON.stringify(selectedResults)));
  };

  // Enhanced Quick Actions with working functionality
  const handleQuickAction = async (action: string) => {
    setActionLoading(action);
    
    try {
      switch (action) {
        case 'create-content':
          handleCreateContent();
          break;
          
        case 'copy-urls':
          if (selectedResults.length > 0) {
            const urls = selectedResults.map(r => r.url).join('\n');
            await navigator.clipboard.writeText(urls);
            toast.success('URLs copied to clipboard');
          } else {
            toast.error('No results selected');
          }
          break;
          
        case 'export-results':
          if (selectedResults.length > 0) {
            const exportData = {
              timestamp: new Date().toISOString(),
              results: selectedResults,
              count: selectedResults.length
            };
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `search-results-${Date.now()}.json`;
            a.click();
            URL.revokeObjectURL(url);
            toast.success('Results exported successfully');
          } else {
            toast.error('No results to export');
          }
          break;
          
        case 'schedule-content':
          if (selectedResults.length > 0) {
            toast.success('Opening scheduler with selected results...');
            router.push('/calendar?action=schedule&selectedResults=' + encodeURIComponent(JSON.stringify(selectedResults)));
          } else {
            toast.error('Please select some results first');
          }
          break;
          
        case 'create-campaign':
          if (selectedResults.length > 0) {
            toast.success('Creating campaign with selected results...');
            router.push('/campaigns?action=create&selectedResults=' + encodeURIComponent(JSON.stringify(selectedResults)));
          } else {
            toast.error('Please select some results first');
          }
          break;
          
        case 'analyze-trends':
          if (selectedResults.length > 0) {
            toast.success('Analyzing trends from selected results...');
            router.push('/analytics?action=trends&selectedResults=' + encodeURIComponent(JSON.stringify(selectedResults)));
          } else {
            toast.error('Please select some results first');
          }
          break;
          
        case 'share-results':
          if (selectedResults.length > 0) {
            const shareText = `Check out these ${selectedResults.length} interesting results I found:\n\n` + 
              selectedResults.map(r => `• ${r.title}\n  ${r.url}`).join('\n\n');
            
            if (navigator.share) {
              await navigator.share({
                title: 'Search Results',
                text: shareText
              });
            } else {
              await navigator.clipboard.writeText(shareText);
              toast.success('Results copied to clipboard for sharing');
            }
          } else {
            toast.error('No results to share');
          }
          break;
          
        case 'save-search':
          const currentQuery = (document.querySelector('input[type="search"]') as HTMLInputElement)?.value || '';
          if (currentQuery && !savedSearches.includes(currentQuery)) {
            setSavedSearches(prev => [...prev, currentQuery]);
            toast.success('Search saved');
          } else if (currentQuery) {
            toast.error('Search already saved');
          } else {
            toast.error('No search query to save');
          }
          break;
          
        case 'clear-selection':
          setSelectedResults([]);
          toast.success('Selection cleared');
          break;
          
        case 'favorite-selection':
          if (selectedResults.length > 0) {
            const newFavorites = selectedResults.map(r => r.url).filter(url => !favoriteResults.includes(url));
            setFavoriteResults(prev => [...prev, ...newFavorites]);
            toast.success(`${newFavorites.length} results added to favorites`);
          } else {
            toast.error('No results to favorite');
          }
          break;
          
        case 'view-favorites':
          toast.success('Opening favorites...');
          router.push('/favorites');
          break;
          
        case 'advanced-search':
          toast.success('Opening advanced search...');
          router.push('/search?advanced=true');
          break;
          
        default:
          toast.error('Action not implemented yet');
      }
    } catch (error) {
      toast.error('Failed to execute action');
      console.error('Quick action error:', error);
    } finally {
      setActionLoading(null);
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  return (
    <div className="h-full p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Content Research</h1>
          <p className="text-muted-foreground">
            Search the web for inspiration and trending content
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            onClick={handleCreateContent}
            disabled={selectedResults.length === 0}
            className="bg-green-600 hover:bg-green-700"
          >
            <Plus className="h-4 w-4 mr-2" />
            Create Content ({selectedResults.length})
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Search Component */}
        <div className="lg:col-span-2">
          <BraveSearchComponent onResultSelect={handleResultSelect} />
        </div>

        {/* Selected Results Sidebar */}
        <div className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bookmark className="h-5 w-5" />
                Selected Results ({selectedResults.length})
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {selectedResults.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Bookmark className="h-12 w-12 mx-auto mb-4" />
                  <p>No results selected</p>
                  <p className="text-sm">Click on search results to add them here</p>
                </div>
              ) : (
                <>
                  {selectedResults.map((result, index) => (
                    <div key={index} className="p-3 border rounded-lg">
                      <div className="flex items-start justify-between gap-2">
                        <div className="flex-1 min-w-0">
                          <h4 className="font-medium text-sm line-clamp-2">
                            {result.title}
                          </h4>
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {result.description}
                          </p>
                          <div className="flex items-center gap-1 mt-2">
                            <Badge variant="outline" className="text-xs">
                              {result.source || 'Web'}
                            </Badge>
                            {result.published_date && (
                              <Badge variant="outline" className="text-xs">
                                {formatDate(result.published_date)}
                              </Badge>
                            )}
                          </div>
                        </div>
                        <div className="flex flex-col gap-1">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => window.open(result.url, '_blank')}
                            className="h-8 w-8 p-0"
                          >
                            <ExternalLink className="h-3 w-3" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleRemoveResult(result.url)}
                            className="h-8 w-8 p-0 text-red-500 hover:text-red-700"
                          >
                            <XCircle className="h-3 w-3" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                  <Button
                    onClick={() => setSelectedResults([])}
                    variant="outline"
                    className="w-full"
                  >
                    Clear All
                  </Button>
                </>
              )}
            </CardContent>
          </Card>

          {/* Enhanced Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5 text-orange-500" />
                Quick Actions
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {/* Primary Actions */}
              <div className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  onClick={() => handleQuickAction('create-content')}
                  disabled={selectedResults.length === 0 || actionLoading === 'create-content'}
                >
                  {actionLoading === 'create-content' ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Plus className="h-4 w-4 mr-2" />
                  )}
                  Create Content ({selectedResults.length})
                </Button>
                
                <Button
                  variant="outline"
                  className="w-full justify-start hover:bg-green-50 hover:border-green-300 transition-colors"
                  onClick={() => handleQuickAction('copy-urls')}
                  disabled={selectedResults.length === 0 || actionLoading === 'copy-urls'}
                >
                  {actionLoading === 'copy-urls' ? (
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  ) : (
                    <Copy className="h-4 w-4 mr-2" />
                  )}
                  Copy URLs
                </Button>
              </div>

              {/* Secondary Actions */}
              <div className="grid grid-cols-2 gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-10 flex items-center justify-center hover:bg-purple-50 transition-colors"
                  onClick={() => handleQuickAction('schedule-content')}
                  disabled={selectedResults.length === 0 || actionLoading === 'schedule-content'}
                >
                  {actionLoading === 'schedule-content' ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Calendar className="h-3 w-3" />
                  )}
                  <span className="ml-1 text-xs">Schedule</span>
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  className="h-10 flex items-center justify-center hover:bg-pink-50 transition-colors"
                  onClick={() => handleQuickAction('create-campaign')}
                  disabled={selectedResults.length === 0 || actionLoading === 'create-campaign'}
                >
                  {actionLoading === 'create-campaign' ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Image className="h-3 w-3" />
                  )}
                  <span className="ml-1 text-xs">Campaign</span>
                </Button>
              </div>

              {/* Tertiary Actions */}
              <div className="grid grid-cols-3 gap-1">
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 flex items-center justify-center hover:bg-yellow-50 transition-colors"
                  onClick={() => handleQuickAction('analyze-trends')}
                  disabled={selectedResults.length === 0 || actionLoading === 'analyze-trends'}
                >
                  {actionLoading === 'analyze-trends' ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <BarChart3 className="h-3 w-3" />
                  )}
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 flex items-center justify-center hover:bg-indigo-50 transition-colors"
                  onClick={() => handleQuickAction('share-results')}
                  disabled={selectedResults.length === 0 || actionLoading === 'share-results'}
                >
                  {actionLoading === 'share-results' ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Share2 className="h-3 w-3" />
                  )}
                </Button>
                
                <Button
                  variant="outline"
                  size="sm"
                  className="h-8 flex items-center justify-center hover:bg-red-50 transition-colors"
                  onClick={() => handleQuickAction('favorite-selection')}
                  disabled={selectedResults.length === 0 || actionLoading === 'favorite-selection'}
                >
                  {actionLoading === 'favorite-selection' ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <Heart className="h-3 w-3" />
                  )}
                </Button>
              </div>

              {/* Advanced Actions */}
              <div className="pt-2 border-t">
                <div className="grid grid-cols-2 gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs hover:bg-gray-50 transition-colors"
                    onClick={() => handleQuickAction('export-results')}
                    disabled={selectedResults.length === 0 || actionLoading === 'export-results'}
                  >
                    {actionLoading === 'export-results' ? (
                      <Loader2 className="h-3 w-3 animate-spin mr-1" />
                    ) : (
                      <Download className="h-3 w-3 mr-1" />
                    )}
                    Export
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    className="h-8 text-xs hover:bg-gray-50 transition-colors"
                    onClick={() => handleQuickAction('clear-selection')}
                    disabled={selectedResults.length === 0 || actionLoading === 'clear-selection'}
                  >
                    {actionLoading === 'clear-selection' ? (
                      <Loader2 className="h-3 w-3 animate-spin mr-1" />
                    ) : (
                      <Trash2 className="h-3 w-3 mr-1" />
                    )}
                    Clear
                  </Button>
                </div>
              </div>

              {/* Utility Actions */}
              <div className="pt-2 border-t">
                <div className="flex gap-1">
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 h-8 text-xs hover:bg-blue-50 transition-colors"
                    onClick={() => handleQuickAction('save-search')}
                    disabled={actionLoading === 'save-search'}
                  >
                    {actionLoading === 'save-search' ? (
                      <Loader2 className="h-3 w-3 animate-spin mr-1" />
                    ) : (
                      <Save className="h-3 w-3 mr-1" />
                    )}
                    Save Search
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1 h-8 text-xs hover:bg-purple-50 transition-colors"
                    onClick={() => handleQuickAction('advanced-search')}
                    disabled={actionLoading === 'advanced-search'}
                  >
                    {actionLoading === 'advanced-search' ? (
                      <Loader2 className="h-3 w-3 animate-spin mr-1" />
                    ) : (
                      <Filter className="h-3 w-3 mr-1" />
                    )}
                    Advanced
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Saved Searches */}
          {savedSearches.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Bookmark className="h-5 w-5" />
                  Saved Searches
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                {savedSearches.map((search, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-2 border rounded"
                  >
                    <span className="text-sm truncate">{search}</span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSavedSearches(prev => prev.filter((_, i) => i !== index))}
                      className="h-6 w-6 p-0"
                    >
                      <XCircle className="h-3 w-3" />
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
