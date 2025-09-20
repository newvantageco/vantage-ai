"use client";

import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
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
  RefreshCw
} from 'lucide-react';
import { apiService, type BraveSearchResponse, type BraveSearchResult } from '@/services/api';
import { toast } from 'react-hot-toast';

interface BraveSearchComponentProps {
  onResultSelect?: (result: BraveSearchResult) => void;
  className?: string;
}

type SearchType = 'web' | 'news' | 'images' | 'videos' | 'local';

export default function BraveSearchComponent({ onResultSelect, className }: BraveSearchComponentProps) {
  const [query, setQuery] = useState('');
  const [searchType, setSearchType] = useState<SearchType>('web');
  const [results, setResults] = useState<BraveSearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [count, setCount] = useState(10);
  const [summary, setSummary] = useState(false);
  const [freshness, setFreshness] = useState('pd');

  const searchTypes = [
    { value: 'web', label: 'Web Search', icon: Globe },
    { value: 'news', label: 'News', icon: Newspaper },
    { value: 'images', label: 'Images', icon: Image },
    { value: 'videos', label: 'Videos', icon: Video },
    { value: 'local', label: 'Local', icon: MapPin },
  ];

  const handleSearch = async () => {
    if (!query.trim()) {
      toast.error('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response: BraveSearchResponse;

      switch (searchType) {
        case 'web':
          response = await apiService.searchWeb({
            query,
            count,
            summary,
            safesearch: 'moderate'
          });
          break;
        case 'news':
          response = await apiService.searchNews({
            query,
            count,
            freshness,
            safesearch: 'moderate'
          });
          break;
        case 'images':
          response = await apiService.searchImages({
            query,
            count,
            safesearch: 'strict'
          });
          break;
        case 'videos':
          response = await apiService.searchVideos({
            query,
            count,
            safesearch: 'moderate'
          });
          break;
        case 'local':
          response = await apiService.searchLocal({
            query,
            count,
            location: 'United States',
            safesearch: 'moderate'
          });
          break;
        default:
          throw new Error('Invalid search type');
      }

      setResults(response);
      toast.success(`Found ${response.total_results} results in ${response.search_time.toFixed(2)}s`);
    } catch (err: any) {
      const errorMessage = err.message || 'Search failed';
      setError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  const formatDate = (dateString?: string) => {
    if (!dateString) return '';
    return new Date(dateString).toLocaleDateString();
  };

  const getSearchIcon = () => {
    const IconComponent = searchTypes.find(t => t.value === searchType)?.icon || Search;
    return <IconComponent className="h-4 w-4" />;
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Search Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Search className="h-5 w-5" />
            Brave Search Integration
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <div className="flex-1">
              <Input
                placeholder="Enter your search query..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyPress={handleKeyPress}
                className="w-full"
              />
            </div>
            <Select value={searchType} onValueChange={(value: SearchType) => setSearchType(value)}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {searchTypes.map((type) => {
                  const IconComponent = type.icon;
                  return (
                    <SelectItem key={type.value} value={type.value}>
                      <div className="flex items-center gap-2">
                        <IconComponent className="h-4 w-4" />
                        {type.label}
                      </div>
                    </SelectItem>
                  );
                })}
              </SelectContent>
            </Select>
            <Button onClick={handleSearch} disabled={loading || !query.trim()}>
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                getSearchIcon()
              )}
            </Button>
          </div>

          {/* Advanced Options */}
          <div className="flex gap-4 items-center">
            <div className="flex items-center gap-2">
              <label className="text-sm font-medium">Results:</label>
              <Select value={count.toString()} onValueChange={(value) => setCount(parseInt(value))}>
                <SelectTrigger className="w-20">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="5">5</SelectItem>
                  <SelectItem value="10">10</SelectItem>
                  <SelectItem value="20">20</SelectItem>
                  <SelectItem value="50">50</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {searchType === 'web' && (
              <div className="flex items-center gap-2">
                <input
                  type="checkbox"
                  id="summary"
                  checked={summary}
                  onChange={(e) => setSummary(e.target.checked)}
                  className="rounded"
                />
                <label htmlFor="summary" className="text-sm font-medium">
                  Include AI Summary
                </label>
              </div>
            )}

            {searchType === 'news' && (
              <div className="flex items-center gap-2">
                <label className="text-sm font-medium">Freshness:</label>
                <Select value={freshness} onValueChange={setFreshness}>
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="pd">Past Day</SelectItem>
                    <SelectItem value="pw">Past Week</SelectItem>
                    <SelectItem value="pm">Past Month</SelectItem>
                    <SelectItem value="py">Past Year</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Error State */}
      {error && (
        <Card className="border-red-200 bg-red-50">
          <CardContent className="p-4">
            <div className="flex items-center gap-2 text-red-600">
              <XCircle className="h-4 w-4" />
              <span className="font-medium">Search Error</span>
            </div>
            <p className="text-sm text-red-600 mt-1">{error}</p>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setError(null)}
              className="mt-2"
            >
              <RefreshCw className="h-4 w-4 mr-2" />
              Try Again
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Results */}
      {results && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                Search Results
              </CardTitle>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <span>{results.total_results} results</span>
                <span>•</span>
                <span>{results.search_time.toFixed(2)}s</span>
              </div>
            </div>
            {results.summary && (
              <div className="mt-2 p-3 bg-blue-50 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-1">AI Summary</h4>
                <p className="text-sm text-blue-800">{results.summary}</p>
              </div>
            )}
          </CardHeader>
          <CardContent className="space-y-4">
            {results.results.map((result, index) => (
              <div
                key={index}
                className="p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => onResultSelect?.(result)}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <h3 className="font-medium text-blue-600 hover:text-blue-800 line-clamp-2">
                      {result.title}
                    </h3>
                    <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                      {result.description}
                    </p>
                    <div className="flex items-center gap-2 mt-2 text-xs text-gray-500">
                      <span className="truncate">{result.url}</span>
                      {result.published_date && (
                        <>
                          <span>•</span>
                          <span>{formatDate(result.published_date)}</span>
                        </>
                      )}
                      {result.source && (
                        <>
                          <span>•</span>
                          <span>{result.source}</span>
                        </>
                      )}
                    </div>
                    {result.rating && (
                      <div className="mt-2">
                        <Badge variant="secondary" className="text-xs">
                          ⭐ {result.rating.toFixed(1)}
                        </Badge>
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col gap-2">
                    {result.thumbnail && (
                      <img
                        src={result.thumbnail}
                        alt={result.title}
                        className="w-16 h-16 object-cover rounded"
                      />
                    )}
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        window.open(result.url, '_blank');
                      }}
                    >
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
