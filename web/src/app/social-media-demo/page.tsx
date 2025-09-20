'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Facebook, Linkedin, MapPin, MessageSquare, Share2, Users } from 'lucide-react';

export default function SocialMediaDemo() {
  const [content, setContent] = useState('');
  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);

  const platforms = [
    {
      id: 'facebook',
      name: 'Facebook',
      icon: Facebook,
      color: 'bg-blue-500',
      description: 'Connect with your audience on Facebook',
      features: ['Text posts', 'Images & Videos', 'Scheduled posting', 'Engagement analytics']
    },
    {
      id: 'linkedin',
      name: 'LinkedIn',
      icon: Linkedin,
      color: 'bg-blue-600',
      description: 'Professional networking and B2B content',
      features: ['Professional posts', 'Company updates', 'Industry insights', 'B2B engagement']
    },
    {
      id: 'google',
      name: 'Google My Business',
      icon: MapPin,
      color: 'bg-green-500',
      description: 'Local business visibility and engagement',
      features: ['Local posts', 'Business updates', 'Call-to-action', 'Local SEO']
    }
  ];

  const togglePlatform = (platformId: string) => {
    setSelectedPlatforms(prev => 
      prev.includes(platformId) 
        ? prev.filter(id => id !== platformId)
        : [...prev, platformId]
    );
  };

  const handlePublish = async () => {
    if (!content.trim() || selectedPlatforms.length === 0) {
      alert('Please enter content and select at least one platform');
      return;
    }

    // Simulate publishing
    alert(`Publishing to ${selectedPlatforms.join(', ')} platforms...`);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Social Media Integration Demo
          </h1>
          <p className="text-xl text-gray-600">
            Experience the power of Vantage AI's social media integration
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Content Creation */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <MessageSquare className="h-5 w-5" />
                Create Content
              </CardTitle>
              <CardDescription>
                Write your post and select platforms to publish to
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Textarea
                placeholder="What's on your mind? Write your social media post here..."
                value={content}
                onChange={(e) => setContent(e.target.value)}
                className="min-h-[120px]"
              />
              
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-500">
                  {content.length} characters
                </span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    Preview
                  </Button>
                  <Button 
                    onClick={handlePublish}
                    disabled={!content.trim() || selectedPlatforms.length === 0}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    <Share2 className="h-4 w-4 mr-2" />
                    Publish
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Platform Selection */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Select Platforms
              </CardTitle>
              <CardDescription>
                Choose which platforms to publish your content to
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {platforms.map((platform) => {
                  const Icon = platform.icon;
                  const isSelected = selectedPlatforms.includes(platform.id);
                  
                  return (
                    <div
                      key={platform.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-all ${
                        isSelected 
                          ? 'border-green-500 bg-green-50' 
                          : 'border-gray-200 hover:border-gray-300'
                      }`}
                      onClick={() => togglePlatform(platform.id)}
                    >
                      <div className="flex items-start gap-3">
                        <div className={`p-2 rounded-lg ${platform.color}`}>
                          <Icon className="h-5 w-5 text-white" />
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h3 className="font-semibold">{platform.name}</h3>
                            {isSelected && (
                              <Badge variant="secondary" className="bg-green-100 text-green-800">
                                Selected
                              </Badge>
                            )}
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            {platform.description}
                          </p>
                          <div className="flex flex-wrap gap-1">
                            {platform.features.map((feature, index) => (
                              <Badge key={index} variant="outline" className="text-xs">
                                {feature}
                              </Badge>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* API Endpoints Demo */}
        <Card className="mt-8">
          <CardHeader>
            <CardTitle>Available API Endpoints</CardTitle>
            <CardDescription>
              Test the social media integration APIs directly
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Tabs defaultValue="oauth" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="oauth">OAuth</TabsTrigger>
                <TabsTrigger value="publishing">Publishing</TabsTrigger>
                <TabsTrigger value="webhooks">Webhooks</TabsTrigger>
              </TabsList>
              
              <TabsContent value="oauth" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">Facebook OAuth</h4>
                    <div className="space-y-2 text-sm">
                      <div>GET /api/v1/oauth/meta/authorize</div>
                      <div>GET /api/v1/oauth/meta/callback</div>
                      <div>GET /api/v1/oauth/meta/me</div>
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">LinkedIn OAuth</h4>
                    <div className="space-y-2 text-sm">
                      <div>GET /api/v1/oauth/linkedin/authorize</div>
                      <div>GET /api/v1/oauth/linkedin/callback</div>
                      <div>GET /api/v1/oauth/linkedin/accounts</div>
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">Google OAuth</h4>
                    <div className="space-y-2 text-sm">
                      <div>GET /api/v1/oauth/google/authorize</div>
                      <div>GET /api/v1/oauth/google/callback</div>
                      <div>GET /api/v1/oauth/google/accounts</div>
                    </div>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="publishing" className="space-y-4">
                <div className="p-4 border rounded-lg">
                  <h4 className="font-semibold mb-2">Publishing Endpoints</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <div>POST /api/v1/publishing/posts</div>
                      <div>GET /api/v1/publishing/posts</div>
                      <div>PUT /api/v1/publishing/posts/{"{id}"}</div>
                      <div>DELETE /api/v1/publishing/posts/{"{id}"}</div>
                    </div>
                    <div>
                      <div>POST /api/v1/publishing/schedule</div>
                      <div>GET /api/v1/publishing/status/{"{id}"}</div>
                      <div>POST /api/v1/publishing/preview</div>
                    </div>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="webhooks" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">Platform Webhooks</h4>
                    <div className="space-y-2 text-sm">
                      <div>POST /webhooks/meta</div>
                      <div>POST /webhooks/linkedin</div>
                      <div>POST /webhooks/google</div>
                      <div>POST /webhooks/whatsapp</div>
                    </div>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h4 className="font-semibold mb-2">Integration Webhooks</h4>
                    <div className="space-y-2 text-sm">
                      <div>POST /api/v1/integrations/webhooks/events</div>
                      <div>GET /api/v1/integrations/webhooks/events</div>
                      <div>POST /api/v1/integrations/webhooks/{"{id}"}/test</div>
                    </div>
                  </div>
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        {/* Status Indicators */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-medium">API Server</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">Running on port 8000</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                <span className="font-medium">Frontend</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">Running on port 3000</p>
            </CardContent>
          </Card>
          
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 bg-yellow-500 rounded-full"></div>
                <span className="font-medium">Database</span>
              </div>
              <p className="text-sm text-gray-600 mt-1">Connection required</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
