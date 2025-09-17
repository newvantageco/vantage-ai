"use client";

import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { 
  Sparkles, 
  Wand2, 
  Copy, 
  RefreshCw, 
  CheckCircle, 
  AlertCircle,
  Loader2,
  Hash,
  Type,
  Image,
  Lightbulb
} from "lucide-react";
import { useAIContent, useCaptionGenerator, usePostIdeas, useHashtagGenerator } from "@/hooks/useAIContent";

interface AIContentGeneratorProps {
  onContentGenerated?: (content: string, type: string) => void;
}

export function AIContentGenerator({ onContentGenerated }: AIContentGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [contentType, setContentType] = useState<'caption' | 'post' | 'idea' | 'hashtags' | 'alt_text'>('caption');
  const [brandVoice, setBrandVoice] = useState('');
  const [platform, setPlatform] = useState('');
  const [generatedContent, setGeneratedContent] = useState<string>('');
  const [copied, setCopied] = useState(false);

  const captionGenerator = useCaptionGenerator();
  const postIdeas = usePostIdeas();
  const hashtagGenerator = useHashtagGenerator();
  const aiContent = useAIContent();

  const handleGenerate = async () => {
    if (!prompt.trim()) return;

    try {
      let result;
      
      switch (contentType) {
        case 'caption':
          result = await captionGenerator.generateCaption(prompt, brandVoice, platform);
          break;
        case 'idea':
          result = await postIdeas.generateIdeas(prompt, platform, 5);
          break;
        case 'hashtags':
          result = await hashtagGenerator.generateHashtags(prompt, platform, 10);
          break;
        default:
          result = await aiContent.generateContent({
            prompt,
            type: contentType,
            brand_voice: brandVoice,
            platform,
          });
      }

      setGeneratedContent(result.content);
      onContentGenerated?.(result.content, contentType);
    } catch (error) {
      console.error('Failed to generate content:', error);
    }
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(generatedContent);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy content:', error);
    }
  };

  const getContentTypeIcon = (type: string) => {
    switch (type) {
      case 'caption': return <Type className="h-4 w-4" />;
      case 'post': return <Wand2 className="h-4 w-4" />;
      case 'idea': return <Lightbulb className="h-4 w-4" />;
      case 'hashtags': return <Hash className="h-4 w-4" />;
      case 'alt_text': return <Image className="h-4 w-4" />;
      default: return <Sparkles className="h-4 w-4" />;
    }
  };

  const getContentTypeLabel = (type: string) => {
    switch (type) {
      case 'caption': return 'Social Media Caption';
      case 'post': return 'Blog Post';
      case 'idea': return 'Content Ideas';
      case 'hashtags': return 'Hashtags';
      case 'alt_text': return 'Alt Text';
      default: return 'Content';
    }
  };

  const isLoading = captionGenerator.isGenerating || postIdeas.isGenerating || hashtagGenerator.isGenerating || aiContent.isGenerating;
  const error = captionGenerator.error || postIdeas.error || hashtagGenerator.error || aiContent.error;

  return (
    <div className="space-y-6">
      {/* Input Section */}
      <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Sparkles className="h-5 w-5 text-blue-600" />
            <span>AI Content Generator</span>
          </CardTitle>
          <CardDescription>
            Generate engaging content using AI. Describe what you want to create and let AI do the work.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="content-type">Content Type</Label>
              <Select value={contentType} onValueChange={(value: any) => setContentType(value)}>
                <SelectTrigger>
                  <SelectValue placeholder="Select content type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="caption">
                    <div className="flex items-center space-x-2">
                      <Type className="h-4 w-4" />
                      <span>Social Media Caption</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="post">
                    <div className="flex items-center space-x-2">
                      <Wand2 className="h-4 w-4" />
                      <span>Blog Post</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="idea">
                    <div className="flex items-center space-x-2">
                      <Lightbulb className="h-4 w-4" />
                      <span>Content Ideas</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="hashtags">
                    <div className="flex items-center space-x-2">
                      <Hash className="h-4 w-4" />
                      <span>Hashtags</span>
                    </div>
                  </SelectItem>
                  <SelectItem value="alt_text">
                    <div className="flex items-center space-x-2">
                      <Image className="h-4 w-4" />
                      <span>Alt Text</span>
                    </div>
                  </SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="platform">Platform (Optional)</Label>
              <Select value={platform} onValueChange={setPlatform}>
                <SelectTrigger>
                  <SelectValue placeholder="Select platform" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="instagram">Instagram</SelectItem>
                  <SelectItem value="twitter">Twitter</SelectItem>
                  <SelectItem value="facebook">Facebook</SelectItem>
                  <SelectItem value="linkedin">LinkedIn</SelectItem>
                  <SelectItem value="tiktok">TikTok</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="brand-voice">Brand Voice (Optional)</Label>
            <Input
              id="brand-voice"
              placeholder="e.g., Professional, Friendly, Casual, Authoritative"
              value={brandVoice}
              onChange={(e) => setBrandVoice(e.target.value)}
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="prompt">Describe what you want to create</Label>
            <Textarea
              id="prompt"
              placeholder="e.g., A post about our new product launch, focusing on innovation and customer benefits..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              rows={3}
            />
          </div>

          <Button 
            onClick={handleGenerate} 
            disabled={!prompt.trim() || isLoading}
            className="w-full bg-gradient-to-r from-blue-600 to-indigo-700 hover:from-blue-700 hover:to-indigo-800"
          >
            {isLoading ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Wand2 className="h-4 w-4 mr-2" />
                Generate {getContentTypeLabel(contentType)}
              </>
            )}
          </Button>

          {error && (
            <div className="flex items-center space-x-2 text-red-600 text-sm">
              <AlertCircle className="h-4 w-4" />
              <span>{error}</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Generated Content */}
      {generatedContent && (
        <Card className="border-0 shadow-lg bg-white/80 backdrop-blur-sm">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {getContentTypeIcon(contentType)}
                <CardTitle>Generated {getContentTypeLabel(contentType)}</CardTitle>
              </div>
              <div className="flex space-x-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCopy}
                  className="flex items-center space-x-1"
                >
                  {copied ? (
                    <>
                      <CheckCircle className="h-4 w-4" />
                      <span>Copied!</span>
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4" />
                      <span>Copy</span>
                    </>
                  )}
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setGeneratedContent('')}
                >
                  <RefreshCw className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-slate-50 rounded-lg p-4">
              <pre className="whitespace-pre-wrap text-sm text-slate-900 font-mono">
                {generatedContent}
              </pre>
            </div>
            
            {contentType === 'hashtags' && (
              <div className="mt-4">
                <Label className="text-sm font-medium text-slate-600">Hashtag Count</Label>
                <div className="mt-2">
                  <Badge variant="secondary" className="text-xs">
                    {generatedContent.split(' ').length} hashtags
                  </Badge>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
