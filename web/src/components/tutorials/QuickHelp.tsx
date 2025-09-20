"use client";

import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { 
  HelpCircle, 
  X, 
  ExternalLink,
  BookOpen,
  Video,
  MessageCircle,
  Search
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface QuickHelpProps {
  context?: string;
  className?: string;
}

const helpResources = {
  'content-creation': [
    {
      title: 'AI Content Composer',
      description: 'Learn how to create content with AI assistance',
      type: 'tutorial',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/tutorials/content-creation'
    },
    {
      title: 'Brand Voice Setup',
      description: 'Configure your brand voice for consistent content',
      type: 'guide',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/guides/brand-voice'
    }
  ],
  'scheduling': [
    {
      title: 'Smart Scheduling',
      description: 'Learn about optimal posting times',
      type: 'tutorial',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/tutorials/scheduling'
    },
    {
      title: 'Calendar Management',
      description: 'Master the scheduling calendar',
      type: 'video',
      icon: <Video className="h-4 w-4" />,
      url: '/videos/calendar'
    }
  ],
  'analytics': [
    {
      title: 'Analytics Dashboard',
      description: 'Understand your performance metrics',
      type: 'tutorial',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/tutorials/analytics'
    },
    {
      title: 'Performance Insights',
      description: 'Learn how to optimize your content',
      type: 'guide',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/guides/optimization'
    }
  ],
  'integrations': [
    {
      title: 'Connect Social Accounts',
      description: 'Link your Facebook, Instagram, and LinkedIn',
      type: 'tutorial',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/tutorials/integrations'
    },
    {
      title: 'OAuth Setup Guide',
      description: 'Detailed setup instructions for each platform',
      type: 'guide',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/guides/oauth-setup'
    }
  ],
  'automation': [
    {
      title: 'Automation Rules',
      description: 'Set up automated workflows',
      type: 'tutorial',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/tutorials/automation'
    },
    {
      title: 'Workflow Examples',
      description: 'See real-world automation examples',
      type: 'guide',
      icon: <BookOpen className="h-4 w-4" />,
      url: '/guides/workflows'
    }
  ]
};

const generalHelp = [
  {
    title: 'Getting Started',
    description: 'Complete beginner tutorial',
    type: 'tutorial',
    icon: <BookOpen className="h-4 w-4" />,
    url: '/tutorials/getting-started'
  },
  {
    title: 'Video Tutorials',
    description: 'Watch step-by-step videos',
    type: 'video',
    icon: <Video className="h-4 w-4" />,
    url: '/videos'
  },
  {
    title: 'Contact Support',
    description: 'Get help from our team',
    type: 'support',
    icon: <MessageCircle className="h-4 w-4" />,
    url: '/support'
  },
  {
    title: 'Search Help',
    description: 'Find answers to your questions',
    type: 'search',
    icon: <Search className="h-4 w-4" />,
    url: '/help/search'
  }
];

export function QuickHelp({ context, className }: QuickHelpProps) {
  const [isOpen, setIsOpen] = useState(false);

  const getTypeColor = (type: string) => {
    switch (type) {
      case 'tutorial': return 'bg-blue-100 text-blue-800';
      case 'guide': return 'bg-green-100 text-green-800';
      case 'video': return 'bg-purple-100 text-purple-800';
      case 'support': return 'bg-orange-100 text-orange-800';
      case 'search': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const resources = context && helpResources[context as keyof typeof helpResources] 
    ? helpResources[context as keyof typeof helpResources]
    : generalHelp;

  return (
    <>
      <Button
        onClick={() => setIsOpen(true)}
        variant="ghost"
        size="sm"
        className={cn("flex items-center space-x-1", className)}
      >
        <HelpCircle className="h-4 w-4" />
        <span>Help</span>
      </Button>

      {isOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-2xl mx-4 max-h-[80vh] overflow-hidden">
            <CardHeader className="border-b">
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="text-lg">Quick Help</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {context ? `Help for ${context}` : 'Get help with VANTAGE AI'}
                  </p>
                </div>
                <Button variant="ghost" size="sm" onClick={() => setIsOpen(false)}>
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="p-6 overflow-y-auto max-h-[60vh]">
              <div className="space-y-4">
                {resources.map((resource, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() => {
                      // In a real app, this would navigate to the resource
                      console.log('Navigate to:', resource.url);
                      setIsOpen(false);
                    }}
                  >
                    <div className="flex items-center space-x-3">
                      {resource.icon}
                      <div>
                        <h4 className="font-medium">{resource.title}</h4>
                        <p className="text-sm text-muted-foreground">{resource.description}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge variant="outline" className={getTypeColor(resource.type)}>
                        {resource.type}
                      </Badge>
                      <ExternalLink className="h-4 w-4 text-muted-foreground" />
                    </div>
                  </div>
                ))}
              </div>
              
              {context && (
                <div className="mt-6 pt-4 border-t">
                  <h4 className="font-medium mb-3">General Help</h4>
                  <div className="space-y-2">
                    {generalHelp.slice(0, 2).map((resource, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                        onClick={() => {
                          console.log('Navigate to:', resource.url);
                          setIsOpen(false);
                        }}
                      >
                        <div className="flex items-center space-x-2">
                          {resource.icon}
                          <span className="text-sm">{resource.title}</span>
                        </div>
                        <ExternalLink className="h-3 w-3 text-muted-foreground" />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}
    </>
  );
}
