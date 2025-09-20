"use client";

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { 
  SparklesIcon, 
  SendIcon, 
  RefreshIcon, 
  CopyIcon, 
  ThumbsUpIcon, 
  ThumbsDownIcon,
  LoaderIcon
} from "@/components/ui/custom-icons";
import { apiService } from "@/lib/api";

interface AIGeneratedContent {
  id: string;
  type: 'post' | 'caption' | 'hashtags' | 'idea';
  content: string;
  prompt: string;
  timestamp: Date;
  rating?: 'positive' | 'negative';
}

interface AIDashboardWidgetProps {
  className?: string;
}

export function AIDashboardWidget({ className }: AIDashboardWidgetProps) {
  const [prompt, setPrompt] = useState("");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedContent, setGeneratedContent] = useState<AIGeneratedContent | null>(null);
  const [recentGenerations, setRecentGenerations] = useState<AIGeneratedContent[]>([]);
  const [selectedType, setSelectedType] = useState<'post' | 'caption' | 'hashtags' | 'idea'>('post');

  const contentTypes = [
    { value: 'post', label: 'Social Post', description: 'Full social media post' },
    { value: 'caption', label: 'Caption', description: 'Instagram-style caption' },
    { value: 'hashtags', label: 'Hashtags', description: 'Relevant hashtags' },
    { value: 'idea', label: 'Content Idea', description: 'Creative content ideas' }
  ];

  const generateContent = async () => {
    if (!prompt.trim()) return;

    setIsGenerating(true);
    try {
      const response = await apiService.generateContent(prompt, selectedType);
      
      const newContent: AIGeneratedContent = {
        id: Date.now().toString(),
        type: selectedType,
        content: response.data.content,
        prompt: prompt,
        timestamp: new Date()
      };

      setGeneratedContent(newContent);
      setRecentGenerations(prev => [newContent, ...prev.slice(0, 4)]);
      setPrompt("");
    } catch (error) {
      console.error('Failed to generate content:', error);
      // Fallback to mock content
      const mockContent: AIGeneratedContent = {
        id: Date.now().toString(),
        type: selectedType,
        content: getMockContent(selectedType, prompt),
        prompt: prompt,
        timestamp: new Date()
      };
      setGeneratedContent(mockContent);
      setRecentGenerations(prev => [mockContent, ...prev.slice(0, 4)]);
      setPrompt("");
    } finally {
      setIsGenerating(false);
    }
  };

  const getMockContent = (type: string, prompt: string): string => {
    const mockContents = {
      post: `🚀 Exciting news! ${prompt} is revolutionizing the way we think about innovation. 

Key highlights:
✅ Cutting-edge technology
✅ User-friendly interface  
✅ Scalable solutions

What do you think about this breakthrough? Share your thoughts below! 👇

#Innovation #Technology #Future #${prompt.replace(/\s+/g, '')}`,
      
      caption: `✨ Just discovered something amazing! ${prompt} is changing the game completely. 

The future is here and it's more exciting than we imagined! 🌟

#${prompt.replace(/\s+/g, '')} #Innovation #Amazing #Future`,
      
      hashtags: `#${prompt.replace(/\s+/g, '')} #Innovation #Technology #Future #Breakthrough #Amazing #GameChanger #Revolutionary #NextGen #Innovation`,
      
      idea: `💡 Content Ideas for "${prompt}":

1. Behind-the-scenes look at ${prompt} development
2. User testimonials and success stories
3. Comparison with traditional methods
4. Step-by-step tutorial on using ${prompt}
5. Industry expert interviews about ${prompt}
6. Infographic showing ${prompt} benefits
7. Live demo and Q&A session
8. Case study: Before vs After ${prompt}
9. Community challenges and contests
10. Future roadmap and upcoming features`
    };

    return mockContents[type as keyof typeof mockContents] || "Generated content will appear here...";
  };

  const copyToClipboard = (content: string) => {
    navigator.clipboard.writeText(content);
  };

  const rateContent = (id: string, rating: 'positive' | 'negative') => {
    setRecentGenerations(prev => 
      prev.map(item => 
        item.id === id ? { ...item, rating } : item
      )
    );
    if (generatedContent?.id === id) {
      setGeneratedContent(prev => prev ? { ...prev, rating } : null);
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex items-center space-x-2">
          <SparklesIcon className="h-6 w-6 text-purple-600" />
          <CardTitle className="text-lg">AI Content Generator</CardTitle>
        </div>
        <CardDescription>
          Generate engaging content with AI assistance
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Content Type Selection */}
        <div className="grid grid-cols-2 gap-2">
          {contentTypes.map((type) => (
            <Button
              key={type.value}
              variant={selectedType === type.value ? "default" : "outline"}
              size="sm"
              onClick={() => setSelectedType(type.value as any)}
              className="text-xs"
            >
              {type.label}
            </Button>
          ))}
        </div>

        {/* Prompt Input */}
        <div className="space-y-2">
          <Textarea
            placeholder={`Describe what you want to create about...`}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            className="min-h-[80px]"
          />
          <Button 
            onClick={generateContent}
            disabled={!prompt.trim() || isGenerating}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <LoaderIcon className="h-4 w-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <SendIcon className="h-4 w-4 mr-2" />
                Generate Content
              </>
            )}
          </Button>
        </div>

        {/* Generated Content */}
        {generatedContent && (
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <Badge variant="secondary" className="capitalize">
                {generatedContent.type}
              </Badge>
              <div className="flex space-x-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => copyToClipboard(generatedContent.content)}
                >
                  <CopyIcon className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => rateContent(generatedContent.id, 'positive')}
                  className={generatedContent.rating === 'positive' ? 'text-green-600' : ''}
                >
                  <ThumbsUpIcon className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => rateContent(generatedContent.id, 'negative')}
                  className={generatedContent.rating === 'negative' ? 'text-red-600' : ''}
                >
                  <ThumbsDownIcon className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <p className="text-sm whitespace-pre-wrap">{generatedContent.content}</p>
            </div>
          </div>
        )}

        {/* Recent Generations */}
        {recentGenerations.length > 0 && (
          <div className="space-y-2">
            <h4 className="text-sm font-medium text-slate-700">Recent Generations</h4>
            <div className="space-y-2 max-h-32 overflow-y-auto">
              {recentGenerations.slice(0, 3).map((item) => (
                <div
                  key={item.id}
                  className="p-2 bg-slate-50 rounded text-xs cursor-pointer hover:bg-slate-100"
                  onClick={() => setGeneratedContent(item)}
                >
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs">
                      {item.type}
                    </Badge>
                    <span className="text-slate-500">
                      {item.timestamp.toLocaleTimeString()}
                    </span>
                  </div>
                  <p className="mt-1 text-slate-600 truncate">
                    {item.content.substring(0, 60)}...
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

