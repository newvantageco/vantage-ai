"use client";

import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";
import {
  Send,
  Image,
  Video,
  Link,
  Hash,
  AtSign,
  Smile,
  Bold,
  Italic,
  Underline,
  List,
  ListOrdered,
  Quote,
  Code,
  AlignLeft,
  AlignCenter,
  AlignRight,
  Wand2,
  Sparkles,
  Eye,
  Calendar,
  Clock,
  Globe,
  Smartphone,
  Monitor,
  Tablet,
  Save,
  X,
  Plus,
  ChevronDown,
  Zap,
  Target,
  Palette,
  Type,
  Languages,
  Settings,
  Edit
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
} from "@/components/ui/dropdown-menu";
import { toast } from "react-hot-toast";
import { apiService, type AIContentResponse } from "@/services/api";

interface ComposerFormProps {
  initialData?: {
    content: string;
    platforms: string[];
    scheduledDate?: string;
    brandGuide?: string;
    locale?: string;
  };
  onSave?: (data: ComposerData) => void;
  onPublish?: (data: ComposerData) => void;
  onSchedule?: (data: ComposerData) => void;
  loading?: boolean;
  className?: string;
}

export interface ComposerData {
  content: string;
  platforms: string[];
  scheduledDate?: string;
  brandGuide?: string;
  locale?: string;
  media?: File[];
  hashtags?: string[];
  mentions?: string[];
  aiOptimized?: boolean;
  characterCount?: { [platform: string]: number };
}

const PLATFORMS = [
  { id: "facebook", name: "Facebook", icon: "📘", color: "bg-blue-500", maxLength: 2200 },
  { id: "instagram", name: "Instagram", icon: "📷", color: "bg-pink-500", maxLength: 2200 },
  { id: "twitter", name: "Twitter", icon: "🐦", color: "bg-sky-500", maxLength: 280 },
  { id: "linkedin", name: "LinkedIn", icon: "💼", color: "bg-blue-700", maxLength: 3000 },
  { id: "tiktok", name: "TikTok", icon: "🎵", color: "bg-black", maxLength: 2200 },
  { id: "youtube", name: "YouTube", icon: "📺", color: "bg-red-600", maxLength: 5000 }
];

const BRAND_GUIDES = [
  { id: "professional", name: "Professional", tone: "Formal and authoritative" },
  { id: "casual", name: "Casual", tone: "Friendly and approachable" },
  { id: "creative", name: "Creative", tone: "Playful and innovative" },
  { id: "technical", name: "Technical", tone: "Precise and detailed" }
];

const LOCALES = [
  { id: "en", name: "English", flag: "🇺🇸" },
  { id: "es", name: "Spanish", flag: "🇪🇸" },
  { id: "fr", name: "French", flag: "🇫🇷" },
  { id: "de", name: "German", flag: "🇩🇪" },
  { id: "it", name: "Italian", flag: "🇮🇹" },
  { id: "pt", name: "Portuguese", flag: "🇵🇹" }
];

export function ComposerForm({ 
  initialData, 
  onSave, 
  onPublish, 
  onSchedule, 
  loading = false, 
  className 
}: ComposerFormProps) {
  const [content, setContent] = useState(initialData?.content || "");
  const [platforms, setPlatforms] = useState<string[]>(initialData?.platforms || []);
  const [scheduledDate, setScheduledDate] = useState(initialData?.scheduledDate || "");
  const [brandGuide, setBrandGuide] = useState(initialData?.brandGuide || "");
  const [locale, setLocale] = useState(initialData?.locale || "en");
  const [hashtags, setHashtags] = useState<string[]>([]);
  const [mentions, setMentions] = useState<string[]>([]);
  const [aiOptimized, setAiOptimized] = useState(false);
  const [activeTab, setActiveTab] = useState("compose");
  const [isGenerating, setIsGenerating] = useState(false);
  const [isOptimizing, setIsOptimizing] = useState(false);
  
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Character count calculation
  const getCharacterCount = (platformId: string) => {
    const platform = PLATFORMS.find(p => p.id === platformId);
    return platform ? Math.min(content.length, platform.maxLength) : content.length;
  };

  const getCharacterLimit = (platformId: string) => {
    const platform = PLATFORMS.find(p => p.id === platformId);
    return platform?.maxLength || 280;
  };

  const isOverLimit = (platformId: string) => {
    return getCharacterCount(platformId) > getCharacterLimit(platformId);
  };

  // Platform management
  const togglePlatform = (platformId: string) => {
    setPlatforms(prev => 
      prev.includes(platformId) 
        ? prev.filter(p => p !== platformId)
        : [...prev, platformId]
    );
  };

  // AI Generation
  const handleAIGenerate = async () => {
    if (!content.trim()) {
      toast.error("Please enter a prompt first");
      return;
    }
    
    setIsGenerating(true);
    try {
      const response: AIContentResponse = await apiService.generateAIContent({
        prompt: content,
        content_type: "post",
        brand_voice: brandGuide || undefined,
        platform: platforms[0] || undefined,
        locale: locale
      });
      
      setContent(response.content);
      toast.success(`Content generated successfully! (${response.tokens_used} tokens used)`);
    } catch (error: any) {
      console.error("AI generation error:", error);
      toast.error(error.message || "Failed to generate content. Please try again.");
    } finally {
      setIsGenerating(false);
    }
  };

  // AI Optimization
  const handleAIOptimize = async () => {
    setIsOptimizing(true);
    try {
      // Simulate AI optimization
      await new Promise(resolve => setTimeout(resolve, 1500));
      setAiOptimized(true);
      toast.success("Content optimized for better engagement!");
    } catch (error) {
      toast.error("Failed to optimize content. Please try again.");
    } finally {
      setIsOptimizing(false);
    }
  };

  // Hashtag extraction
  const extractHashtags = (text: string) => {
    const hashtagRegex = /#\w+/g;
    return text.match(hashtagRegex) || [];
  };

  const extractMentions = (text: string) => {
    const mentionRegex = /@\w+/g;
    return text.match(mentionRegex) || [];
  };

  // Update hashtags and mentions when content changes
  useEffect(() => {
    setHashtags(extractHashtags(content));
    setMentions(extractMentions(content));
  }, [content]);

  // Form submission
  const handleSave = async () => {
    try {
      const data = {
        content,
        platforms,
        content_type: "text",
        scheduled_date: scheduledDate ? new Date(scheduledDate).toISOString() : undefined,
        media_urls: [], // TODO: Handle media uploads
        hashtags,
        mentions,
        brand_guide_id: brandGuide ? 1 : undefined, // TODO: Map brand guide to ID
        locale
      };
      
      await apiService.createContent(data);
      toast.success("Draft saved successfully!");
      onSave?.(data as ComposerData);
    } catch (error: any) {
      console.error("Save error:", error);
      toast.error(error.message || "Failed to save content. Please try again.");
    }
  };

  const handlePublish = async () => {
    if (platforms.length === 0) {
      toast.error("Please select at least one platform");
      return;
    }
    
    try {
      const data = {
        content,
        platforms,
        content_type: "text",
        scheduled_date: new Date().toISOString(), // Publish immediately
        media_urls: [], // TODO: Handle media uploads
        hashtags,
        mentions,
        brand_guide_id: brandGuide ? 1 : undefined, // TODO: Map brand guide to ID
        locale
      };
      
      await apiService.createContent(data);
      toast.success("Content published successfully!");
      onPublish?.(data as ComposerData);
    } catch (error: any) {
      console.error("Publish error:", error);
      toast.error(error.message || "Failed to publish content. Please try again.");
    }
  };

  const handleSchedule = async () => {
    if (platforms.length === 0) {
      toast.error("Please select at least one platform");
      return;
    }
    
    if (!scheduledDate) {
      toast.error("Please select a scheduled date");
      return;
    }
    
    try {
      const data = {
        content,
        platforms,
        content_type: "text",
        scheduled_date: new Date(scheduledDate).toISOString(),
        media_urls: [], // TODO: Handle media uploads
        hashtags,
        mentions,
        brand_guide_id: brandGuide ? 1 : undefined, // TODO: Map brand guide to ID
        locale
      };
      
      await apiService.createContent(data);
      toast.success("Content scheduled successfully!");
      onSchedule?.(data as ComposerData);
    } catch (error: any) {
      console.error("Schedule error:", error);
      toast.error(error.message || "Failed to schedule content. Please try again.");
    }
  };

  return (
    <div className={cn("max-w-4xl mx-auto", className)} data-testid="composer-form">
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="compose" data-testid="compose-tab">
            <Type className="h-4 w-4 mr-2" />
            Compose
          </TabsTrigger>
          <TabsTrigger value="preview" data-testid="preview-tab">
            <Eye className="h-4 w-4 mr-2" />
            Preview
          </TabsTrigger>
          <TabsTrigger value="schedule" data-testid="schedule-tab">
            <Calendar className="h-4 w-4 mr-2" />
            Schedule
          </TabsTrigger>
        </TabsList>

        <TabsContent value="compose" className="space-y-6">
          {/* Platform Selection */}
          <Card className="card-premium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Select Platforms
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {PLATFORMS.map((platform) => (
                  <button
                    key={platform.id}
                    onClick={() => togglePlatform(platform.id)}
                    className={cn(
                      "flex items-center gap-3 p-4 rounded-xl border-2 transition-all duration-200",
                      platforms.includes(platform.id)
                        ? "border-brand-500 bg-brand-50 text-brand-700"
                        : "border-neutral-200 hover:border-neutral-300 text-neutral-600"
                    )}
                    data-testid={`platform-${platform.id}`}
                    aria-pressed={platforms.includes(platform.id)}
                  >
                    <span className="text-2xl" aria-hidden="true">{platform.icon}</span>
                    <div className="text-left">
                      <div className="font-medium">{platform.name}</div>
                      <div className="text-xs text-muted-foreground">
                        {platform.maxLength} chars
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Content Editor */}
          <Card className="card-premium">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Edit className="h-5 w-5" />
                  Content
                </CardTitle>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleAIGenerate}
                    disabled={isGenerating}
                    data-testid="ai-generate-button"
                  >
                    <Wand2 className="h-4 w-4 mr-2" />
                    {isGenerating ? "Generating..." : "Generate"}
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={handleAIOptimize}
                    disabled={isOptimizing || !content}
                    data-testid="ai-optimize-button"
                  >
                    <Sparkles className="h-4 w-4 mr-2" />
                    {isOptimizing ? "Optimizing..." : "Optimize"}
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Formatting Toolbar */}
              <div className="flex items-center gap-1 p-2 bg-neutral-50 rounded-lg">
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Bold className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Italic className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Underline className="h-4 w-4" />
                </Button>
                <Separator orientation="vertical" className="h-6" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <List className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <ListOrdered className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Quote className="h-4 w-4" />
                </Button>
                <Separator orientation="vertical" className="h-6" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Hash className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <AtSign className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <Smile className="h-4 w-4" />
                </Button>
              </div>

              {/* Text Editor */}
              <div className="space-y-2">
                <Textarea
                  ref={textareaRef}
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  placeholder="What's on your mind? Share your thoughts with the world..."
                  className="min-h-[200px] resize-none border-0 focus-visible:ring-0 text-base"
                  data-testid="content-textarea"
                />
                
                {/* Character Count for Selected Platforms */}
                {platforms.length > 0 && (
                  <div className="space-y-2">
                    {platforms.map((platformId) => {
                      const platform = PLATFORMS.find(p => p.id === platformId);
                      const count = getCharacterCount(platformId);
                      const limit = getCharacterLimit(platformId);
                      const isOver = isOverLimit(platformId);
                      
                      return (
                        <div key={platformId} className="flex items-center justify-between text-sm">
                          <div className="flex items-center gap-2">
                            <span className="text-lg" aria-hidden="true">{platform?.icon}</span>
                            <span className="font-medium">{platform?.name}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <Progress 
                              value={(count / limit) * 100} 
                              className="w-20 h-2"
                              data-testid={`progress-${platformId}`}
                            />
                            <span className={cn(
                              "font-medium",
                              isOver ? "text-error-600" : "text-neutral-600"
                            )}>
                              {count}/{limit}
                            </span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              {/* Media Upload */}
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => fileInputRef.current?.click()}
                  data-testid="media-upload-button"
                >
                  <Image className="h-4 w-4 mr-2" />
                  Image
                </Button>
                <Button variant="outline" size="sm" data-testid="video-upload-button">
                  <Video className="h-4 w-4 mr-2" />
                  Video
                </Button>
                <Button variant="outline" size="sm" data-testid="link-button">
                  <Link className="h-4 w-4 mr-2" />
                  Link
                </Button>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  data-testid="file-input"
                />
              </div>
            </CardContent>
          </Card>

          {/* Brand Guide & Locale */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="card-premium">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Palette className="h-5 w-5" />
                  Brand Guide
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={brandGuide} onValueChange={setBrandGuide}>
                  <SelectTrigger data-testid="brand-guide-select">
                    <SelectValue placeholder="Select brand guide" />
                  </SelectTrigger>
                  <SelectContent>
                    {BRAND_GUIDES.map((guide) => (
                      <SelectItem key={guide.id} value={guide.id}>
                        <div>
                          <div className="font-medium">{guide.name}</div>
                          <div className="text-xs text-muted-foreground">{guide.tone}</div>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>

            <Card className="card-premium">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Languages className="h-5 w-5" />
                  Language
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Select value={locale} onValueChange={setLocale}>
                  <SelectTrigger data-testid="locale-select">
                    <SelectValue placeholder="Select language" />
                  </SelectTrigger>
                  <SelectContent>
                    {LOCALES.map((loc) => (
                      <SelectItem key={loc.id} value={loc.id}>
                        <div className="flex items-center gap-2">
                          <span>{loc.flag}</span>
                          <span>{loc.name}</span>
                        </div>
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </CardContent>
            </Card>
          </div>

          {/* Hashtags & Mentions */}
          {(hashtags.length > 0 || mentions.length > 0) && (
            <Card className="card-premium">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Hash className="h-5 w-5" />
                  Extracted Elements
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {hashtags.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium">Hashtags</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {hashtags.map((tag, index) => (
                          <Badge key={index} variant="secondary" className="text-brand-600">
                            {tag}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                  {mentions.length > 0 && (
                    <div>
                      <Label className="text-sm font-medium">Mentions</Label>
                      <div className="flex flex-wrap gap-2 mt-2">
                        {mentions.map((mention, index) => (
                          <Badge key={index} variant="secondary" className="text-success-600">
                            {mention}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="preview" className="space-y-6">
          <Card className="card-premium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Eye className="h-5 w-5" />
                Platform Previews
              </CardTitle>
            </CardHeader>
            <CardContent>
              {platforms.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Globe className="h-12 w-12 mx-auto mb-4" />
                  <p>Select platforms to see previews</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {platforms.map((platformId) => {
                    const platform = PLATFORMS.find(p => p.id === platformId);
                    return (
                      <div key={platformId} className="border rounded-xl p-4">
                        <div className="flex items-center gap-2 mb-4">
                          <span className="text-2xl">{platform?.icon}</span>
                          <span className="font-medium">{platform?.name}</span>
                        </div>
                        <div className="bg-neutral-50 rounded-lg p-4 min-h-[200px]">
                          <p className="text-sm whitespace-pre-wrap">{content || "No content yet..."}</p>
                        </div>
                        <div className="mt-2 text-xs text-muted-foreground">
                          {getCharacterCount(platformId)}/{getCharacterLimit(platformId)} characters
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="schedule" className="space-y-6">
          <Card className="card-premium">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5" />
                Schedule Settings
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="scheduled-date">Scheduled Date & Time</Label>
                <Input
                  id="scheduled-date"
                  type="datetime-local"
                  value={scheduledDate}
                  onChange={(e) => setScheduledDate(e.target.value)}
                  className="mt-2"
                  data-testid="scheduled-date-input"
                />
              </div>
              
              <div className="flex items-center space-x-2">
                <Switch
                  id="ai-optimized"
                  checked={aiOptimized}
                  onCheckedChange={setAiOptimized}
                  data-testid="ai-optimized-switch"
                />
                <Label htmlFor="ai-optimized">AI Optimized</Label>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-6">
        <Button
          variant="outline"
          onClick={handleSave}
          disabled={loading}
          data-testid="save-button"
        >
          <Save className="h-4 w-4 mr-2" />
          Save Draft
        </Button>
        
        <div className="flex items-center gap-3">
          <Button
            variant="outline"
            onClick={handleSchedule}
            disabled={loading || !scheduledDate}
            data-testid="schedule-button"
          >
            <Calendar className="h-4 w-4 mr-2" />
            Schedule
          </Button>
          <Button
            onClick={handlePublish}
            disabled={loading}
            className="btn-premium"
            data-testid="publish-button"
          >
            <Send className="h-4 w-4 mr-2" />
            Publish Now
          </Button>
        </div>
      </div>
    </div>
  );
}
